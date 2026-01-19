# 🚀 Auto-Upload System untuk GitHub

Sistem otomatis untuk memonitor perubahan file di komputer dan langsung upload ke repository GitHub `willeam10101010-afk/komputer`.

## 📋 Deskripsi

Auto-upload system ini adalah tool yang akan memantau setiap perubahan file di folder project Anda dan secara otomatis melakukan commit & push ke GitHub repository. Sangat berguna untuk:

- ✅ Backup otomatis kode Anda
- ✅ Menyimpan history perubahan secara real-time
- ✅ Tidak perlu manual git add/commit/push
- ✅ Mencegah kehilangan data

## 🔧 Prerequisites

Sebelum menggunakan tool ini, pastikan Anda sudah memiliki:

1. **Node.js** (versi 14 atau lebih baru)
   - Download: https://nodejs.org/
   - Cek versi: `node --version`

2. **Git** (versi 2.0 atau lebih baru)
   - Download: https://git-scm.com/
   - Cek versi: `git --version`

3. **GitHub Account**
   - Daftar gratis di: https://github.com/

4. **GitHub Personal Access Token (PAT)**
   - Diperlukan untuk authentication
   - Panduan lengkap ada di `SETUP-GUIDE.md`

## 📥 Instalasi

### 1. Clone atau Download Repository

```bash
git clone https://github.com/willeam10101010-afk/komputer.git
cd komputer
```

### 2. Install Dependencies

```bash
npm install
```

Perintah ini akan menginstall:
- `chokidar` - Library untuk file watching

### 3. Setup GitHub Authentication

**PENTING**: Anda perlu setup GitHub authentication agar bisa push ke repository.

Lihat panduan lengkap di **SETUP-GUIDE.md** untuk cara setup Personal Access Token (PAT).

### 4. Jalankan Setup Wizard

```bash
npm run setup
```

Setup wizard akan membantu Anda:
- Inisialisasi git repository (jika belum ada)
- Setup git user config
- Setup remote origin
- Membuat .gitignore
- Test koneksi ke GitHub

## 🚀 Cara Menggunakan

### Menjalankan Auto-Upload

Ada beberapa cara untuk menjalankan auto-upload:

**1. Menggunakan npm:**
```bash
npm start
```

**2. Menggunakan Node.js langsung:**
```bash
node auto-upload.js
```

**3. Menggunakan batch file (Windows):**
```batch
auto-upload.bat
```

**4. Menggunakan shell script (Linux/Mac):**
```bash
./auto-upload.sh
```

### Output yang Diharapkan

Setelah menjalankan, Anda akan melihat:

```
╔════════════════════════════════════════╗
║   🚀 AUTO UPLOAD TO GITHUB AKTIF 🚀   ║
╚════════════════════════════════════════╝

📂 Folder    : /path/to/project
📦 Repository: willeam10101010-afk/komputer
🌿 Branch    : main
⏱️  Delay     : 10 detik

────────────────────────────────────────

👀 Monitoring dimulai... (Tekan Ctrl+C untuk berhenti)
```

### Menghentikan Auto-Upload

Tekan `Ctrl+C` pada terminal. Script akan:
1. Menghentikan monitoring
2. Upload perubahan yang masih tertunda
3. Keluar dengan graceful

### Background Mode (Opsional)

Jika Anda ingin menjalankan di background:

**Linux/Mac:**
```bash
nohup node auto-upload.js > auto-upload.log 2>&1 &
```

**Windows (dengan PowerShell):**
```powershell
Start-Process node -ArgumentList "auto-upload.js" -WindowStyle Hidden
```

## ⚙️ Konfigurasi

### Mengubah Delay Upload

Edit file `auto-upload.js`, cari baris:

```javascript
const CONFIG = {
  uploadDelay: 10000, // 10 detik (dalam milidetik)
  // ...
};
```

Ubah nilai `uploadDelay` sesuai kebutuhan (dalam milidetik):
- 5 detik = 5000
- 30 detik = 30000
- 1 menit = 60000

### Mengubah File yang Di-Ignore

Edit array `ignoredPatterns` di `auto-upload.js`:

```javascript
ignoredPatterns: [
  '**/node_modules/**',
  '**/.git/**',
  '**/dist/**',
  '**/build/**',
  '**/.env*',
  '**/*.log',
  // Tambahkan pattern Anda di sini
]
```

Atau edit file `.gitignore` untuk ignore permanent.

### Mengubah Branch

Edit `CONFIG.branch` di `auto-upload.js`:

```javascript
const CONFIG = {
  branch: 'main', // Ganti dengan branch Anda
  // ...
};
```

## 🔍 Troubleshooting

### 1. Error: "Authentication failed"

**Masalah**: GitHub menolak push karena authentication gagal.

**Solusi**:
1. Pastikan Personal Access Token (PAT) sudah dibuat
2. Setup git credential helper:
   ```bash
   git config --global credential.helper store
   ```
3. Jalankan `git push` manual sekali, masukkan username dan PAT
4. Baca `SETUP-GUIDE.md` untuk panduan detail

### 2. Error: "Push rejected"

**Masalah**: Ada konflik atau remote lebih baru dari local.

**Solusi**:
1. Stop auto-upload (Ctrl+C)
2. Pull perubahan terbaru:
   ```bash
   git pull origin main
   ```
3. Resolve konflik jika ada
4. Jalankan auto-upload lagi

### 3. File Tidak Ter-Monitor

**Masalah**: Perubahan file tidak terdeteksi.

**Solusi**:
1. Cek apakah file ter-ignore di `.gitignore`
2. Cek pattern di `CONFIG.ignoredPatterns`
3. Restart auto-upload script

### 4. Error: "Git repository tidak ditemukan"

**Masalah**: Folder bukan git repository.

**Solusi**:
```bash
npm run setup
```

Atau manual:
```bash
git init
git remote add origin https://github.com/willeam10101010-afk/komputer.git
```

### 5. High CPU/Memory Usage

**Masalah**: Script consume banyak resource.

**Solusi**:
1. Tambahkan lebih banyak pattern ke `ignoredPatterns`
2. Tingkatkan `uploadDelay` untuk mengurangi frekuensi upload
3. Pastikan tidak memonitor folder besar (node_modules, dll)

## 💡 Tips & Best Practices

### 1. Gunakan .gitignore dengan Baik

Jangan upload file yang tidak perlu:
- Dependencies (`node_modules`)
- Build artifacts (`dist`, `build`)
- Environment files (`.env`)
- Log files (`*.log`)
- OS files (`.DS_Store`, `Thumbs.db`)

### 2. Delay yang Tepat

- **Development aktif**: 10-30 detik (default: 10)
- **Background backup**: 60-300 detik
- **Jarang edit**: 300+ detik

### 3. Commit Message

Auto-upload menggunakan format:
```
Auto-upload: Update files [2026-01-19 14:23:45]
```

Jika ingin custom, edit function `uploadToGitHub()` di `auto-upload.js`.

### 4. Security

⚠️ **JANGAN** commit file sensitive:
- API keys
- Password
- Private keys
- Credentials

Selalu tambahkan ke `.gitignore`!

### 5. Monitoring Log

Untuk save log ke file:
```bash
node auto-upload.js > upload.log 2>&1
```

## ❓ FAQ

**Q: Apakah aman menggunakan auto-upload?**  
A: Ya, asalkan Anda menggunakan .gitignore dengan benar untuk exclude file sensitive.

**Q: Berapa banyak space yang dibutuhkan?**  
A: Minimal, hanya ~2MB untuk dependencies (chokidar).

**Q: Apakah bisa digunakan untuk project besar?**  
A: Ya, tapi pastikan ignore folder besar seperti node_modules, build artifacts, dll.

**Q: Bagaimana jika internet terputus?**  
A: Script akan menampilkan error tapi tetap monitoring. Saat internet kembali, upload otomatis akan dilanjutkan.

**Q: Bisa untuk multiple repository?**  
A: Ya, jalankan instance terpisah untuk setiap repository di folder berbeda.

**Q: Apakah perlu running terus?**  
A: Tidak harus. Anda bisa jalankan saat bekerja dan stop saat tidak perlu.

**Q: Bagaimana cara uninstall?**  
A: Cukup stop script dan hapus folder project. Tidak ada perubahan system.

## 📝 License

MIT License - Bebas digunakan untuk keperluan apapun.

## 👨‍💻 Author

**willeam10101010-afk**

## 🤝 Kontribusi

Kontribusi, issues, dan feature requests sangat welcome!

## 📞 Support

Jika mengalami masalah:
1. Baca `SETUP-GUIDE.md`
2. Cek section Troubleshooting di atas
3. Buka issue di GitHub repository

---

**Happy Coding! 🚀**