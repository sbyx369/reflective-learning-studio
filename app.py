import streamlit as st
import time
import re
import datetime

try:
    import PyPDF2
    PDF_OK = True
except ImportError:
    PDF_OK = False

try:
    from docx import Document
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

from groq import Groq

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="LearnFlow AI — Study Smarter",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════
# GROQ  →  .streamlit/secrets.toml  →  GROQ_API_KEY = "gsk_..."
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_resource
def groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

MODELS = ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"]

def ai(prompt: str, temp: float = 0.4) -> str:
    client = groq_client()
    for model in MODELS:
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
                max_tokens=2000,
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            err = str(e)
            if "rate_limit" in err.lower() or "429" in err:
                time.sleep(2)
                continue
            if "model" in err.lower() or "not found" in err.lower():
                continue
            return f"❌ {err}"
    return "❌ All models rate-limited. Wait a moment and try again."

# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════
DEFAULTS: dict = {
    "dark_mode":     True,
    "level":         "Intermediate",
    "persona":       "University Professor",
    "creativity":    0.4,
    "history":       [],
    "notes":         None,
    "notes_heading": "",
    "tldr":          None,
    "out_content":   None,
    "out_label":     "",
    "quiz_raw":      None,
    "quiz_score":    None,
    "quiz_answers":  {},
    "tutor_history": [],
    "feynman_fb":    None,
    "pomo_running":  False,
    "pomo_start":    None,
    "pomo_duration": 25 * 60,
    "fc_revealed":   {},
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════════
# THEME
# ═══════════════════════════════════════════════════════════════════════════
dark = st.session_state.dark_mode

if dark:
    BG, SB, CARD, CARD2      = "#050810", "#080c18", "#0c1222", "#101828"
    BORDER, BORDER2           = "#1a2744", "#243560"
    TEXT, TEXT2, TEXT3        = "#e8eeff", "#8ba4d4", "#3d5580"
    ACCENT, ACCENT2, ACCENT3  = "#4f8ef7", "#7c6ff7", "#06d6a0"
    INPUT, BTN, BTN_T         = "#090e1d", "#0e1830", "#7aa8e8"
    HERO_G                    = "linear-gradient(135deg,#060c1e 0%,#0b1535 40%,#070d1e 100%)"
    HTITLE, HSUB              = "#a8c8ff", "#4a6a9a"
    PILL_BG, PILL_T           = "#0b1428", "#4a7aaa"
    STAT_V                    = "#4f8ef7"
    GREEN                     = "#06d6a0"
    MONO                      = "#4f8ef7"
    GLOW                      = "rgba(79,142,247,0.12)"
    GLOW2                     = "rgba(124,111,247,0.08)"
    SHADOW                    = "0 8px 32px rgba(0,0,0,0.4)"
else:
    BG, SB, CARD, CARD2      = "#f4f6fc", "#eaeff8", "#ffffff", "#f8faff"
    BORDER, BORDER2           = "#d0daf0", "#b8c8e8"
    TEXT, TEXT2, TEXT3        = "#0d1a35", "#2a4070", "#6880aa"
    ACCENT, ACCENT2, ACCENT3  = "#2563eb", "#4f46e5", "#059669"
    INPUT, BTN, BTN_T         = "#ffffff", "#eef2ff", "#2563eb"
    HERO_G                    = "linear-gradient(135deg,#ddeaff 0%,#eef3ff 50%,#e8e4ff 100%)"
    HTITLE, HSUB              = "#1e40af", "#3a5a90"
    PILL_BG, PILL_T           = "#eef2ff", "#3a5aaa"
    STAT_V                    = "#2563eb"
    GREEN                     = "#059669"
    MONO                      = "#4338ca"
    GLOW                      = "rgba(37,99,235,0.08)"
    GLOW2                     = "rgba(79,70,229,0.06)"
    SHADOW                    = "0 8px 32px rgba(0,0,0,0.1)"

# ═══════════════════════════════════════════════════════════════════════════
# CSS — COMPLETE PREMIUM STYLESHEET
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── RESET & BASE ── */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"]>.main{{
  background:{BG}!important;color:{TEXT}!important;
  font-family:'DM Sans',sans-serif!important;
}}
#MainMenu,footer,[data-testid="stDecoration"],[data-testid="stStatusWidget"]{{display:none!important}}
header[data-testid="stHeader"]{{background:transparent!important}}
::-webkit-scrollbar{{width:3px;height:3px}}
::-webkit-scrollbar-track{{background:transparent}}
::-webkit-scrollbar-thumb{{background:{BORDER2};border-radius:10px}}
::-webkit-scrollbar-thumb:hover{{background:{ACCENT}}}

/* ── MAIN CONTENT — centres when sidebar collapses ── */
.block-container{{
  max-width:920px!important;
  margin:0 auto!important;
  padding:1rem 2.5rem 8rem!important;
  background:{BG}!important;
  transition:all 0.3s ease!important;
}}

/* ── CUSTOM SIDEBAR TOGGLE ICON ── */
/* Hide the default arrow SVG, replace with our brain icon */
[data-testid="collapsedControl"]{{
  background:linear-gradient(135deg,{ACCENT},{ACCENT2})!important;
  border-radius:0 12px 12px 0!important;
  width:28px!important;
  height:56px!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  cursor:pointer!important;
  border:none!important;
  box-shadow:4px 0 16px {GLOW}!important;
  transition:all 0.2s!important;
  top:50%!important;
  transform:translateY(-50%)!important;
}}
[data-testid="collapsedControl"]:hover{{
  width:34px!important;
  box-shadow:6px 0 24px {GLOW}!important;
}}
[data-testid="collapsedControl"] svg{{display:none!important}}
[data-testid="collapsedControl"]::after{{
  content:'🧠';
  font-size:16px;
  line-height:1;
}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{{
  background:{SB}!important;
  border-right:1px solid {BORDER}!important;
  min-width:270px!important;
  max-width:280px!important;
}}
[data-testid="stSidebar"]>div,
[data-testid="stSidebar"]>div>div,
section[data-testid="stSidebar"],
section[data-testid="stSidebar"]>div{{background:{SB}!important}}
[data-testid="stSidebar"]>div:first-child{{padding:1rem 1rem 2rem!important;background:{SB}!important}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small{{color:{TEXT2}!important;font-family:'DM Sans',sans-serif!important}}
[data-testid="stSidebar"] [data-baseweb="select"]>div{{
  background:{INPUT}!important;border:1px solid {BORDER}!important;
  border-radius:10px!important;color:{TEXT}!important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div[class*="singleValue"]{{color:{TEXT}!important}}
[data-testid="stSidebar"] .stButton>button{{
  background:{BTN}!important;color:{BTN_T}!important;
  border:1px solid {BORDER}!important;font-size:0.8rem!important;
  font-family:'DM Sans',sans-serif!important;border-radius:10px!important;
}}
[data-testid="stSidebar"] .stButton>button:hover{{border-color:{ACCENT}!important;color:{ACCENT}!important}}
[data-testid="stSidebar"] [data-testid="metric-container"]{{
  background:{INPUT}!important;border:1px solid {BORDER}!important;
  border-radius:12px!important;padding:0.6rem 0.85rem!important;
}}
[data-testid="stSidebar"] [data-testid="stMetricValue"]{{
  color:{STAT_V}!important;font-family:'JetBrains Mono',monospace!important;font-size:1.2rem!important;
}}
[data-testid="stSidebar"] [data-testid="metric-container"] label{{
  color:{TEXT3}!important;font-size:0.6rem!important;
  text-transform:uppercase!important;letter-spacing:0.12em!important;
}}

/* ── BUTTONS ── */
.stButton>button{{
  background:{BTN}!important;color:{BTN_T}!important;
  border:1px solid {BORDER}!important;border-radius:12px!important;
  font-family:'DM Sans',sans-serif!important;font-weight:600!important;
  font-size:0.84rem!important;padding:0.6rem 1rem!important;
  transition:all 0.2s cubic-bezier(0.4,0,0.2,1)!important;
  cursor:pointer!important;width:100%!important;
}}
.stButton>button:hover{{
  border-color:{ACCENT}!important;color:{ACCENT}!important;
  transform:translateY(-2px)!important;box-shadow:0 8px 24px {GLOW}!important;
}}
.stButton>button:active{{transform:translateY(0)!important}}
.stButton>button[kind="primary"]{{
  background:linear-gradient(135deg,{ACCENT},{ACCENT2})!important;
  color:#fff!important;border:none!important;
  box-shadow:0 4px 20px {GLOW}!important;font-weight:700!important;
}}
.stButton>button[kind="primary"]:hover{{
  box-shadow:0 8px 32px {GLOW}!important;
  transform:translateY(-2px)!important;opacity:0.93!important;
}}

/* ── INPUTS ── */
.stTextArea textarea,.stTextInput>div>div>input{{
  background:{INPUT}!important;border:1px solid {BORDER}!important;
  border-radius:12px!important;color:{TEXT}!important;
  font-family:'DM Sans',sans-serif!important;font-size:0.92rem!important;
  transition:all 0.2s!important;line-height:1.6!important;
}}
.stTextArea textarea:focus,.stTextInput>div>div>input:focus{{
  border-color:{ACCENT}!important;box-shadow:0 0 0 3px {GLOW}!important;outline:none!important;
}}
.stTextArea textarea::placeholder,.stTextInput input::placeholder{{color:{TEXT3}!important}}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"]{{
  background:{INPUT}!important;border:1.5px dashed {BORDER2}!important;
  border-radius:14px!important;transition:all 0.2s!important;
}}
[data-testid="stFileUploader"]:hover{{border-color:{ACCENT}!important}}
[data-testid="stFileUploader"] *{{color:{TEXT2}!important}}

/* ── SELECT ── */
[data-baseweb="select"]>div{{
  background:{INPUT}!important;border:1px solid {BORDER}!important;
  border-radius:10px!important;color:{TEXT}!important;
}}
[data-baseweb="select"] span{{color:{TEXT}!important}}
[data-baseweb="popover"]>div{{
  background:{CARD}!important;border:1px solid {BORDER}!important;
  border-radius:14px!important;box-shadow:{SHADOW}!important;
}}
[data-baseweb="option"]{{background:{CARD}!important;color:{TEXT2}!important;font-size:0.87rem!important}}
[data-baseweb="option"]:hover{{background:{BTN}!important;color:{ACCENT}!important}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{{
  background:{INPUT}!important;border-radius:14px!important;
  padding:5px!important;border:1px solid {BORDER}!important;gap:4px!important;
}}
.stTabs [data-baseweb="tab"]{{
  background:transparent!important;color:{TEXT3}!important;border-radius:10px!important;
  font-family:'DM Sans',sans-serif!important;font-weight:600!important;
  font-size:0.83rem!important;border:none!important;padding:0.5rem 1.1rem!important;
  transition:all 0.2s!important;
}}
.stTabs [aria-selected="true"]{{
  background:linear-gradient(135deg,{ACCENT},{ACCENT2})!important;
  color:#fff!important;box-shadow:0 4px 14px {GLOW}!important;
}}

/* ── EXPANDER ── */
details{{
  background:{CARD}!important;border:1px solid {BORDER}!important;
  border-radius:14px!important;overflow:hidden!important;margin-bottom:0.6rem!important;
}}
details:hover{{border-color:{BORDER2}!important}}
details>summary{{
  color:{TEXT2}!important;font-family:'DM Sans',sans-serif!important;
  font-weight:600!important;font-size:0.88rem!important;
  padding:0.85rem 1.1rem!important;cursor:pointer!important;
  background:{CARD}!important;list-style:none!important;
}}
details>summary::-webkit-details-marker{{display:none}}

/* ── PROGRESS ── */
.stProgress>div{{background:{BORDER}!important;border-radius:100px!important;height:6px!important}}
.stProgress>div>div{{
  background:linear-gradient(90deg,{ACCENT},{ACCENT2},{ACCENT3})!important;
  border-radius:100px!important;
}}

/* ── METRICS ── */
[data-testid="metric-container"]{{
  background:{CARD}!important;border:1px solid {BORDER}!important;
  border-radius:14px!important;padding:0.9rem 1.1rem!important;
}}
[data-testid="metric-container"]:hover{{border-color:{BORDER2}!important;box-shadow:0 4px 20px {GLOW}!important}}
[data-testid="stMetricValue"]{{color:{STAT_V}!important;font-family:'JetBrains Mono',monospace!important;font-weight:600!important}}
[data-testid="metric-container"] label{{
  color:{TEXT3}!important;font-size:0.68rem!important;
  text-transform:uppercase!important;letter-spacing:0.1em!important;
}}

/* ── ALERTS ── */
[data-testid="stAlert"]{{border-radius:12px!important;font-family:'DM Sans',sans-serif!important}}
hr{{border:none!important;border-top:1px solid {BORDER}!important;margin:1.2rem 0!important}}

/* ══════════════════════════════════
   CUSTOM COMPONENTS
══════════════════════════════════ */

/* App name bar at top of main */
.lf-appbar{{
  display:flex;align-items:center;gap:0.75rem;
  padding:0.75rem 0 1.25rem;
  border-bottom:1px solid {BORDER};
  margin-bottom:1.5rem;
}}
.lf-appbar-icon{{
  width:38px;height:38px;border-radius:10px;
  background:linear-gradient(135deg,{ACCENT},{ACCENT2});
  display:flex;align-items:center;justify-content:center;
  font-size:18px;flex-shrink:0;
  box-shadow:0 4px 12px {GLOW};
}}
.lf-appbar-name{{
  font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:800;
  color:{TEXT};letter-spacing:-0.03em;
}}
.lf-appbar-name span{{
  background:linear-gradient(135deg,{ACCENT},{ACCENT2});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}}
.lf-appbar-sub{{
  font-family:'JetBrains Mono',monospace;font-size:0.55rem;
  color:{TEXT3};letter-spacing:0.18em;text-transform:uppercase;margin-top:1px;
}}
.lf-appbar-right{{margin-left:auto;display:flex;align-items:center;gap:0.5rem}}
.lf-appbar-badge{{
  background:{GLOW};border:1px solid {BORDER2};
  border-radius:100px;padding:0.25rem 0.75rem;
  font-family:'JetBrains Mono',monospace;
  font-size:0.58rem;color:{ACCENT};letter-spacing:0.1em;text-transform:uppercase;
}}

/* Sidebar section label */
.sb-label{{
  font-family:'JetBrains Mono',monospace;font-size:0.57rem;font-weight:600;
  letter-spacing:0.2em;text-transform:uppercase;color:{TEXT3};
  padding:0.85rem 0 0.4rem;border-bottom:1px solid {BORDER};
  margin-bottom:0.6rem;display:block;
}}

/* Hero */
.lf-hero{{
  background:{HERO_G};border:1px solid {BORDER};border-radius:24px;
  padding:2.75rem 3rem 2.25rem;margin-bottom:1.5rem;
  position:relative;overflow:hidden;
}}
.lf-hero::before{{
  content:'';position:absolute;top:-80px;right:-60px;
  width:300px;height:300px;
  background:radial-gradient(circle,{GLOW} 0%,transparent 70%);
  pointer-events:none;border-radius:50%;
}}
.lf-hero::after{{
  content:'';position:absolute;bottom:-50px;left:-30px;
  width:200px;height:200px;
  background:radial-gradient(circle,{GLOW2} 0%,transparent 70%);
  pointer-events:none;border-radius:50%;
}}
.lf-eyebrow{{
  font-family:'JetBrains Mono',monospace;font-size:0.6rem;letter-spacing:0.22em;
  text-transform:uppercase;color:{MONO};margin-bottom:1rem;
  display:inline-flex;align-items:center;gap:0.5rem;
}}
.lf-eyebrow::before{{
  content:'';width:6px;height:6px;border-radius:50%;background:{ACCENT3};
  display:inline-block;box-shadow:0 0 8px {ACCENT3};
  animation:glow-pulse 2.5s infinite;
}}
@keyframes glow-pulse{{
  0%,100%{{box-shadow:0 0 6px {ACCENT3}}}
  50%{{box-shadow:0 0 16px {ACCENT3}}}
}}
.lf-title{{
  font-family:'Syne',sans-serif;font-size:2.8rem;font-weight:800;
  line-height:1.05;color:{HTITLE};margin-bottom:0.9rem;letter-spacing:-0.04em;
}}
.lf-title span{{
  background:linear-gradient(135deg,{ACCENT},{ACCENT2});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}}
.lf-subtitle{{font-size:0.98rem;color:{HSUB};line-height:1.75;max-width:500px;font-weight:400}}
.lf-stats{{
  display:flex;gap:2.5rem;margin-top:1.8rem;padding-top:1.6rem;border-top:1px solid {BORDER};
}}
.lf-stat-val{{
  font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;color:{STAT_V};line-height:1;
}}
.lf-stat-lbl{{
  font-size:0.62rem;color:{TEXT3};text-transform:uppercase;letter-spacing:0.12em;margin-top:0.2rem;
}}

/* Feature pills */
.lf-pills{{display:flex;flex-wrap:wrap;gap:0.4rem;margin:1.2rem 0 2rem}}
.lf-pill{{
  background:{PILL_BG};border:1px solid {BORDER};border-radius:100px;
  padding:0.28rem 0.85rem;font-size:0.7rem;color:{PILL_T};font-weight:500;
  transition:all 0.2s;font-family:'DM Sans',sans-serif;
}}
.lf-pill:hover{{border-color:{ACCENT};color:{ACCENT};transform:translateY(-1px)}}

/* Section header */
.lf-section{{display:flex;align-items:flex-start;gap:1rem;margin:2.25rem 0 1.1rem}}
.lf-section-num{{
  width:34px;height:34px;flex-shrink:0;margin-top:2px;
  background:linear-gradient(135deg,{ACCENT},{ACCENT2});border-radius:10px;
  display:flex;align-items:center;justify-content:center;
  font-family:'JetBrains Mono',monospace;font-size:0.78rem;font-weight:700;color:#fff;
  box-shadow:0 4px 14px {GLOW};
}}
.lf-section-title{{
  font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:{TEXT};letter-spacing:-0.02em;
}}
.lf-section-sub{{font-size:0.77rem;color:{TEXT3};margin-top:0.2rem;line-height:1.5}}

/* Flashcard */
.lf-fc{{
  background:{CARD};border:1px solid {BORDER};border-radius:16px;
  padding:1.2rem 1.4rem;margin-bottom:0.75rem;
  transition:all 0.2s;position:relative;overflow:hidden;
}}
.lf-fc::before{{
  content:'';position:absolute;top:0;left:0;width:3px;height:100%;
  background:linear-gradient(180deg,{ACCENT},{ACCENT2});
}}
.lf-fc:hover{{border-color:{BORDER2};box-shadow:0 4px 20px {GLOW};transform:translateY(-1px)}}
.lf-fc-num{{
  font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:{TEXT3};
  letter-spacing:0.15em;margin-bottom:0.5rem;text-transform:uppercase;
}}
.lf-fc-q{{font-size:0.9rem;color:{TEXT2};font-weight:500;line-height:1.6}}

/* Chat bubbles */
.lf-bubble-ai{{
  background:{CARD};border:1px solid {BORDER};
  border-radius:16px 16px 16px 4px;padding:0.9rem 1.1rem;
  margin:0.75rem 0;color:{TEXT2};font-size:0.88rem;line-height:1.6;max-width:88%;
  position:relative;
}}
.lf-bubble-ai-label{{
  font-size:0.62rem;font-family:'JetBrains Mono',monospace;
  color:{ACCENT};letter-spacing:0.1em;text-transform:uppercase;
  margin-bottom:0.4rem;
}}
.lf-bubble-user{{
  background:linear-gradient(135deg,{GLOW},{GLOW2});border:1px solid {BORDER2};
  border-radius:16px 16px 4px 16px;padding:0.9rem 1.1rem;
  margin:0.75rem 0 0.75rem auto;color:{TEXT};font-size:0.88rem;line-height:1.6;
  max-width:88%;text-align:right;
}}
.lf-bubble-user-label{{
  font-size:0.62rem;font-family:'JetBrains Mono',monospace;
  color:{ACCENT2};letter-spacing:0.1em;text-transform:uppercase;
  margin-bottom:0.4rem;text-align:right;
}}

/* Empty state */
.lf-empty{{
  text-align:center;padding:3.5rem 1rem;
  border:1.5px dashed {BORDER};border-radius:20px;
  background:{CARD};margin-top:0.5rem;
}}
.lf-empty-icon{{font-size:2.8rem;margin-bottom:0.75rem;display:block}}
.lf-empty-title{{font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:{TEXT2}}}
.lf-empty-sub{{font-size:0.78rem;color:{TEXT3};margin-top:0.4rem;line-height:1.6}}

/* Pomodoro */
.lf-pomo{{
  font-family:'JetBrains Mono',monospace;font-size:2.2rem;font-weight:700;
  color:{ACCENT};text-align:center;letter-spacing:0.08em;padding:0.4rem 0;line-height:1;
}}
.lf-pomo-label{{
  font-size:0.58rem;color:{TEXT3};text-align:center;
  text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.25rem;
  font-family:'JetBrains Mono',monospace;
}}

/* API status dot */
.lf-dot{{
  display:inline-block;width:7px;height:7px;border-radius:50%;
  background:{ACCENT3};margin-right:6px;vertical-align:middle;
  animation:dot-pulse 2.5s infinite;
}}
@keyframes dot-pulse{{
  0%,100%{{box-shadow:0 0 4px {ACCENT3}}}
  50%{{box-shadow:0 0 12px {ACCENT3}}}
}}

/* Score badge */
.lf-score-badge{{
  display:inline-flex;align-items:center;justify-content:center;
  width:72px;height:72px;border-radius:50%;
  background:linear-gradient(135deg,{ACCENT},{ACCENT2});
  color:#fff;font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
  box-shadow:0 8px 24px {GLOW};
}}

/* Divider with label */
.lf-divider{{
  display:flex;align-items:center;gap:0.75rem;margin:1.5rem 0;
  color:{TEXT3};font-size:0.68rem;font-family:'JetBrains Mono',monospace;
  letter-spacing:0.12em;text-transform:uppercase;
}}
.lf-divider::before,.lf-divider::after{{content:'';flex:1;height:1px;background:{BORDER}}}

/* Feynman result card */
.feynman-card{{
  background:linear-gradient(135deg,{CARD},{CARD2});
  border:1px solid {BORDER};border-radius:16px;padding:1.5rem;margin-top:0.75rem;
  font-size:0.9rem;line-height:1.75;color:{TEXT2};
}}

/* Output box */
.lf-output{{
  background:{CARD};border:1px solid {BORDER};border-radius:16px;
  padding:1.5rem 1.75rem;margin-top:0.75rem;
  border-left:3px solid {ACCENT};
  font-size:0.91rem;line-height:1.8;color:{TEXT2};
}}
</style>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# FILE READER
# ═══════════════════════════════════════════════════════════════════════════
def read_file(f) -> str:
    import io
    name = f.name.lower()
    try:
        if name.endswith(".pdf"):
            if not PDF_OK:
                return "Install PyPDF2: pip install PyPDF2"
            reader = PyPDF2.PdfReader(io.BytesIO(f.read()))
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        elif name.endswith(".docx"):
            if not DOCX_OK:
                return "Install python-docx: pip install python-docx"
            doc = Document(io.BytesIO(f.read()))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        elif name.endswith(".txt"):
            return f.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"Error: {e}"
    return "Unsupported file type."

# ═══════════════════════════════════════════════════════════════════════════
# PROMPT TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════
TEMPLATES = {
    "Notes":
        "Create structured, comprehensive academic notes.\n"
        "Use ## for main sections, ### for subsections, bullet points for details.\n"
        "Include: key definitions, important facts, exam tips, and a summary.\n"
        "Max 600 words. Start directly with the first heading.\n",
    "TL;DR":
        "Summarise in exactly 5 bullet points.\n"
        "Each bullet: start with '•', max 15 words, exam-focused, punchy.\n"
        "No intro, no preamble. Start with the first bullet.\n",
    "Key Concepts":
        "List exactly 7 key concepts.\n"
        "Format each as:\n**[Concept Name]** — [one-line definition]\n→ Why it matters: [one sentence]\n\n"
        "Start directly with the first concept.\n",
    "Mnemonics":
        "Create 3 powerful mnemonics or acronyms for key concepts.\n"
        "For each:\n1. The mnemonic/acronym in bold\n2. What each letter stands for\n3. A quick tip to use it\n"
        "Be creative and memorable. Start directly.\n",
    "Mind Map":
        "Create a detailed text mind map.\n"
        "Format:\n🎯 Central Topic: [TOPIC NAME]\n\n"
        "  📌 Branch 1: [Name]\n    ├── [sub-point]\n    ├── [sub-point]\n    └── [sub-point]\n\n"
        "  📌 Branch 2: [Name]\n    ├── ...\n\n"
        "Create exactly 5 branches, 3 sub-points each. Start directly.\n",
    "ELI5":
        "Explain this topic like I'm 10 years old.\n"
        "Use one fun analogy or story. Short sentences. Zero jargon. Make it stick.\n"
        "Max 200 words. Start directly.\n",
    "Study Plan":
        "Create a detailed 7-day study plan for mastering this topic.\n"
        "Each day: Day X — [Focus Area]\n• Task 1\n• Task 2\n• Task 3\n⏱ Time: [estimate]\n\n"
        "Include review sessions on Day 5 and 7. Start directly with Day 1.\n",
    "Flashcards":
        "Generate exactly 5 high-quality exam flashcards.\n"
        "Use this EXACT format:\n\n"
        "Flashcard 1\nQuestion: [specific, clear question]\nAnswer: [concise, complete answer]\n\n"
        "Flashcard 2\nQuestion: ...\nAnswer: ...\n\n"
        "(Repeat for all 5. No other text.)\n",
    "Quiz":
        "Generate exactly 5 multiple choice questions at exam difficulty.\n"
        "Use this EXACT format:\n\n"
        "Question 1: [question text]\nA. [option]\nB. [option]\nC. [option]\nD. [option]\nCorrect Answer: [letter only]\n\n"
        "Question 2: ...\n\n"
        "(All 5 questions. Correct Answer line is mandatory for each.)\n",
    "Reflection":
        "Generate 5 deep critical thinking questions that go beyond recall.\n"
        "Each question should challenge assumptions or connect to real world.\n"
        "Format: 1. [question]\n2. [question] etc. Start directly.\n",
    "Feynman":
        "You are a strict but fair professor evaluating a student's explanation.\n"
        "Structure your response exactly as:\n\n"
        "✅ **What you got right:**\n• [point]\n• [point]\n\n"
        "❌ **Gaps or misconceptions:**\n• [point]\n• [point]\n\n"
        "📊 **Score: [X]/10** — [one sentence justification]\n\n"
        "💡 **3 tips to improve:**\n1. [tip]\n2. [tip]\n3. [tip]\n",
    "Socratic":
        "Ask ONE powerful Socratic question about this topic.\n"
        "It must challenge a common assumption or reveal hidden complexity.\n"
        "One sentence only. No preamble. Start directly with the question.\n",
    "Exam Mode":
        "Create a complete professional exam paper.\n\n"
        "**SECTION A — Multiple Choice** (3 questions)\n"
        "[Question] A. B. C. D. ✓ Correct: [letter]\n\n"
        "**SECTION B — Fill in the Blanks** (3 questions)\n"
        "[Sentence with ___ blank] → Answer: [word]\n\n"
        "**SECTION C — Short Answer** (2 questions with model answers)\n\n"
        "**SECTION D — Essay Question** (1 question + marking criteria)\n",
}

def build_prompt(content: str, fmt: str) -> str:
    return (
        f"Topic/Content:\n{content[:3800]}\n\n"
        f"Difficulty Level: {st.session_state.level}\n"
        f"Teaching Persona: {st.session_state.persona}\n\n"
        f"CRITICAL RULE: Output ONLY the requested format below. "
        f"Do NOT start with 'Sure!', 'Here are', 'Of course', 'Certainly' or any preamble. "
        f"Begin your response directly with the content.\n\n"
        + TEMPLATES.get(fmt, TEMPLATES["Notes"])
    )

def generate(fmt: str, content: str) -> str | None:
    if not content.strip():
        st.warning("⚠️ Enter a topic or upload a file first.")
        return None
    with st.spinner(f"✨ Generating {fmt}..."):
        result = ai(build_prompt(content, fmt), st.session_state.creativity)
    st.session_state.history.append({
        "ts":     datetime.datetime.now().strftime("%H:%M · %d %b"),
        "format": fmt,
        "topic":  content[:50],
        "output": result,
    })
    return result

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo row
    lc, tc = st.columns([5, 1])
    with lc:
        st.markdown(f"""
<div style="padding:0.2rem 0 0.9rem">
  <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:800;
              color:{TEXT};letter-spacing:-0.02em;display:flex;align-items:center;gap:0.45rem">
    🧠 <span>LearnFlow <span style="color:{ACCENT}">AI</span></span>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.5rem;color:{TEXT3};
              letter-spacing:0.2em;margin-top:0.2rem;text-transform:uppercase">
    Study Companion · Groq
  </div>
</div>""", unsafe_allow_html=True)
    with tc:
        if st.button("🌙" if dark else "☀️", help="Toggle theme", key="theme_btn"):
            st.session_state.dark_mode = not dark
            st.rerun()

    st.markdown(f'<div style="height:1px;background:{BORDER};margin-bottom:0.4rem"></div>',
                unsafe_allow_html=True)

    # API Status
    st.markdown('<span class="sb-label">⚡ API Status</span>', unsafe_allow_html=True)
    try:
        _ = st.secrets["GROQ_API_KEY"]
        st.markdown(
            f'<span class="lf-dot"></span>'
            f'<span style="font-size:0.8rem;color:{ACCENT3};font-weight:600">Groq connected</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="font-size:0.68rem;color:{TEXT3};margin-top:0.15rem;padding-left:1rem">'
            f'Llama 3.3 · 70B · Fast inference</div>',
            unsafe_allow_html=True,
        )
    except Exception:
        st.error("Add GROQ_API_KEY to .streamlit/secrets.toml")

    # Learning Settings
    st.markdown('<span class="sb-label">⚙️ Learning Settings</span>', unsafe_allow_html=True)
    LEVELS   = ["Beginner", "Intermediate", "Advanced", "Expert"]
    PERSONAS = ["University Professor", "School Teacher", "Child-Friendly Tutor",
                "Scientist", "Exam Coach", "Motivational Mentor"]
    st.session_state.level = st.selectbox(
        "Level", LEVELS,
        index=LEVELS.index(st.session_state.level),
        label_visibility="collapsed",
    )
    st.session_state.persona = st.selectbox(
        "Persona", PERSONAS,
        index=PERSONAS.index(st.session_state.persona),
        label_visibility="collapsed",
    )
    st.markdown(
        f'<div style="font-size:0.72rem;color:{TEXT2};margin:0.55rem 0 0.15rem;font-weight:500">'
        f'🎨 Creativity — {st.session_state.creativity:.2f}</div>',
        unsafe_allow_html=True,
    )
    st.session_state.creativity = st.slider(
        "cr", 0.1, 1.0, st.session_state.creativity, 0.05,
        label_visibility="collapsed",
    )

    # Pomodoro
    st.markdown('<span class="sb-label">⏱ Pomodoro</span>', unsafe_allow_html=True)
    pc1, pc2 = st.columns([3, 1])
    with pc1:
        pmin = st.selectbox(
            "mins", [25, 5, 10, 15, 20, 30, 45, 60],
            label_visibility="collapsed",
        )
    with pc2:
        pomo_icon = "■" if st.session_state.pomo_running else "▶"
        if st.button(pomo_icon, use_container_width=True, key="pomo_btn"):
            if not st.session_state.pomo_running:
                st.session_state.pomo_start    = time.time()
                st.session_state.pomo_duration = pmin * 60
                st.session_state.pomo_running  = True
            else:
                st.session_state.pomo_running = False
                st.session_state.pomo_start   = None
            st.rerun()

    if st.session_state.pomo_running and st.session_state.pomo_start:
        elapsed   = time.time() - st.session_state.pomo_start
        remaining = max(0.0, st.session_state.pomo_duration - elapsed)
        m, s      = int(remaining // 60), int(remaining % 60)
        st.markdown('<div class="lf-pomo-label">focus time remaining</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="lf-pomo">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        st.progress(1.0 - remaining / max(st.session_state.pomo_duration, 1))
        if remaining == 0:
            st.session_state.pomo_running = False
            st.session_state.pomo_start   = None
            st.balloons()
            st.success("🎉 Session done! Take a break.")
    else:
        m_i, s_i = divmod(pmin * 60, 60)
        st.markdown(f'<div class="lf-pomo">{m_i:02d}:{s_i:02d}</div>', unsafe_allow_html=True)

    # Session Stats
    st.markdown('<span class="sb-label">📊 Session</span>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    with s1: st.metric("Generated", len(st.session_state.history))
    with s2: st.metric("Notes",     1 if st.session_state.notes else 0)

    # Quick history
    if st.session_state.history:
        st.markdown('<span class="sb-label">📜 Recent</span>', unsafe_allow_html=True)
        for item in reversed(st.session_state.history[-4:]):
            st.markdown(
                f'<div style="font-size:0.72rem;color:{TEXT3};padding:0.22rem 0;'
                f'border-bottom:1px solid {BORDER}">'
                f'<span style="color:{ACCENT};font-weight:600">{item["format"]}</span>'
                f' · {item["ts"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑 Reset Session", use_container_width=True, key="reset_btn"):
        dark_saved = st.session_state.dark_mode
        for k, v in DEFAULTS.items():
            st.session_state[k] = v
        st.session_state.dark_mode = dark_saved
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# APP NAME BAR  (always visible at top of main, even when sidebar is closed)
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="lf-appbar">
  <div class="lf-appbar-icon">🧠</div>
  <div>
    <div class="lf-appbar-name">LearnFlow <span>AI</span></div>
    <div class="lf-appbar-sub">Study Smarter · Not Harder</div>
  </div>
  <div class="lf-appbar-right">
    <span class="lf-appbar-badge">Groq · Llama 3.3 70B</span>
  </div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="lf-hero">
  <div class="lf-eyebrow">Powered by Groq · Llama 3.3 70B · Ultra-fast inference</div>
  <div class="lf-title">Learn <span>Smarter.</span><br>Not Harder.</div>
  <div class="lf-subtitle">
    Transform any topic, notes, or document into structured study content —
    flashcards, quizzes, mind maps, and a personal AI tutor — in seconds.
  </div>
  <div class="lf-stats">
    <div><div class="lf-stat-val">12+</div><div class="lf-stat-lbl">AI Tools</div></div>
    <div><div class="lf-stat-val">∞</div><div class="lf-stat-lbl">Topics</div></div>
    <div><div class="lf-stat-val">Free</div><div class="lf-stat-lbl">Forever</div></div>
    <div><div class="lf-stat-val">&lt;2s</div><div class="lf-stat-lbl">Response</div></div>
  </div>
</div>
<div class="lf-pills">
  <span class="lf-pill">📝 Smart Notes</span>
  <span class="lf-pill">🎴 Flashcards</span>
  <span class="lf-pill">❓ AI Quiz</span>
  <span class="lf-pill">🧪 Feynman Check</span>
  <span class="lf-pill">🤖 Socratic Tutor</span>
  <span class="lf-pill">📅 7-Day Study Plan</span>
  <span class="lf-pill">🎓 Exam Mode</span>
  <span class="lf-pill">🧠 Mind Map</span>
  <span class="lf-pill">💡 Mnemonics</span>
  <span class="lf-pill">⚡ TL;DR</span>
  <span class="lf-pill">👶 ELI5</span>
  <span class="lf-pill">🔑 Key Concepts</span>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1 — INPUT
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""<div class="lf-section">
  <div class="lf-section-num">1</div>
  <div>
    <div class="lf-section-title">Enter Topic or Upload File</div>
    <div class="lf-section-sub">Type any subject, paste your notes, or upload a PDF / DOCX / TXT</div>
  </div>
</div>""", unsafe_allow_html=True)

uploaded  = st.file_uploader("", type=["pdf", "docx", "txt"], label_visibility="collapsed")
file_text = ""
if uploaded:
    with st.spinner(f"📂 Reading {uploaded.name}..."):
        file_text = read_file(uploaded)
    if file_text.startswith("Error") or file_text.startswith("Install"):
        st.error(file_text)
        file_text = ""
    else:
        wc = len(file_text.split())
        st.success(f"✅ **{uploaded.name}** loaded — {len(file_text):,} chars · ~{wc:,} words")

topic_input = st.text_area(
    "", height=100, label_visibility="collapsed",
    placeholder="e.g.  Photosynthesis  ·  Newton's Laws  ·  French Revolution  ·  Machine Learning  ·  Organic Chemistry...",
)

# Build content
if file_text and topic_input.strip():
    content = f"User instruction: {topic_input.strip()}\n\nDocument content:\n{file_text}"
elif file_text:
    content = file_text
else:
    content = topic_input.strip()

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2 — READ & LEARN
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""<div class="lf-section">
  <div class="lf-section-num">2</div>
  <div>
    <div class="lf-section-title">Read &amp; Learn</div>
    <div class="lf-section-sub">Start with Notes — then explore summaries, concepts, memory aids and study plans</div>
  </div>
</div>""", unsafe_allow_html=True)

# Row 1 — 4 buttons
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("📝 Notes", use_container_width=True, type="primary", key="btn_notes"):
        result = generate("Notes", content)
        if result:
            st.session_state.notes = result
            heading = ai(
                f"Give a 5-word title for this topic (no quotes, no punctuation, no period): "
                f"{topic_input or content[:80]}",
                0.2,
            )
            st.session_state.notes_heading = heading if 3 < len(heading) < 70 else "Smart Notes"
            st.rerun()
with c2:
    if st.button("⚡ TL;DR", use_container_width=True, key="btn_tldr"):
        result = generate("TL;DR", content)
        if result:
            st.session_state.tldr = result
            st.rerun()
with c3:
    if st.button("🔑 Key Concepts", use_container_width=True, key="btn_kc"):
        result = generate("Key Concepts", content)
        if result:
            st.session_state.out_content = result
            st.session_state.out_label   = "Key Concepts"
            st.rerun()
with c4:
    if st.button("💡 Mnemonics", use_container_width=True, key="btn_mn"):
        result = generate("Mnemonics", content)
        if result:
            st.session_state.out_content = result
            st.session_state.out_label   = "Mnemonics"
            st.rerun()

# Row 2 — 3 buttons
c5, c6, c7 = st.columns(3)
with c5:
    if st.button("🧠 Mind Map", use_container_width=True, key="btn_mm"):
        result = generate("Mind Map", content)
        if result:
            st.session_state.out_content = result
            st.session_state.out_label   = "Mind Map"
            st.rerun()
with c6:
    if st.button("👶 ELI5 — Explain Simply", use_container_width=True, key="btn_eli5"):
        result = generate("ELI5", content)
        if result:
            st.session_state.out_content = result
            st.session_state.out_label   = "ELI5"
            st.rerun()
with c7:
    if st.button("📅 7-Day Study Plan", use_container_width=True, key="btn_sp"):
        result = generate("Study Plan", content)
        if result:
            st.session_state.out_content = result
            st.session_state.out_label   = "Study Plan"
            st.rerun()

# ── Display TL;DR ──
if st.session_state.tldr:
    st.markdown('<div class="lf-divider">TL;DR Summary</div>', unsafe_allow_html=True)
    st.info(f"**⚡ TL;DR**\n\n{st.session_state.tldr}")
    if st.button("✕ Clear TL;DR", key="clear_tldr"):
        st.session_state.tldr = None
        st.rerun()

# ── Display Notes ──
if st.session_state.notes:
    st.markdown('<div class="lf-divider">Smart Notes</div>', unsafe_allow_html=True)
    with st.expander(f"📘 {st.session_state.notes_heading or 'Smart Notes'}", expanded=True):
        st.markdown(st.session_state.notes)
        dl_col, clr_col = st.columns([3, 1])
        with dl_col:
            st.download_button(
                "⬇ Download Notes (.txt)",
                data=st.session_state.notes,
                file_name=f"notes_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain", key="dl_notes",
            )
        with clr_col:
            if st.button("✕ Clear", key="clr_notes"):
                st.session_state.notes = None
                st.rerun()

# ── Display other Step-2 outputs ──
LEARN_LABELS = ["Key Concepts", "Mnemonics", "Mind Map", "ELI5", "Study Plan"]
if st.session_state.out_content and st.session_state.out_label in LEARN_LABELS:
    icons = {"Key Concepts": "🔑", "Mnemonics": "💡", "Mind Map": "🧠", "ELI5": "👶", "Study Plan": "📅"}
    icon  = icons.get(st.session_state.out_label, "📄")
    st.markdown(f'<div class="lf-divider">{st.session_state.out_label}</div>', unsafe_allow_html=True)
    with st.expander(f"{icon} {st.session_state.out_label}", expanded=True):
        st.markdown(st.session_state.out_content)
        st.download_button(
            f"⬇ Download {st.session_state.out_label}",
            data=st.session_state.out_content,
            file_name=f"{st.session_state.out_label.replace(' ', '_')}.txt",
            mime="text/plain", key="dl_learn",
        )

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3 — TEST  (locked until notes generated)
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.notes:
    st.markdown("""<div class="lf-section">
  <div class="lf-section-num">3</div>
  <div>
    <div class="lf-section-title">Test Your Knowledge</div>
    <div class="lf-section-sub">Flashcards · AI Quiz · Feynman Technique · Socratic Tutor</div>
  </div>
</div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎴  Flashcards",
        "❓  AI Quiz",
        "🧪  Feynman & Reflect",
        "🤖  AI Tutor",
    ])

    # ── TAB 1: FLASHCARDS ───────────────────────────────────────────────────
    with tab1:
        st.markdown(
            f'<p style="font-size:0.81rem;color:{TEXT3};margin-bottom:1rem">'
            f'Cover the answer and try to recall it — spaced repetition beats re-reading every time.</p>',
            unsafe_allow_html=True,
        )
        if st.button("🎴 Generate Flashcards", type="primary", use_container_width=True, key="gen_fc"):
            result = generate("Flashcards", content)
            if result:
                st.session_state.out_content = result
                st.session_state.out_label   = "Flashcards"
                st.session_state.fc_revealed = {}
                st.rerun()

        if st.session_state.out_label == "Flashcards" and st.session_state.out_content:
            cards = st.session_state.out_content.split("Flashcard")
            idx   = 1
            for blk in cards:
                blk = blk.strip()
                if not blk:
                    continue
                parts = blk.split("Answer:")
                if len(parts) < 2:
                    continue
                q  = parts[0].replace("Question:", "").strip().lstrip("1234567890. \n")
                a  = parts[1].strip()
                rk = f"fc_{idx}"
                if rk not in st.session_state.fc_revealed:
                    st.session_state.fc_revealed[rk] = False

                st.markdown(f"""<div class="lf-fc">
  <div class="lf-fc-num">Card {idx} of 5</div>
  <div class="lf-fc-q">💬 {q}</div>
</div>""", unsafe_allow_html=True)
                btn_col, _ = st.columns([2, 3])
                with btn_col:
                    lbl = "🙈 Hide Answer" if st.session_state.fc_revealed[rk] else "👁 Reveal Answer"
                    if st.button(lbl, key=f"fc_btn_{idx}"):
                        st.session_state.fc_revealed[rk] = not st.session_state.fc_revealed[rk]
                        st.rerun()
                if st.session_state.fc_revealed[rk]:
                    st.success(f"**✅ Answer:** {a}")
                st.markdown("<br>", unsafe_allow_html=True)
                idx += 1

    # ── TAB 2: QUIZ ─────────────────────────────────────────────────────────
    with tab2:
        st.markdown(
            f'<p style="font-size:0.81rem;color:{TEXT3};margin-bottom:1rem">'
            f'Answer all 5 questions, then submit to see your exam readiness score.</p>',
            unsafe_allow_html=True,
        )
        if st.button("❓ Generate Quiz", type="primary", use_container_width=True, key="gen_quiz"):
            result = generate("Quiz", content)
            if result:
                st.session_state.quiz_raw     = result
                st.session_state.quiz_score   = None
                st.session_state.quiz_answers = {}
                st.rerun()

        if st.session_state.quiz_raw:
            qs     = re.split(r'Question\s+\d+[:.]', st.session_state.quiz_raw, flags=re.IGNORECASE)
            qs     = [q.strip() for q in qs if q.strip()]
            c_keys: list = []

            for qi, blk in enumerate(qs, 1):
                lines = [l.strip() for l in blk.split("\n") if l.strip()]
                if not lines:
                    continue
                qtxt  = lines[0].lstrip(".*:) ")
                opts  = [l for l in lines[1:] if re.match(r'^[A-Da-d][.)]\s+', l)]
                cline = [l for l in lines if re.search(r'correct\s*answer', l, re.IGNORECASE)]
                if len(opts) < 2:
                    continue
                st.markdown(
                    f'<div style="font-weight:600;color:{TEXT};margin-bottom:0.4rem;font-size:0.95rem">'
                    f'Q{qi}. {qtxt}</div>',
                    unsafe_allow_html=True,
                )
                sel = st.radio("", opts, key=f"quiz_q_{qi}", index=None, label_visibility="collapsed")
                st.session_state.quiz_answers[qi] = sel
                if cline:
                    m = re.search(r'[:]\s*([A-Da-d])', cline[0])
                    if m:
                        c_keys.append(m.group(1).upper())
                st.markdown("<hr>", unsafe_allow_html=True)

            if c_keys:
                if st.button("🚀 Submit & See Score", type="primary", use_container_width=True, key="quiz_sub"):
                    answers = [st.session_state.quiz_answers.get(i) for i in range(1, len(c_keys) + 1)]
                    if None in answers:
                        st.warning("⚠️ Answer all questions before submitting.")
                    else:
                        score = sum(
                            1 for i, ua in enumerate(answers)
                            if ua and ua.strip().upper().startswith(c_keys[i])
                        )
                        st.session_state.quiz_score = score

                if st.session_state.quiz_score is not None:
                    sc  = st.session_state.quiz_score
                    tot = len(c_keys)
                    pct = int(sc / tot * 100) if tot else 0
                    st.markdown("<hr>", unsafe_allow_html=True)
                    st.markdown(
                        f'<div style="text-align:center;margin-bottom:1.5rem">'
                        f'<div class="lf-score-badge">{pct}%</div>'
                        f'<div style="font-family:\'Syne\',sans-serif;font-size:1.05rem;font-weight:700;'
                        f'color:{TEXT};margin-top:0.6rem">Exam Readiness Score</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    m1, m2, m3 = st.columns(3)
                    with m1: st.metric("Correct",    f"{sc} / {tot}")
                    with m2: st.metric("Score",      f"{pct}%")
                    with m3: st.metric("Exam Ready", f"{min(pct + 10, 100)}%")
                    st.progress(pct / 100)
                    if   pct >= 80: st.success("🎉 Excellent! You are fully exam ready.")
                    elif pct >= 60: st.info("👍 Good effort — review the topics you missed.")
                    elif pct >= 40: st.warning("📚 Keep going — re-read your notes and retry.")
                    else:           st.error("🔴 More study needed — start from Notes and build up.")

    # ── TAB 3: FEYNMAN & REFLECT ────────────────────────────────────────────
    with tab3:
        ref_col, exam_col = st.columns(2)
        with ref_col:
            if st.button("🤔 Reflection Questions", use_container_width=True, key="gen_ref"):
                result = generate("Reflection", content)
                if result:
                    st.session_state.out_content = result
                    st.session_state.out_label   = "Reflection"
                    st.rerun()
        with exam_col:
            if st.button("📝 Mock Exam Paper", use_container_width=True, key="gen_exam_t"):
                result = generate("Exam Mode", content)
                if result:
                    st.session_state.out_content = result
                    st.session_state.out_label   = "Exam Mode"
                    st.rerun()

        if st.session_state.out_label in ["Reflection", "Exam Mode"] and st.session_state.out_content:
            with st.expander(f"📄 {st.session_state.out_label}", expanded=True):
                st.markdown(st.session_state.out_content)
                st.download_button(
                    "⬇ Download",
                    data=st.session_state.out_content,
                    file_name=f"{st.session_state.out_label.replace(' ', '_')}.txt",
                    mime="text/plain", key="dl_ref",
                )

        st.markdown('<div class="lf-divider">Feynman Technique Checker</div>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:0.85rem;color:{TEXT2};margin-bottom:0.75rem;line-height:1.6">'
            f'Write your explanation below. AI will score your understanding /10, '
            f'find gaps, and give you 3 targeted improvement tips.</p>',
            unsafe_allow_html=True,
        )
        feynman_in = st.text_area(
            "Explain in your own words:",
            height=120,
            placeholder="In my own words, this topic is about... The key idea is... It works because...",
            key="feynman_ta",
        )
        if st.button("🔬 Analyse My Understanding", type="primary", use_container_width=True, key="btn_feynman"):
            if not feynman_in.strip():
                st.warning("Write your explanation first.")
            else:
                p = build_prompt(
                    f"Topic: {topic_input or 'the uploaded content'}\n\nStudent explanation:\n{feynman_in}",
                    "Feynman",
                )
                with st.spinner("🔍 Analysing your explanation..."):
                    fb = ai(p, 0.3)
                st.session_state.feynman_fb = fb

        if st.session_state.feynman_fb:
            st.markdown(f'<div class="feynman-card">{st.session_state.feynman_fb}</div>',
                        unsafe_allow_html=True)

    # ── TAB 4: AI TUTOR ─────────────────────────────────────────────────────
    with tab4:
        st.markdown(
            f'<p style="font-size:0.81rem;color:{TEXT3};margin-bottom:1rem">'
            f'Your Socratic AI tutor asks probing questions to challenge and deepen your thinking.</p>',
            unsafe_allow_html=True,
        )
        if st.button("🤖 Ask Me a Question", type="primary", use_container_width=True, key="tutor_ask"):
            with st.spinner("🧠 Crafting a challenging question..."):
                q = ai(build_prompt(content, "Socratic"), 0.7)
            st.session_state.tutor_history.append({"role": "ai", "msg": q})
            st.rerun()

        for msg in st.session_state.tutor_history:
            if msg["role"] == "ai":
                st.markdown(
                    f'<div class="lf-bubble-ai-label">AI Tutor</div>'
                    f'<div class="lf-bubble-ai">{msg["msg"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="lf-bubble-user-label">You</div>'
                    f'<div class="lf-bubble-user">{msg["msg"]}</div>',
                    unsafe_allow_html=True,
                )

        if st.session_state.tutor_history:
            reply = st.text_input(
                "Your answer:",
                key="tutor_input",
                placeholder="Think carefully, then type your answer...",
            )
            ta1, ta2 = st.columns([5, 1])
            with ta1:
                if st.button("📤 Send Answer", use_container_width=True, key="tutor_send"):
                    if reply.strip():
                        st.session_state.tutor_history.append({"role": "user", "msg": reply})
                        follow_up = (
                            f"Topic: {topic_input or 'the uploaded content'}.\n"
                            f"The student answered: {reply}\n"
                            f"Ask ONE short, deeper Socratic follow-up question that builds on their answer. "
                            f"Push their thinking further. One sentence only. No preamble."
                        )
                        with st.spinner("💭 Thinking..."):
                            fq = ai(follow_up, 0.7)
                        st.session_state.tutor_history.append({"role": "ai", "msg": fq})
                        st.rerun()
            with ta2:
                if st.button("🗑 Clear", use_container_width=True, key="tutor_clr"):
                    st.session_state.tutor_history = []
                    st.rerun()

    # ── STEP 4: FULL EXAM MODE ───────────────────────────────────────────────
    st.markdown("""<div class="lf-section">
  <div class="lf-section-num">4</div>
  <div>
    <div class="lf-section-title">Full Exam Mode</div>
    <div class="lf-section-sub">Complete exam paper — MCQ · Fill in blanks · Short answer · Essay question</div>
  </div>
</div>""", unsafe_allow_html=True)

    if st.button("🎓 Generate Full Exam Paper", type="primary", use_container_width=True, key="btn_exam_full"):
        result = generate("Exam Mode", content)
        if result:
            st.session_state.out_content = result
            st.session_state.out_label   = "Exam Mode"
            st.rerun()

    if st.session_state.out_label == "Exam Mode" and st.session_state.out_content:
        st.markdown(f'<div class="lf-output">', unsafe_allow_html=True)
        st.markdown(st.session_state.out_content)
        st.markdown('</div>', unsafe_allow_html=True)
        st.download_button(
            "⬇ Download Exam Paper (.txt)",
            data=st.session_state.out_content,
            file_name=f"exam_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            key="dl_exam_full",
        )

else:
    # ── EMPTY STATE ──────────────────────────────────────────────────────────
    st.markdown(f"""<div class="lf-empty">
  <span class="lf-empty-icon">📖</span>
  <div class="lf-empty-title">Generate Notes first to unlock all testing features</div>
  <div class="lf-empty-sub">
    Enter a topic above and click <strong>📝 Notes</strong> to get started.<br>
    Flashcards · Quiz · Feynman Check · AI Tutor · Exam Mode all unlock automatically.
  </div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SESSION HISTORY
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.history:
    st.markdown("""<div class="lf-section">
  <div class="lf-section-num" style="background:linear-gradient(135deg,#0f766e,#0891b2)">📜</div>
  <div>
    <div class="lf-section-title">Session History</div>
    <div class="lf-section-sub">Everything generated this session — download any output</div>
  </div>
</div>""", unsafe_allow_html=True)

    for i, item in enumerate(reversed(st.session_state.history)):
        label = f"{item['format']}  ·  {item['topic'][:40]}  ·  {item['ts']}"
        with st.expander(label):
            st.markdown(item.get("output", ""))
            st.download_button(
                "⬇ Download",
                data=item.get("output", ""),
                file_name=f"{item['format'].replace(' ', '_')}_{i}.txt",
                mime="text/plain",
                key=f"hist_{i}",
            )