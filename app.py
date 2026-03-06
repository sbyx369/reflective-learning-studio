import streamlit as st
import google.generativeai as genai
import PyPDF2
from docx import Document
import datetime
import time
import re

# ═══════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="LearnFlow AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════
DEFAULTS = {
    "dark_mode": True,
    "user_api_keys": [],
    "history": [],
    "notes_content": None,
    "notes_heading": None,
    "tldr": None,
    "generated_output": None,
    "generated_heading": None,
    "quiz_score": None,
    "tutor_history": [],
    "feynman_feedback": None,
    "pomo_start": None,
    "pomo_duration": 0,
    "pomo_running": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

dark = st.session_state.dark_mode

# ═══════════════════════════════════════════════════════════
# THEME COLORS
# ═══════════════════════════════════════════════════════════
if dark:
    BG = "#06080f"
    SB = "#09111f"
    CARD = "#0d1726"
    BORDER = "#1e3358"
    TEXT = "#e8eeff"
    TEXT2 = "#7b9cc8"
    TEXT3 = "#3d6090"
    ACCENT = "#3b82f6"
    ACCENT2 = "#6366f1"
    INPUT = "#0a1220"
    BTN = "#0e1c35"
    BTN_T = "#7aaad8"
    HERO = "linear-gradient(135deg,#060e20 0%,#0a1530 50%,#060b1a 100%)"
    HTITLE = "#93c5fd"
    HSUB = "#5a82b0"
    PILL_BG = "#0a1428"
    PILL_T = "#4a7aaa"
    POMO_C = "#60a5fa"
    STAT_V = "#60a5fa"
    GREEN = "#10b981"
    EYEBROW = "#2a5898"
else:
    BG = "#f0f4ff"
    SB = "#e0eaf8"
    CARD = "#ffffff"
    BORDER = "#b8cef0"
    TEXT = "#0d1a35"
    TEXT2 = "#2a4070"
    TEXT3 = "#5a78a8"
    ACCENT = "#2563eb"
    ACCENT2 = "#4338ca"
    INPUT = "#ffffff"
    BTN = "#eef2ff"
    BTN_T = "#2563eb"
    HERO = "linear-gradient(135deg,#ddeaff 0%,#eef3ff 50%,#e8e4ff 100%)"
    HTITLE = "#1e40af"
    HSUB = "#3a5a90"
    PILL_BG = "#eef2ff"
    PILL_T = "#3a5aaa"
    POMO_C = "#2563eb"
    STAT_V = "#2563eb"
    GREEN = "#059669"
    EYEBROW = "#4a78cc"

# ═══════════════════════════════════════════════════════════
# GLOBAL CSS — Bulletproof Alignment & Visibilty
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {{
    background: {BG} !important;
    color: {TEXT} !important;
    font-family: 'Outfit', sans-serif !important;
}}

/* ── STREAMLIT CHROME FIX ── */
/* Keep the header transparent so the sidebar toggle works, but hide branding */
header[data-testid="stHeader"] {{
    background: transparent !important;
}}
#MainMenu, footer, [data-testid="stToolbar"] {{
    display: none !important;
    visibility: hidden !important;
}}

/* ── MAIN CONTENT ALIGNMENT ── */
.block-container {{
    max-width: 1050px !important;
    margin: 0 auto !important;
    padding: 3rem 2rem 6rem !important; /* Added top padding to clear transparent header */
    background: {BG} !important;
}}

/* ══════════════════════════════
   SIDEBAR
══════════════════════════════ */
[data-testid="stSidebar"] {{
    background: {SB} !important;
    border-right: 1px solid {BORDER} !important;
    min-width: 280px !important;
    max-width: 300px !important;
}}
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {{
    background: {SB} !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding: 1.5rem 1.2rem !important;
    background: {SB} !important;
}}

/* Sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] small {{
    color: {TEXT2} !important;
    font-family: 'Outfit', sans-serif !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: {TEXT} !important;
}}

/* Sidebar buttons & inputs */
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] details,
[data-testid="stSidebar"] .stTextInput > div > div > input {{
    background: {INPUT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {TEXT} !important;
}}
[data-testid="stSidebar"] .stButton > button {{
    background: {BTN} !important;
    color: {BTN_T} !important;
    border: 1px solid {BORDER} !important;
    font-size: 0.85rem !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    border-color: {ACCENT} !important;
    color: {ACCENT} !important;
}}

/* Sidebar metrics */
[data-testid="stSidebar"] [data-testid="metric-container"] {{
    background: {INPUT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    padding: 0.6rem 0.8rem !important;
}}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {{
    color: {STAT_V} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.3rem !important;
}}

/* ══════════════════════════════
   MAIN UI ELEMENTS
══════════════════════════════ */
.stButton > button {{
    background: {BTN} !important;
    color: {BTN_T} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    border-color: {ACCENT} !important;
    color: {ACCENT} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.15) !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {ACCENT}, {ACCENT2}) !important;
    color: #fff !important;
    border: none !important;
    box-shadow: 0 2px 12px rgba(59,130,246,0.25) !important;
}}
.stButton > button[kind="primary"]:hover {{
    box-shadow: 0 4px 20px rgba(59,130,246,0.4) !important;
    transform: translateY(-1px) !important;
}}

/* Inputs & Textareas */
.stTextArea textarea,
.stTextInput > div > div > input {{
    background: {INPUT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.8rem !important;
}}
.stTextArea textarea:focus,
.stTextInput > div > div > input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    outline: none !important;
}}

/* Tabs & Expanders */
.stTabs [data-baseweb="tab-list"] {{
    background: {INPUT} !important;
    border-radius: 12px !important;
    padding: 6px !important;
    border: 1px solid {BORDER} !important;
    gap: 5px !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {TEXT3} !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    border: none !important;
    padding: 0.5rem 1.2rem !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {ACCENT}, {ACCENT2}) !important;
    color: #ffffff !important;
}}
details {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    margin-bottom: 0.8rem !important;
}}
details > summary {{
    color: {TEXT2} !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 1rem 1.2rem !important;
    background: {CARD} !important;
}}

/* Divider */
hr {{ border-top: 1px solid {BORDER} !important; margin: 2rem 0 !important; }}

/* ══════════════════════════════
   CUSTOM CLASSES
══════════════════════════════ */
.sb-section {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.18em; text-transform: uppercase; color: {TEXT3};
    padding: 1.2rem 0 0.5rem; border-bottom: 1px solid {BORDER}; margin-bottom: 0.8rem; display: block;
}}

/* Hero Section */
.lf-hero {{
    background: {HERO}; border: 1px solid {BORDER}; border-radius: 24px;
    padding: 3rem 3.5rem; margin-bottom: 1.5rem; position: relative; overflow: hidden;
}}
.lf-eyebrow {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; letter-spacing: 0.2em;
    text-transform: uppercase; color: {EYEBROW}; margin-bottom: 1.2rem;
}}
.lf-title {{
    font-size: 3.2rem; font-weight: 900; line-height: 1.1; color: {HTITLE};
    margin-bottom: 1rem; letter-spacing: -0.03em; font-family: 'Outfit', sans-serif;
}}
.lf-subtitle {{ font-size: 1.05rem; color: {HSUB}; line-height: 1.7; max-width: 550px; }}
.lf-stats {{ display: flex; gap: 3rem; margin-top: 2rem; padding-top: 1.8rem; border-top: 1px solid {BORDER}; }}
.lf-stat-val {{ font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 700; color: {STAT_V}; }}
.lf-stat-lbl {{ font-size: 0.7rem; color: {TEXT3}; text-transform: uppercase; letter-spacing: 0.1em; }}

/* Setup UI Overlay */
.lf-setup-wrap {{
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    min-height: 80vh; width: 100%; max-width: 580px; margin: 0 auto;
}}
.lf-setup-logo {{ text-align: center; margin-bottom: 2rem; }}
.lf-setup-logo-icon {{ font-size: 3rem; }}
.lf-setup-logo-name {{ font-size: 1.8rem; font-weight: 800; color: {TEXT}; margin-top: 0.5rem; }}
.lf-setup-logo-name span {{ color: {ACCENT}; }}
.lf-setup-logo-sub {{ font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: {TEXT3}; letter-spacing: 0.2em; text-transform: uppercase; margin-top: 0.3rem; }}

.lf-setup-card {{
    background: {CARD}; border: 1px solid {BORDER}; border-radius: 24px;
    padding: 2.5rem; margin-bottom: 1.5rem; width: 100%; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}}
.lf-setup-badge {{ display: inline-block; background: rgba(59,130,246,0.1); color: {ACCENT}; font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; padding: 0.3rem 1rem; border-radius: 100px; margin-bottom: 1.2rem; font-weight: 600; letter-spacing: 0.1em; }}
.lf-setup-title {{ font-size: 1.6rem; font-weight: 800; color: {TEXT}; margin-bottom: 0.5rem; }}
.lf-setup-sub {{ font-size: 0.95rem; color: {TEXT2}; line-height: 1.6; margin-bottom: 2rem; }}

.lf-steps {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.6rem; margin-bottom: 1.5rem; }}
.lf-step {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 12px; padding: 1rem 0.5rem; text-align: center; }}
.lf-step-n {{ font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 700; color: {ACCENT}; }}
.lf-step-t {{ font-size: 0.7rem; color: {TEXT2}; margin-top: 0.3rem; line-height: 1.4; }}
.lf-tip {{ background: rgba(245,158,11,0.08); border-left: 3px solid #f59e0b; border-radius: 0 8px 8px 0; padding: 0.8rem 1rem; font-size: 0.85rem; color: #fbbf24; margin-bottom: 1.8rem; }}

</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# API KEYS & LLM CONFIG
# ═══════════════════════════════════════════════════════════
builtin_keys = []
try:
    if "GOOGLE_API_KEYS" in st.secrets:
        builtin_keys = list(st.secrets["GOOGLE_API_KEYS"])
except Exception:
    pass


def get_keys():
    return st.session_state.user_api_keys + builtin_keys


def has_key():
    return len(st.session_state.user_api_keys) > 0


def validate_key(key):
    try:
        genai.configure(api_key=key)
        r = genai.GenerativeModel("models/gemini-2.5-flash").generate_content(
            "Say OK", generation_config={"max_output_tokens": 5})
        return bool(r and r.text)
    except Exception:
        return False


def ai(prompt, temp=0.4):
    keys = get_keys()
    if not keys: return "NO_KEYS"
    for key in keys:
        try:
            genai.configure(api_key=key)
            r = genai.GenerativeModel("models/gemini-2.5-flash").generate_content(
                prompt, generation_config={"temperature": temp, "max_output_tokens": 2000})
            if r and r.text: return r.text.strip()
        except Exception:
            time.sleep(0.5)
    return "QUOTA"


def quota_ui():
    st.error("API quota exhausted. Add a new key to continue.")
    nk = st.text_input("New API key:", type="password", placeholder="AIzaSy...", key=f"qk_{time.time():.0f}")
    if st.button("Add Key & Retry", type="primary"):
        if nk.strip() and nk.strip() not in st.session_state.user_api_keys:
            st.session_state.user_api_keys.append(nk.strip())
            st.rerun()


# ═══════════════════════════════════════════════════════════
# FILE READERS
# ═══════════════════════════════════════════════════════════
@st.cache_data
def read_pdf(file_bytes):
    from io import BytesIO
    f = BytesIO(file_bytes)
    return "\n".join(p.extract_text() for p in PyPDF2.PdfReader(f).pages if p.extract_text())


@st.cache_data
def read_docx(file_bytes):
    from io import BytesIO
    f = BytesIO(file_bytes)
    return "\n".join(p.text for p in Document(f).paragraphs if p.text.strip())


@st.cache_data
def read_txt(file_bytes):
    return file_bytes.decode("utf-8", errors="ignore")


# ═══════════════════════════════════════════════════════════
# SIDEBAR (Always renders first so it's globally available)
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    lc, tc = st.columns([5, 1])
    with lc:
        st.markdown(f"""
<div style="padding:0.2rem 0 1rem;">
  <div style="font-size:1.2rem;font-weight:800;color:{TEXT};font-family:'Outfit',sans-serif;letter-spacing:-0.01em;">
    🧠 LearnFlow <span style="color:{ACCENT};">AI</span>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:{TEXT3};letter-spacing:0.17em;margin-top:0.3rem;text-transform:uppercase;">
    Study Companion
  </div>
</div>""", unsafe_allow_html=True)
    with tc:
        if st.button("🌙" if dark else "☀️", help="Toggle theme", use_container_width=True):
            st.session_state.dark_mode = not dark
            st.rerun()

    st.markdown(f'<div style="border-top:1px solid {BORDER};margin-bottom:0.5rem;"></div>', unsafe_allow_html=True)

    st.markdown('<span class="sb-section">Settings</span>', unsafe_allow_html=True)
    difficulty = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"], label_visibility="collapsed")
    persona = st.selectbox("Persona",
                           ["University Professor", "School Teacher", "Child-Friendly Tutor", "Scientist", "Exam Coach",
                            "Motivational Mentor"], label_visibility="collapsed")
    st.markdown(
        f'<div style="font-size:0.75rem;color:{TEXT2};margin:0.8rem 0 0.2rem;font-weight:500;">Creativity Level</div>',
        unsafe_allow_html=True)
    creativity = st.slider("Creativity", 0.1, 1.0, 0.4, 0.05, label_visibility="collapsed")

    st.markdown('<span class="sb-section">Pomodoro Timer</span>', unsafe_allow_html=True)
    pc1, pc2 = st.columns([3, 1])
    with pc1:
        pmin = st.selectbox("Minutes", [25, 5, 10, 15, 30, 45, 60], label_visibility="collapsed")
    with pc2:
        if st.button("▶" if not st.session_state.pomo_running else "■", use_container_width=True, key="pomo_btn"):
            if not st.session_state.pomo_running:
                st.session_state.pomo_start = time.time();
                st.session_state.pomo_duration = pmin * 60;
                st.session_state.pomo_running = True
            else:
                st.session_state.pomo_running = False;
                st.session_state.pomo_start = None
            st.rerun()

    st.markdown('<span class="sb-section">API Management</span>', unsafe_allow_html=True)
    with st.expander("🔑 Manage API Keys"):
        new_key = st.text_input("Add key:", type="password", placeholder="AIzaSy...", key="sb_new_key",
                                label_visibility="collapsed")
        if st.button("Add Key", use_container_width=True, key="sb_add_key") and new_key.strip():
            if new_key.strip() not in st.session_state.user_api_keys:
                st.session_state.user_api_keys.append(new_key.strip());
                st.rerun()
        if st.session_state.user_api_keys:
            if st.button("Clear All Keys", use_container_width=True, key="sb_rm_keys"):
                st.session_state.user_api_keys = [];
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Reset Entire Session", use_container_width=True, key="sb_reset"):
        sk = st.session_state.user_api_keys;
        sm = st.session_state.dark_mode
        for k, v in DEFAULTS.items(): st.session_state[k] = v
        st.session_state.user_api_keys = sk;
        st.session_state.dark_mode = sm
        st.rerun()

# ═══════════════════════════════════════════════════════════
# GATE: SETUP SCREEN (Renders beautifully centered)
# ═══════════════════════════════════════════════════════════
if not has_key():
    st.markdown(f"""
<div class="lf-setup-wrap">
  <div class="lf-setup-logo">
    <div class="lf-setup-logo-icon">🧠</div>
    <div class="lf-setup-logo-name">LearnFlow <span>AI</span></div>
    <div class="lf-setup-logo-sub">Your Personal Study Companion</div>
  </div>
  <div class="lf-setup-card">
    <div style="text-align:center;"><span class="lf-setup-badge">✦ Free · No Credit Card · 2 Minutes</span></div>
    <div class="lf-setup-title" style="text-align:center;">Connect your free API key</div>
    <div class="lf-setup-sub" style="text-align:center;">
      LearnFlow AI is powered by Google Gemini — completely free.<br>
      Get your key and instantly unlock 12 powerful study tools.
    </div>
    <div class="lf-steps">
      <div class="lf-step"><div class="lf-step-n">01</div><div class="lf-step-t">Open Google AI Studio</div></div>
      <div class="lf-step"><div class="lf-step-n">02</div><div class="lf-step-t">Sign in with Google</div></div>
      <div class="lf-step"><div class="lf-step-n">03</div><div class="lf-step-t">Create API Key</div></div>
      <div class="lf-step"><div class="lf-step-n">04</div><div class="lf-step-t">Paste it below</div></div>
    </div>
    <div class="lf-tip">⚡ Keys look like: <strong>AIzaSyA1B2C3...</strong> (39 characters)</div>

    <div style="margin-bottom: 1.5rem;">
      <a href="https://aistudio.google.com/app/apikey" target="_blank" style="display:block; text-align:center; color:{ACCENT}; font-weight:600; text-decoration:none; background:{BTN}; padding:0.8rem; border-radius:10px; border:1px solid {BORDER};">🔑 Click here to get your free key ↗</a>
    </div>
""", unsafe_allow_html=True)

    key_in = st.text_input("Paste Key:", type="password", placeholder="Paste your AIzaSy... key here",
                           label_visibility="collapsed")
    if st.button("🚀 Validate & Start Learning", type="primary", use_container_width=True):
        k = key_in.strip()
        if not k:
            st.warning("Paste your API key above.")
        elif not k.startswith("AIza"):
            st.error("Invalid key — Gemini keys always start with **AIza**")
        else:
            with st.spinner("Validating..."):
                if validate_key(k):
                    st.session_state.user_api_keys = [k];
                    st.balloons();
                    st.rerun()
                else:
                    st.error("Google rejected this key. Try copying it again.")

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════
# PROMPTS & GENERATOR LOGIC
# ═══════════════════════════════════════════════════════════
PROMPTS = {
    "Notes": "Create structured academic notes with clear H2 headings and bullet points. Max 500 words. No preamble.\n",
    "Flashcards": "Generate exactly 5 flashcards.\nFormat strictly:\nFlashcard 1\nQuestion: [question]\nAnswer: [answer]\n\nFlashcard 2\nQuestion: [question]\nAnswer: [answer]\n(continue for all 5)\n",
    "Quiz": "Generate exactly 5 multiple choice questions.\nFormat strictly:\nQuestion 1: [question text]\nA. [option]\nB. [option]\nC. [option]\nD. [option]\nCorrect Answer: A\n\nQuestion 2: ...\n",
    "Reflection": "Generate 5 deep reflection questions. Numbered list. No preamble.\n",
    "Study Plan": "Create a 5-step study plan with clear timelines. Numbered. Actionable.\n",
    "Key Concepts": "List 7 key concepts. Format: **Concept Name** — one-line definition. Why it matters: one sentence.\n",
    "Exam Mode": "Create a full exam paper:\nSection A: 3 MCQ (mark correct answer)\nSection B: 2 Fill in the blanks (provide answers)\nSection C: 2 Short answer (provide model answers)\n",
    "TL;DR": "Summarise in exactly 5 bullet points. Max 15 words each. Exam-focused. No preamble.\n",
    "Feynman": "Evaluate this student explanation:\n- Correct points (list)\n- Missing/wrong (list)\n- Score: X/10\n- Improvement tips\n",
    "Socratic": "Ask ONE deep Socratic question about this topic. Not factual recall. Challenge assumptions. One sentence.\n",
    "Mind Map": "Create a text mind map:\nCentral Topic: [topic]\n  Branch 1: [name]\n    - [sub-point]\n    - [sub-point]\n  Branch 2: ...\n(5 branches total)\n",
    "Mnemonics": "Create 3 memorable mnemonics or acronyms for key concepts in this topic. Explain each.\n",
    "ELI5": "Explain this topic like I am 10 years old. Simple words, fun analogies, max 200 words.\n",
}


def build_prompt(text, difficulty, persona, fmt):
    trimmed = len(text) > 3500
    base = f"Topic/Content:\n{text[:3500]}\n\nDifficulty: {difficulty}\nPersona: {persona}\n\nIMPORTANT: Output ONLY the requested format. No preamble, no intro phrases. Start directly.\n\n"
    return base + PROMPTS.get(fmt, PROMPTS["Notes"]), trimmed


def run_gen(fmt, content, manual, difficulty, persona, temp, mode="output"):
    if not content: st.warning("Enter a topic or upload a file first."); return False
    p, trimmed = build_prompt(content, difficulty, persona, fmt)
    if trimmed: st.caption("Content trimmed to 3500 characters for processing.")
    with st.spinner(f"Generating {fmt}..."):
        r = ai(p, temp)
    if r in ("QUOTA", "NO_KEYS"): quota_ui(); return False
    if mode == "notes":
        st.session_state.notes_content = r
        st.session_state.notes_heading = ai(f"Create a 5-word heading for: {manual or 'this topic'}",
                                            0.2) or "Study Notes"
        st.session_state.generated_output = None;
        st.session_state.generated_heading = None;
        st.session_state.quiz_score = None
    else:
        st.session_state.generated_output = r;
        st.session_state.generated_heading = fmt
    st.session_state.history.append({"ts": datetime.datetime.now().strftime("%H:%M · %d %b"), "format": fmt,
                                     "topic": (manual or "Uploaded file")[:45], "output": r})
    return True


# ═══════════════════════════════════════════════════════════
# MAIN UI — HERO
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="lf-hero">
  <div class="lf-eyebrow">✦ Powered by Google Gemini 2.5 Flash</div>
  <div class="lf-title">Learn Smarter.<br>Not Harder.</div>
  <div class="lf-subtitle">Transform any topic or document into notes, flashcards, quizzes, mind maps and more — in seconds.</div>
  <div class="lf-stats">
    <div><div class="lf-stat-val">12+</div><div class="lf-stat-lbl">AI Tools</div></div>
    <div><div class="lf-stat-val">∞</div><div class="lf-stat-lbl">Topics</div></div>
    <div><div class="lf-stat-val">Free</div><div class="lf-stat-lbl">Forever</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# STEP 1 — INPUT
# ═══════════════════════════════════════════════════════════
st.markdown(
    f'<div style="font-size:1.3rem; font-weight:700; color:{TEXT}; margin-bottom:1rem;">1. Enter Topic or Upload File</div>',
    unsafe_allow_html=True)

uploaded = st.file_uploader("", type=["pdf", "docx", "txt"], label_visibility="collapsed")
file_text = ""
if uploaded:
    with st.spinner(f"Reading {uploaded.name}..."):
        try:
            fb = uploaded.getvalue()
            if "pdf" in uploaded.type:
                file_text = read_pdf(fb)
            elif "document" in uploaded.type:
                file_text = read_docx(fb)
            else:
                file_text = read_txt(fb)
            st.success(f"**{uploaded.name}** loaded — {len(file_text):,} chars")
        except Exception as e:
            st.error(f"Error reading file: {e}")

manual = st.text_area("", height=120, label_visibility="collapsed",
                      placeholder="e.g. Newton's Laws of Motion, French Revolution, Quantum Computing...")

content = f"User instruction: {manual.strip()}\n\nDocument content:\n{file_text}" if (
            file_text and manual.strip()) else (file_text or manual.strip())
G = dict(content=content, manual=manual, difficulty=difficulty, persona=persona, temp=creativity)

# ═══════════════════════════════════════════════════════════
# STEP 2 — GENERATE
# ═══════════════════════════════════════════════════════════
st.markdown(
    f'<hr><div style="font-size:1.3rem; font-weight:700; color:{TEXT}; margin-bottom:1rem;">2. Generate Materials</div>',
    unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("📝 Smart Notes", use_container_width=True, type="primary"):
        if run_gen("Notes", **G, mode="notes"): st.rerun()
with c2:
    if st.button("⚡ Quick TL;DR", use_container_width=True):
        if content:
            r = ai(build_prompt(content, difficulty, persona, "TL;DR")[0], 0.3)
            if r not in ("QUOTA", "NO_KEYS"): st.session_state.tldr = r
        else:
            st.warning("Enter a topic first.")
with c3:
    if st.button("🔑 Key Concepts", use_container_width=True):
        if run_gen("Key Concepts", **G): st.rerun()
with c4:
    if st.button("💡 Mnemonics", use_container_width=True):
        if run_gen("Mnemonics", **G): st.rerun()

if st.session_state.tldr:
    st.info(f"**⚡ TL;DR**\n\n{st.session_state.tldr}")
    if st.button("Dismiss TL;DR", key="dismiss_tldr"): st.session_state.tldr = None; st.rerun()

if st.session_state.notes_content:
    with st.expander(f"📘 {st.session_state.notes_heading}", expanded=True):
        st.markdown(st.session_state.notes_content)

if st.session_state.generated_heading in ["Key Concepts", "Mnemonics", "Mind Map", "ELI5", "Study Plan"]:
    with st.expander(f"📄 {st.session_state.generated_heading}", expanded=True):
        st.markdown(st.session_state.generated_output)

# ═══════════════════════════════════════════════════════════
# STEP 3 — TEST KNOWLEDGE
# ═══════════════════════════════════════════════════════════
if st.session_state.notes_content:
    st.markdown(
        f'<hr><div style="font-size:1.3rem; font-weight:700; color:{TEXT}; margin-bottom:1rem;">3. Test Your Knowledge</div>',
        unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🎴 Flashcards", "❓ Quiz", "🤔 Feynman Check", "🤖 Socratic Tutor"])

    with t1:
        if st.button("Generate Flashcards", type="primary", key="btn_fc"): run_gen("Flashcards", **G)
        if st.session_state.generated_heading == "Flashcards":
            for i, blk in enumerate(
                    [b for b in st.session_state.generated_output.split("Flashcard") if b.strip() and "Answer:" in b],
                    1):
                q, a = [p.strip() for p in blk.split("Answer:")]
                q = q.replace("Question:", "").lstrip("1234567890. \n")
                if f"fc_{i}" not in st.session_state: st.session_state[f"fc_{i}"] = False
                st.markdown(
                    f'<div style="background:{CARD}; border:1px solid {BORDER}; border-left:3px solid {ACCENT}; padding:1rem; border-radius:10px; margin-bottom:0.5rem;"><strong>Q:</strong> {q}</div>',
                    unsafe_allow_html=True)
                if st.button("Toggle Answer", key=f"tgl_{i}"): st.session_state[f"fc_{i}"] = not st.session_state[
                    f"fc_{i}"]; st.rerun()
                if st.session_state[f"fc_{i}"]: st.success(f"**A:** {a}")
                st.markdown("<br>", unsafe_allow_html=True)

    with t2:
        if st.button("Generate Quiz", type="primary", key="btn_qz"): run_gen("Quiz",
                                                                             **G); st.session_state.quiz_score = None
        if st.session_state.generated_heading == "Quiz":
            raw = st.session_state.generated_output
            u_ans, c_keys = [], []
            for i, blk in enumerate([q for q in re.split(r'Question\s+\d+[:.]', raw, flags=re.IGNORECASE) if q.strip()],
                                    1):
                lines = [l.strip() for l in blk.split("\n") if l.strip()]
                qtxt, opts = lines[0].lstrip(".*:) "), [l for l in lines[1:] if re.match(r'^[A-Da-d][.)]\s+', l)]
                ans_line = [l for l in lines if "correct" in l.lower() and "answer" in l.lower()]
                if not opts or not ans_line: continue

                st.markdown(f"**Q{i}.** {qtxt}")
                sel = st.radio("", opts, key=f"qz_{i}", index=None, label_visibility="collapsed")
                u_ans.append(sel)
                m = re.search(r'[:]\s*([A-Da-d])', ans_line[0])
                if m: c_keys.append(m.group(1).upper())
                st.markdown("---")

            if u_ans and c_keys and st.button("Submit Exam", type="primary"):
                if None in u_ans:
                    st.warning("Complete all questions first.")
                else:
                    st.session_state.quiz_score = sum(1 for i, a in enumerate(u_ans) if
                                                      i < len(c_keys) and a and a.strip().upper().startswith(c_keys[i]))
            if st.session_state.quiz_score is not None:
                pct = int(st.session_state.quiz_score / len(c_keys) * 100) if c_keys else 0
                st.metric("Score", f"{st.session_state.quiz_score} / {len(c_keys)} ({pct}%)")
                st.progress(pct / 100)

    with t3:
        st.markdown("**Feynman Technique**: Explain the topic simply. AI will score your understanding out of 10.")
        fi = st.text_area("Your Explanation:", height=120, key="f_in")
        if st.button("Evaluate My Understanding", type="primary"):
            if not fi.strip():
                st.warning("Write something first.")
            else:
                with st.spinner("Evaluating..."):
                    st.session_state.feynman_feedback = ai(
                        build_prompt(f"Topic: {content}\nStudent explanation: {fi}", difficulty, persona, "Feynman")[0],
                        0.3)
        if st.session_state.feynman_feedback: st.info(st.session_state.feynman_feedback)

    with t4:
        if st.button("Start Socratic Chat", type="primary"):
            st.session_state.tutor_history = [
                {"role": "ai", "msg": ai(build_prompt(content, difficulty, "Analytical", "Socratic")[0], 0.6)}]
            st.rerun()
        for m in st.session_state.tutor_history:
            bg = f"background:{CARD};" if m["role"] == "ai" else f"background:rgba(59,130,246,0.1); text-align:right;"
            st.markdown(
                f'<div style="{bg} padding:1rem; border-radius:10px; border:1px solid {BORDER}; margin-bottom:0.5rem;">{m["msg"]}</div>',
                unsafe_allow_html=True)
        if st.session_state.tutor_history:
            reply = st.text_input("Reply:", key="tutor_in", label_visibility="collapsed", placeholder="Type answer...")
            c1, c2 = st.columns([4, 1])
            with c1:
                if st.button("Send Reply", use_container_width=True) and reply.strip():
                    st.session_state.tutor_history.append({"role": "user", "msg": reply})
                    with st.spinner("Thinking..."):
                        resp = ai(f"Topic: {content}\nStudent: {reply}\nAsk ONE short deeper follow-up question.", 0.6)
                        st.session_state.tutor_history.append({"role": "ai", "msg": resp})
                    st.rerun()
            with c2:
                if st.button("Clear Chat", use_container_width=True): st.session_state.tutor_history = []; st.rerun()