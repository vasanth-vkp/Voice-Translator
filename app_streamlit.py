"""
=============================================================
  Real-Time Voice Translation System
  Module: app_streamlit.py
  Description: Streamlit-based web UI (Browser audio input & playback)
  Run: streamlit run app_streamlit.py
=============================================================
"""

import streamlit as st
import time
import io

from core.translator_engine import (
    MachineTranslator,
    LanguageDetector,
    SpeechRecognizer,
    TextToSpeech,
    LANGUAGES
)

# ── Page Configuration ─────────────────────────────────────
st.set_page_config(
    page_title="VoiceTranslate AI",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .result-box {
        background: #f0f4ff;
        border-left: 4px solid #4f46e5;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .translated-box {
        background: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-size: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🌐 Real-Time Voice Translation System</h1>
    <p style="opacity:0.8; margin:0">Speak → Detect → Translate → Listen</p>
</div>
""", unsafe_allow_html=True)


# ── Session State ──────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "total_chars" not in st.session_state:
    st.session_state.total_chars = 0


# ── Cached Engine Instances & Helper Functions ─────────────
@st.cache_resource
def get_translator():
    return MachineTranslator()


@st.cache_resource
def get_detector():
    return LanguageDetector()


@st.cache_resource
def get_recognizer():
    return SpeechRecognizer()


@st.cache_resource
def get_tts():
    return TextToSpeech(prefer_online=True)


def get_language_options():
    """Return sorted dict of {display_name: code}."""
    return {v.title(): k for k, v in sorted(LANGUAGES.items(), key=lambda x: x[1])}


def detect_language(text: str) -> tuple[str, str]:
    """Returns (lang_code, lang_name)."""
    detector = get_detector()
    code, _ = detector.detect(text)
    return code, LANGUAGES.get(code, code).title()


def translate_text(text: str, target: str, source: str = "auto") -> str:
    """Translates text and returns result string."""
    translator = get_translator()
    result, _ = translator.translate(text, target_lang=target, source_lang=source)
    return result


def play_audio(text: str, lang_code: str = "en"):
    """Generate audio bytes via gTTS and render directly in the browser player."""
    tts = get_tts()
    audio_bytes = tts.get_audio_bytes(text, lang_code=lang_code)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")


# ══════════════════════════════════════════════════════════
#  SIDEBAR — Settings
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.header("⚙️ Settings")

    lang_options = get_language_options()
    lang_codes = list(lang_options.values())
    lang_names = list(lang_options.keys())

    # Source language
    st.subheader("🎙 Source Language")
    auto_detect = st.checkbox("Auto-detect", value=True)

    if auto_detect:
        source_lang_code = "auto"
        source_lang_display = "Auto Detect"
        st.info("Language will be detected automatically.")
    else:
        src_idx = lang_names.index("English") if "English" in lang_names else 0
        source_lang_name = st.selectbox("Speak in:", lang_names, index=src_idx, key="src")
        source_lang_code = lang_options[source_lang_name]
        source_lang_display = source_lang_name

    st.divider()

    # Target language
    st.subheader("🌐 Target Language")
    tgt_default = lang_names.index("Spanish") if "Spanish" in lang_names else 1
    target_lang_name = st.selectbox("Translate to:", lang_names, index=tgt_default, key="tgt")
    target_lang_code = lang_options[target_lang_name]

    st.divider()

    # TTS settings
    st.subheader("🔊 Voice Output")
    enable_tts = st.checkbox("Enable Text-to-Speech", value=True)

    st.divider()
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.session_state.total_chars = 0
        st.rerun()


# ══════════════════════════════════════════════════════════
#  MAIN AREA — Two modes
# ══════════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["🎙 Voice Mode", "✍️ Text Mode"])

# ─────────────────────────────────────────────────────────
#  TAB 1 — Voice Input (Browser Microphone)
# ─────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Step 1 — Record Your Voice")
        st.info(
            f"**Source:** {source_lang_display} → "
            f"**Target:** {target_lang_name} ({target_lang_code.upper()})"
        )

        # Uses browser microphone (Streamlit audio_input)
        audio_input = st.audio_input("🎙 Record your voice in the browser:", key="browser_mic")

        if audio_input is not None:
            mic_lang = (
                "en-US"
                if source_lang_code == "auto"
                else f"{source_lang_code}-{source_lang_code.upper()}"
            )

            with st.spinner("Processing audio from browser microphone…"):
                recognizer = get_recognizer()
                asr_result = recognizer.recognize_audio(audio_input, language=mic_lang)

            if asr_result.get("success") and asr_result.get("text"):
                recognized_text = asr_result["text"]
                st.success(f"✅ Recognized: **{recognized_text}**")

                # Language detection
                detected_code, detected_name = detect_language(recognized_text)
                actual_src = source_lang_code if source_lang_code != "auto" else detected_code

                with st.spinner("🌐 Translating…"):
                    translated = translate_text(recognized_text, target_lang_code, actual_src)

                if translated:
                    st.markdown(f"""
                    <div class="result-box">
                        <strong>🎙 You said ({detected_name}):</strong><br>
                        <span style="font-size:1.1rem">{recognized_text}</span>
                    </div>
                    <div class="translated-box">
                        <strong>🌐 Translation ({target_lang_name}):</strong><br>
                        <span style="font-size:1.2rem; font-weight:600">{translated}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    if enable_tts:
                        st.write("🔊 **Listen to Translation:**")
                        play_audio(translated, lang_code=target_lang_code)

                    # Save to history
                    st.session_state.history.append({
                        "time": time.strftime("%H:%M:%S"),
                        "mode": "Voice",
                        "original": recognized_text,
                        "src_lang": detected_name,
                        "translated": translated,
                        "tgt_lang": target_lang_name
                    })
                    st.session_state.total_chars += len(recognized_text)
                else:
                    st.error("Translation failed. Please try again.")
            else:
                err = asr_result.get("error") or "No speech detected. Please speak clearly and try again."
                st.warning(f"⚠️ {err}")

    with col2:
        st.subheader("📊 Stats")
        st.metric("Sessions", len(st.session_state.history))
        st.metric("Chars Translated", st.session_state.total_chars)

        st.subheader("🗺 Language Pair")
        st.markdown(f"""
        ```
        {source_lang_display}
             ↓
        {target_lang_name}
        ({target_lang_code.upper()})
        ```
        """)


# ─────────────────────────────────────────────────────────
#  TAB 2 — Text Input
# ─────────────────────────────────────────────────────────
with tab2:
    st.subheader("Type or paste text to translate")

    input_text = st.text_area(
        "Input text:",
        placeholder="Type something here…",
        height=120
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        translate_btn = st.button("🌐 Translate", type="primary", key="text_translate")
    with col_b:
        detect_btn = st.button("🔍 Detect Language Only", key="detect_btn")
    with col_c:
        speak_btn = st.button("🔊 Speak Input", key="speak_input")

    if detect_btn and input_text:
        code, name = detect_language(input_text)
        st.success(f"Detected language: **{name}** (`{code}`)")

    if speak_btn and input_text:
        st.write("🔊 **Listen to Input:**")
        play_audio(input_text, lang_code=source_lang_code if source_lang_code != "auto" else "en")

    if translate_btn and input_text:
        actual_src = source_lang_code
        detected_code, detected_name = detect_language(input_text)
        if source_lang_code == "auto":
            actual_src = detected_code

        with st.spinner("Translating…"):
            translated = translate_text(input_text, target_lang_code, actual_src)

        if translated:
            st.markdown(f"""
            <div class="result-box">
                <strong>Input ({detected_name}):</strong><br>
                {input_text}
            </div>
            <div class="translated-box">
                <strong>Translation ({target_lang_name}):</strong><br>
                <span style="font-size:1.15rem; font-weight:600">{translated}</span>
            </div>
            """, unsafe_allow_html=True)

            if enable_tts:
                st.write("🔊 **Listen to Translation:**")
                play_audio(translated, lang_code=target_lang_code)

            st.session_state.history.append({
                "time": time.strftime("%H:%M:%S"),
                "mode": "Text",
                "original": input_text,
                "src_lang": detected_name,
                "translated": translated,
                "tgt_lang": target_lang_name
            })
            st.session_state.total_chars += len(input_text)
        else:
            st.error("Translation failed.")


# ══════════════════════════════════════════════════════════
#  HISTORY TABLE
# ══════════════════════════════════════════════════════════
st.divider()
st.subheader("📋 Translation History")

if st.session_state.history:
    import pandas as pd
    df = pd.DataFrame(st.session_state.history)
    df.columns = ["Time", "Mode", "Original", "Source Lang", "Translation", "Target Lang"]
    st.dataframe(df, width="stretch", hide_index=True)
else:
    st.info("No translations yet. Start recording or typing!")
