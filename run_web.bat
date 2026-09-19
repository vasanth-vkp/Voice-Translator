@echo off
title VoiceBridge Real-Time Voice Translator
cd /d "%~dp0"

echo =================================================================
echo   VoiceBridge - Real-Time Neural Voice ^& Text Translator
echo =================================================================
echo.

:: Check if virtual environment exists
if not exist ".\venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .\venv\Scripts\python.exe
    echo Please make sure the venv folder is present.
    pause
    exit /b 1
)

echo [INFO] Starting FastAPI Web Server at http://localhost:8000 ...
echo [INFO] Opening your default web browser in 2 seconds...
echo [INFO] Press Ctrl+C in this terminal window to stop the server.
echo.

:: Open browser after 2-second delay so the server is ready first
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000"

:: Start Uvicorn server
".\venv\Scripts\python.exe" -m uvicorn api.index:app --host 127.0.0.1 --port 8000 --reload

pause
