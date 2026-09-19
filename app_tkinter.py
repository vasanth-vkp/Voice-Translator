"""
=============================================================
  Real-Time Voice Translation System
  Module: app_tkinter.py
  Description: Full desktop GUI using Tkinter
  Run: python app_tkinter.py
=============================================================
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import logging

from core.translator_engine import (
    MachineTranslator,
    LanguageDetector,
    SpeechRecognizer,
    TextToSpeech,
    LANGUAGES
)

log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════
#  Backend helpers using core.translator_engine
# ══════════════════════════════════════════════════════════
TRANSLATOR = MachineTranslator()
DETECTOR   = LanguageDetector()
TTS        = TextToSpeech(prefer_online=True)
RECOGNIZER = SpeechRecognizer(record_seconds=5)

LANG_OPTIONS = {v.title(): k for k, v in sorted(LANGUAGES.items(), key=lambda x: x[1])}
LANG_NAMES   = list(LANG_OPTIONS.keys())


def detect_language(text: str) -> tuple[str, str]:
    lang_code, _ = DETECTOR.detect(text)
    return lang_code, LANGUAGES.get(lang_code, lang_code).title()


def translate_text(text: str, target: str, source: str = "auto") -> str:
    translated, _ = TRANSLATOR.translate(text, target_lang=target, source_lang=source)
    return translated


def speak_async(text: str, lang_code: str = "en"):
    def _speak():
        try:
            TTS.speak(text, lang_code=lang_code)
        except Exception as e:
            log.warning(f"TTS error: {e}")
    threading.Thread(target=_speak, daemon=True).start()


def recognize_mic(lang_code: str = "en", timeout: int = 5) -> str | None:
    res = RECOGNIZER.listen(timeout=timeout)
    if res.get("success"):
        return res.get("text")
    return None


# ══════════════════════════════════════════════════════════
#  Main Application Window
# ══════════════════════════════════════════════════════════
class VoiceTranslatorApp(tk.Tk):

    # ── Colour Palette ─────────────────────────────────────
    BG       = "#0f1117"
    SURFACE  = "#1a1d27"
    ACCENT   = "#6366f1"     # indigo
    ACCENT2  = "#10b981"     # emerald
    FG       = "#e2e8f0"
    FG_DIM   = "#94a3b8"
    DANGER   = "#ef4444"
    WARN     = "#f59e0b"

    def __init__(self):
        super().__init__()
        self.title("🌐  Real-Time Voice Translation System")
        self.geometry("1000x720")
        self.configure(bg=self.BG)
        self.resizable(True, True)

        # State
        self.is_recording = False
        self.history: list[dict] = []
        self.tts_enabled = tk.BooleanVar(value=True)
        self.auto_detect = tk.BooleanVar(value=True)

        self._build_ui()
        self._status("Ready. Select languages and press Record.", color=self.ACCENT2)

    # ── UI Construction ────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        self._build_body()
        self._build_statusbar()

    def _build_header(self):
        hdr = tk.Frame(self, bg=self.ACCENT, height=70)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(
            hdr,
            text="🌐  Real-Time Voice Translation System",
            font=("Helvetica", 20, "bold"),
            bg=self.ACCENT, fg="white"
        ).pack(expand=True)

    def _build_body(self):
        body = tk.Frame(self, bg=self.BG)
        body.pack(fill="both", expand=True, padx=16, pady=12)

        # Left panel — controls
        left = tk.Frame(body, bg=self.SURFACE, width=280)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)
        self._build_controls(left)

        # Right panel — IO
        right = tk.Frame(body, bg=self.BG)
        right.pack(side="left", fill="both", expand=True)
        self._build_io(right)

    def _build_controls(self, parent):
        pad = {"padx": 14, "pady": 6}

        tk.Label(parent, text="⚙  Settings", font=("Helvetica", 13, "bold"),
                 bg=self.SURFACE, fg=self.FG).pack(anchor="w", **pad)

        tk.Frame(parent, bg=self.ACCENT, height=2).pack(fill="x", padx=14, pady=2)

        # Source language
        tk.Label(parent, text="Source Language", font=("Helvetica", 10),
                 bg=self.SURFACE, fg=self.FG_DIM).pack(anchor="w", **pad)

        tk.Checkbutton(
            parent, text="Auto-Detect", variable=self.auto_detect,
            bg=self.SURFACE, fg=self.FG, selectcolor=self.SURFACE,
            activebackground=self.SURFACE, font=("Helvetica", 10),
            command=self._toggle_src
        ).pack(anchor="w", padx=14)

        self.src_var = tk.StringVar(value="English")
        self.src_combo = ttk.Combobox(
            parent, textvariable=self.src_var,
            values=LANG_NAMES, state="disabled", width=24
        )
        self.src_combo.pack(padx=14, pady=4, fill="x")

        # Target language
        tk.Label(parent, text="Target Language", font=("Helvetica", 10),
                 bg=self.SURFACE, fg=self.FG_DIM).pack(anchor="w", **pad)

        self.tgt_var = tk.StringVar(value="Spanish")
        ttk.Combobox(
            parent, textvariable=self.tgt_var,
            values=LANG_NAMES, state="readonly", width=24
        ).pack(padx=14, pady=4, fill="x")

        tk.Frame(parent, bg="#2d3148", height=1).pack(fill="x", padx=14, pady=8)

        # TTS
        tk.Checkbutton(
            parent, text="🔊 Enable Text-to-Speech", variable=self.tts_enabled,
            bg=self.SURFACE, fg=self.FG, selectcolor=self.SURFACE,
            activebackground=self.SURFACE, font=("Helvetica", 10)
        ).pack(anchor="w", padx=14)

        tk.Label(parent, text="Speaking Rate (WPM)", font=("Helvetica", 9),
                 bg=self.SURFACE, fg=self.FG_DIM).pack(anchor="w", padx=14, pady=(8, 0))

        self.rate_var = tk.IntVar(value=160)
        ttk.Scale(parent, from_=80, to=250, variable=self.rate_var,
                  orient="horizontal").pack(fill="x", padx=14, pady=2)

        tk.Label(parent, text="Mic Timeout (seconds)", font=("Helvetica", 9),
                 bg=self.SURFACE, fg=self.FG_DIM).pack(anchor="w", padx=14, pady=(8, 0))

        self.timeout_var = tk.IntVar(value=5)
        ttk.Scale(parent, from_=3, to=15, variable=self.timeout_var,
                  orient="horizontal").pack(fill="x", padx=14, pady=2)

        tk.Frame(parent, bg="#2d3148", height=1).pack(fill="x", padx=14, pady=8)

        # Stats
        tk.Label(parent, text="📊 Session Stats", font=("Helvetica", 10, "bold"),
                 bg=self.SURFACE, fg=self.FG).pack(anchor="w", **pad)

        self.stat_sessions = tk.StringVar(value="Sessions: 0")
        self.stat_chars    = tk.StringVar(value="Chars: 0")

        tk.Label(parent, textvariable=self.stat_sessions, font=("Helvetica", 9),
                 bg=self.SURFACE, fg=self.FG_DIM).pack(anchor="w", padx=14)
        tk.Label(parent, textvariable=self.stat_chars, font=("Helvetica", 9),
                 bg=self.SURFACE, fg=self.FG_DIM).pack(anchor="w", padx=14)

        # Clear button
        tk.Button(
            parent, text="🗑  Clear History",
            bg="#2d3148", fg=self.FG, relief="flat",
            font=("Helvetica", 10), cursor="hand2",
            command=self._clear_history
        ).pack(padx=14, pady=12, fill="x")

    def _build_io(self, parent):
        # Input section
        tk.Label(parent, text="🎙  Input / Recognized Text",
                 font=("Helvetica", 11, "bold"),
                 bg=self.BG, fg=self.FG).pack(anchor="w", pady=(0, 4))

        self.input_text = scrolledtext.ScrolledText(
            parent, height=5, bg=self.SURFACE, fg=self.FG,
            font=("Courier", 11), insertbackground=self.FG,
            relief="flat", wrap="word", border=0,
            highlightthickness=1, highlightbackground=self.ACCENT
        )
        self.input_text.pack(fill="x", pady=(0, 8))

        # Buttons row
        btn_row = tk.Frame(parent, bg=self.BG)
        btn_row.pack(fill="x", pady=6)

        self.record_btn = tk.Button(
            btn_row, text="🎙  Record Voice",
            bg=self.ACCENT, fg="white", relief="flat",
            font=("Helvetica", 11, "bold"), padx=20, pady=10,
            cursor="hand2", command=self._start_record
        )
        self.record_btn.pack(side="left", padx=(0, 8))

        tk.Button(
            btn_row, text="🌐  Translate Text",
            bg=self.ACCENT2, fg="white", relief="flat",
            font=("Helvetica", 11, "bold"), padx=20, pady=10,
            cursor="hand2", command=self._translate_text_input
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_row, text="🔊  Speak Output",
            bg="#7c3aed", fg="white", relief="flat",
            font=("Helvetica", 11), padx=14, pady=10,
            cursor="hand2", command=self._speak_output
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_row, text="✖  Clear",
            bg="#374151", fg=self.FG, relief="flat",
            font=("Helvetica", 11), padx=14, pady=10,
            cursor="hand2", command=self._clear_io
        ).pack(side="left")

        # Output section
        info_row = tk.Frame(parent, bg=self.BG)
        info_row.pack(fill="x", pady=(8, 4))

        tk.Label(info_row, text="🌐  Translation Output",
                 font=("Helvetica", 11, "bold"),
                 bg=self.BG, fg=self.FG).pack(side="left")

        self.lang_info = tk.Label(
            info_row, text="", font=("Helvetica", 9),
            bg=self.BG, fg=self.FG_DIM
        )
        self.lang_info.pack(side="right")

        self.output_text = scrolledtext.ScrolledText(
            parent, height=5, bg="#0d1f12", fg="#6ee7b7",
            font=("Courier", 12, "bold"), relief="flat", wrap="word",
            state="disabled", border=0,
            highlightthickness=1, highlightbackground=self.ACCENT2
        )
        self.output_text.pack(fill="x", pady=(0, 12))

        # History
        tk.Label(parent, text="📋  History",
                 font=("Helvetica", 11, "bold"),
                 bg=self.BG, fg=self.FG).pack(anchor="w", pady=(4, 4))

        cols = ("Time", "Mode", "Original", "Source", "Translation", "Target")
        self.history_tree = ttk.Treeview(
            parent, columns=cols, show="headings", height=8
        )
        for col in cols:
            self.history_tree.heading(col, text=col)
            w = 80 if col in ("Time", "Mode", "Source", "Target") else 200
            self.history_tree.column(col, width=w)

        scrollbar = ttk.Scrollbar(parent, orient="vertical",
                                   command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        tree_frame = tk.Frame(parent, bg=self.BG)
        tree_frame.pack(fill="both", expand=True)
        self.history_tree.pack(in_=tree_frame, side="left", fill="both", expand=True)
        scrollbar.pack(in_=tree_frame, side="right", fill="y")

    def _build_statusbar(self):
        self.status_bar = tk.Label(
            self, text="", font=("Helvetica", 9),
            bg="#0a0d13", fg=self.FG_DIM, anchor="w", padx=12
        )
        self.status_bar.pack(fill="x", side="bottom", ipady=4)

    # ── Event Handlers ─────────────────────────────────────
    def _toggle_src(self):
        state = "disabled" if self.auto_detect.get() else "readonly"
        self.src_combo.config(state=state)

    def _status(self, msg: str, color: str = "#94a3b8"):
        self.status_bar.config(text=f"  {msg}", fg=color)
        self.update_idletasks()

    def _start_record(self):
        if self.is_recording:
            return
        self.is_recording = True
        self.record_btn.config(text="🔴  Recording…", bg=self.DANGER, state="disabled")
        self._status("🎙 Listening… speak now!", color=self.WARN)

        src_name = self.src_var.get()
        src_code = LANG_OPTIONS.get(src_name, "en")
        mic_lang = "en-US" if self.auto_detect.get() else f"{src_code}-{src_code.upper()}"
        timeout = int(self.timeout_var.get())

        threading.Thread(target=self._record_thread, args=(mic_lang, timeout), daemon=True).start()

    def _record_thread(self, mic_lang: str, timeout: int):
        text = recognize_mic(mic_lang, timeout)
        self.after(0, lambda: self._on_record_done(text))

    def _on_record_done(self, text: str | None):
        self.is_recording = False
        self.record_btn.config(text="🎙  Record Voice", bg=self.ACCENT, state="normal")

        if not text:
            self._status("⚠ No speech detected. Try again.", color=self.WARN)
            return

        self._set_input(text)
        self._status(f"✅ Recognized: '{text[:60]}…'", color=self.ACCENT2)
        self._do_translate(text, mode="Voice")

    def _translate_text_input(self):
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Empty Input", "Please type or record something first.")
            return
        self._do_translate(text, mode="Text")

    def _do_translate(self, text: str, mode: str = "Text"):
        self._status("🌐 Translating…", color=self.ACCENT)
        auto_detect = self.auto_detect.get()
        src_name = self.src_var.get()
        tgt_name = self.tgt_var.get()
        threading.Thread(
            target=self._translate_thread,
            args=(text, mode, auto_detect, src_name, tgt_name),
            daemon=True
        ).start()

    def _translate_thread(self, text: str, mode: str, auto_detect: bool, src_name: str, tgt_name: str):
        try:
            detected_code, detected_name = detect_language(text)

            if auto_detect:
                effective_src_code = detected_code
                effective_src_name = detected_name
            else:
                effective_src_code = LANG_OPTIONS.get(src_name, "en")
                effective_src_name = src_name

            tgt_code = LANG_OPTIONS.get(tgt_name, "es")
            translated = translate_text(text, tgt_code, effective_src_code)

            self.after(0, lambda: self._on_translate_done(
                text, translated, effective_src_name, effective_src_code,
                tgt_name, tgt_code, mode
            ))
        except Exception as e:
            self.after(0, lambda: self._status(f"❌ Error: {e}", color=self.DANGER))

    def _on_translate_done(
        self, original: str, translated: str,
        src_name: str, src_code: str,
        tgt_name: str, tgt_code: str, mode: str
    ):
        # Show output
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", translated)
        self.output_text.config(state="disabled")

        self.lang_info.config(
            text=f"{src_name} ({src_code}) → {tgt_name} ({tgt_code})"
        )

        self._status(
            f"✅ Translated [{src_name} → {tgt_name}]",
            color=self.ACCENT2
        )

        # TTS
        if self.tts_enabled.get():
            speak_async(translated, lang_code=tgt_code)

        # History
        entry = {
            "time": time.strftime("%H:%M:%S"),
            "mode": mode,
            "original": original[:60],
            "src_lang": src_name,
            "translated": translated[:60],
            "tgt_lang": tgt_name
        }
        self.history.append(entry)
        self.history_tree.insert(
            "", "end",
            values=(
                entry["time"], entry["mode"],
                entry["original"], entry["src_lang"],
                entry["translated"], entry["tgt_lang"]
            )
        )

        # Scroll to bottom
        children = self.history_tree.get_children()
        if children:
            self.history_tree.see(children[-1])

        # Stats
        self.stat_sessions.set(f"Sessions: {len(self.history)}")
        total = sum(len(h["original"]) for h in self.history)
        self.stat_chars.set(f"Chars: {total}")

    def _speak_output(self):
        text = self.output_text.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Nothing to Speak", "No translation output yet.")
            return
        tgt_code = LANG_OPTIONS.get(self.tgt_var.get(), "en")
        speak_async(text, lang_code=tgt_code)
        self._status("🔊 Speaking…", color="#a78bfa")

    def _set_input(self, text: str):
        self.input_text.delete("1.0", "end")
        self.input_text.insert("end", text)

    def _clear_io(self):
        self.input_text.delete("1.0", "end")
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")
        self.lang_info.config(text="")
        self._status("Cleared.", color=self.FG_DIM)

    def _clear_history(self):
        self.history.clear()
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        self.stat_sessions.set("Sessions: 0")
        self.stat_chars.set("Chars: 0")
        self._status("History cleared.", color=self.FG_DIM)


# ── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    app = VoiceTranslatorApp()
    app.mainloop()
