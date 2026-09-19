/**
 * VoiceBridge Real-Time Voice Translation Frontend
 * Integrates Web Audio API, Google Stitch UI, and FastAPI Engine
 */

// ── State Management ────────────────────────────────────────────────────────
const state = {
  activeView: 'translator',
  micState: 'idle', // 'idle' | 'listening' | 'processing' | 'error'
  languages: {},
  popularLanguages: [],
  sourceLang: 'auto',
  targetLang: 'es',
  isRecording: false,
  isTranslating: false,
  lastFailedTranslation: null,
  audioContext: null,
  mediaStream: null,
  audioProcessor: null,
  analyserNode: null,
  audioBuffers: [],
  recordStartTime: 0,
  timerInterval: null,
  currentAudio: null,
  history: [],
  settings: {
    defaultSource: 'auto',
    defaultTarget: 'es',
    playbackSpeed: 1.0,
    autoPlay: true,
    echoCancellation: true,
    noiseSuppression: true
  }
};

// Common flag emojis for language codes
const LANG_FLAGS = {
  auto: "🌐", en: "🇺🇸", es: "🇪🇸", fr: "🇫🇷", de: "🇩🇪",
  it: "🇮🇹", pt: "🇵🇹", ru: "🇷🇺", "zh-cn": "🇨🇳", "zh-tw": "🇹🇼",
  ja: "🇯🇵", ko: "🇰🇷", ar: "🇸🇦", hi: "🇮🇳", ta: "🇮🇳",
  te: "🇮🇳", ml: "🇮🇳", kn: "🇮🇳", bn: "🇧🇩", nl: "🇳🇱",
  pl: "🇵🇱", tr: "🇹🇷", vi: "🇻🇳", th: "🇹🇭", id: "🇮🇩"
};

// ── Initialization ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  loadSettings();
  loadHistory();
  await fetchLanguages();
  setupEventListeners();
  updateHistoryViews();
});

function loadSettings() {
  try {
    const saved = localStorage.getItem('voicebridge_settings');
    if (saved) {
      state.settings = { ...state.settings, ...JSON.parse(saved) };
    }
  } catch (e) {
    console.warn("Could not load settings:", e);
  }
  state.sourceLang = state.settings.defaultSource;
  state.targetLang = state.settings.defaultTarget;

  const autoPlayCheck = document.getElementById('pref-auto-play');
  if (autoPlayCheck) autoPlayCheck.checked = state.settings.autoPlay;

  const speedSlider = document.getElementById('pref-tts-speed');
  if (speedSlider) {
    speedSlider.value = state.settings.playbackSpeed;
    const speedVal = document.getElementById('tts-speed-val');
    if (speedVal) speedVal.textContent = `${state.settings.playbackSpeed}x`;
  }
}

function saveSettings() {
  try {
    localStorage.setItem('voicebridge_settings', JSON.stringify(state.settings));
  } catch (e) {}
}

function loadHistory() {
  try {
    const saved = localStorage.getItem('voicebridge_history');
    if (saved) {
      state.history = JSON.parse(saved);
    }
  } catch (e) {
    state.history = [];
  }
}

function saveHistory() {
  try {
    localStorage.setItem('voicebridge_history', JSON.stringify(state.history));
  } catch (e) {}
  updateHistoryViews();
}

// ── Languages API ───────────────────────────────────────────────────────────
async function fetchLanguages() {
  try {
    const res = await fetch('/api/languages');
    if (!res.ok) throw new Error("Languages API unreachable");
    const data = await res.json();
    state.languages = data.languages || {};
    state.popularLanguages = data.popular || [];
    populateLanguageSelects();
  } catch (err) {
    console.warn("Fallback to offline language dictionary:", err);
    state.languages = {
      en: "english", es: "spanish", fr: "french", de: "german",
      it: "italian", pt: "portuguese", ru: "russian", "zh-cn": "chinese (simplified)",
      ja: "japanese", ko: "korean", ar: "arabic", hi: "hindi", ta: "tamil"
    };
    populateLanguageSelects();
  }
}

// Languages in core/translator_engine.py not supported by gTTS voice synthesis
const GTTS_UNSUPPORTED = new Set(['he', 'fa', 'sl']);

// ── Custom Combobox Implementation ──────────────────────────────────────────
const combobox = {
  source: {
    isOpen: false,
    highlightedIndex: -1,
    filteredList: [],
    container: null,
    trigger: null,
    panel: null,
    input: null,
    clearBtn: null,
    list: null,
    empty: null,
    chevron: null,
    flag: null,
    name: null,
    code: null,
    isSource: true
  },
  target: {
    isOpen: false,
    highlightedIndex: -1,
    filteredList: [],
    container: null,
    trigger: null,
    panel: null,
    input: null,
    clearBtn: null,
    list: null,
    empty: null,
    chevron: null,
    flag: null,
    name: null,
    code: null,
    isSource: false
  }
};

function initComboboxElements() {
  ['source', 'target'].forEach(which => {
    const cb = combobox[which];
    cb.container = document.getElementById(`${which}-combobox-container`);
    cb.trigger = document.getElementById(`${which}-combobox-trigger`);
    cb.panel = document.getElementById(`${which}-combobox-panel`);
    cb.input = document.getElementById(`${which}-search-input`);
    cb.clearBtn = document.getElementById(`${which}-search-clear`);
    cb.list = document.getElementById(`${which}-options-list`);
    cb.empty = document.getElementById(`${which}-empty-msg`);
    cb.chevron = document.getElementById(`${which}-chevron`);
    cb.flag = document.getElementById(`${which}-flag`);
    cb.name = document.getElementById(`${which}-selected-name`);
    cb.code = document.getElementById(`${which}-selected-code`);

    if (cb.trigger && !cb.trigger._hasComboboxInit) {
      cb.trigger._hasComboboxInit = true;
      cb.trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleCombobox(which);
      });
      cb.trigger.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
          e.preventDefault();
          openCombobox(which);
        }
      });
    }

    if (cb.input && !cb.input._hasComboboxInit) {
      cb.input._hasComboboxInit = true;
      cb.input.addEventListener('input', () => {
        filterCombobox(which);
      });
      cb.input.addEventListener('keydown', (e) => {
        handleComboboxKeydown(which, e);
      });
    }

    if (cb.clearBtn && !cb.clearBtn._hasComboboxInit) {
      cb.clearBtn._hasComboboxInit = true;
      cb.clearBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        cb.input.value = '';
        cb.clearBtn.classList.add('hidden');
        filterCombobox(which);
        cb.input.focus();
      });
    }
  });

  if (!window._comboboxOutsideClickInit) {
    window._comboboxOutsideClickInit = true;
    document.addEventListener('click', (e) => {
      ['source', 'target'].forEach(which => {
        const cb = combobox[which];
        if (cb.isOpen && cb.container && !cb.container.contains(e.target)) {
          closeCombobox(which, false);
        }
      });
    });
  }
}

function getBaseLanguageList(isSource) {
  const list = [];
  if (isSource) {
    list.push({
      code: 'auto',
      name: 'Auto-detect (All languages)',
      flag: '🌐',
      ttsSupported: true,
      isAuto: true
    });
  }

  const sortedCodes = Object.keys(state.languages).sort((a, b) => {
    return (state.languages[a] || a).localeCompare(state.languages[b] || b);
  });

  sortedCodes.forEach(c => {
    const rawName = state.languages[c] || c;
    const name = rawName.charAt(0).toUpperCase() + rawName.slice(1);
    list.push({
      code: c,
      name: name,
      flag: LANG_FLAGS[c] || '🌐',
      ttsSupported: !GTTS_UNSUPPORTED.has(c),
      isAuto: false
    });
  });
  return list;
}

function toggleCombobox(which) {
  if (combobox[which].isOpen) {
    closeCombobox(which, true);
  } else {
    openCombobox(which);
  }
}

function openCombobox(which) {
  const cb = combobox[which];
  const otherWhich = which === 'source' ? 'target' : 'source';
  closeCombobox(otherWhich, false);

  cb.isOpen = true;
  if (cb.panel) cb.panel.classList.remove('hidden');
  if (cb.trigger) cb.trigger.setAttribute('aria-expanded', 'true');
  if (cb.chevron) cb.chevron.classList.add('rotate-180');

  // Reset search input
  if (cb.input) {
    cb.input.value = '';
    if (cb.clearBtn) cb.clearBtn.classList.add('hidden');
  }

  cb.filteredList = getBaseLanguageList(cb.isSource);
  if (cb.empty) cb.empty.classList.add('hidden');
  if (cb.list) cb.list.classList.remove('hidden');

  // Highlight currently selected item
  const curSelected = cb.isSource ? state.sourceLang : state.targetLang;
  const selIndex = cb.filteredList.findIndex(item => item.code === curSelected);
  cb.highlightedIndex = selIndex >= 0 ? selIndex : 0;

  renderComboboxOptions(which);

  // Focus search input
  requestAnimationFrame(() => {
    if (cb.input) cb.input.focus();
  });
}

function closeCombobox(which, returnFocus = false) {
  const cb = combobox[which];
  if (!cb.isOpen) return;

  cb.isOpen = false;
  cb.highlightedIndex = -1;
  if (cb.panel) cb.panel.classList.add('hidden');
  if (cb.trigger) {
    cb.trigger.setAttribute('aria-expanded', 'false');
    if (returnFocus) cb.trigger.focus();
  }
  if (cb.chevron) cb.chevron.classList.remove('rotate-180');
}

function filterCombobox(which) {
  const cb = combobox[which];
  const q = cb.input ? cb.input.value.trim().toLowerCase() : '';

  if (cb.clearBtn) {
    if (q) cb.clearBtn.classList.remove('hidden');
    else cb.clearBtn.classList.add('hidden');
  }

  const baseList = getBaseLanguageList(cb.isSource);
  if (!q) {
    cb.filteredList = baseList;
  } else {
    cb.filteredList = baseList.filter(item => {
      const nameMatch = item.name.toLowerCase().includes(q);
      const codeMatch = item.code.toLowerCase().includes(q);
      const autoMatch = item.isAuto && ('auto'.includes(q) || 'detect'.includes(q) || 'all'.includes(q));
      return nameMatch || codeMatch || autoMatch;
    });
  }

  if (cb.filteredList.length === 0) {
    if (cb.empty) cb.empty.classList.remove('hidden');
    if (cb.list) cb.list.classList.add('hidden');
    cb.highlightedIndex = -1;
  } else {
    if (cb.empty) cb.empty.classList.add('hidden');
    if (cb.list) cb.list.classList.remove('hidden');
    cb.highlightedIndex = 0;
    renderComboboxOptions(which);
  }
}

function renderComboboxOptions(which) {
  const cb = combobox[which];
  if (!cb.list) return;

  const currentSelected = cb.isSource ? state.sourceLang : state.targetLang;

  cb.list.innerHTML = '';
  cb.filteredList.forEach((item, index) => {
    const isSelected = item.code === currentSelected;
    const isHighlighted = index === cb.highlightedIndex;

    const row = document.createElement('div');
    row.role = 'option';
    row.setAttribute('aria-selected', isSelected ? 'true' : 'false');
    row.id = `${which}-opt-${index}`;

    let baseClass = "flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer text-xs transition-colors group select-none ";
    if (isSelected) {
      baseClass += "bg-emerald-500/20 text-white font-semibold ";
    } else if (isHighlighted) {
      baseClass += "bg-emerald-500/15 text-white ";
    } else {
      baseClass += "text-slate-300 hover:bg-emerald-500/10 hover:text-white ";
    }

    if (isHighlighted) {
      baseClass += "border-l-2 border-emerald-400 pl-2.5 ";
    } else {
      baseClass += "border-l-2 border-transparent ";
    }

    row.className = baseClass;
    row.setAttribute('data-lang-code', item.code);
    row.setAttribute('role', 'option');

    row.innerHTML = `
      <div class="flex items-center gap-2.5 min-w-0">
        <span class="text-base shrink-0 select-none">${item.flag}</span>
        <span class="truncate">${item.name}</span>
      </div>
      <div class="flex items-center gap-1.5 shrink-0">
        ${!cb.isSource && !item.ttsSupported ? `
          <span class="px-1.5 py-0.5 rounded bg-slate-800/90 text-amber-300/90 border border-amber-500/20 text-[10px] flex items-center gap-0.5" title="Speech playback unavailable for this language">
            <span class="material-symbols-outlined text-[12px]">volume_off</span>
            <span>No voice</span>
          </span>` : ''}
        <span class="px-1.5 py-0.5 rounded bg-surface-container-highest text-slate-300 font-mono text-[10px] uppercase font-bold group-hover:text-emerald-300">${item.code.toUpperCase()}</span>
        ${isSelected ? `<span class="material-symbols-outlined text-[16px] text-emerald-400">check</span>` : `<span class="w-4 inline-block"></span>`}
      </div>
    `;

    row.addEventListener('click', (e) => {
      e.stopPropagation();
      selectLanguage(which, item.code);
      closeCombobox(which, true);
    });

    row.addEventListener('mouseenter', () => {
      cb.highlightedIndex = index;
      updateOptionHighlightStyles(which);
    });

    cb.list.appendChild(row);
  });

  scrollHighlightedIntoView(which);
}

function updateOptionHighlightStyles(which) {
  const cb = combobox[which];
  if (!cb.list) return;
  const currentSelected = cb.isSource ? state.sourceLang : state.targetLang;

  const rows = cb.list.children;
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    const isSelected = cb.filteredList[i]?.code === currentSelected;
    const isHighlighted = i === cb.highlightedIndex;

    let baseClass = "flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer text-xs transition-colors group select-none ";
    if (isSelected) {
      baseClass += "bg-emerald-500/20 text-white font-semibold ";
    } else if (isHighlighted) {
      baseClass += "bg-emerald-500/15 text-white ";
    } else {
      baseClass += "text-slate-300 hover:bg-emerald-500/10 hover:text-white ";
    }

    if (isHighlighted) {
      baseClass += "border-l-2 border-emerald-400 pl-2.5 ";
    } else {
      baseClass += "border-l-2 border-transparent ";
    }

    row.className = baseClass;
  }
}

function scrollHighlightedIntoView(which) {
  const cb = combobox[which];
  if (!cb.list || cb.highlightedIndex < 0) return;
  const activeEl = cb.list.children[cb.highlightedIndex];
  if (activeEl) {
    activeEl.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }
}

function handleComboboxKeydown(which, e) {
  const cb = combobox[which];
  if (!cb.isOpen) return;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    if (cb.filteredList.length === 0) return;
    cb.highlightedIndex = (cb.highlightedIndex + 1) % cb.filteredList.length;
    updateOptionHighlightStyles(which);
    scrollHighlightedIntoView(which);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    if (cb.filteredList.length === 0) return;
    cb.highlightedIndex = (cb.highlightedIndex - 1 + cb.filteredList.length) % cb.filteredList.length;
    updateOptionHighlightStyles(which);
    scrollHighlightedIntoView(which);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (cb.filteredList.length > 0 && cb.highlightedIndex >= 0 && cb.highlightedIndex < cb.filteredList.length) {
      const item = cb.filteredList[cb.highlightedIndex];
      selectLanguage(which, item.code);
      closeCombobox(which, true);
    }
  } else if (e.key === 'Escape') {
    e.preventDefault();
    closeCombobox(which, true);
  } else if (e.key === 'Tab') {
    closeCombobox(which, false);
  }
}

function selectLanguage(which, code) {
  if (which === 'source') {
    state.sourceLang = code;
    const cb = combobox.source;
    if (cb.flag) cb.flag.textContent = LANG_FLAGS[code] || "🌐";
    if (cb.code) cb.code.textContent = code.toUpperCase();
    if (cb.name) {
      if (code === 'auto') {
        cb.name.textContent = "Auto-detect (All languages)";
      } else {
        const raw = state.languages[code] || code;
        cb.name.textContent = raw.charAt(0).toUpperCase() + raw.slice(1);
      }
    }
  } else {
    state.targetLang = code;
    const cb = combobox.target;
    if (cb.flag) cb.flag.textContent = LANG_FLAGS[code] || "🌐";
    if (cb.code) cb.code.textContent = code.toUpperCase();
    const raw = state.languages[code] || code;
    const capitalized = raw.charAt(0).toUpperCase() + raw.slice(1);
    if (cb.name) cb.name.textContent = capitalized;

    const tgtTitle = document.getElementById('target-card-title');
    if (tgtTitle) tgtTitle.textContent = capitalized;

    updateTTSAvailability(code);
  }

  // Sync settings dropdowns if loaded
  const setDefSrc = document.getElementById('settings-default-source');
  const setDefTgt = document.getElementById('settings-default-target');
  if (which === 'source' && setDefSrc) setDefSrc.value = code;
  if (which === 'target' && setDefTgt) setDefTgt.value = code;
}

function updateTTSAvailability(targetLang) {
  const ttsPlayBtn = document.getElementById('tts-play-btn');
  const ttsVoiceLabel = document.getElementById('tts-voice-label');
  const slowTtsBtn = document.getElementById('slow-tts-btn');

  const isUnsupported = GTTS_UNSUPPORTED.has(targetLang);

  if (isUnsupported) {
    if (ttsPlayBtn) {
      ttsPlayBtn.disabled = true;
      ttsPlayBtn.classList.add('opacity-40', 'cursor-not-allowed', 'pointer-events-none');
      ttsPlayBtn.setAttribute('title', 'Voice synthesis is not available for this language');
    }
    if (slowTtsBtn) {
      slowTtsBtn.disabled = true;
      slowTtsBtn.classList.add('opacity-40', 'cursor-not-allowed', 'pointer-events-none');
      slowTtsBtn.setAttribute('title', 'Voice synthesis is not available for this language');
    }
    if (ttsVoiceLabel) {
      ttsVoiceLabel.textContent = "Voice playback unavailable";
      ttsVoiceLabel.classList.add('text-amber-400');
    }
  } else {
    if (ttsPlayBtn) {
      ttsPlayBtn.disabled = false;
      ttsPlayBtn.classList.remove('opacity-40', 'cursor-not-allowed', 'pointer-events-none');
      ttsPlayBtn.setAttribute('title', 'Listen to synthetic voice');
    }
    if (slowTtsBtn) {
      slowTtsBtn.disabled = false;
      slowTtsBtn.classList.remove('opacity-40', 'cursor-not-allowed', 'pointer-events-none');
      slowTtsBtn.setAttribute('title', 'Slow playback (0.8x)');
    }
    if (ttsVoiceLabel) {
      ttsVoiceLabel.textContent = "Google Neural TTS";
      ttsVoiceLabel.classList.remove('text-amber-400');
    }
  }
}

function populateLanguageSelects() {
  initComboboxElements();

  // Populate settings page selects
  const setDefSrc = document.getElementById('settings-default-source');
  const setDefTgt = document.getElementById('settings-default-target');
  if (setDefSrc && setDefTgt) {
    setDefSrc.innerHTML = '<option value="auto">Auto-detect</option>';
    setDefTgt.innerHTML = '';
    const sortedCodes = Object.keys(state.languages).sort((a, b) => {
      return (state.languages[a] || a).localeCompare(state.languages[b] || b);
    });
    sortedCodes.forEach(code => {
      const name = state.languages[code];
      const cap = name.charAt(0).toUpperCase() + name.slice(1);
      const flag = LANG_FLAGS[code] || "🌐";
      const label = `${flag} ${cap} (${code.toUpperCase()})`;
      const opt1 = document.createElement('option');
      opt1.value = code; opt1.textContent = label;
      setDefSrc.appendChild(opt1);
      const opt2 = document.createElement('option');
      opt2.value = code; opt2.textContent = label;
      setDefTgt.appendChild(opt2);
    });
    setDefSrc.value = state.settings.defaultSource;
    setDefTgt.value = state.settings.defaultTarget;
  }

  // Initialize both comboboxes with current state
  selectLanguage('source', state.sourceLang);
  selectLanguage('target', state.targetLang);
}

// ── View Switching ──────────────────────────────────────────────────────────
function switchView(viewName) {
  state.activeView = viewName;
  const views = ['translator', 'history', 'settings', 'mic-error'];
  views.forEach(v => {
    const el = document.getElementById(`view-${v}`);
    if (el) {
      if (v === viewName) {
        el.classList.remove('hidden');
      } else {
        el.classList.add('hidden');
      }
    }
  });

  // Nav buttons
  const navMap = {
    translator: 'nav-btn-translator',
    history: 'nav-btn-history',
    settings: 'nav-btn-settings'
  };
  Object.keys(navMap).forEach(v => {
    const btn = document.getElementById(navMap[v]);
    if (btn) {
      if (v === viewName) {
        btn.className = "flex items-center gap-1.5 px-3 sm:px-4 py-1.5 rounded-full text-xs sm:text-sm font-semibold transition-all bg-emerald-500 text-emerald-950 shadow-sm";
      } else {
        btn.className = "flex items-center gap-1.5 px-3 sm:px-4 py-1.5 rounded-full text-xs sm:text-sm font-semibold transition-all text-slate-300 hover:text-white";
      }
    }
  });

  if (viewName === 'history') {
    updateHistoryViews();
  }
}

function switchSettingsTab(tabName) {
  const tabs = ['audio', 'translation', 'synthesis', 'theme'];
  tabs.forEach(t => {
    const sec = document.getElementById(`set-sec-${t}`);
    const btn = document.getElementById(`set-tab-btn-${t}`);
    if (sec) {
      if (t === tabName) sec.classList.remove('hidden');
      else sec.classList.add('hidden');
    }
    if (btn) {
      if (t === tabName) {
        btn.className = "flex items-center gap-2 px-3 py-2 rounded-full text-xs font-semibold text-emerald-950 bg-emerald-500 transition-all whitespace-nowrap";
      } else {
        btn.className = "flex items-center gap-2 px-3 py-2 rounded-full text-xs font-semibold text-slate-300 hover:text-white hover:bg-surface-container-high transition-all whitespace-nowrap";
      }
    }
  });
}

// ── Mic State Management ────────────────────────────────────────────────────
function setMicState(nextState) {
  state.micState = nextState;
  const tabs = ['listening', 'processing', 'idle', 'error'];
  tabs.forEach(t => {
    const btn = document.getElementById('tab-' + t);
    if (btn) {
      if (t === nextState) {
        btn.className = "px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500 text-emerald-950 font-bold transition-all shadow-sm";
      } else {
        btn.className = "px-3 py-1 rounded-full text-xs font-semibold text-slate-300 hover:text-white transition-all";
      }
    }
  });

  const micBtn = document.getElementById('hero-mic-button');
  const micIcon = document.getElementById('mic-icon');
  const spinner = document.getElementById('processing-spinner');
  const ring1 = document.getElementById('ring-pulse-1');
  const ring2 = document.getElementById('ring-pulse-2');
  const waveform = document.getElementById('waveform-visualizer');
  const statusDot = document.getElementById('status-dot');
  const statusHeadline = document.getElementById('status-headline');
  const dbMeter = document.getElementById('db-meter');
  const errorAlert = document.getElementById('error-alert-banner');

  if (nextState === 'listening') {
    if (micBtn) micBtn.className = "relative z-10 w-24 h-24 sm:w-28 sm:h-28 rounded-full bg-gradient-to-tr from-[#059669] via-[#10b981] to-[#34d399] flex items-center justify-center text-emerald-950 shadow-[0_0_50px_rgba(16,185,129,0.55)] transition-all duration-300 transform active:scale-95 focus:outline-none focus:ring-4 focus:ring-emerald-400/50 border-2 border-emerald-300/60";
    if (micIcon) micIcon.classList.remove('hidden');
    if (spinner) spinner.classList.add('hidden');
    if (ring1) ring1.classList.remove('hidden');
    if (ring2) ring2.classList.remove('hidden');
    if (waveform) waveform.classList.remove('hidden');
    if (errorAlert) errorAlert.classList.add('hidden');
    if (statusDot) statusDot.className = "w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping";
    if (statusHeadline) statusHeadline.textContent = "Listening... speak naturally in any language";
    if (dbMeter) dbMeter.classList.remove('hidden');
  } else if (nextState === 'processing') {
    if (micBtn) micBtn.className = "relative z-10 w-24 h-24 sm:w-28 sm:h-28 rounded-full bg-emerald-600 flex items-center justify-center text-emerald-950 shadow-[0_0_35px_rgba(16,185,129,0.4)] transition-all duration-300 border-2 border-emerald-400/50";
    if (micIcon) micIcon.classList.add('hidden');
    if (spinner) spinner.classList.remove('hidden');
    if (ring1) ring1.classList.add('hidden');
    if (ring2) ring2.classList.remove('hidden');
    if (waveform) waveform.classList.add('hidden');
    if (errorAlert) errorAlert.classList.add('hidden');
    if (statusDot) statusDot.className = "w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse";
    if (statusHeadline) statusHeadline.textContent = "Transcribing & translating speech...";
    if (dbMeter) dbMeter.classList.add('hidden');
  } else if (nextState === 'idle') {
    if (micBtn) micBtn.className = "relative z-10 w-24 h-24 sm:w-28 sm:h-28 rounded-full bg-surface-container-high hover:bg-surface-bright flex items-center justify-center text-slate-300 hover:text-white transition-all duration-300 border border-slate-700";
    if (micIcon) micIcon.classList.remove('hidden');
    if (spinner) spinner.classList.add('hidden');
    if (ring1) ring1.classList.add('hidden');
    if (ring2) ring2.classList.add('hidden');
    if (waveform) waveform.classList.add('hidden');
    if (errorAlert) errorAlert.classList.add('hidden');
    if (statusDot) statusDot.className = "w-2.5 h-2.5 rounded-full bg-outline";
    if (statusHeadline) statusHeadline.textContent = "Idle • Tap mic or press Space to begin translating";
    if (dbMeter) dbMeter.classList.add('hidden');
  } else if (nextState === 'error') {
    if (micBtn) micBtn.className = "relative z-10 w-24 h-24 sm:w-28 sm:h-28 rounded-full bg-error-container text-on-error-container flex items-center justify-center shadow-lg transition-all duration-300 border border-error/40";
    if (micIcon) micIcon.classList.remove('hidden');
    if (spinner) spinner.classList.add('hidden');
    if (ring1) ring1.classList.add('hidden');
    if (ring2) ring2.classList.add('hidden');
    if (waveform) waveform.classList.add('hidden');
    if (errorAlert) errorAlert.classList.remove('hidden');
    if (statusDot) statusDot.className = "w-2.5 h-2.5 rounded-full bg-error";
    if (statusHeadline) statusHeadline.textContent = "Microphone offline or permission denied";
    if (dbMeter) dbMeter.classList.add('hidden');
  }
}

// ── Web Audio API Microphone Recording (16kHz PCM WAV) ─────────────────────
async function startRecording() {
  if (state.isRecording) return;
  state.audioBuffers = [];

  try {
    const audioStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: state.settings.echoCancellation,
        noiseSuppression: state.settings.noiseSuppression,
        sampleRate: 16000
      }
    });

    state.mediaStream = audioStream;
    state.audioContext = new (window.AudioContext || window.webkitAudioContext)({
      sampleRate: 16000
    });

    const source = state.audioContext.createMediaStreamSource(audioStream);
    state.analyserNode = state.audioContext.createAnalyser();
    state.analyserNode.fftSize = 256;

    // Buffer collection
    state.audioProcessor = state.audioContext.createScriptProcessor(4096, 1, 1);
    state.audioProcessor.onaudioprocess = (e) => {
      if (!state.isRecording) return;
      const inputData = e.inputBuffer.getChannelData(0);
      state.audioBuffers.push(new Float32Array(inputData));
    };

    source.connect(state.analyserNode);
    state.analyserNode.connect(state.audioProcessor);
    state.audioProcessor.connect(state.audioContext.destination);

    state.isRecording = true;
    setMicState('listening');
    startTimer();
    startAudioVisualizerLoop();
  } catch (err) {
    console.error("Microphone access failed:", err);
    state.isRecording = false;
    setMicState('error');
    const msg = err.name === 'NotAllowedError'
      ? 'Microphone permission blocked. Please allow mic access in your browser URL bar.'
      : `Audio capture error: ${err.message || 'No mic found'}`;
    const alertMsg = document.getElementById('error-alert-msg');
    if (alertMsg) alertMsg.textContent = msg;
    const diagStatus = document.getElementById('diag-perm-status');
    if (diagStatus) diagStatus.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-error"></span> Denied (${err.name || 'Error'})`;
  }
}

async function stopRecording() {
  if (!state.isRecording) return;
  state.isRecording = false;
  stopTimer();
  setMicState('processing');

  // Stop media tracks
  if (state.mediaStream) {
    state.mediaStream.getTracks().forEach(t => t.stop());
  }
  if (state.audioProcessor && state.audioContext) {
    state.audioProcessor.disconnect();
  }

  // Encode collected Float32 arrays into standard 16-bit PCM WAV
  const wavBlob = encodeWAV(state.audioBuffers, state.audioContext.sampleRate || 16000);

  if (state.audioContext && state.audioContext.state !== 'closed') {
    try { await state.audioContext.close(); } catch (e) {}
  }

  if (!wavBlob || wavBlob.size < 1000) {
    setMicState('idle');
    document.getElementById('status-headline').textContent = "Audio was too short. Speak and hold mic.";
    return;
  }

  // Upload WAV blob to FastAPI backend
  await sendAudioForTranscription(wavBlob);
}

// ── PCM WAV 16-bit Mono Encoder ─────────────────────────────────────────────
function encodeWAV(buffers, sampleRate) {
  let totalLength = 0;
  for (let i = 0; i < buffers.length; i++) {
    totalLength += buffers[i].length;
  }
  if (totalLength === 0) return null;

  const merged = new Float32Array(totalLength);
  let offset = 0;
  for (let i = 0; i < buffers.length; i++) {
    merged.set(buffers[i], offset);
    offset += buffers[i].length;
  }

  // 16-bit PCM WAV: 44 bytes header + totalLength * 2 bytes
  const buffer = new ArrayBuffer(44 + totalLength * 2);
  const view = new DataView(buffer);

  function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  // RIFF chunk descriptor
  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + totalLength * 2, true);
  writeString(view, 8, 'WAVE');

  // fmt sub-chunk
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
  view.setUint16(20, 1, true);  // AudioFormat (1 for PCM)
  view.setUint16(22, 1, true);  // NumChannels (1 mono)
  view.setUint32(24, sampleRate, true); // SampleRate
  view.setUint32(28, sampleRate * 2, true); // ByteRate
  view.setUint16(32, 2, true);  // BlockAlign
  view.setUint16(34, 16, true); // BitsPerSample (16-bit)

  // data sub-chunk
  writeString(view, 36, 'data');
  view.setUint32(40, totalLength * 2, true);

  // Write PCM audio samples
  let dataIndex = 44;
  for (let i = 0; i < totalLength; i++) {
    let s = Math.max(-1, Math.min(1, merged[i]));
    s = s < 0 ? s * 0x8000 : s * 0x7FFF;
    view.setInt16(dataIndex, s, true);
    dataIndex += 2;
  }

  return new Blob([view], { type: 'audio/wav' });
}

// ── Audio Visualizer & Level Meter Loop ─────────────────────────────────────
function startAudioVisualizerLoop() {
  if (!state.analyserNode) return;
  const dataArray = new Uint8Array(state.analyserNode.frequencyBinCount);

  function update() {
    if (!state.isRecording) return;
    state.analyserNode.getByteFrequencyData(dataArray);

    // Compute average amplitude
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      sum += dataArray[i];
    }
    const avg = sum / dataArray.length;
    const db = Math.max(-60, Math.round((avg / 255) * 60 - 60));

    const gainText = document.getElementById('live-gain-text');
    if (gainText) gainText.textContent = `${db} dB`;

    // Dynamic wave bar heights
    const waveEl = document.getElementById('waveform-visualizer');
    if (waveEl) {
      const bars = waveEl.querySelectorAll('span');
      bars.forEach((bar, idx) => {
        const factor = dataArray[(idx * 2) % dataArray.length] / 255;
        const h = Math.max(4, Math.round(factor * 36));
        bar.style.height = `${h}px`;
      });
    }

    requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// ── Timer Logic ─────────────────────────────────────────────────────────────
function startTimer() {
  state.recordStartTime = Date.now();
  const timerEl = document.getElementById('recording-timer');
  state.timerInterval = setInterval(() => {
    const elapsed = Date.now() - state.recordStartTime;
    const sec = Math.floor(elapsed / 1000);
    const ms = Math.floor((elapsed % 1000) / 100);
    const minStr = String(Math.floor(sec / 60)).padStart(2, '0');
    const secStr = String(sec % 60).padStart(2, '0');
    if (timerEl) timerEl.textContent = `${minStr}:${secStr}.${ms}s`;
  }, 100);
}

function stopTimer() {
  if (state.timerInterval) clearInterval(state.timerInterval);
}

// ── Backend API Actions ─────────────────────────────────────────────────────
async function sendAudioForTranscription(wavBlob) {
  try {
    const formData = new FormData();
    formData.append('file', wavBlob, 'recording.wav');
    formData.append('language', state.sourceLang);

    const res = await fetch('/api/transcribe', {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.detail || 'Transcription error');
    }

    const data = await res.json();
    if (!data.success || !data.text) {
      setMicState('idle');
      const err = data.error || "Could not recognize spoken words. Please speak clearly.";
      document.getElementById('status-headline').textContent = err;
      return;
    }

    // Got transcribed text! Now translate it:
    await executeTranslation(data.text, state.sourceLang, state.targetLang);
    setMicState('idle');
  } catch (err) {
    console.error("Transcribe failed:", err);
    setMicState('idle');
    document.getElementById('status-headline').textContent = `Recognition error: ${err.message}`;
  }
}

function showTranslationErrorBanner(msg) {
  const banner = document.getElementById('translation-error-banner');
  const msgEl = document.getElementById('translation-error-message');
  if (banner) {
    if (msgEl) msgEl.textContent = msg || 'Translation service is busy. Please try again.';
    banner.classList.remove('hidden');
  }
}

function hideTranslationErrorBanner() {
  const banner = document.getElementById('translation-error-banner');
  if (banner) {
    banner.classList.add('hidden');
  }
}

async function executeTranslation(text, source, target) {
  if (!text || !text.trim()) return;
  if (state.isTranslating) return; // In-flight request lock

  state.isTranslating = true;
  setMicState('processing');

  const translateBtn = document.getElementById('translate-manual-btn');
  let originalBtnHtml = '';
  if (translateBtn) {
    originalBtnHtml = translateBtn.innerHTML;
    translateBtn.classList.add('opacity-50', 'pointer-events-none', 'cursor-not-allowed');
    translateBtn.innerHTML = `
      <span class="inline-block animate-spin material-symbols-outlined text-[16px]">progress_activity</span>
      <span>Translating...</span>
    `;
  }

  try {
    const res = await fetch('/api/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, source, target })
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok || data.error) {
      const errMsg = data.error || data.detail || (res.status === 429 ? 'Translation service is busy. Please try again in a few seconds.' : 'Translation service error');
      throw new Error(errMsg);
    }

    // Success! Hide error banner
    hideTranslationErrorBanner();

    // Update UI Cards with valid translation ONLY
    document.getElementById('transcript-source-text').textContent = `"${data.original_text}"`;
    document.getElementById('target-translation-text').textContent = `"${data.translated_text}"`;

    // Detected Badge: only display if auto was requested AND text >= 20 chars and detected is not 'auto'
    const detectedBadge = document.getElementById('detected-badge');
    if (detectedBadge) {
      if (data.source_lang === 'auto' && data.detected_lang && data.detected_lang !== 'auto' && data.original_text.length >= 20) {
        const langName = data.source_name || data.detected_lang.toUpperCase();
        detectedBadge.textContent = `Detected: ${langName}`;
        detectedBadge.classList.remove('hidden');
      } else {
        detectedBadge.classList.add('hidden');
      }
    }

    // Update phonetics generator placeholder
    const phoneticText = document.getElementById('phonetic-text');
    if (phoneticText) {
      phoneticText.textContent = generateApproxPhonetic(data.translated_text);
    }

    // Save to History (only on genuine translation, NEVER error strings)
    addHistoryItem(data.original_text, data.translated_text, data.detected_lang, data.target_lang);

    // Auto-play if enabled
    if (state.settings.autoPlay) {
      playTTS(data.translated_text, data.target_lang);
    }

    setMicState('idle');
  } catch (err) {
    console.error("Translation failed:", err);
    setMicState('idle');
    document.getElementById('status-headline').textContent = `Translation paused • ${err.message}`;

    // Store failed request info for Retry button
    state.lastFailedTranslation = { text, source, target };

    // Show inline error banner with Retry button instead of writing error into translation card
    showTranslationErrorBanner(err.message || 'Translation service is busy, try again');
  } finally {
    state.isTranslating = false;
    if (translateBtn) {
      translateBtn.classList.remove('opacity-50', 'pointer-events-none', 'cursor-not-allowed');
      translateBtn.innerHTML = originalBtnHtml || `<span>Translate</span><span class="material-symbols-outlined text-[16px]">arrow_forward</span>`;
    }
  }
}

// ── Text-to-Speech (TTS) Playback ───────────────────────────────────────────
async function playTTS(text, langCode, speed = null) {
  if (!text || !text.trim()) return;
  cleanText = text.replace(/^["'\s]+|["'\s]+$/g, '');

  const ttsAudioBars = document.getElementById('tts-audio-bars');
  const ttsBtnText = document.getElementById('tts-btn-text');
  const ttsIcon = document.getElementById('tts-icon');

  if (state.currentAudio) {
    try {
      state.currentAudio.pause();
      state.currentAudio.currentTime = 0;
    } catch (e) {}
  }

  if (ttsAudioBars) {
    ttsAudioBars.classList.remove('hidden');
    ttsAudioBars.classList.add('flex');
  }
  if (ttsBtnText) ttsBtnText.textContent = "Playing...";
  if (ttsIcon) ttsIcon.textContent = "volume_up";

  try {
    const audioUrl = `/api/speak?text=${encodeURIComponent(cleanText)}&lang=${encodeURIComponent(langCode)}`;
    const audio = new Audio(audioUrl);
    state.currentAudio = audio;

    const effectiveSpeed = speed || state.settings.playbackSpeed || 1.0;
    audio.playbackRate = effectiveSpeed;

    audio.onended = () => {
      resetTTSButton();
    };

    audio.onerror = () => {
      console.warn("TTS audio element error, checking fallback...");
      resetTTSButton();
    };

    await audio.play();
  } catch (err) {
    console.error("Playback error:", err);
    resetTTSButton();
  }
}

function resetTTSButton() {
  const ttsAudioBars = document.getElementById('tts-audio-bars');
  const ttsBtnText = document.getElementById('tts-btn-text');
  const ttsIcon = document.getElementById('tts-icon');
  if (ttsAudioBars) {
    ttsAudioBars.classList.add('hidden');
    ttsAudioBars.classList.remove('flex');
  }
  if (ttsBtnText) ttsBtnText.textContent = "Listen Audio";
  if (ttsIcon) ttsIcon.textContent = "play_arrow";
}

// ── Approximate Phonetics Helper ────────────────────────────────────────────
function generateApproxPhonetic(text) {
  if (!text) return "";
  const cleaned = text.replace(/^["']|["']$/g, '');
  return cleaned
    .replace(/[¿?¡!.,]/g, '')
    .split(' ')
    .map(w => w.length > 3 ? w.slice(0, 2) + '-' + w.slice(2) : w)
    .join(' ');
}

// ── History Management ──────────────────────────────────────────────────────
function addHistoryItem(sourceText, translatedText, sourceLang, targetLang) {
  const item = {
    id: Date.now().toString(),
    timestamp: Date.now(),
    sourceText,
    translatedText,
    sourceLang,
    targetLang,
    timeStr: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };

  state.history.unshift(item);
  if (state.history.length > 50) state.history.pop();
  saveHistory();
}

function updateHistoryViews() {
  const badge = document.getElementById('history-counter-badge');
  const recentTitle = document.getElementById('recent-history-title');
  const recentDrawer = document.getElementById('history-content-drawer');
  const emptyState = document.getElementById('history-empty-state');
  const populatedState = document.getElementById('history-populated-state');
  const fullList = document.getElementById('history-full-list');

  const count = state.history.length;
  if (badge) badge.textContent = count;
  if (recentTitle) recentTitle.textContent = `Recent Translations (${count})`;

  // Recent 3 items in Translator view
  if (recentDrawer) {
    if (count === 0) {
      recentDrawer.innerHTML = `
        <div class="p-4 text-center text-slate-400 font-label-md text-xs">
          No recent translations recorded yet. Start speaking or typing above!
        </div>`;
    } else {
      const recentItems = state.history.slice(0, 3);
      recentDrawer.innerHTML = recentItems.map(item => renderHistoryCard(item, false)).join('');
    }
  }

  // Full History View
  if (count === 0) {
    if (emptyState) emptyState.classList.remove('hidden');
    if (populatedState) populatedState.classList.add('hidden');
  } else {
    if (emptyState) emptyState.classList.add('hidden');
    if (populatedState) populatedState.classList.remove('hidden');
    if (fullList) {
      fullList.innerHTML = state.history.map(item => renderHistoryCard(item, true)).join('');
    }
  }
}

function renderHistoryCard(item, isFullView) {
  const srcCode = (item.sourceLang || 'en').toUpperCase();
  const tgtCode = (item.targetLang || 'es').toUpperCase();
  const escapedSrc = escapeHtml(item.sourceText);
  const escapedTgt = escapeHtml(item.translatedText);

  return `
    <div class="bg-surface-container hover:bg-surface-container-high/70 transition-colors p-3 rounded-DEFAULT flex flex-col md:flex-row md:items-center justify-between gap-3 border border-slate-800/60">
      <div class="space-y-1 min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <span class="px-2 py-0.5 rounded-full bg-surface-container-highest text-emerald-400 font-label-md text-[11px] font-semibold border border-emerald-500/20">
            ${srcCode} → ${tgtCode}
          </span>
          <span class="text-slate-400 font-label-md text-xs">• ${item.timeStr}</span>
        </div>
        <p class="text-white font-body-md text-xs sm:text-sm font-medium">"${escapedSrc}"</p>
        <p class="text-mint-text font-body-md text-xs sm:text-sm">"${escapedTgt}"</p>
      </div>
      <div class="flex items-center gap-1.5 shrink-0 self-end md:self-center">
        <button class="w-8 h-8 rounded-full bg-surface-container-highest hover:bg-emerald-500 hover:text-emerald-950 text-slate-200 flex items-center justify-center transition-colors border border-slate-700/60" onclick="restoreTranslation('${escapedSrc}', '${escapedTgt}', '${item.sourceLang}', '${item.targetLang}')" title="Restore translation" type="button">
          <span class="material-symbols-outlined text-[16px]">replay</span>
        </button>
        <button class="w-8 h-8 rounded-full bg-surface-container-highest hover:bg-surface-bright text-slate-200 hover:text-white flex items-center justify-center transition-colors border border-slate-700/60" onclick="playTTS('${escapedTgt}', '${item.targetLang}')" title="Speak translation" type="button">
          <span class="material-symbols-outlined text-[16px]">volume_up</span>
        </button>
        <button class="w-8 h-8 rounded-full bg-surface-container-highest hover:bg-surface-bright text-slate-200 hover:text-white flex items-center justify-center transition-colors border border-slate-700/60" onclick="copyText('${escapedTgt}')" title="Copy translation" type="button">
          <span class="material-symbols-outlined text-[16px]">content_copy</span>
        </button>
        ${isFullView ? `
        <button class="w-8 h-8 rounded-full bg-surface-container-highest hover:bg-error hover:text-white text-slate-400 flex items-center justify-center transition-colors border border-slate-700/60" onclick="deleteHistoryItem('${item.id}')" title="Delete record" type="button">
          <span class="material-symbols-outlined text-[16px]">delete</span>
        </button>` : ''}
      </div>
    </div>
  `;
}

function restoreTranslation(src, tgt, srcLang, tgtLang) {
  document.getElementById('transcript-source-text').textContent = `"${src}"`;
  document.getElementById('target-translation-text').textContent = `"${tgt}"`;
  if (srcLang && (srcLang === 'auto' || state.languages[srcLang])) {
    selectLanguage('source', srcLang);
  }
  if (tgtLang && state.languages[tgtLang]) {
    selectLanguage('target', tgtLang);
  }
  switchView('translator');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function deleteHistoryItem(id) {
  state.history = state.history.filter(h => h.id !== id);
  saveHistory();
}

function clearAllHistory() {
  if (state.history.length === 0) return;
  state.history = [];
  saveHistory();
}

function filterHistory() {
  const query = (document.getElementById('history-search-input')?.value || '').toLowerCase();
  const fullList = document.getElementById('history-full-list');
  if (!fullList) return;

  const filtered = state.history.filter(item =>
    item.sourceText.toLowerCase().includes(query) ||
    item.translatedText.toLowerCase().includes(query) ||
    item.sourceLang.toLowerCase().includes(query) ||
    item.targetLang.toLowerCase().includes(query)
  );

  fullList.innerHTML = filtered.map(item => renderHistoryCard(item, true)).join('');
}

function toggleHistoryPanel() {
  const drawer = document.getElementById('history-content-drawer');
  const chevron = document.getElementById('history-chevron');
  if (!drawer || !chevron) return;

  const isHidden = drawer.classList.contains('hidden');
  if (isHidden) {
    drawer.classList.remove('hidden');
    chevron.classList.add('rotate-180');
  } else {
    drawer.classList.add('hidden');
    chevron.classList.remove('rotate-180');
  }
}

// ── Mic Hardware Test in Settings ───────────────────────────────────────────
let testAudioContext = null;
let testStream = null;
let isTestingMic = false;

async function toggleMicTest() {
  const btnText = document.getElementById('mic-test-text');
  if (isTestingMic) {
    isTestingMic = false;
    if (testStream) testStream.getTracks().forEach(t => t.stop());
    if (testAudioContext) testAudioContext.close();
    if (btnText) btnText.textContent = "Test Microphone";
    return;
  }

  try {
    testStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    testAudioContext = new (window.AudioContext || window.webkitAudioContext)();
    const source = testAudioContext.createMediaStreamSource(testStream);
    const analyser = testAudioContext.createAnalyser();
    source.connect(analyser);

    isTestingMic = true;
    if (btnText) btnText.textContent = "Stop Test";

    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const barsContainer = document.getElementById('settings-meter-bars');
    const bars = barsContainer ? barsContainer.querySelectorAll('div') : [];

    function anim() {
      if (!isTestingMic) return;
      analyser.getByteFrequencyData(dataArray);
      bars.forEach((bar, idx) => {
        const factor = dataArray[(idx * 4) % dataArray.length] / 255;
        const h = Math.max(3, Math.round(factor * 20));
        bar.style.height = `${h}px`;
      });
      requestAnimationFrame(anim);
    }
    requestAnimationFrame(anim);
  } catch (e) {
    alert("Could not access microphone: " + e.message);
  }
}

async function requestMicPermissionAgain() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(t => t.stop());
    alert("Microphone permission granted!");
    setMicState('idle');
    switchView('translator');
  } catch (err) {
    alert("Microphone permission still blocked: " + err.message);
  }
}

// ── Utilities ───────────────────────────────────────────────────────────────
function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function copyText(str) {
  if (!str) return;
  const clean = str.replace(/^["']|["']$/g, '');
  navigator.clipboard.writeText(clean).catch(() => {});
  const toast = document.getElementById('copy-toast');
  if (toast) {
    toast.classList.remove('opacity-0');
    toast.classList.add('opacity-100');
    setTimeout(() => {
      toast.classList.remove('opacity-100');
      toast.classList.add('opacity-0');
    }, 1500);
  }
}

// ── Event Listeners Setup ───────────────────────────────────────────────────
function setupEventListeners() {
  // Hero Mic Button (Toggle recording)
  const heroMic = document.getElementById('hero-mic-button');
  if (heroMic) {
    heroMic.addEventListener('click', () => {
      if (state.isRecording) {
        stopRecording();
      } else {
        startRecording();
      }
    });
  }

  // Spacebar Hotkey (Hold to talk)
  let spacePressed = false;

  function isTypingOrInteractiveContext() {
    const el = document.activeElement;
    if (!el) return false;
    const tag = el.tagName ? el.tagName.toLowerCase() : '';
    if (tag === 'input' || tag === 'textarea' || tag === 'select' || el.isContentEditable) {
      return true;
    }
    const role = el.getAttribute('role');
    if (role === 'textbox' || role === 'searchbox' || role === 'combobox' || role === 'listbox') {
      return true;
    }
    if (el.closest && el.closest('#source-combobox-panel, #target-combobox-panel, #source-combobox-trigger, #target-combobox-trigger, button, a')) {
      return true;
    }
    return false;
  }

  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && !spacePressed) {
      // Ignore if user is currently typing or inside an interactive control
      if (isTypingOrInteractiveContext()) return;

      e.preventDefault();
      spacePressed = true;
      if (!state.isRecording) startRecording();
    }
  });

  window.addEventListener('keyup', (e) => {
    if (e.code === 'Space' && spacePressed) {
      e.preventDefault();
      spacePressed = false;
      if (state.isRecording) stopRecording();
    }
  });

  // Swap Languages Button
  const swapBtn = document.getElementById('swap-lang-btn');
  if (swapBtn) {
    swapBtn.addEventListener('click', () => {
      const currentSrc = state.sourceLang;
      const currentTgt = state.targetLang;

      let newSrc, newTgt;
      if (currentSrc !== 'auto') {
        newSrc = currentTgt;
        newTgt = currentSrc;
      } else {
        // If source was auto, swap target into source and default target to English
        newSrc = currentTgt;
        newTgt = 'en';
      }

      selectLanguage('source', newSrc);
      selectLanguage('target', newTgt);

      // Also swap card texts
      const srcTextEl = document.getElementById('transcript-source-text');
      const tgtTextEl = document.getElementById('target-translation-text');
      if (srcTextEl && tgtTextEl) {
        const temp = srcTextEl.textContent;
        srcTextEl.textContent = tgtTextEl.textContent;
        tgtTextEl.textContent = temp;
      }
    });
  }

  // Translation Error Banner Buttons
  const retryBtn = document.getElementById('translation-retry-btn');
  if (retryBtn) {
    retryBtn.addEventListener('click', () => {
      if (state.lastFailedTranslation) {
        const { text, source, target } = state.lastFailedTranslation;
        hideTranslationErrorBanner();
        executeTranslation(text, source, target);
      }
    });
  }

  const closeErrorBtn = document.getElementById('translation-error-close');
  if (closeErrorBtn) {
    closeErrorBtn.addEventListener('click', () => {
      hideTranslationErrorBanner();
    });
  }

  // Manual Text Input & Enter Key
  const manualInput = document.getElementById('manual-text-input');
  const charCounter = document.getElementById('char-counter');
  const translateBtn = document.getElementById('translate-manual-btn');

  if (manualInput) {
    manualInput.addEventListener('input', (e) => {
      if (charCounter) charCounter.textContent = `${e.target.value.length} / 1,000`;
    });

    manualInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (state.isTranslating) return; // Prevent duplicate submissions while in-flight
        const text = manualInput.value.trim();
        if (text) {
          executeTranslation(text, state.sourceLang, state.targetLang);
          manualInput.value = '';
          if (charCounter) charCounter.textContent = '0 / 1,000';
        }
      }
    });
  }

  if (translateBtn) {
    translateBtn.addEventListener('click', () => {
      if (state.isTranslating) return; // Prevent duplicate clicks while in-flight
      const text = manualInput ? manualInput.value.trim() : '';
      if (text) {
        executeTranslation(text, state.sourceLang, state.targetLang);
        manualInput.value = '';
        if (charCounter) charCounter.textContent = '0 / 1,000';
      }
    });
  }

  // TTS Play Button on Outbound Card
  const ttsPlayBtn = document.getElementById('tts-play-btn');
  if (ttsPlayBtn) {
    ttsPlayBtn.addEventListener('click', () => {
      const text = document.getElementById('target-translation-text')?.textContent || '';
      playTTS(text, state.targetLang);
    });
  }

  // Slow Playback (0.8x)
  const slowTtsBtn = document.getElementById('slow-tts-btn');
  if (slowTtsBtn) {
    slowTtsBtn.addEventListener('click', () => {
      const text = document.getElementById('target-translation-text')?.textContent || '';
      playTTS(text, state.targetLang, 0.8);
    });
  }

  // Play Capture (Inbound speech)
  const playCaptureBtn = document.getElementById('play-capture-btn');
  if (playCaptureBtn) {
    playCaptureBtn.addEventListener('click', () => {
      const text = document.getElementById('transcript-source-text')?.textContent || '';
      const src = state.sourceLang === 'auto' ? 'en' : state.sourceLang;
      playTTS(text, src);
    });
  }

  // Phonetics Drawer Toggle
  const togglePhonetic = document.getElementById('toggle-phonetic');
  const phoneticContainer = document.getElementById('phonetic-container');
  if (togglePhonetic && phoneticContainer) {
    togglePhonetic.addEventListener('click', () => {
      phoneticContainer.classList.toggle('hidden');
    });
  }

  // Copy Translation Button
  const copyBtn = document.getElementById('copy-btn');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const text = document.getElementById('target-translation-text')?.textContent || '';
      copyText(text);
    });
  }

  // Export / Copy Transcript Button
  const exportBtn = document.getElementById('export-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      const src = document.getElementById('transcript-source-text')?.textContent || '';
      const tgt = document.getElementById('target-translation-text')?.textContent || '';
      const combined = `Source: ${src}\nTranslation: ${tgt}`;
      copyText(combined);
      alert("Bilingual conversation transcript copied to clipboard!");
    });
  }

  // Clear Input Button
  const clearInputBtn = document.getElementById('clear-input-btn');
  if (clearInputBtn) {
    clearInputBtn.addEventListener('click', () => {
      document.getElementById('transcript-source-text').textContent = '""';
      document.getElementById('target-translation-text').textContent = '""';
    });
  }

  // Edit Source Button
  const editSourceBtn = document.getElementById('edit-source-btn');
  if (editSourceBtn && manualInput) {
    editSourceBtn.addEventListener('click', () => {
      const current = document.getElementById('transcript-source-text')?.textContent || '';
      manualInput.value = current.replace(/^["']|["']$/g, '');
      manualInput.focus();
    });
  }

  // Settings inputs
  const autoPlayCheck = document.getElementById('pref-auto-play');
  if (autoPlayCheck) {
    autoPlayCheck.addEventListener('change', (e) => {
      state.settings.autoPlay = e.target.checked;
      saveSettings();
    });
  }

  const speedSlider = document.getElementById('pref-tts-speed');
  if (speedSlider) {
    speedSlider.addEventListener('change', (e) => {
      state.settings.playbackSpeed = parseFloat(e.target.value);
      saveSettings();
    });
  }

  const echoCheck = document.getElementById('pref-echo-cancel');
  if (echoCheck) {
    echoCheck.addEventListener('change', (e) => {
      state.settings.echoCancellation = e.target.checked;
      saveSettings();
    });
  }

  const noiseCheck = document.getElementById('pref-noise-suppress');
  if (noiseCheck) {
    noiseCheck.addEventListener('change', (e) => {
      state.settings.noiseSuppression = e.target.checked;
      saveSettings();
    });
  }
}
