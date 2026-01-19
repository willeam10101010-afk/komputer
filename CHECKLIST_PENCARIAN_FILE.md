# ✅ CHECKLIST: Cara Mencari File yang Hilang

## 📝 LANGKAH-LANGKAH PENCARIAN:

### 1. Cek Folder Backup di Komputer Anda
- [ ] Cek folder `Backup/` atau `Old Files/`
- [ ] Cek folder `Downloads/`
- [ ] Cek `Desktop/` atau `Documents/`
- [ ] Cek folder dengan nama serupa (misalnya: `komputer_old`, `komputer_backup`)

### 2. Cek Recycle Bin / Trash
- [ ] Windows: Cek **Recycle Bin**
- [ ] Mac: Cek **Trash**
- [ ] Linux: Cek **Trash** atau `~/.local/share/Trash/`

### 3. Cari File Menggunakan Search
**Windows:**
```
Win + S (Search)
Ketik: "main.py WEB3"
Ketik: "socks5_monitor.py"
```

**Mac:**
```
Cmd + Space (Spotlight)
Ketik: "main.py"
Ketik: "socks5_monitor.py"
```

**Linux:**
```bash
find ~ -name "main.py" -o -name "socks5_monitor.py"
```

### 4. Cek History Git (Jika Ada)
```bash
cd /path/to/komputer
git log --all --full-history -- WEB3/*.py
git log --all --full-history -- socks/*.py
```

### 5. Cek Versi Sebelumnya (Windows)
- [ ] Klik kanan folder WEB3/ → Properties → Previous Versions
- [ ] Klik kanan folder socks/ → Properties → Previous Versions
- [ ] Restore jika ada versi sebelumnya

### 6. Cek Cloud Storage / Backup Online
- [ ] Google Drive
- [ ] Dropbox
- [ ] OneDrive
- [ ] iCloud
- [ ] GitHub (cek branches lain)

### 7. Cek IDE / Editor History
- [ ] VS Code: File → Open Recent
- [ ] PyCharm: File → Recent Files
- [ ] Sublime Text: File → Open Recent
- [ ] Cek `.vscode/` atau `.idea/` untuk file history

---

## 🔍 FILE YANG DICARI:

### Prioritas TINGGI:
1. **WEB3/main.py** (atau nama file lain di folder WEB3/)
   - Kemungkinan nama: `gsheet_bot.py`, `web3_bot.py`, `app.py`, `script.py`
   - Fungsi: Bot untuk Google Sheets atau Web3

2. **socks/main.py**
   - Fungsi: Entry point untuk SOCKS proxy/monitor

3. **socks/socks5_monitor.py**
   - Fungsi: Monitor untuk SOCKS5 proxy

### Prioritas RENDAH:
4. File-file di **Project/** (jika penting)

---

## 💾 SETELAH FILE DITEMUKAN:

### 1. Copy ke Lokasi yang Benar
```bash
# Copy ke folder WEB3
cp /path/to/found/main.py ~/komputer/WEB3/main.py

# Copy ke folder socks
cp /path/to/found/main.py ~/komputer/socks/main.py
cp /path/to/found/socks5_monitor.py ~/komputer/socks/socks5_monitor.py
```

### 2. Commit ke Git
```bash
cd ~/komputer
git add WEB3/*.py
git add socks/*.py
git commit -m "Add missing Python files"
git push
```

### 3. Verifikasi
```bash
# Cek file sudah ada
ls -la WEB3/*.py
ls -la socks/*.py

# Jalankan untuk test (opsional)
cd WEB3
python main.py --help

cd ../socks
python main.py --help
```

---

## 🚫 JIKA FILE TIDAK DITEMUKAN:

### Opsi 1: Decompile dari .pyc (Tidak Ideal)
File `.pyc` di `socks/__pycache__/` bisa di-decompile:
```bash
pip install uncompyle6
uncompyle6 socks/__pycache__/main.cpython-314.pyc > socks/main.py
uncompyle6 socks/__pycache__/socks5_monitor.cpython-315.pyc > socks/socks5_monitor.py
```

⚠️ **CATATAN:** Hasil decompile tidak sempurna (missing comments, formatting buruk)

### Opsi 2: Buat Ulang Berdasarkan Requirements
Lihat packages di virtual environment untuk mengetahui fungsi:

**WEB3:**
- Packages: `gspread`, `google-auth-oauthlib` → Kemungkinan bot Google Sheets
- Template bisa dibuat ulang

**socks:**
- Packages: `PySocks`, `psutil`, `requests` → Kemungkinan SOCKS proxy monitor
- Template bisa dibuat ulang

### Opsi 3: Restore dari Backup Eksternal
- [ ] Cek hard drive eksternal
- [ ] Cek USB flash drive
- [ ] Cek backup cloud
- [ ] Tanya teman/kolega yang pernah punya copy

---

## 📊 PROGRESS TRACKER:

### WEB3/
- [ ] File ditemukan
- [ ] File di-copy ke folder
- [ ] File di-commit ke Git
- [ ] File di-verify working

### socks/
- [ ] main.py ditemukan
- [ ] socks5_monitor.py ditemukan
- [ ] Files di-copy ke folder
- [ ] Files di-commit ke Git
- [ ] Files di-verify working

### Project/
- [ ] Tentukan apakah masih diperlukan
- [ ] Jika ya: restore atau buat baru
- [ ] Jika tidak: hapus folder

---

## 📞 BUTUH BANTUAN?

Jika file tidak ditemukan setelah semua langkah di atas:
1. Buka issue di GitHub repository
2. Jelaskan apa yang sudah dicoba
3. Sertakan informasi packages di virtual environment
4. Tim bisa membantu recreate file berdasarkan dependencies

---

**Good luck! 🍀**

Checklist ini akan membantu Anda menemukan file yang hilang secara sistematis.
