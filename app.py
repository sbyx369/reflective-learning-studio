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
    BG      = "#06080f"
    SB      = "#09111f"
    CARD    = "#0d1726"
    BORDER  = "#1e3358"
    TEXT    = "#e8eeff"
    TEXT2   = "#7b9cc8"
    TEXT3   = "#3d6090"
    ACCENT  = "#3b82f6"
    ACCENT2 = "#6366f1"
    INPUT   = "#0a1220"
    BTN     = "#0e1c35"
    BTN_T   = "#7aaad8"
    HERO    = "linear-gradient(135deg,#060e20 0%,#0a1530 50%,#060b1a 100%)"
    HTITLE  = "#93c5fd"
    HSUB    = "#5a82b0"
    PILL_BG = "#0a1428"
    PILL_T  = "#4a7aaa"
    POMO_C  = "#60a5fa"
    STAT_V  = "#60a5fa"
    GREEN   = "#10b981"
    EYEBROW = "#2a5898"
else:
    BG      = "#f0f4ff"
    SB      = "#e0eaf8"
    CARD    = "#ffffff"
    BORDER  = "#b8cef0"
    TEXT    = "#0d1a35"
    TEXT2   = "#2a4070"
    TEXT3   = "#5a78a8"
    ACCENT  = "#2563eb"
    ACCENT2 = "#4338ca"
    INPUT   = "#ffffff"
    BTN     = "#eef2ff"
    BTN_T   = "#2563eb"
    HERO    = "linear-gradient(135deg,#ddeaff 0%,#eef3ff 50%,#e8e4ff 100%)"
    HTITLE  = "#1e40af"
    HSUB    = "#3a5a90"
    PILL_BG = "#eef2ff"
    PILL_T  = "#3a5aaa"
    POMO_C  = "#2563eb"
    STAT_V  = "#2563eb"
    GREEN   = "#059669"
    EYEBROW = "#4a78cc"

# ═══════════════════════════════════════════════════════════
# GLOBAL CSS
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

/* ── HIDE STREAMLIT CHROME (Kept Sidebar Toggles Visible) ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {{
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 10px; }}

/* ── MAIN CONTENT ── */
.block-container {{
    max-width: 1000px !important;
    margin: 0 auto !important;
    padding: 1.5rem 2rem 6rem !important;
    background: {BG} !important;
}}

/* ══════════════════════════════
   SIDEBAR
══════════════════════════════ */
[data-testid="stSidebar"] {{
    background: {SB} !important;
    border-right: 1px solid {BORDER} !important;
    min-width: 260px !important;
    max-width: 280px !important;
}}
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {{
    background: {SB} !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding: 1rem 0.9rem !important;
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

/* Sidebar selectbox */
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: {INPUT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {TEXT} !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div[class*="singleValue"] {{
    color: {TEXT} !important;
}}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {{
    background: {BTN} !important;
    color: {BTN_T} !important;
    border: 1px solid {BORDER} !important;
    font-size: 0.82rem !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    border-color: {ACCENT} !important;
    color: {ACCENT} !important;
}}

/* Sidebar expander */
[data-testid="stSidebar"] details {{
    background: {INPUT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] details summary {{
    color: {TEXT2} !important;
    background: {INPUT} !important;
    font-size: 0.83rem !important;
    padding: 0.6rem 0.8rem !important;
    cursor: pointer !important;
}}

/* Sidebar text input */
[data-testid="stSidebar"] .stTextInput > div > div > input {{
    background: {INPUT} !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
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
[data-testid="stSidebar"] [data-testid="metric-container"] label {{
    color: {TEXT3} !important;
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}}

/* Slider */
[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] {{
    color: {ACCENT} !important;
    font-size: 0.75rem !important;
}}

/* ══════════════════════════════
   BUTTONS
══════════════════════════════ */
.stButton > button {{
    background: {BTN} !important;
    color: {BTN_T} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
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

/* ── CURSOR ── */
button, [role="button"], label, summary,
[data-baseweb="tab"], [data-baseweb="option"],
[data-testid="stFileUploader"] * {{ cursor: pointer !important; }}
[data-baseweb="select"] input {{
    caret-color: transparent !important;
    cursor: pointer !important;
    pointer-events: none !important;
}}

/* ── INPUTS ── */
.stTextArea textarea,
.stTextInput > div > div > input {{
    background: {INPUT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.15s !important;
}}
.stTextArea textarea:focus,
.stTextInput > div > div > input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
    outline: none !important;
}}
.stTextArea textarea::placeholder,
.stTextInput input::placeholder {{ color: {TEXT3} !important; }}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {{
    background: {INPUT} !important;
    border: 1.5px dashed {BORDER} !important;
    border-radius: 12px !important;
    transition: border-color 0.15s !important;
}}
[data-testid="stFileUploader"]:hover {{ border-color: {ACCENT} !important; }}
[data-testid="stFileUploader"] * {{ color: {TEXT2} !important; }}

/* ── SELECTBOX ── */
[data-baseweb="select"] > div {{
    background: {INPUT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
    cursor: pointer !important;
}}
[data-baseweb="select"] span {{ color: {TEXT} !important; }}
[data-baseweb="popover"] > div {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
}}
[data-baseweb="option"] {{
    background: {CARD} !important;
    color: {TEXT2} !important;
    cursor: pointer !important;
    font-size: 0.88rem !important;
}}
[data-baseweb="option"]:hover {{
    background: {BTN} !important;
    color: {ACCENT} !important;
}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {INPUT} !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid {BORDER} !important;
    gap: 3px !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {TEXT3} !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    border: none !important;
    cursor: pointer !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.15s !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {ACCENT}, {ACCENT2}) !important;
    color: #ffffff !important;
}}

/* ── EXPANDER ── */
details {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    margin-bottom: 0.5rem !important;
}}
details > summary {{
    color: {TEXT2} !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.75rem 1rem !important;
    cursor: pointer !important;
    background: {CARD} !important;
    list-style: none !important;
}}
details > summary::-webkit-details-marker {{ display: none; }}

/* ── ALERTS ── */
[data-testid="stAlert"] {{
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.88rem !important;
}}

/* ── METRICS ── */
[data-testid="metric-container"] {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    padding: 0.8rem 1rem !important;
}}
[data-testid="stMetricValue"] {{
    color: {STAT_V} !important;
    font-family: 'JetBrains Mono', monospace !important;
}}
[data-testid="metric-container"] label {{
    color: {TEXT3} !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}}

/* ── PROGRESS ── */
.stProgress > div {{
    background: {BORDER} !important;
    border-radius: 100px !important;
    height: 5px !important;
}}
.stProgress > div > div {{
    background: linear-gradient(90deg, {ACCENT}, {ACCENT2}) !important;
    border-radius: 100px !important;
}}

/* ── RADIO ── */
.stRadio [data-testid="stMarkdownContainer"] p {{
    font-size: 0.88rem !important;
    color: {TEXT2} !important;
}}

/* ── DIVIDER ── */
hr {{
    border: none !important;
    border-top: 1px solid {BORDER} !important;
    margin: 1.2rem 0 !important;
}}

/* ══════════════════════════════
   CUSTOM COMPONENTS
══════════════════════════════ */

/* Sidebar section label */
.sb-section {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: {TEXT3};
    padding: 1rem 0 0.4rem;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 0.55rem;
    display: block;
}}

/* Hero */
.lf-hero {{
    background: {HERO};
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 2.5rem 2.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}}
.lf-hero::after {{
    content: '';
    position: absolute;
    top: -120px; right: -80px;
    width: 360px; height: 360px;
    background: radial-gradient(circle, rgba(59,130,246,0.06) 0%, transparent 65%);
    pointer-events: none;
}}
.lf-eyebrow {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: {EYEBROW};
    margin-bottom: 1rem;
}}
.lf-title {{
    font-size: 2.8rem;
    font-weight: 900;
    line-height: 1.1;
    color: {HTITLE};
    margin-bottom: 0.9rem;
    letter-spacing: -0.03em;
    font-family: 'Outfit', sans-serif;
}}
.lf-subtitle {{
    font-size: 0.98rem;
    color: {HSUB};
    line-height: 1.7;
    max-width: 500px;
    font-weight: 400;
}}
.lf-stats {{
    display: flex;
    gap: 2.5rem;
    margin-top: 1.8rem;
    padding-top: 1.5rem;
    border-top: 1px solid {BORDER};
}}
.lf-stat-val {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: {STAT_V};
}}
.lf-stat-lbl {{
    font-size: 0.65rem;
    color: {TEXT3};
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.15rem;
}}

/* Pills */
.lf-pills {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin: 1rem 0 1.8rem;
}}
.lf-pill {{
    background: {PILL_BG};
    border: 1px solid {BORDER};
    border-radius: 100px;
    padding: 0.28rem 0.85rem;
    font-size: 0.72rem;
    color: {PILL_T};
    font-weight: 500;
    letter-spacing: 0.01em;
}}

/* Section header */
.lf-section {{
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    margin: 2rem 0 1rem;
}}
.lf-section-num {{
    width: 32px; height: 32px;
    background: linear-gradient(135deg, {ACCENT}, {ACCENT2});
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 700; color: #fff;
    flex-shrink: 0; margin-top: 2px;
    font-family: 'JetBrains Mono', monospace;
}}
.lf-section-title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: {TEXT};
    letter-spacing: -0.01em;
}}
.lf-section-sub {{
    font-size: 0.78rem;
    color: {TEXT3};
    margin-top: 0.15rem;
    line-height: 1.5;
}}

/* Flashcard */
.lf-fc {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-left: 3px solid {ACCENT};
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.7rem;
}}
.lf-fc-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: {TEXT3};
    letter-spacing: 0.12em;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}}
.lf-fc-q {{
    font-size: 0.9rem;
    color: {TEXT2};
    font-weight: 500;
    line-height: 1.55;
}}

/* Tutor bubbles */
.lf-bubble-ai {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px 14px 14px 4px;
    padding: 0.85rem 1rem;
    margin: 0.4rem 0;
    color: {TEXT2};
    font-size: 0.87rem;
    line-height: 1.55;
    max-width: 85%;
}}
.lf-bubble-user {{
    background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(99,102,241,0.1));
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 14px 14px 4px 14px;
    padding: 0.85rem 1rem;
    margin: 0.4rem 0 0.4rem auto;
    color: {TEXT};
    font-size: 0.87rem;
    line-height: 1.55;
    max-width: 85%;
    text-align: right;
}}

/* Empty state */
.lf-empty {{
    text-align: center;
    padding: 3rem 1rem;
    border: 1.5px dashed {BORDER};
    border-radius: 16px;
    margin-top: 0.5rem;
}}
.lf-empty-icon {{ font-size: 2.5rem; margin-bottom: 0.7rem; }}
.lf-empty-title {{ font-size: 0.92rem; font-weight: 700; color: {TEXT2}; }}
.lf-empty-sub {{ font-size: 0.78rem; color: {TEXT3}; margin-top: 0.3rem; }}

/* Pomodoro timer */
.lf-pomo {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: {POMO_C};
    text-align: center;
    letter-spacing: 0.05em;
    padding: 0.3rem 0;
    line-height: 1;
}}
.lf-pomo-label {{
    font-size: 0.65rem;
    color: {TEXT3};
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.3rem;
}}

/* API key status */
.lf-key-dot {{
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: {GREEN};
    margin-right: 6px;
    vertical-align: middle;
    animation: lf-pulse 2s infinite;
}}
@keyframes lf-pulse {{
    0%, 100% {{ opacity: 1; box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }}
    50% {{ opacity: 0.7; box-shadow: 0 0 0 4px rgba(16,185,129,0); }}
}}

/* Setup page */
.lf-setup-wrap {{
    max-width: 540px;
    margin: 0 auto;
    padding: 1.5rem 0 4rem;
}}
.lf-setup-logo {{
    text-align: center;
    margin-bottom: 1.8rem;
}}
.lf-setup-logo-icon {{ font-size: 2.6rem; }}
.lf-setup-logo-name {{
    font-size: 1.5rem;
    font-weight: 800;
    color: {TEXT};
    font-family: 'Outfit', sans-serif;
    margin-top: 0.3rem;
}}
.lf-setup-logo-name span {{ color: {ACCENT}; }}
.lf-setup-logo-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: {TEXT3};
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 0.25rem;
}}
.lf-setup-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 2rem 2rem 1.5rem;
    margin-bottom: 1rem;
}}
.lf-setup-badge {{
    display: inline-block;
    background: rgba(59,130,246,0.08);
    border: 1px solid rgba(59,130,246,0.2);
    color: {ACCENT};
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 0.28rem 0.8rem;
    border-radius: 100px;
    margin-bottom: 1rem;
}}
.lf-setup-title {{
    font-size: 1.4rem;
    font-weight: 800;
    color: {TEXT};
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}}
.lf-setup-sub {{
    font-size: 0.87rem;
    color: {TEXT2};
    line-height: 1.65;
    margin-bottom: 1.6rem;
}}
.lf-steps {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.5rem;
    margin-bottom: 1.3rem;
}}
.lf-step {{
    background: {BG};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 0.7rem 0.4rem;
    text-align: center;
}}
.lf-step-n {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    color: {ACCENT};
}}
.lf-step-t {{
    font-size: 0.66rem;
    color: {TEXT2};
    margin-top: 0.25rem;
    line-height: 1.35;
}}
.lf-tip {{
    background: rgba(245,158,11,0.06);
    border-left: 3px solid #f59e0b;
    border-radius: 0 8px 8px 0;
    padding: 0.55rem 0.85rem;
    font-size: 0.77rem;
    color: #fbbf24;
    margin-bottom: 1.4rem;
}}
.lf-cta-btn {{
    display: block;
    text-align: center;
    background: linear-gradient(135deg, {ACCENT}, {ACCENT2});
    color: #fff !important;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 0.92rem;
    padding: 0.85rem 2rem;
    border-radius: 12px;
    text-decoration: none !important;
    box-shadow: 0 4px 18px rgba(59,130,246,0.3);
    letter-spacing: 0.01em;
    margin-bottom: 0.5rem;
    transition: all 0.15s;
}}
.lf-cta-hint {{
    font-size: 0.72rem;
    color: {TEXT3};
    text-align: center;
    margin-bottom: 1.2rem;
}}
.lf-privacy {{
    background: rgba(59,130,246,0.05);
    border: 1px solid rgba(59,130,246,0.12);
    border-radius: 10px;
    padding: 0.65rem 0.85rem;
    font-size: 0.77rem;
    color: {TEXT3};
    line-height: 1.55;
    margin-top: 0.8rem;
}}
.lf-unlock-label {{
    font-size: 0.75rem;
    font-weight: 700;
    color: {TEXT2};
    margin: 1.1rem 0 0.5rem;
}}
.lf-unlock-pills {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.32rem;
}}
.lf-unlock-pill {{
    background: {BG};
    border: 1px solid {BORDER};
    border-radius: 100px;
    padding: 0.22rem 0.65rem;
    font-size: 0.68rem;
    color: {TEXT2};
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# API KEYS
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
    if not keys:
        return "NO_KEYS"
    for key in keys:
        try:
            genai.configure(api_key=key)
            r = genai.GenerativeModel("models/gemini-2.5-flash").generate_content(
                prompt, generation_config={"temperature": temp, "max_output_tokens": 2000})
            if r and r.text:
                return r.text.strip()
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
    # Using BytesIO to handle the uploaded file properly in cache
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
# PROMPTS
# ═══════════════════════════════════════════════════════════
PROMPTS = {
    "Notes":      "Create structured academic notes with clear H2 headings and bullet points. Max 500 words. No preamble.\n",
    "Flashcards": "Generate exactly 5 flashcards.\nFormat strictly:\nFlashcard 1\nQuestion: [question]\nAnswer: [answer]\n\nFlashcard 2\nQuestion: [question]\nAnswer: [answer]\n(continue for all 5)\n",
    "Quiz":       "Generate exactly 5 multiple choice questions.\nFormat strictly:\nQuestion 1: [question text]\nA. [option]\nB. [option]\nC. [option]\nD. [option]\nCorrect Answer: A\n\nQuestion 2: ...\n",
    "Reflection": "Generate 5 deep reflection questions. Numbered list. No preamble.\n",
    "Study Plan": "Create a 5-step study plan with clear timelines. Numbered. Actionable.\n",
    "Key Concepts":"List 7 key concepts. Format: **Concept Name** — one-line definition. Why it matters: one sentence.\n",
    "Exam Mode":  "Create a full exam paper:\nSection A: 3 MCQ (mark correct answer)\nSection B: 2 Fill in the blanks (provide answers)\nSection C: 2 Short answer (provide model answers)\n",
    "TL;DR":      "Summarise in exactly 5 bullet points. Max 15 words each. Exam-focused. No preamble.\n",
    "Feynman":    "Evaluate this student explanation:\n- Correct points (list)\n- Missing/wrong (list)\n- Score: X/10\n- Improvement tips\n",
    "Socratic":   "Ask ONE deep Socratic question about this topic. Not factual recall. Challenge assumptions. One sentence.\n",
    "Mind Map":   "Create a text mind map:\nCentral Topic: [topic]\n  Branch 1: [name]\n    - [sub-point]\n    - [sub-point]\n  Branch 2: ...\n(5 branches total)\n",
    "Mnemonics":  "Create 3 memorable mnemonics or acronyms for key concepts in this topic. Explain each.\n",
    "ELI5":       "Explain this topic like I am 10 years old. Simple words, fun analogies, max 200 words.\n",
}

def build_prompt(text, difficulty, persona, fmt):
    trimmed = len(text) > 3500
    t = text[:3500]
    base = f"Topic/Content:\n{t}\n\nDifficulty: {difficulty}\nPersona: {persona}\n\nIMPORTANT: Output ONLY the requested format. No preamble, no intro phrases, no 'Sure!' or 'Here are...'. Start directly.\n\n"
    return base + PROMPTS.get(fmt, PROMPTS["Notes"]), trimmed

def short_heading(txt):
    r = ai(f"Create a short 5-word heading for this topic. No quotes, no punctuation.\nTopic: {txt}", 0.2)
    return r if r not in ("QUOTA","NO_KEYS") and len(r) < 60 else "Study Notes"

def run_gen(fmt, content, manual, difficulty, persona, temp, mode="output"):
    if not content:
        st.warning("Enter a topic or upload a file first.")
        return False
    p, trimmed = build_prompt(content, difficulty, persona, fmt)
    if trimmed:
        st.caption("Content trimmed to 3500 characters for processing.")
    with st.spinner(f"Generating {fmt}..."):
        r = ai(p, temp)
    if r in ("QUOTA", "NO_KEYS"):
        quota_ui(); return False
    if mode == "notes":
        st.session_state.notes_content = r
        st.session_state.notes_heading = short_heading(manual or "this topic")
        st.session_state.generated_output = None
        st.session_state.generated_heading = None
        st.session_state.quiz_score = None
    else:
        st.session_state.generated_output = r
        st.session_state.generated_heading = fmt
    st.session_state.history.append({
        "ts": datetime.datetime.now().strftime("%H:%M · %d %b"),
        "format": fmt,
        "topic": (manual or "Uploaded file")[:45],
        "output": r,
    })
    return True

# ═══════════════════════════════════════════════════════════
# SETUP SCREEN
# ═══════════════════════════════════════════════════════════
def show_setup():
    # Override background, leaving sidebar visible
    st.markdown(f"""
<style>
html, body, [data-testid="stApp"],
[data-testid="stAppViewContainer"] > .main,
.block-container {{
    background: {BG} !important;
}}
</style>""", unsafe_allow_html=True)

    # Render setup UI
    st.markdown(f"""
<div class="lf-setup-wrap">
  <div class="lf-setup-logo">
    <div class="lf-setup-logo-icon">🧠</div>
    <div class="lf-setup-logo-name">LearnFlow <span>AI</span></div>
    <div class="lf-setup-logo-sub">Study Companion</div>
  </div>
  <div class="lf-setup-card">
    <div><span class="lf-setup-badge">✦ Free · No Credit Card · 2 Minutes</span></div>
    <div class="lf-setup-title">Connect your free API key</div>
    <div class="lf-setup-sub">
      LearnFlow AI is powered by Google Gemini — completely free.<br>
      Get your key in 2 minutes and unlock 12 AI study tools instantly.
    </div>
    <div class="lf-steps">
      <div class="lf-step"><div class="lf-step-n">01</div><div class="lf-step-t">Open Google AI Studio</div></div>
      <div class="lf-step"><div class="lf-step-n">02</div><div class="lf-step-t">Sign in with Google</div></div>
      <div class="lf-step"><div class="lf-step-n">03</div><div class="lf-step-t">Click Create API Key</div></div>
      <div class="lf-step"><div class="lf-step-n">04</div><div class="lf-step-t">Paste it below</div></div>
    </div>
    <div class="lf-tip">⚡ Keys look like: <strong>AIzaSyA1B2C3...</strong> &nbsp;(39 characters, starts with AIza)</div>
    <a class="lf-cta-btn" href="https://aistudio.google.com/app/apikey" target="_blank">🔑 Get My Free API Key →</a>
    <div class="lf-cta-hint">Opens Google AI Studio in a new tab</div>
  </div>
</div>
""", unsafe_allow_html=True)

    _, mc, _ = st.columns([1, 2, 1])
    with mc:
        key_in = st.text_input("Paste your API key here:", type="password",
                               placeholder="AIzaSy...", key="setup_key_input")

        if st.button("Validate & Start Learning", type="primary", use_container_width=True):
            k = key_in.strip()
            if not k:
                st.warning("Paste your API key above.")
            elif not k.startswith("AIza"):
                st.error("Invalid key — Gemini keys always start with **AIza**")
            elif len(k) < 30:
                st.error("Key is too short — copy the full key from Google AI Studio.")
            else:
                with st.spinner("Validating your key with Google..."):
                    ok = validate_key(k)
                if ok:
                    st.session_state.user_api_keys = [k]
                    st.balloons()
                    st.success("Key validated! Welcome to LearnFlow AI")
                    time.sleep(1.2)
                    st.rerun()
                else:
                    st.error("Google rejected this key. Try copying it again from AI Studio.")

        st.markdown(f"""
<div class="lf-privacy">
  🔒 <strong>Privacy:</strong> Your key is stored only in this browser session.
  It is never sent to any server and is deleted automatically when you close this tab.
</div>
<div class="lf-unlock-label">Everything you unlock:</div>
<div class="lf-unlock-pills">
  <span class="lf-unlock-pill">📝 Smart Notes</span>
  <span class="lf-unlock-pill">🎴 Flashcards</span>
  <span class="lf-unlock-pill">❓ AI Quiz</span>
  <span class="lf-unlock-pill">🧪 Feynman Check</span>
  <span class="lf-unlock-pill">🤖 Socratic Tutor</span>
  <span class="lf-unlock-pill">🎓 Exam Mode</span>
  <span class="lf-unlock-pill">🧠 Mind Map</span>
  <span class="lf-unlock-pill">💡 Mnemonics</span>
  <span class="lf-unlock-pill">⚡ TL;DR</span>
  <span class="lf-unlock-pill">👶 ELI5</span>
  <span class="lf-unlock-pill">📅 Study Plan</span>
  <span class="lf-unlock-pill">⏱ Pomodoro</span>
  <span class="lf-unlock-pill">🌙 Dark / Light Mode</span>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SIDEBAR (Moved Above the Gate)
# ═══════════════════════════════════════════════════════════
with st.sidebar:

    # ── Logo + theme toggle ──
    lc, tc = st.columns([5, 1])
    with lc:
        st.markdown(f"""
<div style="padding:0.2rem 0 0.8rem;">
  <div style="font-size:1.02rem;font-weight:800;color:{TEXT};font-family:'Outfit',sans-serif;letter-spacing:-0.01em;">
    🧠 LearnFlow <span style="color:{ACCENT};">AI</span>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.56rem;color:{TEXT3};letter-spacing:0.17em;margin-top:0.2rem;text-transform:uppercase;">
    Study Companion
  </div>
</div>""", unsafe_allow_html=True)
    with tc:
        if st.button("🌙" if dark else "☀️", help="Toggle theme", use_container_width=True):
            st.session_state.dark_mode = not dark
            st.rerun()

    st.markdown(f'<div style="border-top:1px solid {BORDER};margin-bottom:0.2rem;"></div>', unsafe_allow_html=True)

    # ── Settings ──
    st.markdown('<span class="sb-section">Settings</span>', unsafe_allow_html=True)
    difficulty = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"],
                              label_visibility="collapsed")
    persona = st.selectbox("Persona", [
        "University Professor", "School Teacher", "Child-Friendly Tutor",
        "Scientist", "Exam Coach", "Motivational Mentor",
    ], label_visibility="collapsed")
    st.markdown(f'<div style="font-size:0.75rem;color:{TEXT2};margin:0.5rem 0 0.1rem;font-weight:500;">Creativity</div>', unsafe_allow_html=True)
    creativity = st.slider("Creativity", 0.1, 1.0, 0.4, 0.05, label_visibility="collapsed")

    # ── Pomodoro ──
    st.markdown('<span class="sb-section">Pomodoro Timer</span>', unsafe_allow_html=True)

    pc1, pc2 = st.columns([3, 1])
    with pc1:
        pmin = st.selectbox("Minutes", [25, 5, 10, 15, 30, 45, 60],
                            label_visibility="collapsed")
    with pc2:
        start_stop = st.button("▶" if not st.session_state.pomo_running else "■",
                               use_container_width=True, key="pomo_btn")
        if start_stop:
            if not st.session_state.pomo_running:
                st.session_state.pomo_start    = time.time()
                st.session_state.pomo_duration = pmin * 60
                st.session_state.pomo_running   = True
            else:
                st.session_state.pomo_running   = False
                st.session_state.pomo_start    = None
            st.rerun()

    if st.session_state.pomo_running and st.session_state.pomo_start:
        elapsed   = time.time() - st.session_state.pomo_start
        remaining = max(0, st.session_state.pomo_duration - elapsed)
        if remaining > 0:
            m, s = int(remaining // 60), int(remaining % 60)
            pct  = 1 - (remaining / st.session_state.pomo_duration)
            st.markdown(f'<div class="lf-pomo-label">Focus time remaining</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="lf-pomo">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
            st.progress(pct)
        else:
            st.session_state.pomo_running = False
            st.session_state.pomo_start   = None
            st.success("Break time! Great focus session.")
            if st.button("Restart Timer", use_container_width=True):
                st.session_state.pomo_start    = time.time()
                st.session_state.pomo_duration = pmin * 60
                st.session_state.pomo_running   = True
                st.rerun()
    elif not st.session_state.pomo_running:
        st.markdown(f'<div style="text-align:center;font-size:0.75rem;color:{TEXT3};padding:0.3rem 0;">Press ▶ to start focus session</div>', unsafe_allow_html=True)

    # ── API Keys ──
    st.markdown('<span class="sb-section">API Keys</span>', unsafe_allow_html=True)
    uk = len(st.session_state.user_api_keys)
    st.markdown(f'<span class="lf-key-dot"></span><span style="font-size:0.82rem;color:{GREEN};font-weight:600;">{uk} key active</span>', unsafe_allow_html=True)

    with st.expander("Manage Keys"):
        st.caption("Get a free key: [aistudio.google.com](https://aistudio.google.com/app/apikey)")
        new_key = st.text_input("Add key:", type="password",
                                placeholder="AIzaSy...", key="sb_new_key",
                                label_visibility="collapsed")
        if st.button("Add Key", use_container_width=True, key="sb_add_key"):
            k = new_key.strip()
            if k and k not in st.session_state.user_api_keys:
                st.session_state.user_api_keys.append(k)
                st.success("Key added!")
                st.rerun()
            elif k in st.session_state.user_api_keys:
                st.warning("Key already added.")
        if st.session_state.user_api_keys:
            st.markdown(f'<div style="font-size:0.75rem;color:{TEXT3};margin-top:0.4rem;">{uk} key(s) stored</div>', unsafe_allow_html=True)
            if st.button("Remove All Keys", use_container_width=True, key="sb_rm_keys"):
                st.session_state.user_api_keys = []
                st.rerun()

    # ── Session Stats ──
    st.markdown('<span class="sb-section">Session</span>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    with s1: st.metric("Generated", len(st.session_state.history))
    with s2: st.metric("Notes", 1 if st.session_state.notes_content else 0)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Reset Session", use_container_width=True, key="sb_reset"):
        saved_keys = st.session_state.user_api_keys
        saved_mode = st.session_state.dark_mode
        for k, v in DEFAULTS.items():
            st.session_state[k] = v
        st.session_state.user_api_keys = saved_keys
        st.session_state.dark_mode     = saved_mode
        st.rerun()

# ═══════════════════════════════════════════════════════════
# GATE (Now Appears Below Sidebar Rendering)
# ═══════════════════════════════════════════════════════════
if not has_key():
    show_setup()
    st.stop()

# ═══════════════════════════════════════════════════════════
# MAIN — HERO
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="lf-hero">
  <div class="lf-eyebrow">✦ Powered by Google Gemini 2.5 Flash</div>
  <div class="lf-title">Learn Smarter.<br>Not Harder.</div>
  <div class="lf-subtitle">Transform any topic or document into notes, flashcards, quizzes, mind maps and more — in seconds.</div>
  <div class="lf-stats">
    <div><div class="lf-stat-val">12+</div><div class="lf-stat-lbl">AI Features</div></div>
    <div><div class="lf-stat-val">∞</div><div class="lf-stat-lbl">Topics</div></div>
    <div><div class="lf-stat-val">Free</div><div class="lf-stat-lbl">Forever</div></div>
  </div>
</div>
<div class="lf-pills">
  <span class="lf-pill">📝 Smart Notes</span>
  <span class="lf-pill">🎴 Flashcards</span>
  <span class="lf-pill">❓ AI Quiz</span>
  <span class="lf-pill">🧪 Feynman Check</span>
  <span class="lf-pill">🤖 Socratic Tutor</span>
  <span class="lf-pill">📅 Study Plan</span>
  <span class="lf-pill">🎓 Exam Mode</span>
  <span class="lf-pill">🧠 Mind Map</span>
  <span class="lf-pill">💡 Mnemonics</span>
  <span class="lf-pill">⚡ TL;DR</span>
  <span class="lf-pill">👶 ELI5</span>
  <span class="lf-pill">⏱ Pomodoro</span>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# STEP 1 — INPUT
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="lf-section">
  <div class="lf-section-num">1</div>
  <div>
    <div class="lf-section-title">Enter Topic or Upload File</div>
    <div class="lf-section-sub">Type any subject, paste your notes, or upload a PDF / DOCX / TXT file</div>
  </div>
</div>""", unsafe_allow_html=True)

uploaded  = st.file_uploader("", type=["pdf","docx","txt"], label_visibility="collapsed")
file_text = ""

if uploaded:
    with st.spinner(f"Reading {uploaded.name}..."):
        try:
            ft = uploaded.type
            # We pass the bytes to the cached reader function
            file_bytes = uploaded.getvalue()
            if   "pdf"      in ft: file_text = read_pdf(file_bytes)
            elif "document" in ft: file_text = read_docx(file_bytes)
            else:                  file_text = read_txt(file_bytes)
            st.success(f"**{uploaded.name}** loaded — {len(file_text):,} characters")
        except Exception as e:
            st.error(f"Could not read file: {e}")

manual = st.text_area("", height=100, label_visibility="collapsed",
    placeholder="e.g. Photosynthesis  ·  Newton's Laws  ·  French Revolution  ·  Machine Learning  ·  Thermodynamics...")

# Combine
if file_text and manual.strip():
    content = f"User instruction: {manual.strip()}\n\nDocument content:\n{file_text}"
elif file_text:
    content = file_text
else:
    content = manual.strip()

G = dict(content=content, manual=manual, difficulty=difficulty,
         persona=persona, temp=creativity)

# ═══════════════════════════════════════════════════════════
# STEP 2 — LEARN
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="lf-section">
  <div class="lf-section-num">2</div>
  <div>
    <div class="lf-section-title">Read &amp; Learn</div>
    <div class="lf-section-sub">Generate notes first, then explore summaries, concepts, and memory aids</div>
  </div>
</div>""", unsafe_allow_html=True)

r1c1, r1c2, r1c3, r1c4 = st.columns(4)
with r1c1:
    if st.button("📝 Notes", use_container_width=True, type="primary"):
        if run_gen("Notes", **G, mode="notes"): st.rerun()
with r1c2:
    if st.button("⚡ TL;DR", use_container_width=True):
        if content:
            p, _ = build_prompt(content, difficulty, persona, "TL;DR")
            with st.spinner("Summarising..."): r = ai(p, 0.3)
            if r in ("QUOTA","NO_KEYS"): quota_ui()
            else: st.session_state.tldr = r
        else: st.warning("Enter a topic first.")
with r1c3:
    if st.button("🔑 Key Concepts", use_container_width=True):
        if run_gen("Key Concepts", **G): st.rerun()
with r1c4:
    if st.button("💡 Mnemonics", use_container_width=True):
        if run_gen("Mnemonics", **G): st.rerun()

r2c1, r2c2, r2c3 = st.columns(3)
with r2c1:
    if st.button("🧠 Mind Map", use_container_width=True):
        if run_gen("Mind Map", **G): st.rerun()
with r2c2:
    if st.button("👶 ELI5", use_container_width=True):
        if run_gen("ELI5", **G): st.rerun()
with r2c3:
    if st.button("📅 Study Plan", use_container_width=True):
        if run_gen("Study Plan", **G): st.rerun()

# Display TL;DR
if st.session_state.tldr:
    st.info(f"**⚡ TL;DR**\n\n{st.session_state.tldr}")
    if st.button("Clear TL;DR", key="clear_tldr"):
        st.session_state.tldr = None; st.rerun()

# Display Notes
if st.session_state.notes_content:
    with st.expander(f"📘 {st.session_state.notes_heading}", expanded=True):
        st.markdown(st.session_state.notes_content)
        st.download_button("Download Notes", data=st.session_state.notes_content,
            file_name=f"notes_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain", key="dl_notes")

# Display Step 2 outputs
S2 = ["Key Concepts","Mnemonics","Mind Map","ELI5","Study Plan"]
if st.session_state.generated_output and st.session_state.generated_heading in S2:
    with st.expander(f"📄 {st.session_state.generated_heading}", expanded=True):
        st.markdown(st.session_state.generated_output)
        st.download_button("Download", data=st.session_state.generated_output,
            file_name=f"{st.session_state.generated_heading}.txt",
            mime="text/plain", key="dl_s2")

# ═══════════════════════════════════════════════════════════
# STEP 3 — TEST (unlocks after notes)
# ═══════════════════════════════════════════════════════════
if st.session_state.notes_content:
    st.markdown("""
<div class="lf-section">
  <div class="lf-section-num">3</div>
  <div>
    <div class="lf-section-title">Test Your Knowledge</div>
    <div class="lf-section-sub">Flashcards, quiz, Feynman check, and your personal AI tutor</div>
  </div>
</div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎴  Flashcards", "❓  Quiz", "🤔  Feynman & Reflect", "🤖  AI Tutor"
    ])

    # ── FLASHCARDS ──
    with tab1:
        st.caption("Test yourself before revealing answers — builds stronger memory retention.")
        if st.button("Generate Flashcards", type="primary", use_container_width=True, key="gen_fc"):
            run_gen("Flashcards", **G)

        if st.session_state.generated_heading == "Flashcards" and st.session_state.generated_output:
            cards = st.session_state.generated_output.split("Flashcard")
            idx = 1
            for blk in cards:
                blk = blk.strip()
                if not blk: continue
                parts = blk.split("Answer:")
                if len(parts) >= 2:
                    q = parts[0].replace("Question:","").strip().lstrip("1234567890. \n")
                    a = parts[1].strip()
                    rk = f"fc_reveal_{idx}"
                    if rk not in st.session_state: st.session_state[rk] = False
                    st.markdown(f"""
<div class="lf-fc">
  <div class="lf-fc-num">Card {idx} of 5</div>
  <div class="lf-fc-q">{q}</div>
</div>""", unsafe_allow_html=True)
                    label = "Hide Answer" if st.session_state[rk] else "Reveal Answer"
                    if st.button(label, key=f"fc_btn_{idx}"):
                        st.session_state[rk] = not st.session_state[rk]
                        st.rerun()
                    if st.session_state[rk]:
                        st.success(f"**Answer:** {a}")
                    st.markdown("<br>", unsafe_allow_html=True)
                    idx += 1

    # ── QUIZ ──
    with tab2:
        st.caption("Answer all questions then submit to see your exam readiness score.")
        if st.button("Generate Quiz", type="primary", use_container_width=True, key="gen_qz"):
            run_gen("Quiz", **G)
            st.session_state.quiz_score = None

        if st.session_state.generated_heading == "Quiz" and st.session_state.generated_output:
            raw   = st.session_state.generated_output
            qs    = re.split(r'Question\s+\d+[:.]', raw, flags=re.IGNORECASE)
            qs    = [q.strip() for q in qs if q.strip()]
            u_ans, c_keys = [], []

            for qi, blk in enumerate(qs, 1):
                lines  = [l.strip() for l in blk.split("\n") if l.strip()]
                if not lines: continue
                qtxt   = lines[0].lstrip(".*:) ")
                opts   = [l for l in lines[1:] if re.match(r'^[A-Da-d][.)]\s+', l)]
                cline  = [l for l in lines if re.search(r'correct\s*answer', l, re.IGNORECASE)]
                if not opts or len(opts) < 2: continue

                st.markdown(f"**Q{qi}.** {qtxt}")
                sel = st.radio("", opts, key=f"quiz_q_{qi}", index=None, label_visibility="collapsed")
                u_ans.append(sel)
                if cline:
                    m = re.search(r'[:]\s*([A-Da-d])', cline[0])
                    if m: c_keys.append(m.group(1).upper())
                st.markdown("---")

            if u_ans and c_keys:
                if st.button("Submit & See Score", type="primary", use_container_width=True):
                    if None in u_ans:
                        st.warning("Answer all questions before submitting.")
                    else:
                        score = sum(
                            1 for i, ua in enumerate(u_ans)
                            if i < len(c_keys) and ua and ua.strip().upper().startswith(c_keys[i])
                        )
                        st.session_state.quiz_score = score

                if st.session_state.quiz_score is not None:
                    sc  = st.session_state.quiz_score
                    tot = len(c_keys)
                    pct = int(sc / tot * 100) if tot else 0
                    st.markdown("---")
                    m1, m2, m3 = st.columns(3)
                    with m1: st.metric("Score",      f"{sc} / {tot}")
                    with m2: st.metric("Percentage",  f"{pct}%")
                    with m3: st.metric("Exam Ready",  f"{min(pct+10,100)}%")
                    st.progress(pct / 100)
                    if pct >= 80:   st.success("Excellent! You are exam ready.")
                    elif pct >= 60: st.info("Good effort — review the topics you missed.")
                    elif pct >= 40: st.warning("Keep going — re-read your notes and retry.")
                    else:            st.error("More study needed — go back to notes first.")

    # ── FEYNMAN + REFLECT ──
    with tab3:
        rc1, rc2 = st.columns(2)
        with rc1:
            if st.button("Reflection Questions", use_container_width=True, key="gen_ref"):
                run_gen("Reflection", **G)
        with rc2:
            if st.button("Generate Exam Paper", use_container_width=True, key="gen_exam"):
                run_gen("Exam Mode", **G)

        if st.session_state.generated_heading in ["Reflection","Exam Mode"] and st.session_state.generated_output:
            with st.expander(f"{st.session_state.generated_heading}", expanded=True):
                st.markdown(st.session_state.generated_output)
                st.download_button("Download", data=st.session_state.generated_output,
                    file_name=f"{st.session_state.generated_heading}.txt",
                    mime="text/plain", key="dl_ref")

        st.markdown("---")
        st.markdown("#### 🧪 Feynman Technique Check")
        st.caption("Write your explanation of the topic below. AI will score your understanding out of 10 and pinpoint gaps.")
        fi = st.text_area("Explain the topic in your own words:", height=110,
                          placeholder="In my own words, this topic is about...",
                          key="feynman_input")
        if st.button("Analyse My Understanding", type="primary", use_container_width=True):
            if not fi.strip():
                st.warning("Write your explanation first.")
            else:
                fp, _ = build_prompt(
                    f"Topic: {manual or 'uploaded content'}\n\nStudent explanation:\n{fi}",
                    difficulty, persona, "Feynman"
                )
                with st.spinner("Analysing your explanation..."):
                    fr = ai(fp, 0.3)
                if fr in ("QUOTA","NO_KEYS"): quota_ui()
                else: st.session_state.feynman_feedback = fr

        if st.session_state.feynman_feedback:
            st.markdown(st.session_state.feynman_feedback)

    # ── AI TUTOR ──
    with tab4:
        st.caption("Your Socratic AI tutor asks deep questions to challenge and deepen your understanding.")
        if st.button("Ask Me a Question", type="primary", use_container_width=True, key="tutor_ask"):
            sp, _ = build_prompt(content, difficulty, "Analytical", "Socratic")
            with st.spinner("Thinking of a good question..."): sr = ai(sp, 0.6)
            if sr in ("QUOTA","NO_KEYS"): quota_ui()
            else:
                st.session_state.tutor_history.append({"role":"ai","msg":sr})
                st.rerun()

        for msg in st.session_state.tutor_history:
            if msg["role"] == "ai":
                st.markdown(f'<div class="lf-bubble-ai">🤖 {msg["msg"]}</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="lf-bubble-user">{msg["msg"]} 👤</div>',
                            unsafe_allow_html=True)

        if st.session_state.tutor_history:
            reply = st.text_input("Your answer:", key="tutor_reply_input",
                                  placeholder="Type your answer here...")
            tc1, tc2 = st.columns([4,1])
            with tc1:
                if st.button("Send", use_container_width=True, key="tutor_send"):
                    if reply.strip():
                        st.session_state.tutor_history.append({"role":"user","msg":reply})
                        fup = (f"The topic is: {manual or 'the uploaded content'}.\n"
                               f"Student just answered: {reply}\n"
                               f"Ask ONE short, deeper Socratic follow-up question.")
                        with st.spinner("..."):
                            fur = ai(fup, 0.6)
                        if fur not in ("QUOTA","NO_KEYS"):
                            st.session_state.tutor_history.append({"role":"ai","msg":fur})
                        st.rerun()
            with tc2:
                if st.button("Clear", use_container_width=True, key="tutor_clear"):
                    st.session_state.tutor_history = []
                    st.rerun()

    # ── EXAM MODE ──
    st.markdown("""
<div class="lf-section">
  <div class="lf-section-num">4</div>
  <div>
    <div class="lf-section-title">Full Exam Mode</div>
    <div class="lf-section-sub">Generate a complete exam paper with MCQs, fill-in-the-blanks, and short answers</div>
  </div>
</div>""", unsafe_allow_html=True)

    if st.button("Generate Full Exam Paper", type="primary", use_container_width=True, key="gen_full_exam"):
        if run_gen("Exam Mode", **G):
            st.success("Exam paper ready! Scroll down to view it.")

    if st.session_state.generated_heading == "Exam Mode" and st.session_state.generated_output:
        st.markdown(st.session_state.generated_output)
        st.download_button("Download Exam Paper",
            data=st.session_state.generated_output,
            file_name=f"exam_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain", key="dl_exam")

else:
    st.markdown(f"""
<div class="lf-empty">
  <div class="lf-empty-icon">📖</div>
  <div class="lf-empty-title">Generate your notes to unlock testing features</div>
  <div class="lf-empty-sub">Enter a topic above and click <strong>Notes</strong> to get started</div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HISTORY
# ═══════════════════════════════════════════════════════════
if st.session_state.history:
    st.markdown("""
<div class="lf-section">
  <div class="lf-section-num" style="background:linear-gradient(135deg,#0f766e,#0891b2);">📜</div>
  <div>
    <div class="lf-section-title">Session History</div>
    <div class="lf-section-sub">All content generated in this session</div>
  </div>
</div>""", unsafe_allow_html=True)

    for i, item in enumerate(reversed(st.session_state.history)):
        label = f"{item['format']}  —  {item['topic']}  ·  {item['ts']}"
        with st.expander(label):
            st.markdown(item.get("output",""))
            st.download_button("Download", data=item.get("output",""),
                file_name=f"{item['format']}_{i}.txt",
                mime="text/plain", key=f"hist_dl_{i}")