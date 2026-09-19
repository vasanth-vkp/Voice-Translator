@echo off
title Voice Translator - Streamlit Edition
cd /d "%~dp0"

if not exist ".\venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    pause
    exit /b 1
)

echo Starting Streamlit on http://localhost:8501 ...
".\venv\Scripts\python.exe" -m streamlit run app_streamlit.py
pause
