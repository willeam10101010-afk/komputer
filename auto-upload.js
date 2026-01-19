#!/usr/bin/env node

/**
 * AUTO-UPLOAD.JS
 * Script otomatis untuk monitoring dan upload file ke GitHub
 * Repository: willeam10101010-afk/komputer
 */

const chokidar = require('chokidar');
const { exec } = require('child_process');
const { promisify } = require('util');
const path = require('path');
const fs = require('fs');

const execAsync = promisify(exec);

// Konfigurasi
const CONFIG = {
  repository: 'willeam10101010-afk/komputer',
  branch: 'main',
  uploadDelay: 10000, // 10 detik
  watchPath: process.cwd(),
  ignoredPatterns: [
    '**/node_modules/**',
    '**/.git/**',
    '**/dist/**',
    '**/build/**',
    '**/.env*',
    '**/*.log',
    '**/package-lock.json',
    '**/*.swp',
    '**/*.swo',
    '**/.DS_Store',
    '**/Thumbs.db'
  ]
};

// State management
let pendingChanges = new Set();
let uploadTimer = null;
let isUploading = false;
let isShuttingDown = false;

/**
 * Format waktu untuk display
 */
function getTimestamp() {
  const now = new Date();
  return now.toTimeString().split(' ')[0]; // HH:MM:SS
}

/**
 * Format datetime lengkap untuk commit message
 */
function getDateTimeString() {
  const now = new Date();
  return now.toISOString().replace('T', ' ').substring(0, 19);
}

/**
 * Print banner
 */
function printBanner() {
  console.log('\n╔════════════════════════════════════════╗');
  console.log('║   🚀 AUTO UPLOAD TO GITHUB AKTIF 🚀   ║');
  console.log('╚════════════════════════════════════════╝\n');
  console.log(`📂 Folder    : ${CONFIG.watchPath}`);
  console.log(`📦 Repository: ${CONFIG.repository}`);
  console.log(`🌿 Branch    : ${CONFIG.branch}`);
  console.log(`⏱️  Delay     : ${CONFIG.uploadDelay / 1000} detik\n`);
  console.log('────────────────────────────────────────\n');
  console.log('👀 Monitoring dimulai... (Tekan Ctrl+C untuk berhenti)\n');
}

/**
 * Cek apakah git sudah dikonfigurasi
 */
async function checkGitConfig() {
  try {
    await execAsync('git rev-parse --git-dir');
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Dapatkan status git
 */
async function getGitStatus() {
  try {
    const { stdout } = await execAsync('git status --porcelain');
    return stdout.trim();
  } catch (error) {
    throw new Error('❌ Gagal mendapatkan git status: ' + error.message);
  }
}

/**
 * Upload perubahan ke GitHub
 */
async function uploadToGitHub() {
  if (isUploading || pendingChanges.size === 0) {
    return;
  }

  isUploading = true;
  const changedFiles = Array.from(pendingChanges);
  pendingChanges.clear();

  try {
    console.log(`📦 Memproses ${changedFiles.length} file...\n`);
    console.log('📝 Perubahan:');
    
    // Tampilkan file yang berubah
    changedFiles.forEach(file => {
      console.log(`   ✏️  ${file}`);
    });
    console.log('');

    // Cek status git untuk melihat perubahan sebenarnya
    const status = await getGitStatus();
    
    if (!status) {
      console.log('ℹ️  Tidak ada perubahan untuk di-upload.\n');
      isUploading = false;
      return;
    }

    // Add all changes
    console.log('📤 Uploading ke GitHub...');
    await execAsync('git add -A');

    // Commit dengan timestamp
    const commitMessage = `Auto-upload: Update files [${getDateTimeString()}]`;
    await execAsync(`git commit -m "${commitMessage}"`);

    // Push ke GitHub
    await execAsync(`git push origin ${CONFIG.branch}`);

    console.log(`✅ Upload berhasil! [${getDateTimeString()}]`);
    console.log('────────────────────────────────────────\n');

  } catch (error) {
    console.error('❌ Error saat upload:\n');
    
    if (error.message.includes('nothing to commit')) {
      console.log('ℹ️  Tidak ada perubahan untuk di-commit.\n');
    } else if (error.message.includes('remote: Permission denied')) {
      console.error('   🔐 Authentication error! Pastikan kredensial GitHub sudah benar.');
      console.error('   💡 Tips: Jalankan "npm run setup" untuk setup authentication.\n');
    } else if (error.message.includes('rejected')) {
      console.error('   ⚠️  Push ditolak! Mungkin ada konflik.');
      console.error('   💡 Tips: Pull perubahan terbaru dengan "git pull origin main"\n');
    } else {
      console.error('   ' + error.message);
      console.error('   💡 Tips: Cek koneksi internet dan kredensial GitHub.\n');
    }

    // Restore pending changes jika gagal
    changedFiles.forEach(file => pendingChanges.add(file));
  } finally {
    isUploading = false;
  }
}

/**
 * Schedule upload dengan debounce
 */
function scheduleUpload() {
  if (uploadTimer) {
    clearTimeout(uploadTimer);
  }

  uploadTimer = setTimeout(() => {
    uploadToGitHub();
  }, CONFIG.uploadDelay);
}

/**
 * Handle file change event
 */
function handleFileChange(eventType, filePath) {
  if (isShuttingDown) return;

  // Get relative path
  const relativePath = path.relative(CONFIG.watchPath, filePath);
  
  // Skip jika file di-ignore
  if (relativePath.includes('node_modules') || 
      relativePath.includes('.git') ||
      relativePath.includes('package-lock.json')) {
    return;
  }

  // Icon berdasarkan event type
  let icon = '✏️ ';
  let action = 'Diubah';
  
  if (eventType === 'add') {
    icon = '➕';
    action = 'Ditambahkan';
  } else if (eventType === 'unlink') {
    icon = '🗑️ ';
    action = 'Dihapus';
  }

  console.log(`${icon} [${getTimestamp()}] ${action}: ${relativePath}`);

  // Add to pending changes
  pendingChanges.add(relativePath);

  // Schedule upload
  scheduleUpload();
}

/**
 * Setup file watcher
 */
function setupWatcher() {
  const watcher = chokidar.watch(CONFIG.watchPath, {
    ignored: CONFIG.ignoredPatterns,
    persistent: true,
    ignoreInitial: true,
    awaitWriteFinish: {
      stabilityThreshold: 2000,
      pollInterval: 100
    }
  });

  watcher
    .on('add', filePath => handleFileChange('add', filePath))
    .on('change', filePath => handleFileChange('change', filePath))
    .on('unlink', filePath => handleFileChange('unlink', filePath))
    .on('error', error => console.error('❌ Watcher error:', error));

  return watcher;
}

/**
 * Graceful shutdown
 */
async function shutdown(watcher) {
  if (isShuttingDown) return;
  
  isShuttingDown = true;
  console.log('\n\n🛑 Menghentikan monitoring...');

  // Clear upload timer
  if (uploadTimer) {
    clearTimeout(uploadTimer);
  }

  // Upload pending changes
  if (pendingChanges.size > 0) {
    console.log('📤 Upload perubahan yang tertunda...\n');
    await uploadToGitHub();
  }

  // Close watcher
  await watcher.close();
  
  console.log('✅ Auto-upload dihentikan. Goodbye! 👋\n');
  process.exit(0);
}

/**
 * Main function
 */
async function main() {
  try {
    // Cek apakah git sudah dikonfigurasi
    const hasGit = await checkGitConfig();
    if (!hasGit) {
      console.error('\n❌ Repository git tidak ditemukan!');
      console.error('💡 Jalankan "npm run setup" untuk setup awal.\n');
      process.exit(1);
    }

    // Print banner
    printBanner();

    // Setup watcher
    const watcher = setupWatcher();

    // Handle graceful shutdown
    process.on('SIGINT', () => shutdown(watcher));
    process.on('SIGTERM', () => shutdown(watcher));

  } catch (error) {
    console.error('❌ Fatal error:', error.message);
    process.exit(1);
  }
}

// Run main
if (require.main === module) {
  main();
}

module.exports = { CONFIG, uploadToGitHub, handleFileChange };
