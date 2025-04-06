# Panduan Deployment ke Koyeb

## Persiapan

1. Buat akun di [Koyeb](https://app.koyeb.com)
2. Install [Koyeb CLI](https://www.koyeb.com/docs/quickstart/koyeb-cli)

### Troubleshooting Instalasi CLI

Jika mengalami masalah saat instalasi CLI:

1. Pastikan koneksi internet stabil
2. Cek apakah ada firewall yang memblokir koneksi
3. Alternatif instalasi:
   - Download installer dari browser di [Koyeb CLI Releases](https://github.com/koyeb/koyeb-cli/releases)
   - Atau install menggunakan package manager:
     ```bash
     # Untuk macOS dengan Homebrew
     brew install koyeb/tap/cli
     
     # Untuk Linux dengan Snap
     snap install koyeb
     ```

## Langkah-langkah Deployment

1. Dapatkan Personal Access Token:
   - Kunjungi halaman pengaturan API Koyeb di https://app.koyeb.com/user/settings/api
   - Buat token baru dan simpan token tersebut dengan aman

2. Login ke Koyeb CLI menggunakan token:
   ```bash
   koyeb login --token YOUR_ACCESS_TOKEN
   ```

2. Siapkan Database PostgreSQL:
   - Buat database PostgreSQL di Koyeb atau gunakan layanan database eksternal
   - Catat URL database untuk konfigurasi environment variable

3. Setup Environment Variables di Koyeb:
   - DATABASE_URL: URL PostgreSQL database Anda
   - SECRET_KEY: Key rahasia untuk aplikasi

4. Deploy Aplikasi:
   ```bash
   koyeb app init
   koyeb app deploy
   ```

## Konfigurasi yang Sudah Disiapkan

1. Dockerfile sudah dikonfigurasi untuk production
2. File koyeb.yaml berisi konfigurasi deployment
3. Requirements.txt sudah mencakup semua dependensi
4. Gunicorn sudah dikonfigurasi sebagai WSGI server

## Monitoring

- Pantau aplikasi melalui dashboard Koyeb
- Cek logs untuk troubleshooting
- Monitor metrics performa aplikasi

## Maintenance

- Update aplikasi dengan push ke repository
- Koyeb akan otomatis melakukan deployment
- Gunakan `koyeb app logs` untuk melihat logs