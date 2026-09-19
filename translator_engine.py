"""
=============================================================
  Real-Time Voice Translation System
  Module: translator_engine.py
  Description: Core translation engine — ASR → NLP → MT → TTS
=============================================================
"""

import speech_recognition as sr
from googletrans import Translator, LANGUAGES
import pyttsx3
import time
import logging

# ── Logging Setup ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s » %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#  COMPONENT 1 — Speech Recognition (ASR)
# ═══════════════════════════════════════════════════════════
class SpeechRecognizer:
    """
    Captures voice from the microphone and converts it to text.
    Uses Google Web Speech API (free, no key needed for basic use).
    """

    def __init__(self, language: str = "en-US", timeout: int = 5):
        self.recognizer = sr.Recognizer()
        self.language = language          # e.g. "en-US", "fr-FR", "ta-IN"
        self.timeout = timeout            # max seconds to wait for speech

        # Tune for ambient noise sensitivity
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8   # silence gap before ending

    def calibrate_noise(self, source: sr.AudioSource, duration: float = 1.5):
        """Adjust microphone sensitivity to background noise level."""
        log.info("Calibrating microphone to ambient noise…")
        self.recognizer.adjust_for_ambient_noise(source, duration=duration)
        log.info(f"Energy threshold set to {self.recognizer.energy_threshold:.0f}")

    def listen(self) -> tuple[str | None, str | None]:
        """
        Listens to microphone and returns (text, detected_language_code).
        Returns (None, None) on failure.
        """
        with sr.Microphone() as source:
            self.calibrate_noise(source)
            log.info("🎙  Listening… Speak now!")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=15
                )
            except sr.WaitTimeoutError:
                log.warning("No speech detected within timeout period.")
                return None, None

        return self._recognize(audio)

    def _recognize(self, audio: sr.AudioData) -> tuple[str | None, str | None]:
        """Send audio to Google STT API and return transcript."""
        try:
            # Google STT — returns text in the source language
            text = self.recognizer.recognize_google(
                audio,
                language=self.language,
                show_all=False
            )
            log.info(f"📝 Recognized: '{text}'")
            return text, self.language.split("-")[0]   # e.g. "en"

        except sr.UnknownValueError:
            log.error("Could not understand the audio. Please speak clearly.")
        except sr.RequestError as e:
            log.error(f"STT API error: {e}")

        return None, None


# ═══════════════════════════════════════════════════════════
#  COMPONENT 2 — Language Detection (NLP)
# ═══════════════════════════════════════════════════════════
class LanguageDetector:
    """
    Uses googletrans to auto-detect the language of input text.
    Useful when the user's source language is unknown.
    """

    def __init__(self):
        self.translator = Translator()

    def detect(self, text: str) -> tuple[str, float]:
        """
        Returns (language_code, confidence).
        e.g. ("en", 0.98)
        """
        try:
            result = self.translator.detect(text)
            lang_name = LANGUAGES.get(result.lang, result.lang)
            log.info(
                f"🔍 Detected language: {lang_name} "
                f"({result.lang}) — confidence {result.confidence:.2%}"
            )
            return result.lang, result.confidence
        except Exception as e:
            log.error(f"Language detection failed: {e}")
            return "en", 0.0


# ═══════════════════════════════════════════════════════════
#  COMPONENT 3 — Machine Translation
# ═══════════════════════════════════════════════════════════
class MachineTranslator:
    """
    Translates text from one language to another using Google Translate.
    Supports 100+ languages via googletrans.
    """

    def __init__(self):
        self.translator = Translator()
        self.detector = LanguageDetector()

    def translate(
        self,
        text: str,
        target_lang: str,
        source_lang: str = "auto"
    ) -> tuple[str | None, str]:
        """
        Translates text.
        Returns (translated_text, detected_source_language).
        """
        if not text or not text.strip():
            log.warning("Empty text received — skipping translation.")
            return None, source_lang

        try:
            result = self.translator.translate(
                text,
                dest=target_lang,
                src=source_lang
            )
            src = LANGUAGES.get(result.src, result.src)
            tgt = LANGUAGES.get(result.dest, result.dest)
            log.info(f"🌐 Translated [{src} → {tgt}]: '{result.text}'")
            return result.text, result.src

        except Exception as e:
            log.error(f"Translation failed: {e}")
            return None, source_lang

    @staticmethod
    def list_languages() -> dict[str, str]:
        """Return all supported languages as {code: name}."""
        return dict(sorted(LANGUAGES.items(), key=lambda x: x[1]))


# ═══════════════════════════════════════════════════════════
#  COMPONENT 4 — Text-to-Speech (TTS)
# ═══════════════════════════════════════════════════════════
class TextToSpeech:
    """
    Converts translated text to audible speech.
    Primary: pyttsx3 (offline, no internet needed).
    Fallback: prints text if TTS engine fails.
    """

    def __init__(self, rate: int = 160, volume: float = 1.0):
        self.engine = None
        self.rate = rate        # words per minute
        self.volume = volume    # 0.0 – 1.0
        self._init_engine()

    def _init_engine(self):
        """Initialize pyttsx3 engine safely."""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self.rate)
            self.engine.setProperty("volume", self.volume)
            log.info("🔊 TTS engine initialized (pyttsx3).")
        except Exception as e:
            log.warning(f"TTS engine init failed ({e}). Audio output disabled.")

    def speak(self, text: str, lang: str = "en"):
        """Convert text to speech. Falls back to print if engine unavailable."""
        if not text:
            return

        log.info(f"🔈 Speaking [{lang}]: '{text}'")

        if self.engine:
            try:
                # Try to select a voice matching the target language
                voices = self.engine.getProperty("voices")
                for voice in voices:
                    if lang.lower() in voice.id.lower() or \
                       lang.lower() in voice.name.lower():
                        self.engine.setProperty("voice", voice.id)
                        break

                self.engine.say(text)
                self.engine.runAndWait()
                return
            except Exception as e:
                log.warning(f"TTS speak error: {e}")

        # Fallback: just print
        print(f"\n🔈 [Audio Output — {lang}]: {text}\n")


# ═══════════════════════════════════════════════════════════
#  ORCHESTRATOR — Ties all components together
# ═══════════════════════════════════════════════════════════
class VoiceTranslationSystem:
    """
    High-level orchestrator for the full pipeline:
      Mic → ASR → Language Detection → Translation → TTS
    """

    def __init__(
        self,
        source_lang: str = "auto",
        target_lang: str = "es",
        tts_rate: int = 160
    ):
        self.source_lang = source_lang
        self.target_lang = target_lang

        # Instantiate all components
        self.asr = SpeechRecognizer(
            language="en-US" if source_lang == "auto" else f"{source_lang}-XX"
        )
        self.translator = MachineTranslator()
        self.tts = TextToSpeech(rate=tts_rate)

        log.info(
            f"✅ VoiceTranslationSystem ready │ "
            f"src={source_lang} │ tgt={target_lang}"
        )

    # ── Single Translation Cycle ───────────────────────────
    def translate_once(self) -> dict:
        """
        Run one full voice-to-translated-speech cycle.
        Returns a result dict with all intermediate values.
        """
        result = {
            "original_text": None,
            "source_lang": self.source_lang,
            "translated_text": None,
            "target_lang": self.target_lang,
            "success": False,
            "timestamp": time.strftime("%H:%M:%S")
        }

        # Step 1 — Capture voice
        text, detected_src = self.asr.listen()
        if not text:
            result["error"] = "No speech captured."
            return result

        result["original_text"] = text

        # Step 2 — Translate
        translated, actual_src = self.translator.translate(
            text,
            target_lang=self.target_lang,
            source_lang=self.source_lang
        )
        if not translated:
            result["error"] = "Translation failed."
            return result

        result["translated_text"] = translated
        result["source_lang"] = actual_src
        result["success"] = True

        # Step 3 — Speak the translation
        self.tts.speak(translated, lang=self.target_lang)

        return result

    # ── Continuous / Real-Time Mode ────────────────────────
    def run_continuous(self, rounds: int = 10):
        """
        Continuously listen and translate.
        Press Ctrl+C to stop, or set rounds to limit cycles.
        """
        log.info(f"🔁 Starting continuous translation (max {rounds} rounds)…")
        print("\n" + "═" * 60)
        print("  REAL-TIME VOICE TRANSLATION SYSTEM  —  Running")
        print("  Press Ctrl+C to stop")
        print("═" * 60 + "\n")

        for i in range(rounds):
            print(f"\n{'─'*40}")
            print(f"  Round {i + 1}/{rounds}")
            print(f"{'─'*40}")

            result = self.translate_once()

            if result["success"]:
                print(f"  🎙  You said  [{result['source_lang']}]: {result['original_text']}")
                print(f"  🌐  Translated [{result['target_lang']}]: {result['translated_text']}")
            else:
                print(f"  ⚠️  {result.get('error', 'Unknown error')}")

        print("\n✅ Translation session complete.")


# ═══════════════════════════════════════════════════════════
#  Quick self-test (text-only, no mic required)
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n── Self-Test: Text Translation (no mic) ──\n")
    tr = MachineTranslator()

    samples = [
        ("Hello, how are you today?", "fr"),
        ("Good morning! Have a nice day.", "de"),
        ("I love programming.", "ja"),
        ("Where is the nearest hospital?", "ta"),
    ]

    for text, tgt in samples:
        translated, src = tr.translate(text, target_lang=tgt)
        print(f"  [{src} → {tgt}] '{text}'  →  '{translated}'")

    print("\nSelf-test complete ✅")
