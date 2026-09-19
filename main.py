"""
=============================================================
  Real-Time Voice Translation System
  Module: main.py
  Description: CLI entry point — text demo + voice pipeline
  Run: python main.py
=============================================================
"""

import sys
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import time
from core.translator_engine import (
    VoiceTranslationSystem,
    MachineTranslator,
    LanguageDetector,
    TextToSpeech,
    LANGUAGES
)


# ══════════════════════════════════════════════════════════
#  Pretty Print Helpers
# ══════════════════════════════════════════════════════════
def banner(title: str):
    width = 60
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)


def section(title: str):
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}")


# ══════════════════════════════════════════════════════════
#  DEMO 1 — Text Translation Showcase
# ══════════════════════════════════════════════════════════
def demo_text_translation():
    banner("DEMO 1 — Text Translation (no mic needed)")

    translator = MachineTranslator()
    detector   = LanguageDetector()

    samples = [
        # (input_text, target_language_code)
        ("Hello! How are you today?",             "fr"),
        ("Artificial Intelligence is the future.", "de"),
        ("I need help. Where is the hospital?",    "ta"),   # Tamil
        ("Good morning. Have a wonderful day.",    "ja"),
        ("Please translate this sentence.",        "ar"),
        ("Technology connects the whole world.",   "hi"),
        ("Bonjour, comment allez-vous?",           "en"),   # French → English
        ("Guten Morgen! Wie geht es Ihnen?",       "es"),   # German → Spanish
    ]

    for i, (text, tgt) in enumerate(samples, 1):
        section(f"Sample {i}")

        # Auto-detect source language
        src_code, confidence = detector.detect(text)
        src_name = LANGUAGES.get(src_code, src_code).title()
        tgt_name = LANGUAGES.get(tgt, tgt).title()

        translated, _ = translator.translate(text, target_lang=tgt)

        print(f"  Input  [{src_name} / {src_code}]: {text}")
        print(f"  Output [{tgt_name} / {tgt}]:  {translated}")
        print(f"  Detection confidence: {confidence:.0%}")

        time.sleep(0.3)   # avoid hammering the free API

    print("\n✅ Demo 1 complete!\n")


# ══════════════════════════════════════════════════════════
#  DEMO 2 — Algorithm Walk-Through
# ══════════════════════════════════════════════════════════
def demo_algorithm():
    banner("DEMO 2 — Step-by-Step Algorithm")

    steps = [
        ("STEP 1 — INPUT",
         "User speaks into the microphone or types text."),

        ("STEP 2 — AUDIO CAPTURE (PyAudio)",
         "Raw audio is recorded from the default microphone at 16kHz."),

        ("STEP 3 — SPEECH-TO-TEXT (Google ASR)",
         "Audio frames are sent to Google Web Speech API.\n"
         "          API returns a text transcript."),

        ("STEP 4 — LANGUAGE DETECTION (NLP)",
         "The transcript is sent to Google Translate's detect() API.\n"
         "          Returns: language code + confidence score."),

        ("STEP 5 — MACHINE TRANSLATION",
         "Detected (or user-specified) language + transcript\n"
         "          are sent to the translation engine.\n"
         "          Returns: translated text in target language."),

        ("STEP 6 — TEXT-TO-SPEECH (pyttsx3)",
         "Translated text is fed to the TTS engine.\n"
         "          Engine synthesizes speech and plays through speakers."),

        ("STEP 7 — OUTPUT",
         "User hears the translation + sees it on screen.\n"
         "          Session is logged to history."),
    ]

    for title, desc in steps:
        print(f"\n  🔹 {title}")
        print(f"          {desc}")
        time.sleep(0.1)

    print("\n\n  PSEUDOCODE:")
    print("""
  ┌─────────────────────────────────────────────────────┐
  │  function translate_voice():                        │
  │    audio  ← capture_microphone(timeout=5s)         │
  │    text   ← speech_to_text(audio, lang=src_lang)   │
  │    if text is None: return error                   │
  │    src    ← detect_language(text)                  │
  │    result ← translate(text, src→target_lang)       │
  │    if tts_enabled: speak(result, lang=target_lang) │
  │    log(text, src, result, target)                  │
  │    return result                                   │
  └─────────────────────────────────────────────────────┘
  """)


# ══════════════════════════════════════════════════════════
#  DEMO 3 — Data Flow
# ══════════════════════════════════════════════════════════
def demo_dataflow():
    banner("DEMO 3 — Data Flow Explanation")

    print("""
  The system processes data through 4 discrete stages:

  ┌──────────┐    PCM Audio     ┌──────────┐   Text String  ┌──────────────┐
  │ Mic /    │ ─────────────►  │  ASR     │ ─────────────► │  Language    │
  │ Text Box │  (wav bytes)     │  Engine  │  ("Hello…")    │  Detector    │
  └──────────┘                 └──────────┘                 └──────┬───────┘
                                                                    │
                                                           lang="en", conf=0.98
                                                                    │
  ┌──────────┐  Synthesized    ┌──────────┐  Translated    ┌────────▼──────┐
  │ Speaker  │ ◄────────────── │  TTS     │ ◄────────────  │  Translation  │
  │ Screen   │  Speech + Text  │  Engine  │  ("Hola…")     │  Engine       │
  └──────────┘                 └──────────┘                └───────────────┘

  Data formats at each stage:
    • Mic       → bytes (16-bit PCM WAV @ 16kHz)
    • ASR       → str  (UTF-8 text)
    • Detector  → (str, float) — (lang_code, confidence)
    • Translator→ str  (UTF-8 translated text)
    • TTS       → bytes (audio) → played via system speakers
  """)


# ══════════════════════════════════════════════════════════
#  DEMO 4 — Supported Languages
# ══════════════════════════════════════════════════════════
def demo_languages():
    banner("DEMO 4 — Supported Language Codes (sample)")

    popular = [
        ("en", "English"), ("es", "Spanish"), ("fr", "French"),
        ("de", "German"),  ("zh-cn", "Chinese"), ("ja", "Japanese"),
        ("ko", "Korean"),  ("ar", "Arabic"),  ("hi", "Hindi"),
        ("ta", "Tamil"),   ("te", "Telugu"),  ("pt", "Portuguese"),
        ("ru", "Russian"), ("it", "Italian"), ("tr", "Turkish"),
        ("nl", "Dutch"),   ("pl", "Polish"),  ("vi", "Vietnamese"),
    ]

    print(f"\n  {'Code':<12} {'Language'}")
    print(f"  {'─'*10} {'─'*20}")
    for code, name in popular:
        print(f"  {code:<12} {name}")

    total = len(LANGUAGES)
    print(f"\n  …and {total - len(popular)} more! Total: {total} languages supported.")


# ══════════════════════════════════════════════════════════
#  DEMO 5 — Voice Pipeline (real mic, optional)
# ══════════════════════════════════════════════════════════
def demo_voice(target_lang: str = "es", rounds: int = 3):
    banner("DEMO 5 — Live Voice Translation")
    print(f"  Target language: {LANGUAGES.get(target_lang, target_lang).title()}")
    print("  Press Ctrl+C to stop early.\n")

    system = VoiceTranslationSystem(
        source_lang="auto",
        target_lang=target_lang
    )
    system.run_continuous(rounds=rounds)


# ══════════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════════
def main():
    banner("REAL-TIME VOICE TRANSLATION SYSTEM  v1.0")

    print("""
  Select a demo to run:
    1 — Text Translation Demo (no mic)
    2 — Algorithm Walk-Through
    3 — Data Flow Explanation
    4 — Supported Languages
    5 — Live Voice Translation (requires mic)
    6 — Run all non-interactive demos
    q — Quit
    """)

    choice = input("  Enter choice: ").strip().lower()

    demos = {
        "1": demo_text_translation,
        "2": demo_algorithm,
        "3": demo_dataflow,
        "4": demo_languages,
    }

    if choice == "q":
        print("\n  Goodbye! 👋\n")
        sys.exit(0)
    elif choice == "5":
        lang = input("  Target language code (e.g. es, fr, de, ta): ").strip() or "es"
        rounds = int(input("  Number of rounds [3]: ").strip() or "3")
        demo_voice(lang, rounds)
    elif choice == "6":
        for fn in demos.values():
            fn()
    elif choice in demos:
        demos[choice]()
    else:
        print("  Invalid choice.")

    print("\n  ─── Done ───\n")


if __name__ == "__main__":
    main()
