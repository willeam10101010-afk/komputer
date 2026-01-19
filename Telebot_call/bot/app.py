import os
import asyncio
import logging
import time
from datetime import datetime
from typing import Dict

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# Import singleton manager
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from bot_singleton import BotSingleton
    SINGLETON_AVAILABLE = True
except ImportError:
    SINGLETON_AVAILABLE = False
    print("⚠️  bot_singleton.py tidak ditemukan, singleton protection disabled")

# Load env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")

# In-memory store: user_id -> start_timestamp
user_start_times: Dict[int, float] = {}
# Track users currently in "call" state
active_call_users: set[int] = set()
MAX_ACTIVE = 4

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN tidak ditemukan di environment (.env)")
# Optional: GROUP_CHAT_ID dapat terdeteksi otomatis saat bot berada di grup
detected_group_id: int | None = None

# Persistence for detected group id
DETECTED_GROUP_FILE = os.path.join(os.path.dirname(__file__), '..', 'detected_group_id.json')
def load_detected_group_id():
    global detected_group_id
    try:
        import json
        p = os.path.normpath(DETECTED_GROUP_FILE)
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
                gid = data.get('group_id')
                if gid is not None:
                    detected_group_id = int(gid)
    except Exception:
        detected_group_id = None

def save_detected_group_id(gid: int | None):
    try:
        import json
        p = os.path.normpath(DETECTED_GROUP_FILE)
        dirp = os.path.dirname(p)
        os.makedirs(dirp, exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump({'group_id': gid}, f)
    except Exception:
        pass

# Load persisted group id on import
load_detected_group_id()

async def call_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return
    # Enforce max concurrent calls
    if user.id in active_call_users:
        await update.message.reply_text("Anda sudah memulai pencatatan. Gunakan /kembali_kursi saat kembali.")
        return

    if len(active_call_users) >= MAX_ACTIVE:
        await update.message.reply_text(
            "Maaf, kapasitas penuh: 4/4 orang sedang melakukan call. \n"
            "Silakan coba lagi nanti saat ada slot kosong."
        )
        return

    active_call_users.add(user.id)
    user_start_times[user.id] = time.time()

    now_str = datetime.now().strftime("%H:%M:%S")
    active_count = len(active_call_users)
    await update.message.reply_text(
        f"👋 {user.full_name}, pencatatan dimulai pada pukul {now_str} \n"
        f"Sedang call: {active_count}/{MAX_ACTIVE} orang\n"
        f"batas maximum {MAX_ACTIVE} orang untuk melakukan call",
        reply_markup=_main_keyboard()
    )

async def kembali_kursi_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return
    start_ts = user_start_times.get(user.id)
    if not start_ts:
        await update.message.reply_text("Belum ada catatan. Mulai dengan /call terlebih dahulu.")
        return

    end_ts = time.time()
    elapsed = int(end_ts - start_ts)
    del user_start_times[user.id]
    if user.id in active_call_users:
        active_call_users.remove(user.id)
    active_count = len(active_call_users)

    # Format durasi
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60
    seconds = elapsed % 60
    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    when_str = datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S")

    text = (
        f"⏱️ {user.first_name} kembali ke kursi.\n"
        f"Mulai: {when_str}\n"
        f"Durasi: {duration_str}\n"
        f"Sedang call: {active_count}/{MAX_ACTIVE} orang"
    )

    # Tentukan target grup: env > deteksi > fallback user
    target_group_id = None
    try:
        if GROUP_CHAT_ID:
            target_group_id = int(GROUP_CHAT_ID)
    except Exception:
        target_group_id = None
    if target_group_id is None and detected_group_id is not None:
        target_group_id = detected_group_id

    # Kirim ke grup atau fallback
    try:
        if target_group_id is not None:
            await context.bot.send_message(chat_id=target_group_id, text=text)
            await update.message.reply_text("Durasi dikirim ke grup. Terima kasih!")
        else:
            await update.message.reply_text(
                text + "\n\n(Info: GROUP_CHAT_ID belum terdeteksi. Pesan ini dikirim ke chat pribadi sebagai fallback.)"
            )
    except BadRequest as e:
        # Common case: Chat not found (bot removed from group or wrong ID)
        logging.warning(f"Failed to send to group {target_group_id}: {e}")
        await update.message.reply_text(
            f"Gagal kirim ke grup (id={target_group_id}): {e}.\n"
            "Solusi: pastikan bot adalah member grup dan memiliki izin kirim pesan, atau perbarui GROUP_CHAT_ID di .env"
        )
    except Exception as e:
        logging.exception(f"Unexpected error sending to group {target_group_id}")
        await update.message.reply_text(f"Gagal kirim ke grup: {e}")

def _main_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Call"), KeyboardButton(text="Kembali ke kursi")],
        [KeyboardButton(text="Buka GUI")],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Jika dipanggil di grup, deteksi dan simpan group id
    chat = update.effective_chat
    global detected_group_id
    if chat and chat.type in ("group", "supergroup"):
        detected_group_id = chat.id
        save_detected_group_id(detected_group_id)
    await update.message.reply_text(
        "Bot aktif. Gunakan tombol di bawah untuk mulai/selesai.",
        reply_markup=_main_keyboard()
    )

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Map GUI button text to commands
    text = (update.message.text or "").strip().lower()
    # Deteksi group id dari pesan biasa di grup
    chat = update.effective_chat
    global detected_group_id
    if chat and chat.type in ("group", "supergroup"):
        detected_group_id = chat.id
        save_detected_group_id(detected_group_id)
    if text == "call":
        await call_cmd(update, context)
    elif text == "kembali ke kursi":
        await kembali_kursi_cmd(update, context)
    elif text in ("menu", "buka gui"):
        await menu_cmd(update, context)

def _menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Call", callback_data="call")],
        [InlineKeyboardButton(text="Kembali ke kursi", callback_data="kembali")],
        [InlineKeyboardButton(text="Status", callback_data="status")],
    ])

def _status_text() -> str:
    active_count = len(active_call_users)
    slots_left = MAX_ACTIVE - active_count
    return (
        f"Status: {active_count}/{MAX_ACTIVE} aktif. Sisa slot: {slots_left}.\n"
        "Gunakan tombol untuk aksi cepat."
    )

async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Deteksi group id dari pemanggilan menu di grup
    chat = update.effective_chat
    global detected_group_id
    if chat and chat.type in ("group", "supergroup"):
        detected_group_id = chat.id
        save_detected_group_id(detected_group_id)
    await update.message.reply_text(_status_text(), reply_markup=_menu_inline())

async def menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    data = query.data
    # Answer callback to remove 'loading' state
    await query.answer()
    # Deteksi group id dari interaksi inline di grup
    chat = update.effective_chat
    global detected_group_id
    if chat and chat.type in ("group", "supergroup"):
        detected_group_id = chat.id
        save_detected_group_id(detected_group_id)
    # Route based on callback
    if data == "call":
        # Reuse existing handler with synthetic Update context
        await call_cmd(update, context)
    elif data == "kembali":
        await kembali_kursi_cmd(update, context)
    elif data == "status":
        await query.edit_message_text(_status_text(), reply_markup=_menu_inline())

def main():
    # Singleton check
    singleton = None
    if SINGLETON_AVAILABLE:
        singleton = BotSingleton('call')
        if not singleton.acquire():
            print("❌ Bot Call sudah berjalan! Keluar...")
            import sys
            sys.exit(1)
    
    try:
        # Set up event loop first (needed for Python 3.10+ on Windows)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            filename=os.path.join(os.path.dirname(__file__), '..', 'bot.log')
        )
        # Also log to console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logging.getLogger('').addHandler(console)

        logging.info("Starting Telebot Call application")
        app = Application.builder().token(BOT_TOKEN).build()

        async def _post_init(application: Application) -> None:
            await application.bot.set_my_commands([
                BotCommand("start", "Mulai dan tampilkan tombol"),
                BotCommand("menu", "Tampilkan menu aksi"),
                BotCommand("call", "Mulai pencatatan waktu"),
                BotCommand("kembali_kursi", "Selesai dan kirim durasi"),
            ])

        app.post_init = _post_init
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("menu", menu_cmd))
        app.add_handler(CommandHandler("call", call_cmd))
        app.add_handler(CommandHandler("kembali_kursi", kembali_kursi_cmd))
        # Simple text router to support one-click buttons
        from telegram.ext import MessageHandler, filters
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
        app.add_handler(CallbackQueryHandler(menu_cb))

        async def setgroup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            """Set group id. Usage: /setgroup or /setgroup <id>. If run inside a group, it sets that group's id."""
            chat = update.effective_chat
            global detected_group_id
            text = (update.message.text or "").strip()
            parts = text.split()
            if chat and chat.type in ("group", "supergroup") and len(parts) == 1:
                detected_group_id = chat.id
                save_detected_group_id(detected_group_id)
                await update.message.reply_text(f"GROUP_CHAT_ID diset ke grup ini: {detected_group_id}")
                return
            if len(parts) >= 2:
                try:
                    gid = int(parts[1])
                    detected_group_id = gid
                    save_detected_group_id(detected_group_id)
                    await update.message.reply_text(f"GROUP_CHAT_ID diset ke: {detected_group_id}")
                    return
                except Exception:
                    await update.message.reply_text("Argumen tidak valid. Gunakan: /setgroup <group_id>")
                    return
            await update.message.reply_text("Gunakan: /setgroup di dalam grup atau /setgroup <group_id>")

        async def showgroup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            gid = detected_group_id
            env_gid = GROUP_CHAT_ID or "(kosong)"
            await update.message.reply_text(f"Detected: {gid}\nENV GROUP_CHAT_ID: {env_gid}")

        app.add_handler(CommandHandler("setgroup", setgroup_cmd))
        app.add_handler(CommandHandler("showgroup", showgroup_cmd))

        logging.info("Running polling...")
        try:
            app.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None, drop_pending_updates=True)
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
        except Exception as e:
            logging.error(f"Polling error: {e}")
            raise
    finally:
        if singleton:
            singleton.release()


if __name__ == "__main__":
    main()
