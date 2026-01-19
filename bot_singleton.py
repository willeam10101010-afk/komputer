"""
Bot Singleton Manager - Mencegah multiple instances bot berjalan bersamaan
Menggunakan file lock untuk memastikan hanya 1 instance per bot
"""
import os
import sys
import time
import json
from pathlib import Path

try:
    import psutil
except ImportError as exc:
    raise ImportError("psutil diperlukan untuk bot_singleton. Install: pip install psutil") from exc


class BotSingleton:
    """Singleton pattern untuk mencegah bot duplikat"""

    def __init__(self, bot_name: str, base_dir: str | None = None):
        self.bot_name = bot_name
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.lock_file = os.path.join(self.base_dir, f'.{bot_name}_bot.lock')
        self.pid = os.getpid()
        self.locked = False

    def acquire(self, force: bool = False) -> bool:
        """Dapatkan lock untuk bot ini."""
        if os.path.exists(self.lock_file):
            try:
                with open(self.lock_file, 'r') as f:
                    lock_data = json.load(f)
                old_pid = lock_data.get('pid')
                old_time = lock_data.get('timestamp')

                if old_pid and self._is_process_running(old_pid):
                    if not force:
                        print(f"❌ Bot {self.bot_name} sudah berjalan (PID: {old_pid})")
                        print(f"   Lock created: {old_time}")
                        return False
                    else:
                        print(f"⚠️  FORCE MODE: Menghapus lock lama (PID: {old_pid})")
                        os.remove(self.lock_file)
                else:
                    print(f"🧹 Membersihkan lock lama (PID {old_pid} tidak aktif)")
                    os.remove(self.lock_file)
            except Exception as e:
                print(f"⚠️  Error membaca lock file: {e}")
                if force and os.path.exists(self.lock_file):
                    os.remove(self.lock_file)

        try:
            lock_data = {
                'bot_name': self.bot_name,
                'pid': self.pid,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'hostname': os.environ.get('COMPUTERNAME', 'unknown')
            }
            with open(self.lock_file, 'w') as f:
                json.dump(lock_data, f, indent=2)
            self.locked = True
            print(f"✅ Lock acquired untuk bot {self.bot_name} (PID: {self.pid})")
            return True
        except Exception as e:
            print(f"❌ Gagal membuat lock file: {e}")
            return False

    def release(self):
        """Lepaskan lock"""
        if self.locked and os.path.exists(self.lock_file):
            try:
                with open(self.lock_file, 'r') as f:
                    lock_data = json.load(f)
                if lock_data.get('pid') == self.pid:
                    os.remove(self.lock_file)
                    self.locked = False
                    print(f"🔓 Lock released untuk bot {self.bot_name}")
                else:
                    print("⚠️  Lock file bukan milik process ini")
            except Exception as e:
                print(f"⚠️  Error melepas lock: {e}")

    def _is_process_running(self, pid: int) -> bool:
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f"Bot {self.bot_name} sudah berjalan!")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


def check_all_bots(base_dir: str | None = None) -> dict:
    base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
    bot_names = ['absen', 'call', 'web3', 'socks', 'data', 'web_dashboard']

    status = {}
    for bot_name in bot_names:
        lock_file = os.path.join(base_dir, f'.{bot_name}_bot.lock')
        if os.path.exists(lock_file):
            try:
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                pid = lock_data.get('pid')
                is_running = BotSingleton(bot_name, base_dir)._is_process_running(pid)
                status[bot_name] = {
                    'running': is_running,
                    'pid': pid,
                    'timestamp': lock_data.get('timestamp'),
                    'stale': not is_running
                }
            except Exception:
                status[bot_name] = {'running': False, 'error': True}
        else:
            status[bot_name] = {'running': False}

    return status


def cleanup_stale_locks(base_dir: str | None = None) -> int:
    base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
    lock_files = Path(base_dir).glob('.*_bot.lock')
    cleaned = 0

    for lock_file in lock_files:
        try:
            with open(lock_file, 'r') as f:
                lock_data = json.load(f)
            pid = lock_data.get('pid')
            bot_name = lock_data.get('bot_name', 'unknown')

            try:
                process = psutil.Process(pid)
                if not process.is_running():
                    raise psutil.NoSuchProcess(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                os.remove(lock_file)
                print(f"🧹 Cleaned stale lock: {bot_name} (PID {pid})")
                cleaned += 1
        except Exception as e:
            print(f"⚠️  Error processing {lock_file}: {e}")

    return cleaned


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Bot Singleton Manager')
    parser.add_argument('command', choices=['status', 'cleanup'], help='Command to execute')
    args = parser.parse_args()

    if args.command == 'status':
        print("\n" + "="*50)
        print("BOT STATUS")
        print("="*50)
        status = check_all_bots()
        for bot_name, info in status.items():
            if info.get('running'):
                print(f"✅ {bot_name:15} - Running (PID: {info.get('pid')})")
                print(f"   Started: {info.get('timestamp')}")
            elif info.get('stale'):
                print(f"⚠️  {bot_name:15} - Stale lock (PID: {info.get('pid')} tidak berjalan)")
            else:
                print(f"⚫ {bot_name:15} - Not running")
        print("="*50)
    elif args.command == 'cleanup':
        print("\n" + "="*50)
        print("CLEANUP STALE LOCKS")
        print("="*50)
        cleaned = cleanup_stale_locks()
        print(f"\n✅ Cleaned {cleaned} stale lock(s)")
        print("="*50)
