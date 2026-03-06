import streamlit as st
import google.generativeai as genai
import PyPDF2
from docx import Document
import datetime
import time
import re

st.set_page_config(
    page_title="LearnFlow AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SESSION STATE ──
defaults = {
    "dark_mode": True, "user_api_keys": [], "history": [],
    "notes_content": None, "notes_heading": None, "tldr": None,
    "generated_output": None, "generated_heading": None,
    "quiz_score": None, "tutor_history": [], "feynman_feedback": None,
    "timer_start": None, "timer_duration": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

dark = st.session_state.dark_mode

# ── COLOR TOKENS ──
if dark:
    BG=     "#07090f"; SB_BG="#0d1220"; CARD="#111828"
    BORDER= "#243858"; TEXT="#e8f0ff";  TEXT2="#90b0d8"; TEXT3="#5888b8"
    ACCENT= "#3b82f6"; ACCENT2="#6366f1"
    INPUT=  "#0a1020"; BTN="#0e1c35";   BTN_T="#7aaad8"
    HERO_BG="linear-gradient(135deg,#060d1e,#091428,#050b18)"
    HERO_BR="#1c3060"
    HTITLE= "linear-gradient(135deg,#ffffff,#93c5fd,#a5b4fc,#c084fc)"
    PILL_BG="#091428"; PILL_T="#4a78aa"; FC_BG="#0a1428"
    PROG_BG="#1a2e50"; SETUP="linear-gradient(135deg,#060d1e,#091428)"
    STAT_V= "#60a5fa"; EYEBROW="#2a5898"
else:
    BG=     "#f0f4ff"; SB_BG="#d8e4f8"; CARD="#ffffff"
    BORDER= "#a8bedc"; TEXT="#0f1a30";  TEXT2="#1e3050"; TEXT3="#3a5070"
    ACCENT= "#2563eb"; ACCENT2="#4338ca"
    INPUT=  "#ffffff"; BTN="#eef2ff";   BTN_T="#2563eb"
    HERO_BG="linear-gradient(135deg,#dce8ff,#eef3ff,#f0ecff)"
    HERO_BR="#b0c8f0"
    HTITLE= "linear-gradient(135deg,#1a3a8f,#2563eb,#4f46e5,#7c3aed)"
    PILL_BG="#eef2ff"; PILL_T="#3a5aaa"; FC_BG="#f5f8ff"
    PROG_BG="#d0daf0"; SETUP="linear-gradient(135deg,#dce8ff,#eef3ff)"
    STAT_V= "#2563eb"; EYEBROW="#4a78cc"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');
*,*::before,*::after{{box-sizing:border-box;}}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]>.main{{
    background-color:{BG}!important; color:{TEXT}!important;
    font-family:'Plus Jakarta Sans',sans-serif!important;}}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{{display:none!important;}}
::-webkit-scrollbar{{width:4px;}} ::-webkit-scrollbar-thumb{{background:{BORDER};border-radius:10px;}}
.block-container{{max-width:1080px!important;margin:0 auto!important;padding:1rem 2rem 6rem!important;background:{BG}!important;}}
/* ══ SIDEBAR NUCLEAR FIX ══ */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div > div,
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {{
    background-color:{SB_BG}!important;
    background:{SB_BG}!important;
    transform: none !important;
    visibility: visible !important;
    display: block !important;
    opacity: 1 !important;
}}
[data-testid="stSidebar"] {{
    border-right:2px solid {BORDER}!important;
    min-width:260px!important;
    max-width:320px!important;
    width:270px!important;
    position:relative!important;
    flex-shrink:0!important;
}}
[data-testid="collapsedControl"] {{
    display:none!important;
}}
[data-testid="stSidebarNav"] {{
    display:none!important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding:1.2rem 1rem!important;
    background-color:{SB_BG}!important;
}}
/* All text in sidebar */
[data-testid="stSidebar"] *:not(button):not([data-baseweb="select"] input) {{
    color:{TEXT2}!important;
    font-family:'Plus Jakarta Sans',sans-serif!important;
}}
[data-testid="stSidebar"] .sb-label {{
    color:{TEXT3}!important;
    font-family:'Space Mono',monospace!important;
    font-weight:700!important;
    letter-spacing:0.14em!important;
}}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {{
    color:{STAT_V}!important;
    font-family:'Space Mono',monospace!important;
    font-size:1.3rem!important;
    font-weight:700!important;
}}
[data-testid="stSidebar"] [data-testid="metric-container"] {{
    background:{CARD}!important;
    border:1px solid {BORDER}!important;
    border-radius:10px!important;
}}
[data-testid="stSidebar"] [data-testid="metric-container"] label {{
    color:{TEXT3}!important;
    font-size:0.68rem!important;
    text-transform:uppercase!important;
    letter-spacing:0.1em!important;
}}
[data-testid="stSidebar"] button {{
    background:{BTN}!important;
    color:{BTN_T}!important;
    border:1px solid {BORDER}!important;
}}
[data-testid="stSidebar"] button:hover {{
    border-color:{ACCENT}!important;
    color:{ACCENT}!important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background:{INPUT}!important;
    border:1px solid {BORDER}!important;
    color:{TEXT}!important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div {{
    color:{TEXT}!important;
    background:{INPUT}!important;
}}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {{
    background:{INPUT}!important;
}}
[data-testid="stSidebar"] details {{
    background:{CARD}!important;
    border:1px solid {BORDER}!important;
}}
[data-testid="stSidebar"] details summary {{
    color:{TEXT2}!important;
    background:{CARD}!important;
}}
[data-testid="stSidebar"] .stTextInput>div>div>input {{
    background:{INPUT}!important;
    color:{TEXT}!important;
    border:1px solid {BORDER}!important;
}}
button,[role="button"],label,[data-baseweb="tab"],[data-baseweb="option"],[data-testid="stFileUploader"] *{{cursor:pointer!important;}}
[data-baseweb="select"] input,[data-baseweb="combobox"] input{{caret-color:transparent!important;cursor:pointer!important;pointer-events:none!important;}}
.stButton>button{{background:{BTN}!important;color:{BTN_T}!important;border:1px solid {BORDER}!important;border-radius:10px!important;font-family:'Plus Jakarta Sans',sans-serif!important;font-weight:600!important;font-size:0.85rem!important;padding:0.55rem 1rem!important;transition:all 0.18s!important;cursor:pointer!important;width:100%!important;}}
.stButton>button:hover{{border-color:{ACCENT}!important;color:{ACCENT}!important;transform:translateY(-1px)!important;}}
.stButton>button[kind="primary"]{{background:linear-gradient(135deg,{ACCENT},{ACCENT2})!important;color:#fff!important;border:none!important;}}
.stButton>button[kind="primary"]:hover{{box-shadow:0 4px 20px rgba(59,130,246,0.4)!important;transform:translateY(-1px)!important;}}
.stTextArea textarea,.stTextInput>div>div>input{{background:{INPUT}!important;border:1px solid {BORDER}!important;border-radius:10px!important;color:{TEXT}!important;font-family:'Plus Jakarta Sans',sans-serif!important;}}
.stTextArea textarea:focus,.stTextInput>div>div>input:focus{{border-color:{ACCENT}!important;box-shadow:0 0 0 3px rgba(59,130,246,0.12)!important;}}
.stTextArea textarea::placeholder,.stTextInput input::placeholder{{color:{TEXT3}!important;}}
[data-testid="stFileUploader"]{{background:{INPUT}!important;border:1.5px dashed {BORDER}!important;border-radius:12px!important;}}
[data-testid="stFileUploader"] *{{color:{TEXT2}!important;}}
[data-baseweb="select"]>div{{background:{INPUT}!important;border:1px solid {BORDER}!important;border-radius:10px!important;color:{TEXT}!important;cursor:pointer!important;}}
[data-baseweb="select"] span{{color:{TEXT}!important;}}
[data-baseweb="popover"]>div{{background:{CARD}!important;border:1px solid {BORDER}!important;border-radius:12px!important;}}
[data-baseweb="option"]{{background:{CARD}!important;color:{TEXT2}!important;cursor:pointer!important;}}
[data-baseweb="option"]:hover{{background:{BTN}!important;color:{ACCENT}!important;}}
.stTabs [data-baseweb="tab-list"]{{background:{INPUT}!important;border-radius:12px!important;padding:0.3rem!important;border:1px solid {BORDER}!important;gap:0.2rem!important;}}
.stTabs [data-baseweb="tab"]{{background:transparent!important;color:{TEXT3}!important;border-radius:8px!important;font-family:'Plus Jakarta Sans',sans-serif!important;font-weight:600!important;font-size:0.84rem!important;border:none!important;cursor:pointer!important;padding:0.5rem 1rem!important;}}
.stTabs [aria-selected="true"]{{background:linear-gradient(135deg,{ACCENT},{ACCENT2})!important;color:#fff!important;}}
details{{background:{CARD}!important;border:1px solid {BORDER}!important;border-radius:12px!important;overflow:hidden!important;margin-bottom:0.5rem!important;}}
details>summary{{color:{TEXT2}!important;font-family:'Plus Jakarta Sans',sans-serif!important;font-weight:600!important;padding:0.8rem 1rem!important;cursor:pointer!important;background:{CARD}!important;}}
[data-testid="stAlert"]{{border-radius:10px!important;font-family:'Plus Jakarta Sans',sans-serif!important;font-size:0.88rem!important;border:none!important;}}
[data-testid="metric-container"]{{background:{CARD}!important;border:1px solid {BORDER}!important;border-radius:12px!important;padding:0.8rem 1rem!important;}}
.stProgress>div{{background:{PROG_BG}!important;border-radius:100px!important;height:6px!important;}}
.stProgress>div>div{{background:linear-gradient(90deg,{ACCENT},{ACCENT2},#ec4899)!important;border-radius:100px!important;}}
.stRadio label{{background:{INPUT}!important;border:1px solid {BORDER}!important;border-radius:8px!important;padding:0.4rem 0.9rem!important;color:{TEXT2}!important;font-size:0.85rem!important;cursor:pointer!important;transition:all 0.15s!important;}}
.stRadio label:hover{{border-color:{ACCENT}!important;color:{ACCENT}!important;}}
hr{{border:none!important;border-top:1px solid {BORDER}!important;margin:1.5rem 0!important;}}
.sb-label{{font-family:'Space Mono',monospace;font-size:0.6rem;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:{TEXT3}!important;padding:1.2rem 0 0.4rem;border-bottom:1px solid {BORDER};margin-bottom:0.6rem;display:block;}}
.hero{{background:{HERO_BG};border:1px solid {HERO_BR};border-radius:20px;padding:2.5rem 3rem;margin:1.5rem 0;position:relative;overflow:hidden;}}
.hero::before{{content:'';position:absolute;top:-150px;right:-80px;width:400px;height:400px;background:radial-gradient(circle,rgba(59,130,246,0.07) 0%,transparent 65%);pointer-events:none;}}
.eyebrow{{font-family:'Space Mono',monospace;font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;color:{EYEBROW};margin-bottom:0.8rem;}}
.hero-title{{font-size:2.6rem;font-weight:800;line-height:1.15;background:{HTITLE};-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:0.8rem;letter-spacing:-0.02em;color:{TEXT};}}
.hero-sub{{font-size:1rem;color:{TEXT2};line-height:1.65;max-width:520px;font-weight:400;}}
.hero-stats{{display:flex;gap:2.5rem;margin-top:1.8rem;padding-top:1.5rem;border-top:1px solid {BORDER};}}
.stat-val{{font-family:'Space Mono',monospace;font-size:1.3rem;font-weight:700;color:{STAT_V};}}
.stat-lbl{{font-size:0.68rem;color:{TEXT3};text-transform:uppercase;letter-spacing:0.08em;}}
.fpills{{display:flex;flex-wrap:wrap;gap:0.4rem;margin:1rem 0 1.5rem;}}
.fp{{background:{PILL_BG};border:1px solid {BORDER};border-radius:100px;padding:0.3rem 0.85rem;font-size:0.73rem;color:{PILL_T};font-weight:500;}}
.sec{{display:flex;align-items:flex-start;gap:0.85rem;margin:2.2rem 0 1rem;}}
.sec-n{{width:34px;height:34px;background:linear-gradient(135deg,{ACCENT},{ACCENT2});border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:0.82rem;font-weight:700;color:#fff;flex-shrink:0;margin-top:2px;}}
.sec-title{{font-size:1.05rem;font-weight:700;color:{TEXT};}}
.sec-sub{{font-size:0.78rem;color:{TEXT3};margin-top:0.1rem;}}
.fc-card{{background:{FC_BG};border:1px solid {BORDER};border-left:3px solid {ACCENT};border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:0.8rem;}}
.fc-num{{font-family:'Space Mono',monospace;font-size:0.65rem;color:{TEXT3};letter-spacing:0.1em;margin-bottom:0.5rem;}}
.fc-q{{font-size:0.92rem;color:{TEXT2};font-weight:500;line-height:1.5;}}
.tutor-q{{background:{CARD};border:1px solid {BORDER};border-radius:14px 14px 14px 4px;padding:0.9rem 1.1rem;margin:0.5rem 0;color:{TEXT2};font-size:0.88rem;}}
.tutor-a{{background:{CARD};border:1px solid {BORDER};border-radius:14px 14px 4px 14px;padding:0.9rem 1.1rem;margin:0.5rem 0;color:#34d399;font-size:0.88rem;text-align:right;}}
.empty-state{{text-align:center;padding:3.5rem 1rem;border:1.5px dashed {BORDER};border-radius:18px;}}
.pomo-time{{font-family:'Space Mono',monospace;font-size:2rem;font-weight:700;text-align:center;color:{STAT_V};letter-spacing:0.05em;padding:0.3rem 0;}}
.key-live{{display:inline-block;width:7px;height:7px;border-radius:50%;background:#10b981;margin-right:5px;animation:blink 2s infinite;}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
.setup-card{{background:{SETUP};border:1px solid {HERO_BR};border-radius:22px;padding:2.5rem;text-align:center;position:relative;overflow:hidden;}}
.setup-card::before{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 50% 0%,rgba(59,130,246,0.08) 0%,transparent 60%);pointer-events:none;}}
.setup-title{{font-size:1.6rem;font-weight:800;background:{HTITLE};-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:0.5rem;}}
.setup-sub{{font-size:0.9rem;color:{TEXT2};margin-bottom:1.8rem;line-height:1.6;}}
.steps-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:1.8rem;}}
.step-box{{background:{CARD};border:1px solid {BORDER};border-radius:10px;padding:0.8rem 0.5rem;}}
.step-n{{font-family:'Space Mono',monospace;font-size:1rem;font-weight:700;color:{ACCENT};margin-bottom:0.3rem;}}
.step-t{{font-size:0.7rem;color:{TEXT2};line-height:1.3;}}
.tip-box{{background:rgba(245,158,11,0.08);border-left:3px solid #f59e0b;border-radius:0 8px 8px 0;padding:0.65rem 0.9rem;font-size:0.8rem;color:#fbbf24;text-align:left;margin-bottom:1rem;}}
.privacy-box{{background:rgba(59,130,246,0.06);border:1px solid rgba(59,130,246,0.15);border-radius:9px;padding:0.7rem 0.9rem;font-size:0.78rem;color:{TEXT3};margin-top:0.8rem;text-align:left;}}
</style>
""", unsafe_allow_html=True)

# ── API KEYS ──
builtin_keys = []
try:
    if "GOOGLE_API_KEYS" in st.secrets:
        builtin_keys = list(st.secrets["GOOGLE_API_KEYS"])
except Exception:
    builtin_keys = []

def get_all_keys():
    return st.session_state.user_api_keys + builtin_keys

def user_has_key():
    return len(st.session_state.user_api_keys) > 0

def validate_key(key):
    try:
        genai.configure(api_key=key)
        r = genai.GenerativeModel("models/gemini-2.5-flash").generate_content(
            "Say OK", generation_config={"max_output_tokens": 5})
        return bool(r and r.text)
    except Exception:
        return False

def generate(prompt, creativity=0.4):
    keys = get_all_keys()
    if not keys:
        return "NO_KEYS"
    for key in keys:
        try:
            genai.configure(api_key=key)
            resp = genai.GenerativeModel("models/gemini-2.5-flash").generate_content(
                prompt, generation_config={"temperature": creativity, "max_output_tokens": 2000})
            if resp and resp.text:
                return resp.text.strip()
        except Exception:
            time.sleep(0.8)
    return "QUOTA_EXCEEDED"

def quota_ui():
    st.error("⚠️ API quota exhausted.")
    with st.expander("🔑 Add a free key to continue", expanded=True):
        st.markdown("**Get free key →** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)")
        nk = st.text_input("Paste key:", type="password", placeholder="AIzaSy...", key=f"qk_{len(st.session_state.history)}")
        if st.button("➕ Add Key & Retry", type="primary", use_container_width=True):
            if nk.strip() and nk.strip() not in st.session_state.user_api_keys:
                st.session_state.user_api_keys.append(nk.strip())
                st.success("✅ Added! Try again.")
                st.rerun()

# ── FILE READERS ──
def read_pdf(f):
    return "\n".join([p.extract_text() for p in PyPDF2.PdfReader(f).pages if p.extract_text()])
def read_docx(f):
    return "\n".join([p.text for p in Document(f).paragraphs if p.text.strip()])
def read_txt(f):
    return f.read().decode("utf-8")

# ── PROMPTS ──
FORMATS = {
    "Notes":       "Write structured academic notes with clear headings and bullets. Max 400 words.\n",
    "Flashcards":  "Generate exactly 5 flashcards.\nFormat:\nFlashcard 1\nQuestion:\nAnswer:\n\nFlashcard 2\nQuestion:\nAnswer:\n",
    "Quiz":        "Generate exactly 5 MCQ questions.\nFormat:\nQuestion 1:\nA.\nB.\nC.\nD.\nCorrect Answer: X\n\nQuestion 2:\n",
    "Reflection":  "Generate exactly 5 deep reflection questions. Numbered list.\n",
    "Study Plan":  "Generate a 5-step study plan with timelines. Numbered.\n",
    "Key Concepts":"Extract 7 key concepts. Bold name, one-line definition, why it matters.\n",
    "Exam Mode":   "Write full exam: 3 MCQ (Correct Answer), 2 Fill blank (Answer:), 2 Short answer (Model Answer:).\n",
    "TL;DR":       "Summarize in exactly 5 bullet points. Max 15 words each.\n",
    "Feynman":     "Evaluate student explanation: what correct, what missing, score /10, how to improve.\n",
    "Socratic":    "Ask ONE deep Socratic question. Not factual. Thought-provoking.\n",
    "Mind Map":    "Text mind map: 1 central idea, 5 branches, 2-3 sub-points each. Use indentation.\n",
    "Mnemonics":   "Create 3 mnemonics or acronyms for key concepts.\n",
    "ELI5":        "Explain like I am 10. Simple words, fun analogies. Max 200 words.\n",
}

def build_prompt(text, difficulty, persona, fmt):
    trimmed = len(text) > 3000
    text = text[:3000]
    base = f"Content:\n{text}\n\nDifficulty:{difficulty}\nPersona:{persona}\n\nRules:\n- Output ONLY the requested format\n- No preamble\n- Complete sentences\n\n"
    return base + FORMATS.get(fmt, FORMATS["Notes"]), trimmed

def gen_heading(txt):
    r = generate(f"Short heading, max 7 words, no quotes, no punctuation.\nInput: {txt}", 0.2)
    return r.strip() if r not in ("QUOTA_EXCEEDED","NO_KEYS") else "Study Notes"

def run_gen(fmt, content, manual, difficulty, persona, creativity, save_as="output"):
    if not content:
        st.warning("⚠️ Enter a topic or upload a file first.")
        return False
    p, trimmed = build_prompt(content, difficulty, persona, fmt)
    if trimmed: st.caption("⚠️ Content trimmed to 3000 chars")
    with st.spinner(f"Generating {fmt}..."):
        r = generate(p, creativity)
    if r in ("QUOTA_EXCEEDED","NO_KEYS"):
        quota_ui(); return False
    if save_as == "notes":
        st.session_state.notes_content  = r
        st.session_state.notes_heading  = gen_heading(manual if manual.strip() else "Document")
        st.session_state.generated_output  = None
        st.session_state.generated_heading = None
        st.session_state.quiz_score = None
    else:
        st.session_state.generated_output  = r
        st.session_state.generated_heading = fmt
    st.session_state.history.append({
        "ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "format": fmt, "topic": (manual or "Document")[:50], "output": r,
    })
    return True

# ── SETUP SCREEN ──
def show_setup():
    # Force page background + hide sidebar
    st.markdown(f"""
<style>
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"] > .main,.block-container{{
    background-color:{BG}!important;background:{BG}!important;
}}
[data-testid="stSidebar"]{{display:none!important;}}
.setup-page{{max-width:560px;margin:0 auto;padding:2rem 1rem 4rem;}}
.setup-logo-name{{font-family:'Plus Jakarta Sans',sans-serif;font-size:1.5rem;font-weight:800;
    background:linear-gradient(135deg,{TEXT},{ACCENT},#a78bfa);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
.setup-logo-sub{{font-family:'Space Mono',monospace;font-size:0.6rem;color:{TEXT3};
    letter-spacing:0.18em;text-transform:uppercase;margin-top:0.2rem;}}
.setup-main-card{{background:{CARD};border:1px solid {BORDER};border-radius:22px;
    padding:2.2rem 2.2rem 1.8rem;width:100%;margin-bottom:0;}}
.setup-badge{{display:inline-block;background:rgba(59,130,246,0.1);
    border:1px solid rgba(59,130,246,0.2);color:{ACCENT};
    font-family:'Space Mono',monospace;font-size:0.62rem;letter-spacing:0.14em;
    text-transform:uppercase;padding:0.3rem 0.9rem;border-radius:100px;}}
.setup-card-title{{font-size:1.45rem;font-weight:800;
    background:linear-gradient(135deg,{TEXT},{ACCENT},#a78bfa);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-clip:text;margin:0.8rem 0 0.5rem;letter-spacing:-0.02em;}}
.setup-card-sub{{font-size:0.87rem;color:{TEXT2};line-height:1.65;margin-bottom:1.6rem;}}
.setup-steps{{display:grid;grid-template-columns:repeat(4,1fr);gap:0.55rem;margin-bottom:1.4rem;}}
.setup-step{{background:{BG};border:1px solid {BORDER};border-radius:10px;
    padding:0.75rem 0.4rem;text-align:center;}}
.setup-step-n{{font-family:'Space Mono',monospace;font-size:0.95rem;font-weight:700;color:{ACCENT};}}
.setup-step-t{{font-size:0.67rem;color:{TEXT2};margin-top:0.25rem;line-height:1.3;}}
.setup-tip{{background:rgba(245,158,11,0.07);border-left:3px solid #f59e0b;
    border-radius:0 8px 8px 0;padding:0.55rem 0.85rem;font-size:0.77rem;color:#fbbf24;}}
.setup-cta{{display:inline-block;background:linear-gradient(135deg,{ACCENT},{ACCENT2});
    color:#fff!important;font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
    font-size:0.9rem;padding:0.8rem 2rem;border-radius:12px;text-decoration:none!important;
    box-shadow:0 4px 20px rgba(59,130,246,0.3);}}
.setup-hint{{font-size:0.72rem;color:{TEXT3};margin-top:0.5rem;}}
.setup-privacy{{background:rgba(59,130,246,0.06);border:1px solid rgba(59,130,246,0.15);
    border-radius:10px;padding:0.7rem 0.9rem;font-size:0.77rem;color:{TEXT3};margin-top:0.8rem;}}
.setup-unlock-title{{font-size:0.76rem;font-weight:700;color:{TEXT2};margin:1.2rem 0 0.5rem;}}
.setup-pills{{display:flex;flex-wrap:wrap;gap:0.35rem;}}
.setup-pill{{background:{BG};border:1px solid {BORDER};border-radius:100px;
    padding:0.22rem 0.7rem;font-size:0.7rem;color:{TEXT2};}}
</style>
""", unsafe_allow_html=True)

    # Theme toggle
    _, tc = st.columns([10,1])
    with tc:
        if st.button("🌙" if not dark else "☀️", help="Toggle theme"):
            st.session_state.dark_mode = not dark
            st.rerun()

    # Logo
    st.markdown("""
<div class="setup-page">
<div style="text-align:center;margin-bottom:1.8rem;">
    <div style="font-size:2.8rem;margin-bottom:0.4rem;">🧠</div>
    <div class="setup-logo-name">LearnFlow AI</div>
    <div class="setup-logo-sub">Study Companion</div>
</div>
<div class="setup-main-card">
    <div style="text-align:center;">
        <span class="setup-badge">✦ Free Setup — 2 Minutes</span>
    </div>
    <div class="setup-card-title" style="text-align:center;">Connect your free AI key</div>
    <div class="setup-card-sub" style="text-align:center;">
        LearnFlow AI runs on Google Gemini — 100% free, no credit card needed.<br>
        Get your key in 2 minutes and start learning instantly.
    </div>
    <div class="setup-steps">
        <div class="setup-step"><div class="setup-step-n">01</div><div class="setup-step-t">Open Google AI Studio</div></div>
        <div class="setup-step"><div class="setup-step-n">02</div><div class="setup-step-t">Sign in with Google</div></div>
        <div class="setup-step"><div class="setup-step-n">03</div><div class="setup-step-t">Click Create API Key</div></div>
        <div class="setup-step"><div class="setup-step-n">04</div><div class="setup-step-t">Paste below and go!</div></div>
    </div>
    <div class="setup-tip">⚡ Keys look like: <strong>AIzaSyAbc123...</strong> (39 characters)</div>
    <div style="text-align:center;margin:1.5rem 0 0.5rem;">
        <a class="setup-cta" href="https://aistudio.google.com/app/apikey" target="_blank">🔑 Get My Free API Key →</a>
        <div class="setup-hint">Opens Google AI Studio in a new tab</div>
    </div>
</div>
</div>
""", unsafe_allow_html=True)

    # Input + button
    _, mc, _ = st.columns([1,2,1])
    with mc:
        key_in = st.text_input("Paste your Gemini API key:", type="password",
                               placeholder="AIzaSy...", key="setup_key")
        if st.button("🚀 Validate & Start Learning", type="primary", use_container_width=True):
            k = key_in.strip()
            if not k:
                st.warning("⚠️ Paste your API key above first.")
            elif not k.startswith("AIza"):
                st.warning("⚠️ Invalid — Gemini keys always start with AIza")
            elif len(k) < 30:
                st.warning("⚠️ Too short — copy the full key")
            else:
                with st.spinner("🔍 Validating with Google..."):
                    valid = validate_key(k)
                if valid:
                    st.session_state.user_api_keys = [k]
                    st.balloons()
                    st.success("✅ Key validated! Welcome to LearnFlow AI 🎉")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("❌ Google rejected this key. Check you copied it fully.")

        st.markdown("""
<div class="setup-privacy">
    🔒 <strong>Your privacy:</strong> Key stored only in your browser session.
    Never sent to our servers. Auto-deleted when you close this tab.
</div>
<div class="setup-unlock-title">🎓 Everything you unlock:</div>
<div class="setup-pills">
    <span class="setup-pill">📝 Smart Notes</span>
    <span class="setup-pill">🎴 Flashcards</span>
    <span class="setup-pill">❓ AI Quiz</span>
    <span class="setup-pill">🧪 Feynman Check</span>
    <span class="setup-pill">🤖 Socratic Tutor</span>
    <span class="setup-pill">🎓 Exam Mode</span>
    <span class="setup-pill">🧠 Mind Map</span>
    <span class="setup-pill">💡 Mnemonics</span>
    <span class="setup-pill">⚡ TL;DR</span>
    <span class="setup-pill">👶 ELI5</span>
    <span class="setup-pill">⏱ Pomodoro</span>
    <span class="setup-pill">🌙 Dark / Light</span>
</div>
""", unsafe_allow_html=True)

# ── GATE ──
if not user_has_key():
    show_setup()
    st.stop()

# ── SIDEBAR ──
with st.sidebar:
    lc, tc = st.columns([4,1])
    with lc:
        st.markdown(f"""
        <div style="padding:0.3rem 0 0.8rem;">
            <div style="font-size:1rem;font-weight:800;color:{TEXT};font-family:'Plus Jakarta Sans',sans-serif;">
                🧠 LearnFlow <span style="color:{ACCENT};">AI</span></div>
            <div style="font-family:'Space Mono',monospace;font-size:0.58rem;color:{TEXT3};letter-spacing:0.14em;margin-top:0.2rem;">
                STUDY COMPANION</div>
        </div>""", unsafe_allow_html=True)
    with tc:
        if st.button("🌙" if dark else "☀️", help="Toggle theme", use_container_width=True):
            st.session_state.dark_mode = not dark
            st.rerun()

    st.markdown(f'<div style="border-top:1px solid {BORDER};margin-bottom:0.3rem;"></div>', unsafe_allow_html=True)

    st.markdown('<span class="sb-label">⚙ Learning Settings</span>', unsafe_allow_html=True)
    difficulty = st.selectbox("Difficulty", ["Beginner","Intermediate","Advanced"], label_visibility="collapsed")
    persona    = st.selectbox("Persona", [
        "🎓 University Professor","👩‍🏫 School Teacher","🧒 Child-Friendly",
        "🔬 Scientist","📊 Analytical","📝 Exam-Oriented","💪 Motivational",
    ], label_visibility="collapsed")
    st.markdown(f'<div style="font-size:0.75rem;color:{TEXT2};margin:0.5rem 0 0.1rem;">Creativity</div>', unsafe_allow_html=True)
    creativity = st.slider("", 0.1, 1.0, 0.4, label_visibility="collapsed")

    st.markdown('<span class="sb-label">⏱ Pomodoro</span>', unsafe_allow_html=True)
    pc1, pc2 = st.columns([3,1])
    with pc1: pmin = st.selectbox("", [25,10,15,30,45,60], label_visibility="collapsed")
    with pc2:
        if st.button("▶", use_container_width=True):
            st.session_state.timer_start    = time.time()
            st.session_state.timer_duration = pmin * 60
    if st.session_state.timer_start:
        rem = st.session_state.timer_duration - (time.time() - st.session_state.timer_start)
        if rem > 0:
            st.markdown(f'<div class="pomo-time">{int(rem//60):02d}:{int(rem%60):02d}</div>', unsafe_allow_html=True)
            st.progress(1 - rem/st.session_state.timer_duration)
        else:
            st.error("🔔 Break time!")
            if st.button("Reset Timer", use_container_width=True):
                st.session_state.timer_start = None; st.rerun()

    st.markdown('<span class="sb-label">🔑 API Keys</span>', unsafe_allow_html=True)
    uk = len(st.session_state.user_api_keys)
    st.markdown(f'<span class="key-live"></span><span style="font-size:0.82rem;color:#10b981;">{uk} personal key(s) active</span>', unsafe_allow_html=True)
    with st.expander("➕ Add / Manage Keys"):
        st.caption("👉 [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)")
        nk = st.text_input("", type="password", placeholder="AIzaSy...", key="sb_key", label_visibility="collapsed")
        if st.button("Add Key", use_container_width=True, key="sb_add"):
            if nk.strip() and nk.strip() not in st.session_state.user_api_keys:
                st.session_state.user_api_keys.append(nk.strip()); st.success("✅ Added!"); st.rerun()
        if st.session_state.user_api_keys:
            if st.button("🗑 Remove All Keys", use_container_width=True, key="sb_rm"):
                st.session_state.user_api_keys = []; st.rerun()

    st.markdown('<span class="sb-label">📊 Session</span>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    with s1: st.metric("Generated", len(st.session_state.history))
    with s2: st.metric("Notes", 1 if st.session_state.notes_content else 0)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑 Reset Session", use_container_width=True):
        saved = st.session_state.user_api_keys; mode = st.session_state.dark_mode
        for k,v in defaults.items(): st.session_state[k] = v
        st.session_state.user_api_keys = saved; st.session_state.dark_mode = mode
        st.rerun()

# ── HERO ──
st.markdown(f"""
<div class="hero">
    <div class="eyebrow">✦ Powered by Google Gemini 2.5 Flash</div>
    <div class="hero-title" style="color:#93c5fd;">Learn Smarter.<br>Not Harder.</div>
    <div class="hero-sub">Transform any topic or document into notes, flashcards, quizzes and more — in seconds.</div>
    <div class="hero-stats">
        <div><div class="stat-val">10+</div><div class="stat-lbl">AI Features</div></div>
        <div><div class="stat-val">∞</div><div class="stat-lbl">Topics</div></div>
        <div><div class="stat-val">Free</div><div class="stat-lbl">Forever</div></div>
    </div>
</div>
<div class="fpills">
    <span class="fp">📝 Smart Notes</span>
    <span class="fp">🎴 Flashcards</span>
    <span class="fp">❓ AI Quiz</span>
    <span class="fp">🧪 Feynman Check</span>
    <span class="fp">🤖 Socratic Tutor</span>
    <span class="fp">📅 Study Plan</span>
    <span class="fp">🎓 Exam Mode</span>
    <span class="fp">🧠 Mind Map</span>
    <span class="fp">💡 Mnemonics</span>
    <span class="fp">⚡ TL;DR</span>
    <span class="fp">👶 ELI5</span>
    <span class="fp">⏱ Pomodoro</span>
</div>
""", unsafe_allow_html=True)

# ── STEP 1 ──
st.markdown(f"""<div class="sec"><div class="sec-n">1</div>
<div><div class="sec-title">Enter Topic or Upload File</div>
<div class="sec-sub">Type any topic, paste notes, or upload PDF / DOCX / TXT</div></div></div>""", unsafe_allow_html=True)

uploaded = st.file_uploader("", type=["pdf","docx","txt"], label_visibility="collapsed")
file_text = ""
if uploaded:
    with st.spinner("Reading file..."):
        try:
            ft = uploaded.type
            if ft == "application/pdf": file_text = read_pdf(uploaded)
            elif "document" in ft:      file_text = read_docx(uploaded)
            else:                        file_text = read_txt(uploaded)
            st.success(f"✅ **{uploaded.name}** — {len(file_text):,} characters loaded")
        except Exception as e:
            st.error(f"❌ Failed to read: {e}")

manual = st.text_area("", height=110, label_visibility="collapsed",
    placeholder="e.g. Photosynthesis · Newton's Laws · French Revolution · Machine Learning...")

if file_text and manual.strip(): content = f"Instruction:\n{manual.strip()}\n\nDocument:\n{file_text}"
elif file_text:                   content = file_text
else:                              content = manual.strip()

G = dict(content=content, manual=manual, difficulty=difficulty, persona=persona, creativity=creativity)

# ── STEP 2 ──
st.markdown(f"""<div class="sec"><div class="sec-n">2</div>
<div><div class="sec-title">Read & Learn</div>
<div class="sec-sub">Start with Notes — then explore summaries, concepts and memory aids — start here!</div></div></div>""", unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
with c1:
    if st.button("📝 Notes", use_container_width=True, type="primary"):
        if run_gen("Notes", save_as="notes", **G): st.success("✅ Notes ready!")
with c2:
    if st.button("⚡ TL;DR Summary", use_container_width=True):
        if content:
            p,_ = build_prompt(content, difficulty, persona, "TL;DR")
            with st.spinner("Summarizing..."): r = generate(p, 0.3)
            if r in ("QUOTA_EXCEEDED","NO_KEYS"): quota_ui()
            else: st.session_state.tldr = r; st.success("✅ Done!")
        else: st.warning("Enter a topic first.")
with c3:
    if st.button("🔑 Key Concepts", use_container_width=True):
        if run_gen("Key Concepts", **G): st.success("✅ Done!")
with c4:
    if st.button("💡 Mnemonics", use_container_width=True):
        if run_gen("Mnemonics", **G): st.success("✅ Done!")

c5,c6,c7 = st.columns(3)
with c5:
    if st.button("🧠 Mind Map", use_container_width=True):
        if run_gen("Mind Map", **G): st.success("✅ Done!")
with c6:
    if st.button("😊 ELI5 (Explain Simply)", use_container_width=True):
        if run_gen("ELI5", **G): st.success("✅ Done!")
with c7:
    if st.button("📅 Study Plan", use_container_width=True):
        if run_gen("Study Plan", **G): st.success("✅ Done!")

if st.session_state.tldr:
    st.info(f"⚡ **TL;DR**\n\n{st.session_state.tldr}")

if st.session_state.notes_content:
    with st.expander(f"📘 {st.session_state.notes_heading}", expanded=True):
        st.markdown(st.session_state.notes_content)
        st.download_button("📥 Download Notes", data=st.session_state.notes_content,
            file_name=f"Notes_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", mime="text/plain")

S2 = ["Key Concepts","Mnemonics","Mind Map","ELI5","Study Plan"]
if st.session_state.generated_output and st.session_state.generated_heading in S2:
    with st.expander(f"📄 {st.session_state.generated_heading}", expanded=True):
        st.markdown(st.session_state.generated_output)
        st.download_button("📥 Download", data=st.session_state.generated_output,
            file_name=f"{st.session_state.generated_heading}.txt", mime="text/plain", key="dl_s2")

# ── STEP 3 ──
if st.session_state.notes_content:
    st.markdown(f"""<div class="sec"><div class="sec-n">3</div>
    <div><div class="sec-title">Test Your Knowledge</div>
    <div class="sec-sub">Flashcards, Quiz, Reflection, Feynman Check & your AI Tutor</div></div></div>""", unsafe_allow_html=True)

    tab1,tab2,tab3,tab4 = st.tabs(["🎴  Flashcards","❓  Quiz","🤔  Reflect & Feynman","🤖  AI Tutor"])

    with tab1:
        st.caption("Reveal answers one by one to test your memory.")
        if st.button("Generate Flashcards", use_container_width=True, type="primary", key="fc_gen"):
            run_gen("Flashcards", **G)
        if st.session_state.generated_heading == "Flashcards" and st.session_state.generated_output:
            idx = 1
            for blk in st.session_state.generated_output.split("Flashcard"):
                if not blk.strip(): continue
                parts = blk.split("Answer:")
                if len(parts) == 2:
                    q = parts[0].replace("Question:","").strip().lstrip("0123456789. \n")
                    a = parts[1].strip()
                    rk = f"fc_{idx}"
                    if rk not in st.session_state: st.session_state[rk] = False
                    st.markdown(f'<div class="fc-card"><div class="fc-num">CARD {idx} / 5</div><div class="fc-q">{q}</div></div>', unsafe_allow_html=True)
                    if st.button("👁 Reveal" if not st.session_state[rk] else "🙈 Hide", key=f"fcb_{idx}"):
                        st.session_state[rk] = not st.session_state[rk]
                    if st.session_state[rk]: st.success(f"**Answer:** {a}")
                    st.markdown("<br>", unsafe_allow_html=True)
                    idx += 1

    with tab2:
        st.caption("Answer all 5 questions then submit for your score.")
        if st.button("Generate Quiz", use_container_width=True, type="primary", key="qz_gen"):
            run_gen("Quiz", **G); st.session_state.quiz_score = None
        if st.session_state.generated_heading == "Quiz" and st.session_state.generated_output:
            blocks = re.split(r'\*?\*?Question\s*\d+[\.\:]?\*?\*?', st.session_state.generated_output, flags=re.IGNORECASE)
            blocks = [b.strip() for b in blocks if b.strip()]
            u_ans, c_ans, qi = [], [], 1
            for blk in blocks:
                lines = [l.strip() for l in blk.split("\n") if l.strip()]
                if not lines: continue
                qtxt  = lines[0].lstrip("0123456789:.*) ")
                opts  = [l for l in lines if re.match(r'^[A-Da-d][\.\)]\s+.+', l)]
                cline = [l for l in lines if re.search(r'correct\s*answer', l, re.IGNORECASE)]
                if opts and qtxt and len(opts) >= 2:
                    st.markdown(f"**Q{qi}.** {qtxt}")
                    sel = st.radio("", opts, key=f"q_{qi}", index=None, label_visibility="collapsed")
                    u_ans.append(sel)
                    if cline:
                        m = re.search(r':\s*([A-Da-d])', cline[0])
                        if m: c_ans.append(m.group(1).upper())
                    st.markdown("---"); qi += 1
            if u_ans:
                if st.button("📝 Submit Quiz", use_container_width=True, type="primary"):
                    if None in u_ans: st.warning("⚠️ Answer all questions first!")
                    else:
                        score = sum(1 for i in range(len(c_ans))
                            if u_ans[i] and re.match(r'^'+c_ans[i], u_ans[i].strip(), re.IGNORECASE))
                        st.session_state.quiz_score = score
                if st.session_state.quiz_score is not None:
                    sc=st.session_state.quiz_score; tot=len(c_ans) or 1
                    pct=int(sc/tot*100); rd=min(100,pct+10)
                    st.markdown("---")
                    m1,m2,m3 = st.columns(3)
                    with m1: st.metric("Score",f"{sc}/{tot}")
                    with m2: st.metric("Percentage",f"{pct}%")
                    with m3: st.metric("Exam Ready",f"{rd}%")
                    st.progress(rd/100)
                    if pct>=80:   st.success("🎉 Excellent! You are exam ready.")
                    elif pct>=50: st.warning("👍 Good effort — review weak areas.")
                    else:          st.error("📚 Keep going — re-read notes and retry.")

    with tab3:
        rc1,rc2 = st.columns(2)
        with rc1:
            if st.button("Reflection Questions", use_container_width=True, key="ref_gen"):
                run_gen("Reflection", **G)
        with rc2:
            if st.button("Generate Exam Paper", use_container_width=True, key="exam_gen"):
                run_gen("Exam Mode", **G)
        if st.session_state.generated_heading in ["Reflection","Exam Mode"] and st.session_state.generated_output:
            st.markdown(st.session_state.generated_output)
            st.download_button("📥 Download", data=st.session_state.generated_output,
                file_name=f"{st.session_state.generated_heading}.txt", mime="text/plain", key="dl_ref")
        st.markdown("---")
        st.markdown("#### 🧪 Feynman Technique Checker")
        st.caption("Explain the topic in your own words. AI scores your understanding.")
        fi = st.text_area("Your explanation:", height=120, key="feynman_ta",
            placeholder="In simple terms, this topic is about...")
        if st.button("✅ Analyse My Understanding", use_container_width=True, type="primary"):
            if not fi.strip(): st.warning("Write your explanation first!")
            else:
                cp = f"Topic: {manual if manual.strip() else 'uploaded content'}\n\nStudent explanation:\n{fi}\n\n"
                fp,_ = build_prompt(cp, difficulty, persona, "Feynman")
                with st.spinner("Analysing..."): fr = generate(fp, 0.3)
                if fr in ("QUOTA_EXCEEDED","NO_KEYS"): quota_ui()
                else: st.session_state.feynman_feedback = fr
        if st.session_state.feynman_feedback:
            st.markdown(st.session_state.feynman_feedback)

    with tab4:
        st.caption("AI asks deep Socratic questions — challenges real understanding, not just memory.")
        if st.button("🤔 Ask Me a Question", use_container_width=True, type="primary"):
            sp,_ = build_prompt(content, difficulty, "Analytical", "Socratic")
            with st.spinner("Thinking..."): sr = generate(sp, 0.6)
            if sr in ("QUOTA_EXCEEDED","NO_KEYS"): quota_ui()
            else: st.session_state.tutor_history.append({"role":"tutor","msg":sr})
        for msg in st.session_state.tutor_history:
            if msg["role"]=="tutor":
                st.markdown(f'<div class="tutor-q">🤖 <strong>Tutor:</strong> {msg["msg"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="tutor-a">👤 <strong>You:</strong> {msg["msg"]}</div>', unsafe_allow_html=True)
        if st.session_state.tutor_history:
            reply = st.text_input("Your answer:", key="tutor_in", placeholder="Type your answer...")
            tc1,tc2 = st.columns([4,1])
            with tc1:
                if st.button("Send ➡️", use_container_width=True):
                    if reply.strip():
                        st.session_state.tutor_history.append({"role":"student","msg":reply})
                        fup=f"Topic:{manual or 'the content'}\nStudent answered:{reply}\nAsk deeper Socratic follow-up. Short."
                        with st.spinner("Thinking..."): fur=generate(fup, 0.6)
                        if fur not in ("QUOTA_EXCEEDED","NO_KEYS"):
                            st.session_state.tutor_history.append({"role":"tutor","msg":fur})
                        st.rerun()
            with tc2:
                if st.button("Reset", use_container_width=True):
                    st.session_state.tutor_history=[]; st.rerun()

    # ── STEP 4 ──
    st.markdown(f"""<div class="sec"><div class="sec-n">4</div>
    <div><div class="sec-title">Exam Mode</div>
    <div class="sec-sub">Full simulated exam — MCQs, fill in blanks, short answers all in one</div></div></div>""", unsafe_allow_html=True)
    if st.button("🎓 Generate Full Exam Paper", use_container_width=True, type="primary"):
        if run_gen("Exam Mode", **G): st.success("✅ Exam paper ready! Good luck 🍀")
    if st.session_state.generated_heading == "Exam Mode" and st.session_state.generated_output:
        st.markdown(st.session_state.generated_output)
        st.download_button("📥 Download Exam Paper", data=st.session_state.generated_output,
            file_name=f"Exam_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", mime="text/plain")

else:
    st.markdown(f"""
    <div class="empty-state">
        <div style="font-size:2.8rem;margin-bottom:0.8rem;">📖</div>
        <div style="font-size:0.95rem;font-weight:700;color:{TEXT2};">Generate Notes first to unlock all testing features</div>
        <div style="font-size:0.8rem;color:{TEXT3};margin-top:0.3rem;">Enter a topic above and click 📝 Generate Notes</div>
    </div>
    """, unsafe_allow_html=True)

# ── HISTORY ──
if st.session_state.history:
    st.markdown(f"""<div class="sec">
    <div class="sec-n" style="background:linear-gradient(135deg,#0f766e,#0891b2);">📜</div>
    <div><div class="sec-title">Session History</div>
    <div class="sec-sub">All generated content from this session</div></div></div>""", unsafe_allow_html=True)
    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"**{item['format']}** — {item['topic']} | {item['ts']}"):
            st.markdown(item.get("output",""))
            st.download_button("📥 Download", data=item.get("output",""),
                file_name=f"{item['format']}_{i}.txt", mime="text/plain", key=f"hl_{i}")

# ── AUTO-OPEN SIDEBAR ──
st.markdown("""
<script>
(function() {
    function openSidebar() {
        var btn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
        if (btn) { btn.click(); }
    }
    setTimeout(openSidebar, 500);
    setTimeout(openSidebar, 1500);
})();
</script>
""", unsafe_allow_html=True)