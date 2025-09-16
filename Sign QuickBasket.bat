@echo off
title QuickBasket Code Signing
echo.
echo ============================================================
echo 🔐 QuickBasket Code Signing Utility
echo ============================================================
echo This will sign QuickBasket.exe to reduce Windows Defender warnings.
echo.
echo IMPORTANT: This requires Administrator privileges!
echo.
echo What this does:
echo ✅ Creates a self-signed development certificate
echo ✅ Signs QuickBasket.exe with the certificate  
echo ✅ Installs certificate in Windows trusted store
echo ✅ Reduces "Unknown Publisher" warnings
echo.
echo ============================================================
echo.

REM Check if executable exists
if not exist "dist\QuickBasket.exe" (
    echo ❌ QuickBasket.exe not found in dist folder!
    echo Please build the executable first using PyInstaller.
    echo.
    pause
    exit /b 1
)

echo 🔍 Found QuickBasket.exe - ready to sign!
echo.
echo Press any key to start the signing process...
pause >nul

echo.
echo 🚀 Starting PowerShell script with Administrator privileges...
echo.

REM Run PowerShell script as Administrator
echo 🚀 Running signing script with Administrator privileges...
echo You will see a UAC prompt - click "Yes" to continue.
echo.
powershell -Command "Start-Process PowerShell -ArgumentList '-ExecutionPolicy Bypass -File admin_signing.ps1' -Verb RunAs -Wait"

echo.
echo 🔐 Installing certificate for trust...
echo You will see another UAC prompt - click "Yes" to trust the certificate.
echo.
powershell -Command "Start-Process PowerShell -ArgumentList '-ExecutionPolicy Bypass -File trust_certificate.ps1' -Verb RunAs -Wait"

echo.
echo ============================================================
echo.
if exist "dist\QuickBasket.exe" (
    echo 🔍 Checking signature status...
    powershell -Command "(Get-AuthenticodeSignature 'dist\QuickBasket.exe').Status"
    echo.
    echo ✅ Signing process completed!
    echo.
    echo 📋 Next steps:
    echo 1. Test the signed executable by running it
    echo 2. Check Properties → Digital Signatures to verify
    echo 3. Upload the signed version to GitHub
    echo.
) else (
    echo ❌ Something went wrong during the signing process.
)

echo Press any key to exit...
pause >nul