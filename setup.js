#!/usr/bin/env node

/**
 * SETUP.JS
 * Interactive setup wizard untuk konfigurasi awal auto-upload
 */

const { exec } = require('child_process');
const { promisify } = require('util');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

const execAsync = promisify(exec);

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const question = (query) => new Promise((resolve) => rl.question(query, resolve));

/**
 * Print banner
 */
function printBanner() {
  console.log('\n╔════════════════════════════════════════╗');
  console.log('║   🔧 SETUP AUTO-UPLOAD TO GITHUB 🔧   ║');
  console.log('╚════════════════════════════════════════╝\n');
}

/**
 * Cek apakah git sudah terinstall
 */
async function checkGitInstalled() {
  try {
    await execAsync('git --version');
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Cek apakah sudah ada git repository
 */
async function checkGitRepo() {
  try {
    await execAsync('git rev-parse --git-dir');
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Initialize git repository
 */
async function initGitRepo() {
  console.log('📦 Inisialisasi git repository...');
  try {
    await execAsync('git init');
    console.log('✅ Git repository berhasil diinisialisasi.\n');
    return true;
  } catch (error) {
    console.error('❌ Gagal inisialisasi git:', error.message);
    return false;
  }
}

/**
 * Setup git config
 */
async function setupGitConfig() {
  console.log('\n📝 Konfigurasi Git User\n');
  
  try {
    // Cek apakah sudah ada config
    let userName, userEmail;
    
    try {
      const { stdout: nameStdout } = await execAsync('git config user.name');
      userName = nameStdout.trim();
    } catch (e) {
      userName = '';
    }

    try {
      const { stdout: emailStdout } = await execAsync('git config user.email');
      userEmail = emailStdout.trim();
    } catch (e) {
      userEmail = '';
    }

    if (userName && userEmail) {
      console.log(`   Current user: ${userName} <${userEmail}>`);
      const useExisting = await question('   Gunakan konfigurasi ini? (y/n): ');
      
      if (useExisting.toLowerCase() === 'y') {
        console.log('✅ Menggunakan konfigurasi git yang ada.\n');
        return true;
      }
    }

    // Setup new config
    const name = await question('   Nama Anda: ');
    const email = await question('   Email Anda: ');

    if (name && email) {
      await execAsync(`git config user.name "${name}"`);
      await execAsync(`git config user.email "${email}"`);
      console.log('✅ Git config berhasil disetup.\n');
      return true;
    } else {
      console.log('⚠️  Git config tidak lengkap, dilewati.\n');
      return false;
    }
  } catch (error) {
    console.error('❌ Error setup git config:', error.message);
    return false;
  }
}

/**
 * Setup git remote
 */
async function setupGitRemote() {
  console.log('🌐 Setup Git Remote\n');
  
  try {
    // Cek apakah sudah ada remote
    let hasRemote = false;
    try {
      const { stdout } = await execAsync('git remote get-url origin');
      if (stdout.trim()) {
        console.log(`   Remote origin sudah ada: ${stdout.trim()}`);
        const useExisting = await question('   Gunakan remote ini? (y/n): ');
        
        if (useExisting.toLowerCase() === 'y') {
          console.log('✅ Menggunakan remote yang ada.\n');
          return true;
        }
        
        // Remove existing remote
        await execAsync('git remote remove origin');
      }
    } catch (e) {
      // No remote exists
    }

    // Add new remote
    const repoUrl = 'https://github.com/willeam10101010-afk/komputer.git';
    await execAsync(`git remote add origin ${repoUrl}`);
    console.log(`✅ Remote origin berhasil ditambahkan: ${repoUrl}\n`);
    return true;

  } catch (error) {
    console.error('❌ Error setup remote:', error.message);
    return false;
  }
}

/**
 * Create .gitignore if not exists
 */
async function ensureGitignore() {
  const gitignorePath = path.join(process.cwd(), '.gitignore');
  
  if (fs.existsSync(gitignorePath)) {
    console.log('✅ File .gitignore sudah ada.\n');
    return true;
  }

  console.log('📝 Membuat .gitignore...');
  
  const gitignoreContent = `# Dependencies
node_modules/
package-lock.json

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
npm-debug.log*
yarn-debug.log*

# OS
.DS_Store
Thumbs.db
desktop.ini

# IDE
.vscode/
.idea/
*.swp
*.swo

# Build
dist/
build/
*.min.js

# Temporary
*.tmp
*.temp
~*
`;

  try {
    fs.writeFileSync(gitignorePath, gitignoreContent);
    console.log('✅ File .gitignore berhasil dibuat.\n');
    return true;
  } catch (error) {
    console.error('❌ Gagal membuat .gitignore:', error.message);
    return false;
  }
}

/**
 * Test koneksi ke GitHub
 */
async function testGitHubConnection() {
  console.log('🔍 Testing koneksi ke GitHub...');
  
  try {
    await execAsync('git ls-remote origin', { timeout: 10000 });
    console.log('✅ Koneksi ke GitHub berhasil!\n');
    return true;
  } catch (error) {
    console.log('❌ Gagal koneksi ke GitHub.\n');
    console.log('⚠️  Kemungkinan penyebab:');
    console.log('   1. Belum setup authentication (Personal Access Token)');
    console.log('   2. Repository tidak ditemukan');
    console.log('   3. Tidak ada koneksi internet\n');
    console.log('💡 Cara setup authentication:');
    console.log('   Baca panduan di SETUP-GUIDE.md\n');
    return false;
  }
}

/**
 * Initial commit
 */
async function createInitialCommit() {
  console.log('📤 Membuat initial commit...');
  
  try {
    // Check if there are any commits
    let hasCommits = false;
    try {
      await execAsync('git rev-parse HEAD');
      hasCommits = true;
    } catch (e) {
      // No commits yet
    }

    if (hasCommits) {
      console.log('ℹ️  Repository sudah memiliki commit.\n');
      return true;
    }

    // Create initial commit
    await execAsync('git add -A');
    await execAsync('git commit -m "Initial commit: Setup auto-upload system"');
    console.log('✅ Initial commit berhasil dibuat.\n');
    
    return true;
  } catch (error) {
    if (error.message.includes('nothing to commit')) {
      console.log('ℹ️  Tidak ada file untuk commit.\n');
      return true;
    }
    console.error('❌ Error membuat commit:', error.message);
    return false;
  }
}

/**
 * Setup branch
 */
async function setupBranch() {
  console.log('🌿 Setup branch main...');
  
  try {
    // Get current branch
    const { stdout } = await execAsync('git branch --show-current');
    const currentBranch = stdout.trim();

    if (currentBranch === 'main') {
      console.log('✅ Sudah di branch main.\n');
      return true;
    }

    // Check if main branch exists
    try {
      await execAsync('git rev-parse --verify main');
      // Main exists, checkout
      await execAsync('git checkout main');
      console.log('✅ Pindah ke branch main.\n');
    } catch (e) {
      // Main doesn't exist, create it
      if (currentBranch) {
        await execAsync('git branch -M main');
        console.log('✅ Branch berhasil direname ke main.\n');
      } else {
        console.log('ℹ️  Branch akan dibuat saat commit pertama.\n');
      }
    }

    return true;
  } catch (error) {
    console.error('❌ Error setup branch:', error.message);
    return false;
  }
}

/**
 * Main setup process
 */
async function main() {
  printBanner();

  try {
    // 1. Check git installation
    console.log('🔍 Checking prerequisites...\n');
    
    const hasGit = await checkGitInstalled();
    if (!hasGit) {
      console.error('❌ Git belum terinstall!');
      console.error('💡 Install Git dari: https://git-scm.com/downloads\n');
      rl.close();
      process.exit(1);
    }
    console.log('✅ Git terinstall.\n');

    // 2. Check/init git repo
    const hasRepo = await checkGitRepo();
    if (!hasRepo) {
      const shouldInit = await question('📦 Git repository belum ada. Inisialisasi sekarang? (y/n): ');
      if (shouldInit.toLowerCase() === 'y') {
        const success = await initGitRepo();
        if (!success) {
          rl.close();
          process.exit(1);
        }
      } else {
        console.log('⚠️  Setup dibatalkan.\n');
        rl.close();
        process.exit(0);
      }
    } else {
      console.log('✅ Git repository sudah ada.\n');
    }

    // 3. Setup git config
    await setupGitConfig();

    // 4. Setup remote
    await setupGitRemote();

    // 5. Ensure .gitignore
    await ensureGitignore();

    // 6. Setup branch
    await setupBranch();

    // 7. Create initial commit if needed
    await createInitialCommit();

    // 8. Test GitHub connection
    const connected = await testGitHubConnection();

    // Final instructions
    console.log('╔════════════════════════════════════════╗');
    console.log('║          ✅ SETUP SELESAI! ✅          ║');
    console.log('╚════════════════════════════════════════╝\n');

    if (connected) {
      console.log('🎉 Semuanya siap! Anda bisa menjalankan:');
      console.log('   npm start      - Mulai auto-upload monitoring\n');
    } else {
      console.log('⚠️  Setup hampir selesai!');
      console.log('📖 Langkah selanjutnya:');
      console.log('   1. Setup GitHub authentication (Personal Access Token)');
      console.log('   2. Baca panduan lengkap di SETUP-GUIDE.md');
      console.log('   3. Jalankan "npm start" untuk memulai monitoring\n');
    }

    console.log('💡 Tips:');
    console.log('   - Lihat README.md untuk dokumentasi lengkap');
    console.log('   - Lihat SETUP-GUIDE.md untuk panduan setup GitHub auth\n');

  } catch (error) {
    console.error('❌ Setup error:', error.message);
    process.exit(1);
  } finally {
    rl.close();
  }
}

// Run main
if (require.main === module) {
  main();
}

module.exports = { setupGitConfig, setupGitRemote, testGitHubConnection };
