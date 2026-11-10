@echo off
title Push Project ke GitHub
cls
echo ============================================================
echo       PUSH BANK AI AUTOMATION PROJECT KE GITHUB
echo ============================================================
echo.
echo Pastikan Anda sudah membuat repository kosong di https://github.com/new
echo.
set /p REPO_URL="Masukkan Link Repository GitHub Anda (contoh: https://github.com/user/repo.git): "

if "%REPO_URL%"=="" (
    echo.
    echo [ERROR] Link repository tidak boleh kosong!
    echo Silakan jalankan kembali file ini dan masukkan link repo GitHub Anda.
    echo.
    pause
    exit /b
)

echo.
echo [*] Mengonfigurasi safe.directory...
git config --global --add safe.directory "%CD%" 2>nul

echo [*] Menghubungkan remote origin ke: %REPO_URL%
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo [*] Memastikan branch utama adalah 'main'...
git branch -M main

echo [*] Mengunggah (Push) berkas ke GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo [BERHASIL] Seluruh file project berhasil di-push ke GitHub!
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo [CATATAN] Jika diminta login, silakan login di jendela browser.
    echo Jika ada kendala hak akses, pastikan Anda adalah pemilik repository.
    echo ============================================================
)

echo.
pause

