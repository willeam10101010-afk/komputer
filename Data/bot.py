import os
import sys
import pandas as pd
import re
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Singleton guard
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
try:
    from bot_singleton import BotSingleton
    SINGLETON_AVAILABLE = True
except ImportError:
    SINGLETON_AVAILABLE = False
    print("⚠️  bot_singleton.py tidak ditemukan, singleton protection disabled")

TOKEN = "8135130155:AAE3h4TOiD4rQGWD3L9pbkuhpxMFL825fD0"
EXCEL_FILE = "data.xlsx"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo 👋! Kirimkan nomor HP internasional (+62..., +1..., dst) atau link.\n"
        "- Nomor HP akan dicek dan disimpan jika belum ada.\n"
        "- Link akan dicatat dan dibalas jika belum pernah dikirim.\n"
        "Gunakan /file untuk menerima file data.xlsx.",
        reply_to_message_id=update.message.message_id
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start → mulai bot\n/help → bantuan\n/file → kirim file data.xlsx",
        reply_to_message_id=update.message.message_id
    )

async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(EXCEL_FILE, "rb") as f:
            await update.message.reply_document(f, filename="data.xlsx", reply_to_message_id=update.message.message_id)
    except FileNotFoundError:
        await update.message.reply_text("File data.xlsx belum ada. Kirim nomor atau link dulu agar file dibuat.", reply_to_message_id=update.message.message_id)

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = f"{update.message.from_user.username or 'N/A'} ({update.message.from_user.first_name} {update.message.from_user.last_name or ''})".strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
        df["konten"] = df["konten"].astype(str).str.strip().str.lstrip("'")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["tipe", "konten", "user", "tanggal_jam"])

    if re.match(r"^\+?\d{8,15}$", text):
        tipe = "nomor_hp"
    elif re.match(r"https?://\S+|www\.\S+", text):
        tipe = "link"
    else:
        await update.message.reply_text("Format tidak dikenali. Kirim nomor HP (+62..., +1..., dst) atau link (https://...)", reply_to_message_id=update.message.message_id)
        return

    if (df["konten"].astype(str).str.strip() == text.strip()).any():
        row = df[df["konten"].astype(str).str.strip() == text.strip()].iloc[0]
        await update.message.reply_text(
            f"{tipe.replace('_', ' ').title()} ❌ ❌ ❌ sudah pernah dikirim oleh {row['user']} pada {row['tanggal_jam']}",
            reply_to_message_id=update.message.message_id
        )
    else:
        new_row = {"tipe": tipe, "konten": "'"+str(text).strip(), "user": user, "tanggal_jam": now}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        try:
            df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
            await update.message.reply_text(f"{tipe.replace('_', ' ').title()} ✅ ✅ ✅data berhasil disimpan ✅ ✅ ✅", reply_to_message_id=update.message.message_id)
        except Exception as e:
            await update.message.reply_text(f"Error menyimpan data: {str(e)}", reply_to_message_id=update.message.message_id)


def main():
    # Ensure event loop exists (Windows/Python 3.12+)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("file", send_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    singleton = None
    if SINGLETON_AVAILABLE:
        singleton = BotSingleton('data')
        if not singleton.acquire():
            print("❌ Data bot sudah berjalan! Keluar...")
            sys.exit(1)

    try:
        main()
    finally:
        if singleton:
            singleton.release()
