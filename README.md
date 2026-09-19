# VoiceBridge — Real-Time Voice & Text Translation System

A modern, full-stack real-time speech-to-speech and text translation application with neural voice synthesis, dark-themed Stitch UI, and intelligent rate-limiting protection.

![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-2.0.0-009688.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## ✨ Features

- **🎙️ Real-Time Voice Translation**: Inbound voice capture via Web Audio API or local microphone (`sounddevice`) transcribed through neural speech recognition.
- **🌐 50+ Supported Languages**: Seamless translation across 52 global languages, including English, Spanish, French, German, Japanese, Chinese, Tamil, Hindi, Arabic, and more.
- **🔍 Custom Searchable Combobox**: Accessible dropdown with instant name and ISO code filtering, country flag icons, uppercase badges (`[ES]`, `[TA]`), and full keyboard navigation (<kbd>↑</kbd>, <kbd>↓</kbd>, <kbd>Enter</kbd>, <kbd>Esc</kbd>).
- **🔊 Neural Text-to-Speech (TTS)**: High-fidelity audio playback via Google Neural TTS with inline audio waveforms, speed adjustments, and voice synthesis compatibility indicators.
- **⚡ Rate-Limiting & Caching Engine**:
  - Thread-safe in-memory cache for repeated translations.
  - Server-side throttling ensuring at least 250ms spacing between outbound requests.
  - 3-stage exponential backoff retry on HTTP 429 rate limits.
  - Dual-client architecture with direct Google neural endpoints.
- **🛡️ In-Flight Request Locking & Error Recovery**:
  - Automatically disables submission controls and shows an animated spinner while translations are processing.
  - Non-intrusive inline error banner with one-click **Retry** functionality.
  - Spacebar push-to-talk isolation that prevents accidental microphone triggering while typing.
- **💻 Multiple Interfaces**:
  - **Modern Web App**: Google Stitch emerald dark theme (FastAPI + Tailwind CSS).
  - **Streamlit App**: Interactive dashboard with session history (`app_streamlit.py`).
  - **Desktop GUI**: Native desktop interface built with Tkinter (`app_tkinter.py`).

---

## 🚀 Quick Start (Windows)

### Option 1: One-Click Launchers
Double-click any of the provided `.bat` scripts:
- **`run_web.bat`** — Launches the FastAPI server and automatically opens `http://localhost:8000` in your default browser.
- **`run_streamlit.bat`** — Launches the Streamlit dashboard on `http://localhost:8501`.
- **`run_desktop.bat`** — Launches the native Tkinter desktop application.

---

### Option 2: Command Line Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vasanth-vkp/Voice-Translator.git
   cd Voice-Translator
   ```

2. **Create and activate a virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the modern web server**:
   ```bash
   python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
   ```
   Open your browser at **`http://localhost:8000`**.

---

## 📁 Project Structure

```
Voice-Translator/
├── api.py                     # FastAPI backend routes (/api/translate, /api/speak, /api/transcribe)
├── core/
│   └── translator_engine.py   # Core engine: ASR, translation, detection, TTS, caching & throttling
├── web/                       # Modern Stitch UI frontend
│   ├── index.html             # Single-page application markup
│   ├── app.js                 # Web Audio API, combobox, and real-time interaction logic
│   └── logo.svg               # Application brand icon
├── app_streamlit.py           # Streamlit web application
├── app_tkinter.py             # Desktop Tkinter GUI
├── run_web.bat                # Windows one-click web launcher
├── run_streamlit.bat          # Windows one-click Streamlit launcher
├── run_desktop.bat            # Windows one-click desktop launcher
├── requirements.txt           # Python dependencies (Python 3.14 compatible)
└── README.md
```

---

## 🛠️ Built With

- **Backend**: Python 3.14, FastAPI, Uvicorn, SoundDevice, NumPy, SciPy, SpeechRecognition
- **Frontend**: HTML5, Tailwind CSS, Material Symbols, Web Audio API, Vanilla JavaScript
- **Translation & TTS**: Google Neural Translate API, deep-translator, gTTS, pyttsx3

---

## 📄 License

This project is licensed under the MIT License.
