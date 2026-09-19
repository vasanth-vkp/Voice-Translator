@echo off
title Voice Translator - Desktop Tkinter GUI
cd /d "%~dp0"

if not exist ".\venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    pause
    exit /b 1
)

echo Starting Tkinter Desktop Application...
".\venv\Scripts\python.exe" app_tkinter.py
pause
