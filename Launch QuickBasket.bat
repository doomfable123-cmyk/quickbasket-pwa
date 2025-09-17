@echo off
title QuickBasket PWA
echo.
echo ============================================================
echo 🍽️  QuickBasket - Windows Desktop App
echo ============================================================
echo Starting QuickBasket PWA...
echo.
echo Your recipe and grocery list manager is launching!
echo The app will open in a new window.
echo.
echo 📱 Install on tablets: Visit the web version
echo 🖥️ Desktop use: This standalone app
echo 🌐 Recipe import: Add recipes from any cooking website
echo.
echo ============================================================
echo.

REM Check if executable exists
if not exist "dist\QuickBasket.exe" (
    echo ❌ QuickBasket.exe not found in dist folder!
    echo Please ensure the executable is present.
    echo.
    pause
    exit /b 1
)

REM Run the application
echo 🚀 Launching QuickBasket...
start "" "dist\QuickBasket.exe"

echo.
echo ✅ QuickBasket is starting up!
echo Check your system tray or taskbar for the application window.
echo.
echo Press any key to close this launcher...
pause >nul