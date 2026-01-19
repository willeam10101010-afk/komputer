# 📖 Panduan Setup Detail - Auto-Upload System

Panduan step-by-step untuk setup auto-upload system pertama kali, termasuk cara membuat GitHub Personal Access Token (PAT) dan konfigurasi git credential.

## 📑 Daftar Isi

1. [Persiapan Awal](#persiapan-awal)
2. [Membuat Personal Access Token (PAT)](#membuat-personal-access-token-pat)
3. [Setup Git Credential Helper](#setup-git-credential-helper)
4. [Initial Git Configuration](#initial-git-configuration)
5. [First Push Setup](#first-push-setup)
6. [Verifikasi Setup](#verifikasi-setup)
7. [Troubleshooting](#troubleshooting)

---

## 1. Persiapan Awal

### Install Prerequisites

**Node.js:**
1. Kunjungi https://nodejs.org/
2. Download versi LTS (Long Term Support)
3. Install dengan mengikuti wizard
4. Verifikasi instalasi:
   ```bash
   node --version
   npm --version
   ```

**Git:**
1. Kunjungi https://git-scm.com/
2. Download sesuai OS Anda (Windows/Mac/Linux)
3. Install dengan default settings
4. Verifikasi instalasi:
   ```bash
   git --version
   ```

### Clone Repository

```bash
# Clone repository
git clone https://github.com/willeam10101010-afk/komputer.git

# Masuk ke folder
cd komputer

# Install dependencies
npm install
```

---

## 2. Membuat Personal Access Token (PAT)

Personal Access Token diperlukan untuk authentication ke GitHub tanpa password.

### Langkah-langkah:

**Step 1:** Login ke GitHub
- Buka https://github.com/
- Login dengan akun Anda

**Step 2:** Buka Settings
- Klik foto profil di kanan atas
- Pilih **Settings**

**Step 3:** Buka Developer Settings
- Scroll ke bawah di sidebar kiri
- Klik **Developer settings**

**Step 4:** Buat Token Baru
- Klik **Personal access tokens**
- Pilih **Tokens (classic)**
- Klik **Generate new token**
- Pilih **Generate new token (classic)**

**Step 5:** Konfigurasi Token
- **Note**: Beri nama, contoh: "komputer-auto-upload"
- **Expiration**: Pilih durasi (recommended: 90 days atau No expiration)
- **Select scopes**: Centang yang diperlukan:
  - ✅ **repo** (Full control of private repositories)
    - ✅ repo:status
    - ✅ repo_deployment
    - ✅ public_repo
    - ✅ repo:invite
    - ✅ security_events

**Step 6:** Generate dan Simpan Token
- Klik **Generate token** di bawah
- **PENTING**: Copy token yang muncul dan simpan di tempat aman
- Token hanya ditampilkan SEKALI, jika hilang harus buat baru

**Contoh Token:**
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ **JANGAN share token ke siapapun!**

---

## 3. Setup Git Credential Helper

Git credential helper akan menyimpan username dan token Anda sehingga tidak perlu input setiap kali push.

### Windows

**Menggunakan Git Credential Manager (Recommended):**

Git Credential Manager biasanya sudah terinstall dengan Git for Windows.

```bash
# Cek apakah sudah ada
git config --global credential.helper

# Jika belum, set credential helper
git config --global credential.helper manager
```

**Atau menggunakan store (alternatif):**

```bash
git config --global credential.helper store
```

⚠️ **Note**: `store` menyimpan credentials dalam plain text di `~/.git-credentials`

### Linux

```bash
# Setup credential helper dengan cache (15 menit)
git config --global credential.helper cache

# Atau dengan cache timeout custom (1 jam = 3600 detik)
git config --global credential.helper 'cache --timeout=3600'

# Atau permanent storage
git config --global credential.helper store
```

### Mac

```bash
# Mac menggunakan Keychain
git config --global credential.helper osxkeychain
```

### Verifikasi

```bash
git config --global credential.helper
```

Harus menampilkan: `manager`, `store`, `cache`, atau `osxkeychain`

---

## 4. Initial Git Configuration

Setup informasi user git Anda.

```bash
# Set nama Anda
git config --global user.name "Nama Anda"

# Set email Anda
git config --global user.email "email@example.com"

# Verifikasi
git config --global user.name
git config --global user.email
```

**Atau jalankan setup wizard:**

```bash
npm run setup
```

Setup wizard akan memandu Anda melalui semua konfigurasi.

---

## 5. First Push Setup

Langkah untuk first push dan input credentials.

### Manual First Push

**Step 1:** Pastikan ada remote origin

```bash
# Cek remote
git remote -v

# Jika belum ada, tambahkan
git remote add origin https://github.com/willeam10101010-afk/komputer.git
```

**Step 2:** Buat perubahan dan commit

```bash
# Cek status
git status

# Add files
git add .

# Commit
git commit -m "Initial setup"
```

**Step 3:** Push pertama kali

```bash
# Push ke main branch
git push -u origin main
```

**Step 4:** Input Credentials

Saat pertama kali push, Git akan meminta credentials:

```
Username for 'https://github.com': willeam10101010-afk
Password for 'https://willeam10101010-afk@github.com':
```

⚠️ **PENTING**: 
- **Username**: Isi dengan GitHub username Anda
- **Password**: **JANGAN** isi dengan password GitHub Anda!
  - Isi dengan **Personal Access Token (PAT)** yang sudah dibuat tadi
  - Paste token (ghp_xxxxx...)

Credentials akan disimpan oleh credential helper dan tidak perlu input lagi untuk push berikutnya.

---

## 6. Verifikasi Setup

### Test Koneksi

```bash
# Test koneksi ke GitHub
git ls-remote origin
```

Jika berhasil, akan menampilkan daftar refs.

### Test Auto-Upload

```bash
# Jalankan auto-upload
npm start
```

Jika setup benar, akan muncul:

```
╔════════════════════════════════════════╗
║   🚀 AUTO UPLOAD TO GITHUB AKTIF 🚀   ║
╚════════════════════════════════════════╝

📂 Folder    : /path/to/komputer
📦 Repository: willeam10101010-afk/komputer
🌿 Branch    : main
⏱️  Delay     : 10 detik

────────────────────────────────────────

👀 Monitoring dimulai... (Tekan Ctrl+C untuk berhenti)
```

### Test File Changes

1. Buat file baru: `echo "test" > test.txt`
2. Tunggu ~10 detik
3. Auto-upload akan mendeteksi dan upload file

Output yang diharapkan:

```
➕ [14:23:45] Ditambahkan: test.txt

📦 Memproses 1 file...

📝 Perubahan:
   ✏️  test.txt

📤 Uploading ke GitHub...
✅ Upload berhasil! [2026-01-19 14:23:57]
```

4. Cek GitHub repository, file `test.txt` harus ada

---

## 7. Troubleshooting

### Problem: "Authentication failed"

**Penyebab**: Credentials salah atau expired.

**Solusi**:

```bash
# Clear stored credentials
# Windows
cmdkey /delete:git:https://github.com

# Linux/Mac
git credential-cache exit

# Generate token baru di GitHub
# Push manual lagi untuk re-input credentials
git push origin main
```

### Problem: "Support for password authentication was removed"

**Penyebab**: Menggunakan password GitHub, bukan PAT.

**Solusi**: Gunakan Personal Access Token (PAT) sebagai password, bukan password GitHub Anda.

### Problem: "Could not resolve host 'github.com'"

**Penyebab**: Tidak ada koneksi internet atau DNS issue.

**Solusi**:
1. Cek koneksi internet
2. Ping github.com: `ping github.com`
3. Coba pakai DNS Google (8.8.8.8)

### Problem: "Permission denied (publickey)"

**Penyebab**: Menggunakan SSH URL tapi tidak ada SSH key.

**Solusi**:
```bash
# Ganti remote ke HTTPS
git remote set-url origin https://github.com/willeam10101010-afk/komputer.git
```

### Problem: Token Expired

**Penyebab**: Token sudah kadaluarsa.

**Solusi**:
1. Generate token baru di GitHub
2. Clear credential cache
3. Push manual untuk input token baru

### Problem: "Repository not found"

**Penyebab**: Repository tidak ada atau tidak punya akses.

**Solusi**:
1. Cek URL repository benar
2. Pastikan sudah login dengan akun yang benar
3. Pastikan repository `willeam10101010-afk/komputer` accessible

---

## 📝 Quick Reference

### Command Cheat Sheet

```bash
# Install dependencies
npm install

# Run setup wizard
npm run setup

# Start auto-upload
npm start

# Test connection
git ls-remote origin

# Check git config
git config --list

# Clear credentials (if needed)
git credential-cache exit  # Linux/Mac
cmdkey /delete:git:https://github.com  # Windows
```

### Personal Access Token Permissions

Minimal permissions needed:
- ✅ **repo** (full control)

Optional tapi recommended:
- ✅ **workflow** (jika pakai GitHub Actions)

### Git Credential Helper Options

| OS | Recommended Helper |
|---|---|
| Windows | `manager` |
| Linux | `cache` or `store` |
| Mac | `osxkeychain` |

---

## 🎯 Next Steps

Setelah setup selesai:

1. ✅ Jalankan `npm start` untuk mulai monitoring
2. ✅ Test dengan create/edit file
3. ✅ Cek GitHub repository untuk verifikasi upload
4. ✅ Baca `README.md` untuk dokumentasi lengkap

---

## 💡 Tips

1. **Backup Token**: Simpan PAT di password manager
2. **Token Expiration**: Set reminder sebelum token expired
3. **Multiple Repos**: Buat token dengan scope `repo` bisa dipakai untuk semua repo
4. **Security**: Jangan commit token ke repository
5. **Rotation**: Rotate token secara berkala untuk keamanan

---

## 📞 Need Help?

Jika masih ada masalah:
1. Cek README.md
2. Baca troubleshooting di atas
3. Buka issue di GitHub repository
4. Contact: willeam10101010-afk

---

**Good luck! 🚀**
