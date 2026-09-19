"""
=============================================================
  VoiceBridge Real-Time Voice Translation API
  FastAPI Backend (Python 3.14 Compatible)
=============================================================
"""

import os
import sys
import io
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure core package can be imported
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from core.translator_engine import (
    LanguageDetector,
    MachineTranslator,
    SpeechRecognizer,
    TextToSpeech,
    LANGUAGES,
    TranslationRateLimitError
)

try:
    from deep_translator.exceptions import TooManyRequests
except ImportError:
    class TooManyRequests(Exception):
        pass

app = FastAPI(
    title="VoiceBridge Translation API",
    description="Real-Time Neural Speech-to-Speech & Text Translation Backend",
    version="2.0.0"
)

# CORS middleware for local frontend development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class TranslateRequest(BaseModel):
    text: str
    source: str = "auto"
    target: str = "en"

class SpeakRequest(BaseModel):
    text: str
    lang: str = "en"


# Helper language tag mapping for Speech Recognition
LANGUAGE_BCP47_MAP = {
    "auto": "en-US",
    "en": "en-US",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
    "pt": "pt-PT",
    "ru": "ru-RU",
    "zh-cn": "zh-CN",
    "zh-tw": "zh-TW",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "ar": "ar-SA",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "ml": "ml-IN",
    "kn": "kn-IN",
    "bn": "bn-IN",
    "gu": "gu-IN",
    "mr": "mr-IN",
    "ur": "ur-PK",
    "pa": "pa-IN",
    "nl": "nl-NL",
    "pl": "pl-PL",
    "tr": "tr-TR",
    "vi": "vi-VN",
    "th": "th-TH",
    "id": "id-ID",
    "ms": "ms-MY",
    "sv": "sv-SE",
    "da": "da-DK",
    "fi": "fi-FI",
    "no": "no-NO",
    "cs": "cs-CZ",
    "sk": "sk-SK",
    "ro": "ro-RO",
    "hu": "hu-HU",
    "el": "el-GR",
    "he": "he-IL",
    "fa": "fa-IR",
    "uk": "uk-UA",
    "ca": "ca-ES",
    "hr": "hr-HR",
    "sr": "sr-RS",
    "bg": "bg-BG",
    "lt": "lt-LT",
    "lv": "lv-LV",
    "et": "et-EE",
    "sl": "sl-SI",
    "af": "af-ZA",
    "sw": "sw-KE",
    "tl": "fil-PH"
}


@app.get("/api/languages")
def get_languages():
    """Return dictionary of supported languages and popular presets."""
    popular = ["en", "es", "fr", "de", "zh-cn", "ja", "hi", "ta", "ar", "ru", "pt", "it"]
    return {
        "languages": LANGUAGES,
        "popular": popular
    }


@app.post("/api/translate")
def translate_text(req: TranslateRequest):
    """Translate text from source to target language with auto-detection."""
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text field cannot be empty")

    detector = LanguageDetector()
    translator = MachineTranslator()

    detected_lang = req.source
    confidence = 1.0

    # Auto-detection handling:
    # Use langdetect solely for the UI "Detected:" badge;
    # Hide or suppress the badge when input is < 20 characters or confidence is low (< 0.7).
    if req.source == "auto":
        if len(text) >= 20:
            detected_lang, confidence = detector.detect(text)
            if confidence < 0.7:
                detected_lang = "auto"
                confidence = 0.0
        else:
            detected_lang = "auto"
            confidence = 0.0

    try:
        # Crucial fix: Pass req.source ("auto") directly to Google Translator rather than overriding it with langdetect's result
        result = translator.translate(
            text,
            target_lang=req.target,
            source_lang=req.source
        )
        translated_text, target_lang = result[0], result[1]

        # If Google returned detected_lang and user used "auto", use Google's detected lang for UI badge
        if hasattr(result, "detected_lang") and result.detected_lang and result.detected_lang != "auto":
            if detected_lang == "auto" and len(text) >= 20:
                detected_lang = result.detected_lang
                confidence = 0.85
            elif detected_lang == "auto":
                detected_lang = result.detected_lang

    except (TranslationRateLimitError, TooManyRequests) as e:
        return JSONResponse(
            status_code=429,
            content={"error": "Translation service is busy. Please try again in a few seconds."}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Translation service error: {str(e)}"}
        )

    return {
        "success": True,
        "original_text": text,
        "translated_text": translated_text,
        "source_lang": req.source,
        "detected_lang": detected_lang,
        "target_lang": target_lang,
        "confidence": confidence,
        "source_name": translator.get_language_name(detected_lang),
        "target_name": translator.get_language_name(target_lang)
    }


@app.post("/api/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("auto")
):
    """
    Accepts uploaded audio (PCM WAV) and transcribes speech using Google Speech Recognition.
    """
    audio_bytes = await file.read()
    if not audio_bytes or len(audio_bytes) < 44:
        raise HTTPException(status_code=400, detail="Invalid or empty audio file.")

    # Resolve BCP-47 language tag
    bcp47_lang = LANGUAGE_BCP47_MAP.get(language.lower(), "en-US")
    if "-" in language and len(language) >= 4:
        bcp47_lang = language

    recognizer = SpeechRecognizer()
    result = recognizer.recognize_audio(audio_bytes, language=bcp47_lang)
    return result


@app.post("/api/speak")
def speak_audio_post(req: SpeakRequest):
    """Return MP3 audio stream for specified text and language."""
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text field cannot be empty")

    tts = TextToSpeech(prefer_online=True)
    audio_bytes = tts.get_audio_bytes(text, lang_code=req.lang)
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Speech synthesis failed or offline")

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=speech.mp3"}
    )


@app.get("/api/speak")
def speak_audio_get(text: str, lang: str = "en"):
    """GET convenience route to stream MP3 audio directly in <audio> tags."""
    text = (text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty")

    tts = TextToSpeech(prefer_online=True)
    audio_bytes = tts.get_audio_bytes(text, lang_code=lang)
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Speech synthesis failed or offline")

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=speech.mp3"}
    )


# Mount static frontend directory
WEB_DIR = os.path.join(CURRENT_DIR, "web")
if os.path.exists(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
