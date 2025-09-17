@echo off
cd /d "%~dp0"
echo Starting QuickBasket Production Server...
.venv\Scripts\activate && python run_server.py
pause