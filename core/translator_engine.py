"""
=============================================================
  Real-Time Voice Translation System
  Module: core/translator_engine.py
  Updated: Uses sounddevice instead of PyAudio (Python 3.14 compatible)
=============================================================
"""

import os
import time
import tempfile
import wave
import io
import threading
import json
import urllib.request
import urllib.parse

# ── Audio Recording (sounddevice — works on Python 3.14) ──
try:
    import sounddevice as sd
    import numpy as np
    SD_AVAILABLE = True
except ImportError:
    SD_AVAILABLE = False
    print("[WARNING] sounddevice not installed. Run: pip install sounddevice scipy")

# ── Speech Recognition ────────────────────────────────────
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    print("[WARNING] SpeechRecognition not installed.")

# ── Translation ───────────────────────────────────────────
try:
    from deep_translator import GoogleTranslator
    from deep_translator.exceptions import TooManyRequests
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    class TooManyRequests(Exception):
        pass
    print("[WARNING] deep-translator not installed.")

class TranslationRateLimitError(Exception):
    """Raised when translation service returns HTTP 429 or rate limits."""
    pass

class TranslationResult(tuple):
    """2-tuple (translated_text, target_lang) with extra detected_lang attribute."""
    def __new__(cls, translated_text, target_lang, detected_lang="auto"):
        instance = super(TranslationResult, cls).__new__(cls, (translated_text, target_lang))
        instance.detected_lang = detected_lang
        return instance

_throttle_lock = threading.Lock()
_last_request_time = 0.0
_MIN_REQUEST_INTERVAL = 0.25  # 250ms minimum gap

_cache_lock = threading.Lock()
_translation_cache = {}  # key: (text_normalized, source_lang, target_lang) -> TranslationResult

# ── Language Detection ────────────────────────────────────
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("[WARNING] langdetect not installed.")

# ── Text-to-Speech ────────────────────────────────────────
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


LANGUAGES = {
    "en":"english","es":"spanish","fr":"french","de":"german",
    "it":"italian","pt":"portuguese","ru":"russian","zh-cn":"chinese (simplified)",
    "zh-tw":"chinese (traditional)","ja":"japanese","ko":"korean","ar":"arabic",
    "hi":"hindi","ta":"tamil","te":"telugu","ml":"malayalam","kn":"kannada",
    "bn":"bengali","gu":"gujarati","mr":"marathi","ur":"urdu","pa":"punjabi",
    "nl":"dutch","pl":"polish","tr":"turkish","vi":"vietnamese","th":"thai",
    "id":"indonesian","ms":"malay","sv":"swedish","da":"danish","fi":"finnish",
    "no":"norwegian","cs":"czech","sk":"slovak","ro":"romanian","hu":"hungarian",
    "el":"greek","he":"hebrew","fa":"persian","uk":"ukrainian","ca":"catalan",
    "hr":"croatian","sr":"serbian","bg":"bulgarian","lt":"lithuanian",
    "lv":"latvian","et":"estonian","sl":"slovenian","af":"afrikaans",
    "sw":"swahili","tl":"filipino",
}


def record_audio_sounddevice(duration: int = 5, samplerate: int = 16000) -> bytes:
    """Record mic audio using sounddevice. Returns WAV bytes."""
    print(f"  🎙️  Recording for {duration} seconds... speak now!")
    recording = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="int16"
    )
    sd.wait()
    print("  ✅  Recording complete.")
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(recording.tobytes())
    return wav_buffer.getvalue()


class LanguageDetector:
    def detect(self, text: str) -> tuple:
        if not text or not text.strip():
            return ("en", 0.0)
        if LANGDETECT_AVAILABLE:
            try:
                from langdetect import detect_langs
                langs = detect_langs(text)
                return (langs[0].lang, round(langs[0].prob, 4))
            except Exception:
                pass
        if TRANSLATOR_AVAILABLE:
            try:
                detected = GoogleTranslator(source="auto", target="en").detect(text)
                if detected:
                    return (detected if isinstance(detected, str) else "en", 0.85)
            except Exception:
                pass
        return ("en", 0.0)


class MachineTranslator:
    def __init__(self):
        pass

    def translate(self, text: str, target_lang: str = "en", source_lang: str = "auto") -> tuple:
        if not text or not text.strip():
            return TranslationResult("", target_lang, source_lang)

        normalized_text = text.strip()
        sl = (source_lang or "auto").lower()
        tl = (target_lang or "en").lower()

        # If source and target are the same, return as-is
        if sl != "auto" and sl == tl:
            return TranslationResult(normalized_text, target_lang, source_lang)

        # 1. In-memory cache check
        cache_key = (normalized_text.lower(), sl, tl)
        with _cache_lock:
            if cache_key in _translation_cache:
                return _translation_cache[cache_key]

        # 2. Exponential backoff retry loop (3 attempts: 0.5s, 1.0s, 2.0s)
        backoff_delays = [0.5, 1.0, 2.0]
        last_exception = None
        is_rate_limited = False

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "*/*",
        }

        for attempt in range(len(backoff_delays)):
            # Server-side throttle: enforce minimum 250ms interval between outbound calls
            global _last_request_time
            with _throttle_lock:
                now = time.time()
                elapsed = now - _last_request_time
                if elapsed < _MIN_REQUEST_INTERVAL:
                    time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
                _last_request_time = time.time()

            # Attempt 1: Direct Google dict-chrome-ex client
            try:
                url = f"https://translate.googleapis.com/translate_a/single?client=dict-chrome-ex&sl={urllib.parse.quote(sl)}&tl={urllib.parse.quote(tl)}&dt=t&q={urllib.parse.quote(normalized_text)}"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=6) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    translated = "".join(chunk[0] for chunk in data[0] if chunk and chunk[0])
                    detected = data[2] if len(data) > 2 and data[2] else sl
                    if translated:
                        res_obj = TranslationResult(translated, target_lang, detected)
                        with _cache_lock:
                            if len(_translation_cache) >= 2000:
                                _translation_cache.pop(next(iter(_translation_cache)))
                            _translation_cache[cache_key] = res_obj
                        return res_obj
            except urllib.error.HTTPError as http_err:
                if http_err.code == 429:
                    is_rate_limited = True
                last_exception = http_err
            except Exception as e:
                last_exception = e

            # Attempt 2: deep-translator GoogleTranslator fallback
            if TRANSLATOR_AVAILABLE:
                try:
                    translator = GoogleTranslator(source=sl, target=tl)
                    res = translator.translate(normalized_text)
                    if res:
                        res_obj = TranslationResult(res, target_lang, sl)
                        with _cache_lock:
                            if len(_translation_cache) >= 2000:
                                _translation_cache.pop(next(iter(_translation_cache)))
                            _translation_cache[cache_key] = res_obj
                        return res_obj
                except TooManyRequests as e:
                    is_rate_limited = True
                    last_exception = e
                except Exception as e:
                    last_exception = e

            # Sleep exponential backoff if not the final attempt
            if attempt < len(backoff_delays) - 1:
                time.sleep(backoff_delays[attempt])

        # If all retries failed:
        if is_rate_limited:
            raise TranslationRateLimitError("Translation service is busy. Please try again in a few seconds.")
        raise RuntimeError(f"Translation service error: {last_exception}")

    def get_language_name(self, code: str) -> str:
        return LANGUAGES.get(code.lower(), code)


class TextToSpeech:
    def __init__(self, prefer_online: bool = True):
        self.prefer_online = prefer_online and GTTS_AVAILABLE
        self._engine = None

    def speak(self, text: str, lang_code: str = "en") -> bool:
        if not text or not text.strip():
            return False
        if self.prefer_online:
            return self._speak_gtts(text, lang_code)
        return self._speak_pyttsx3(text)

    def get_audio_bytes(self, text: str, lang_code: str = "en") -> bytes | None:
        if not text or not text.strip() or not GTTS_AVAILABLE:
            return None
        try:
            short_code = lang_code.split("-")[0]
            tts = gTTS(text=text, lang=short_code, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            return fp.getvalue()
        except Exception as e:
            print(f"[gTTS bytes error] {e}")
            return None

    def _speak_gtts(self, text: str, lang_code: str) -> bool:
        path = None
        try:
            import uuid
            short_code = lang_code.split("-")[0]
            tts = gTTS(text=text, lang=short_code, slow=False)
            unique_filename = f"tts_{uuid.uuid4().hex}.mp3"
            path = os.path.join(tempfile.gettempdir(), unique_filename)
            tts.save(path)
            self._play(path)
            return True
        except Exception as e:
            print(f"[gTTS error] {e}")
            return self._speak_pyttsx3(text)
        finally:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except Exception as e:
                    print(f"[TTS cleanup error] {e}")

    def _speak_pyttsx3(self, text: str) -> bool:
        if not PYTTSX3_AVAILABLE:
            print("[TTS] No TTS engine available.")
            return False
        try:
            if self._engine is None:
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", 150)
                self._engine.setProperty("volume", 0.9)
            self._engine.say(text)
            self._engine.runAndWait()
            return True
        except Exception as e:
            print(f"[pyttsx3 error] {e}")
            return False

    @staticmethod
    def _play(path: str):
        import platform
        import subprocess
        system = platform.system()
        if system == "Darwin":
            subprocess.run(["afplay", path], check=False)
        elif system == "Linux":
            subprocess.run(
                ["sh", "-c", f"mpg123 '{path}' 2>/dev/null || aplay '{path}' 2>/dev/null"],
                check=False
            )
        elif system == "Windows":
            uri = path.replace("\\", "/")
            cmd = (
                "Add-Type -AssemblyName presentationCore; "
                "$mp = New-Object System.Windows.Media.MediaPlayer; "
                f"$mp.Open([uri]\"{uri}\"); "
                "$timeout = 0; "
                "while ((-not $mp.NaturalDuration.HasTimeSpan) -and ($timeout -lt 60)) { "
                "    Start-Sleep -Milliseconds 50; "
                "    $timeout++; "
                "} "
                "if ($mp.NaturalDuration.HasTimeSpan) { "
                "    $sec = $mp.NaturalDuration.TimeSpan.TotalSeconds; "
                "    $mp.Play(); "
                "    Start-Sleep -Milliseconds ([int](($sec + 0.3) * 1000)); "
                "} else { "
                "    $mp.Play(); "
                "    Start-Sleep -Seconds 3; "
                "} "
                "$mp.Close();"
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd],
                shell=False,
                check=False
            )


class SpeechRecognizer:
    """Records via sounddevice — no PyAudio needed. Python 3.14 compatible."""

    def __init__(self, record_seconds: int = 5):
        self.record_seconds = record_seconds
        if SR_AVAILABLE:
            self.recognizer = sr.Recognizer()
        else:
            self.recognizer = None

    def listen(self, timeout: int = 5, phrase_limit: int = 10) -> dict:
        result = {"success": False, "text": "", "error": ""}

        if not SR_AVAILABLE:
            result["error"] = "Install SpeechRecognition: pip install SpeechRecognition"
            return result

        if not SD_AVAILABLE:
            result["error"] = "Install sounddevice: pip install sounddevice scipy"
            return result

        try:
            wav_bytes = record_audio_sounddevice(
                duration=self.record_seconds,
                samplerate=16000
            )
            wav_io = io.BytesIO(wav_bytes)
            with sr.AudioFile(wav_io) as source:
                audio = self.recognizer.record(source)

            print("  🔄  Recognising speech...")
            text = self.recognizer.recognize_google(audio)
            result["success"] = True
            result["text"]    = text

        except sr.UnknownValueError:
            result["error"] = "Could not understand audio. Please speak clearly."
        except sr.RequestError as e:
            result["error"] = f"Speech API error: {e}"
        except Exception as e:
            result["error"] = f"Unexpected error: {e}"

        return result

    def recognize_audio(self, audio_source, language: str = "en-US") -> dict:
        result = {"success": False, "text": "", "error": ""}
        if not SR_AVAILABLE:
            result["error"] = "Install SpeechRecognition: pip install SpeechRecognition"
            return result

        try:
            if isinstance(audio_source, bytes):
                wav_io = io.BytesIO(audio_source)
            elif hasattr(audio_source, "getvalue"):
                wav_io = io.BytesIO(audio_source.getvalue())
            elif hasattr(audio_source, "read"):
                wav_io = io.BytesIO(audio_source.read())
            else:
                wav_io = audio_source

            with sr.AudioFile(wav_io) as source:
                audio = self.recognizer.record(source)

            text = self.recognizer.recognize_google(audio, language=language)
            result["success"] = True
            result["text"] = text
        except sr.UnknownValueError:
            result["error"] = "Could not understand audio. Please speak clearly."
        except sr.RequestError as e:
            result["error"] = f"Speech API error: {e}"
        except Exception as e:
            result["error"] = f"Audio recognition error: {e}"

        return result


class VoiceTranslationSystem:
    """Full pipeline: Mic → ASR → Detect → Translate → TTS"""

    def __init__(self, source_lang: str = "auto", target_lang: str = "en", tts_enabled: bool = True):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.tts_enabled = tts_enabled
        self.recognizer  = SpeechRecognizer(record_seconds=5)
        self.detector    = LanguageDetector()
        self.translator  = MachineTranslator()
        self.tts         = TextToSpeech(prefer_online=True)
        self.history: list = []

    def translate_once(self) -> dict:
        result = {"success": False, "original": "", "translated": "",
                  "src_lang": self.source_lang, "tgt_lang": self.target_lang, "error": ""}

        asr = self.recognizer.listen()
        if not asr["success"]:
            result["error"] = asr["error"]
            return result

        original = asr["text"]
        result["original"] = original
        print(f"\n  📝 You said   : \"{original}\"")

        detected_code, confidence = self.detector.detect(original)
        result["src_lang"] = detected_code
        src_name = LANGUAGES.get(detected_code, detected_code).title()
        print(f"  🔍 Detected   : {src_name} ({detected_code}) — {confidence:.0%} confidence")

        effective_src = self.source_lang

        if effective_src != "auto" and effective_src == self.target_lang:
            print("  ℹ️  Already in target language.")
            result["translated"] = original
            result["success"]    = True
            if self.tts_enabled:
                self.tts.speak(original, self.target_lang)
            return result

        try:
            translated, _ = self.translator.translate(
                original, target_lang=self.target_lang, source_lang=effective_src)
        except TranslationRateLimitError:
            result["error"] = "Translation service is busy. Please try again in a few seconds."
            return result
        except Exception as e:
            result["error"] = f"Translation error: {e}"
            return result

        result["translated"] = translated
        tgt_name = LANGUAGES.get(self.target_lang, self.target_lang).title()
        print(f"  🌐 Translated  : \"{translated}\"  [{tgt_name}]")

        if self.tts_enabled:
            print("  🔊 Speaking...")
            self.tts.speak(translated, self.target_lang)

        result["success"] = True
        self.history.append({
            "timestamp": time.strftime("%H:%M:%S"),
            "original": original, "translated": translated,
            "src_lang": detected_code, "tgt_lang": self.target_lang,
        })
        return result

    def run_continuous(self, rounds: int = 3):
        tgt_name = LANGUAGES.get(self.target_lang, self.target_lang).title()
        print(f"\n  Starting continuous translation → {tgt_name}")
        print("  Press Ctrl+C to stop.\n")
        count = 0
        try:
            while rounds == -1 or count < rounds:
                print(f"\n  {'─'*40}")
                print(f"  Round {count + 1}" + (f" of {rounds}" if rounds != -1 else ""))
                input("  Press ENTER to listen (Ctrl+C to quit)...")
                result = self.translate_once()
                if not result["success"]:
                    print(f"  ❌ {result['error']}")
                count += 1
        except KeyboardInterrupt:
            print("\n\n  ⏹ Stopped by user.")
        self._print_history()

    def _print_history(self):
        if not self.history:
            return
        print("\n\n  ── Session History ──────────────────────────")
        for entry in self.history:
            print(f"  [{entry['timestamp']}] ({entry['src_lang']} → {entry['tgt_lang']})")
            print(f"    Original   : {entry['original']}")
            print(f"    Translated : {entry['translated']}")
        print("  ─────────────────────────────────────────────\n")