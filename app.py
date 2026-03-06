import streamlit as st
import google.generativeai as genai
import PyPDF2
from docx import Document
import datetime
import time
import re

st.set_page_config(page_title="LearnFlow AI", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

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

if dark:
    BG = "#05080f";
    SB_BG = "#080c18";
    CARD = "#0c1220";
    BORDER = "#1c2e50"
    TEXT = "#e2eaf8";
    TEXT2 = "#8aaad4";
    TEXT3 = "#4a78aa";
    ACCENT = "#3b82f6";
    ACCENT2 = "#6366f1"
    INPUT = "#0a1020";
    BTN = "#0e1c35";
    BTN_T = "#7aaad8"
    HERO_BG = "linear-gradient(135deg,#060d1e,#091428,#050b18)";
    HERO_BR = "#1c3060"
    HTITLE = "linear-gradient(135deg,#e2eaf8,#93c5fd,#818cf8,#c084fc)"
    PILL_BG = "#091428";
    PILL_T = "#4a78aa";
    FC_BG = "#0a1428"
    PROG_BG = "#1a2e50";
    STAT_V = "#60a5fa";
    EYEBROW = "#2a5898"
else:
    BG = "#f0f4ff";
    SB_BG = "#e2eaf8";
    CARD = "#ffffff";
    BORDER = "#c0d0ee"
    TEXT = "#0f1a30";
    TEXT2 = "#2a3a5a";
    TEXT3 = "#4a5a7a";
    ACCENT = "#2563eb";
    ACCENT2 = "#4338ca"
    INPUT = "#ffffff";
    BTN = "#eef2ff";
    BTN_T = "#2563eb"
    HERO_BG = "linear-gradient(135deg,#dce8ff,#eef3ff,#f0ecff)";
    HERO_BR = "#b0c8f0"
    HTITLE = "linear-gradient(135deg,#1a3a8f,#2563eb,#4f46e5,#7c3aed)"
    PILL_BG = "#eef2ff";
    PILL_T = "#3a5aaa";
    FC_BG = "#f5f8ff"
    PROG_BG = "#d0daf0";
    STAT_V = "#2563eb";
    EYEBROW = "#4a78cc"

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');
html,body,[data-testid="stApp"]{{background-color:{BG}!important;color:{TEXT}!important;font-family:'Plus Jakarta Sans',sans-serif!important;}}
#MainMenu,footer,header,[data-testid="stToolbar"]{{display:none!important;}}
.block-container{{max-width:1400px!important;margin:0!important;padding:0!important;}}
[data-testid="stSidebar"]{{background-color:{SB_BG}!important;border-right:1px solid {BORDER}!important;width:350px!important;}}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] label{{color:{TEXT2}!important;}}
.stButton>button{{background:{BTN}!important;color:{BTN_T}!important;border:1px solid {BORDER}!important;border-radius:10px!important;font-weight:600!important;padding:0.5rem 1rem!important;transition:all 0.2s!important;}}
.stButton>button:hover{{border-color:{ACCENT}!important;color:{ACCENT}!important;}}
.stButton>button[kind="primary"]{{background:linear-gradient(135deg,{ACCENT},{ACCENT2})!important;color:#fff!important;border:none!important;box-shadow:0 2px 12px rgba(59,130,246,0.3)!important;}}
.stButton>button[kind="primary"]:hover{{box-shadow:0 4px 16px rgba(59,130,246,0.4)!important;}}
[data-baseweb="select"]>div{{background:{INPUT}!important;border:1px solid {BORDER}!important;border-radius:10px!important;color:{TEXT}!important;}}
[data-baseweb="select"] span{{color:{TEXT}!important;}}
.stTextArea textarea{{background:{INPUT}!important;border:1px solid {BORDER}!important;border-radius:12px!important;color:{TEXT}!important;}}
.stTextArea textarea:focus{{border-color:{ACCENT}!important;box-shadow:0 0 0 3px rgba(59,130,246,0.1)!important;}}
.stFileUploader{{background:{INPUT}!important;border:1.5px dashed {BORDER}!important;border-radius:12px!important;}}
[data-testid="metric-container"]{{background:{CARD}!important;border:1px solid {BORDER}!important;border-radius:12px!important;padding:1rem!important;}}
[data-testid="stMetricValue"]{{color:{STAT_V}!important;font-family:'Space Mono',monospace!important;font-size:1.4rem!important;font-weight:700!important;}}
.sb-label{{font-family:'Space Mono',monospace;font-size:0.6rem;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:{TEXT3}!important;padding:1rem 0 0.5rem;border-bottom:1px solid {BORDER};margin-bottom:0.8rem;display:block;}}
.step-number{{width:32px;height:32px;background:linear-gradient(135deg,{ACCENT},{ACCENT2});border-radius:6px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:0.9rem;flex-shrink:0;}}
.step-title{{font-size:0.95rem;font-weight:700;color:{TEXT};}}
.step-sub{{font-size:0.78rem;color:{TEXT3};margin-top:0.1rem;}}
.fpills{{display:flex;flex-wrap:wrap;gap:0.5rem;margin:1rem 0;}}
.fp{{background:{PILL_BG};border:1px solid {BORDER};border-radius:100px;padding:0.35rem 0.8rem;font-size:0.72rem;color:{PILL_T};font-weight:500;}}
.fc-card{{background:{FC_BG};border:1px solid {BORDER};border-left:3px solid {ACCENT};border-radius:12px;padding:1.2rem;margin-bottom:0.8rem;}}
.fc-num{{font-family:'Space Mono',monospace;font-size:0.65rem;color:{TEXT3};letter-spacing:0.08em;margin-bottom:0.5rem;text-transform:uppercase;}}
.fc-q{{font-size:0.92rem;color:{TEXT2};font-weight:500;line-height:1.5;}}
.empty-state{{text-align:center;padding:3.5rem 2rem;border:1.5px dashed {BORDER};border-radius:18px;}}
.empty-icon{{font-size:3.5rem;margin-bottom:1rem;opacity:0.7;}}
.key-live{{display:inline-block;width:6px;height:6px;border-radius:50%;background:#10b981;margin-right:6px;animation:pulse 2s infinite;}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
.hero{{background:{HERO_BG};border:1px solid {HERO_BR};border-radius:20px;padding:2.2rem;margin-bottom:2rem;}}
.hero-title{{font-size:2.2rem;font-weight:800;line-height:1.2;background:{HTITLE};-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0.8rem 0;letter-spacing:-0.01em;}}
.hero-sub{{font-size:0.95rem;color:{TEXT2};line-height:1.6;margin-bottom:1.2rem;}}
.stat-val{{font-family:'Space Mono',monospace;font-size:1.1rem;font-weight:700;color:{STAT_V};}}
.stat-lbl{{font-size:0.65rem;color:{TEXT3};text-transform:uppercase;letter-spacing:0.08em;margin-top:0.2rem;}}
.stats-row{{display:flex;gap:2.5rem;margin-top:1rem;padding-top:1rem;border-top:1px solid {BORDER};}}
[data-testid="stTabs"]{{background:transparent!important;}}
.stTabs [data-baseweb="tab-list"]{{background:{INPUT}!important;border-radius:12px!important;padding:0.3rem!important;border:1px solid {BORDER}!important;gap:0.2rem!important;}}
.stTabs [data-baseweb="tab"]{{background:transparent!important;color:{TEXT3}!important;border-radius:8px!important;font-weight:600!important;font-size:0.84rem!important;border:none!important;cursor:pointer!important;padding:0.5rem 1rem!important;}}
.stTabs [aria-selected="true"]{{background:linear-gradient(135deg,{ACCENT},{ACCENT2})!important;color:#fff!important;}}
details{{background:{CARD}!important;border:1px solid {BORDER}!important;border-radius:12px!important;overflow:hidden!important;margin-bottom:0.5rem!important;}}
details>summary{{color:{TEXT2}!important;font-weight:600!important;padding:0.8rem 1rem!important;cursor:pointer!important;background:{CARD}!important;}}
[data-testid="stAlert"]{{border-radius:10px!important;font-family:'Plus Jakarta Sans',sans-serif!important;font-size:0.88rem!important;border:none!important;}}
[data-testid="stSlider"]{{padding:1rem 0!important;}}
.stSlider > div > div > div > div{{background:{ACCENT}!important;}}
</style>""", unsafe_allow_html=True)

builtin_keys = []
try:
    if "GOOGLE_API_KEYS" in st.secrets:
        builtin_keys = list(st.secrets["GOOGLE_API_KEYS"])
except:
    builtin_keys = []


def get_all_keys():
    return st.session_state.user_api_keys + builtin_keys


def user_has_key():
    return len(st.session_state.user_api_keys) > 0


def validate_key(key):
    try:
        genai.configure(api_key=key)
        r = genai.GenerativeModel("models/gemini-2.5-flash").generate_content("Say OK", generation_config={
            "max_output_tokens": 5})
        return bool(r and r.text)
    except:
        return False


def generate(prompt, creativity=0.4):
    keys = get_all_keys()
    if not keys:
        return "NO_KEYS"
    for key in keys:
        try:
            genai.configure(api_key=key)
            resp = genai.GenerativeModel("models/gemini-2.5-flash").generate_content(prompt, generation_config={
                "temperature": creativity, "max_output_tokens": 2000})
            if resp and resp.text:
                return resp.text.strip()
        except:
            time.sleep(0.8)
    return "QUOTA_EXCEEDED"


def quota_ui():
    st.error("⚠️ API quota exhausted.")
    with st.expander("🔑 Add a free key to continue", expanded=True):
        st.markdown("**Get free key →** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)")
        nk = st.text_input("Paste key:", type="password", placeholder="AIzaSy...",
                           key=f"qk_{len(st.session_state.history)}")
        if st.button("➕ Add Key & Retry", type="primary", use_container_width=True):
            if nk.strip() and nk.strip() not in st.session_state.user_api_keys:
                st.session_state.user_api_keys.append(nk.strip())
                st.success("✅ Added! Try again.")
                st.rerun()


def read_pdf(f):
    return "\n".join([p.extract_text() for p in PyPDF2.PdfReader(f).pages if p.extract_text()])


def read_docx(f):
    return "\n".join([p.text for p in Document(f).paragraphs if p.text.strip()])


def read_txt(f):
    return f.read().decode("utf-8")


FORMATS = {
    "Smart Notes": "Write structured academic notes with clear headings, subheadings and bullet points. Include key concepts and important details. Max 400 words. Format clearly with markdown.\n",
    "Flashcards": "Generate exactly 5 flashcards in this EXACT format:\n\nFlashcard 1\nQuestion: [question]\nAnswer: [answer]\n\nFlashcard 2\nQuestion: [question]\nAnswer: [answer]\n\nFlashcard 3\nQuestion: [question]\nAnswer: [answer]\n\nFlashcard 4\nQuestion: [question]\nAnswer: [answer]\n\nFlashcard 5\nQuestion: [question]\nAnswer: [answer]\n",
    "AI Quiz": "Generate exactly 5 multiple choice questions in this EXACT format:\n\nQuestion 1: [question text]\nA. [option A]\nB. [option B]\nC. [option C]\nD. [option D]\nCorrect Answer: [A/B/C/D]\n\nQuestion 2: [question text]\nA. [option A]\nB. [option B]\nC. [option C]\nD. [option D]\nCorrect Answer: [A/B/C/D]\n\nQuestion 3: [question text]\nA. [option A]\nB. [option B]\nC. [option C]\nD. [option D]\nCorrect Answer: [A/B/C/D]\n\nQuestion 4: [question text]\nA. [option A]\nB. [option B]\nC. [option C]\nD. [option D]\nCorrect Answer: [A/B/C/D]\n\nQuestion 5: [question text]\nA. [option A]\nB. [option B]\nC. [option C]\nD. [option D]\nCorrect Answer: [A/B/C/D]\n",
    "Feynman Check": "Evaluate a student's understanding. Analyze: 1) What they explained correctly 2) What's missing 3) Score out of 10 4) How to improve. Be constructive.\n",
    "Socratic Tutor": "Ask ONE thought-provoking Socratic question that challenges deep understanding, not just facts. Make it open-ended. No preamble.\n",
    "Study Plan": "Create a 5-step study plan with:\n1. Topic overview (1-2 lines)\n2. Learning objectives (3-4 bullet points)\n3. Study method and timeline\n4. Practice exercises\n5. Review strategy\n",
    "Exam Mode": "Create a full exam with:\n- 3 Multiple choice questions (with A/B/C/D options and correct answers)\n- 2 Fill in the blank questions (with answers)\n- 2 Short answer questions (with model answers)\nFormat clearly.\n",
    "Key Concepts": "List exactly 7 key concepts related to this topic. For each, provide:\n- **Concept Name**: [1-2 word name]\n- Definition: [one clear sentence]\n- Why it matters: [brief explanation]\n",
    "Mind Map": "Create a text-based mind map with:\n- Central concept at top\n- 5 main branches (topics)\n- 2-3 sub-points under each branch\nUse indentation and emojis to show hierarchy.\n",
    "Mnemonics": "Create 3 helpful mnemonics or memory tricks for remembering key concepts from this topic. Make them catchy and memorable.\n",
    "ELI5 (Explain Simply)": "Explain this topic as if talking to a 10-year-old. Use:\n- Simple words\n- Fun analogies\n- Real-world examples\n- Short sentences\nMax 200 words.\n",
}


def build_prompt(text, difficulty, persona, fmt):
    trimmed = len(text) > 3000
    text = text[:3000]
    base = f"Content:\n{text}\n\nDifficulty: {difficulty}\nPersona: {persona}\n\nInstructions:\n- Output ONLY what is requested\n- No preamble or explanation\n- Follow the format exactly\n- Be comprehensive but concise\n\n"
    return base + FORMATS.get(fmt, FORMATS["Smart Notes"]), trimmed


def gen_heading(txt):
    r = generate(f"Create a short heading (max 7 words) for this content. No quotes, no punctuation.\nContent: {txt}",
                 0.2)
    return r.strip() if r not in ("QUOTA_EXCEEDED", "NO_KEYS") else "Study Notes"


def run_gen(fmt, content, manual, difficulty, persona, creativity, save_as="output"):
    if not content:
        st.warning("⚠️ Enter a topic or upload a file first.")
        return False
    p, trimmed = build_prompt(content, difficulty, persona, fmt)
    if trimmed:
        st.caption("⚠️ Content trimmed to 3000 characters")
    with st.spinner(f"Generating {fmt}..."):
        r = generate(p, creativity)
    if r in ("QUOTA_EXCEEDED", "NO_KEYS"):
        quota_ui()
        return False
    if save_as == "notes":
        st.session_state.notes_content = r
        st.session_state.notes_heading = gen_heading(manual if manual.strip() else "Document")
        st.session_state.generated_output = None
        st.session_state.generated_heading = None
        st.session_state.quiz_score = None
    else:
        st.session_state.generated_output = r
        st.session_state.generated_heading = fmt
    st.session_state.history.append(
        {"ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "format": fmt, "topic": (manual or "Document")[:50],
         "output": r})
    return True


def show_setup():
    st.markdown(
        f"""<div style="text-align:center;padding:3rem 1rem;"><div style="font-size:3rem;margin-bottom:1rem;">🧠</div><h1 style="color:{TEXT};font-size:2.5rem;margin:0 0 0.5rem 0;">LearnFlow AI</h1><p style="color:{TEXT3};font-size:0.95rem;margin:0 0 2rem 0;">Your AI Study Companion</p></div>""",
        unsafe_allow_html=True)
    _, mc, _ = st.columns([1, 2, 1])
    with mc:
        st.markdown(
            f"<p style='text-align:center;color:{TEXT2};font-size:0.9rem;margin-bottom:1rem;'>Get your free API key from Google and paste it below to start learning.</p>",
            unsafe_allow_html=True)
        key_in = st.text_input("Paste your Gemini API key:", type="password", placeholder="AIzaSy...", key="setup_key")
        if st.button("🚀 Start Learning", type="primary", use_container_width=True):
            k = key_in.strip()
            if not k:
                st.warning("⚠️ Paste your API key above first.")
            elif not k.startswith("AIza"):
                st.warning("⚠️ Invalid — Gemini keys start with AIza")
            else:
                with st.spinner("🔍 Validating..."):
                    valid = validate_key(k)
                if valid:
                    st.session_state.user_api_keys = [k]
                    st.balloons()
                    st.success("✅ Key validated! Welcome to LearnFlow AI 🎉")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("❌ Invalid key. Please check and try again.")
        st.markdown(
            f"<p style='text-align:center;color:{TEXT3};font-size:0.8rem;margin-top:1rem;'><a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:{ACCENT};text-decoration:none;'>Get free API key →</a></p>",
            unsafe_allow_html=True)


if not user_has_key():
    show_setup()
    st.stop()

with st.sidebar:
    st.markdown(
        f"<h3 style='color:{TEXT};font-size:1.1rem;margin:0 0 0.2rem 0;'>🧠 LearnFlow AI</h3><p style='color:{TEXT3};font-size:0.65rem;margin:0 0 1rem 0;text-transform:uppercase;letter-spacing:0.1em;'>STUDY COMPANION</p>",
        unsafe_allow_html=True)
    st.markdown(f"<hr style='border:none;border-top:1px solid {BORDER};margin:0 0 1rem 0;'>", unsafe_allow_html=True)

    st.markdown('<span class="sb-label">⚙ Learning Settings</span>', unsafe_allow_html=True)
    difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"],
                              label_visibility="collapsed", key="diff")
    persona = st.selectbox("Teaching Style",
                           ["🎓 University Professor", "👩‍🏫 School Teacher", "🧒 Child-Friendly", "🔬 Scientist",
                            "📊 Analytical", "📝 Exam-Oriented", "💪 Motivational"], label_visibility="collapsed",
                           key="pers")
    st.markdown(
        f'<div style="font-size:0.75rem;color:{TEXT2};margin:0.8rem 0 0.4rem;font-weight:600;">Creativity Level: {creativity:.1f}</div>',
        unsafe_allow_html=True)
    creativity = st.slider("", 0.1, 1.0, 0.4, step=0.1, label_visibility="collapsed", key="crea")

    st.markdown('<span class="sb-label">⏱ Pomodoro Timer</span>', unsafe_allow_html=True)
    pc1, pc2 = st.columns([3, 1])
    with pc1:
        pmin = st.selectbox("Duration", [25, 10, 15, 30, 45, 60], label_visibility="collapsed", key="pmin")
    with pc2:
        if st.button("▶", use_container_width=True, key="pstart", help="Start timer"):
            st.session_state.timer_start = time.time()
            st.session_state.timer_duration = pmin * 60
    if st.session_state.timer_start:
        rem = st.session_state.timer_duration - (time.time() - st.session_state.timer_start)
        if rem > 0:
            st.markdown(
                f'<div style="font-family:Space Mono;font-size:1.8rem;font-weight:700;text-align:center;color:{STAT_V};margin:0.5rem 0;">{int(rem // 60):02d}:{int(rem % 60):02d}</div>',
                unsafe_allow_html=True)
            st.progress(1 - rem / st.session_state.timer_duration)
        else:
            st.error("🔔 Break time! Time's up.")
            if st.button("Reset Timer", use_container_width=True, key="preset"):
                st.session_state.timer_start = None
                st.rerun()

    st.markdown('<span class="sb-label">🔑 API Keys</span>', unsafe_allow_html=True)
    uk = len(st.session_state.user_api_keys)
    st.markdown(
        f'<span class="key-live"></span><span style="font-size:0.8rem;color:#10b981;font-weight:600;">{uk} personal key(s) active</span>',
        unsafe_allow_html=True)
    with st.expander("➕ Add My Own Key"):
        nk = st.text_input("", type="password", placeholder="AIzaSy...", key="sb_key", label_visibility="collapsed")
        if st.button("Add Key", use_container_width=True, key="sb_add", type="primary"):
            if not nk.strip():
                st.warning("Paste a key first")
            elif nk.strip() in st.session_state.user_api_keys:
                st.warning("Key already added")
            else:
                st.session_state.user_api_keys.append(nk.strip())
                st.success("✅ Key added!")
                st.rerun()
        if st.session_state.user_api_keys:
            if st.button("🗑 Remove All Keys", use_container_width=True, key="sb_rm"):
                st.session_state.user_api_keys = []
                st.rerun()

    st.markdown('<span class="sb-label">📊 Session Stats</span>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    with s1:
        st.metric("Generated", len(st.session_state.history))
    with s2:
        st.metric("Notes", 1 if st.session_state.notes_content else 0)
    if st.button("🗑 Reset Session", use_container_width=True, key="reset"):
        saved = st.session_state.user_api_keys
        mode = st.session_state.dark_mode
        for k, v in defaults.items():
            st.session_state[k] = v
        st.session_state.user_api_keys = saved
        st.session_state.dark_mode = mode
        st.success("Session reset!")
        st.rerun()

col1, col2 = st.columns([0.05, 20])
with col1:
    if st.button("🌙" if dark else "☀️", key="theme", help="Toggle theme", use_container_width=True):
        st.session_state.dark_mode = not dark
        st.rerun()

with col2:
    st.markdown(
        f"""<div class="hero"><div style='font-size:0.75rem;color:{EYEBROW};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.5rem;'>✦ Powered by Google Gemini 2.5 Flash</div><div class="hero-title">Learn Smarter.<br>Not Harder.</div><div class="hero-sub">Transform any topic or document into notes, flashcards, quizzes and more — in seconds.</div><div class="stats-row"><div><div class='stat-val'>10+</div><div class='stat-lbl'>AI Features</div></div><div><div class='stat-val'>∞</div><div class='stat-lbl'>Topics</div></div><div><div class='stat-val'>Free</div><div class='stat-lbl'>Forever</div></div></div></div>""",
        unsafe_allow_html=True)

    st.markdown(
        f"<div class='fpills'><span class='fp'>📝 Smart Notes</span><span class='fp'>🎴 Flashcards</span><span class='fp'>❓ AI Quiz</span><span class='fp'>🧪 Feynman Check</span><span class='fp'>🤖 Socratic Tutor</span><span class='fp'>📅 Study Plan</span><span class='fp'>🎓 Exam Mode</span><span class='fp'>🧠 Mind Map</span><span class='fp'>💡 Mnemonics</span><span class='fp'>⚡ TL;DR</span><span class='fp'>👶 ELI5</span><span class='fp'>⏱ Pomodoro</span></div>",
        unsafe_allow_html=True)

    st.markdown(
        f"<div style='display:flex;align-items:flex-start;gap:1rem;margin:1.5rem 0 1rem;'><div class='step-number'>1</div><div style='flex:1;'><div class='step-title'>Enter Topic or Upload File</div><div class='step-sub'>Type any subject, paste your notes, or upload PDF / DOCX / TXT</div></div></div>",
        unsafe_allow_html=True)

    uploaded = st.file_uploader("", type=["pdf", "docx", "txt"], label_visibility="collapsed")
    file_text = ""
    if uploaded:
        with st.spinner("Reading file..."):
            try:
                ft = uploaded.type
                if ft == "application/pdf":
                    file_text = read_pdf(uploaded)
                elif "document" in ft:
                    file_text = read_docx(uploaded)
                else:
                    file_text = read_txt(uploaded)
                st.success(f"✅ **{uploaded.name}** — {len(file_text):,} characters")
            except Exception as e:
                st.error(f"❌ Failed to read file: {str(e)[:50]}")

    manual = st.text_area("", height=100, label_visibility="collapsed",
                          placeholder="Type any topic → Photosynthesis · Newton's Laws · French Revolution · Machine Learning · Thermodynamics...")

    if file_text and manual.strip():
        content = f"Instruction:\n{manual.strip()}\n\nDocument:\n{file_text}"
    elif file_text:
        content = file_text
    else:
        content = manual.strip()

    G = dict(content=content, manual=manual, difficulty=difficulty, persona=persona, creativity=creativity)

    st.markdown(
        f"<div style='display:flex;align-items:flex-start;gap:1rem;margin:1.5rem 0 1rem;'><div class='step-number'>2</div><div style='flex:1;'><div class='step-title'>Read & Learn</div><div class='step-sub'>Start with Notes — then explore summaries, concepts and memory aids</div></div></div>",
        unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📝 Notes", use_container_width=True, key="btn_notes", type="primary"):
            if run_gen("Smart Notes", save_as="notes", **G):
                st.success("✅ Notes generated!")
    with c2:
        if st.button("⚡ TL;DR", use_container_width=True, key="btn_tldr"):
            if content:
                p, _ = build_prompt(content, difficulty, persona, "TL;DR")
                with st.spinner("Summarizing..."):
                    r = generate(p, 0.3)
                if r in ("QUOTA_EXCEEDED", "NO_KEYS"):
                    quota_ui()
                else:
                    st.session_state.tldr = r
                    st.success("✅ Summary ready!")
            else:
                st.warning("Enter a topic first.")
    with c3:
        if st.button("🔑 Key Concepts", use_container_width=True, key="btn_kc"):
            if run_gen("Key Concepts", **G):
                st.success("✅ Concepts ready!")
    with c4:
        if st.button("💡 Mnemonics", use_container_width=True, key="btn_mnem"):
            if run_gen("Mnemonics", **G):
                st.success("✅ Mnemonics ready!")

    c5, c6, c7 = st.columns(3)
    with c5:
        if st.button("🧠 Mind Map", use_container_width=True, key="btn_mm"):
            if run_gen("Mind Map", **G):
                st.success("✅ Mind map ready!")
    with c6:
        if st.button("👶 ELI5 (Explain Simply)", use_container_width=True, key="btn_eli5"):
            if run_gen("ELI5 (Explain Simply)", **G):
                st.success("✅ Explanation ready!")
    with c7:
        if st.button("📅 Study Plan", use_container_width=True, key="btn_sp"):
            if run_gen("Study Plan", **G):
                st.success("✅ Study plan ready!")

    if st.session_state.tldr:
        st.info(f"⚡ **TL;DR**\n\n{st.session_state.tldr}")

    if st.session_state.notes_content:
        with st.expander(f"📘 {st.session_state.notes_heading}", expanded=True):
            st.markdown(st.session_state.notes_content)
            st.download_button("📥 Download Notes", data=st.session_state.notes_content,
                               file_name=f"Notes_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                               mime="text/plain")

    S2 = ["Key Concepts", "Mnemonics", "Mind Map", "ELI5 (Explain Simply)", "Study Plan"]
    if st.session_state.generated_output and st.session_state.generated_heading in S2:
        with st.expander(f"📄 {st.session_state.generated_heading}", expanded=True):
            st.markdown(st.session_state.generated_output)
            st.download_button("📥 Download", data=st.session_state.generated_output,
                               file_name=f"{st.session_state.generated_heading}.txt", mime="text/plain", key="dl_s2")

    if st.session_state.notes_content:
        st.markdown(
            f"<div style='display:flex;align-items:flex-start;gap:1rem;margin:1.5rem 0 1rem;'><div class='step-number'>3</div><div style='flex:1;'><div class='step-title'>Test Your Knowledge</div><div class='step-sub'>Flashcards, Quiz, Reflection, Feynman Check & your AI Tutor</div></div></div>",
            unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs(["🎴  Flashcards", "❓  AI Quiz", "🤔  Reflect & Feynman", "🤖  Socratic Tutor"])

        with tab1:
            st.caption("Reveal answers one by one to test your memory.")
            if st.button("Generate Flashcards", use_container_width=True, type="primary", key="fc_gen"):
                run_gen("Flashcards", **G)
            if st.session_state.generated_heading == "Flashcards" and st.session_state.generated_output:
                idx = 1
                for blk in st.session_state.generated_output.split("Flashcard"):
                    if not blk.strip():
                        continue
                    parts = blk.split("Answer:")
                    if len(parts) == 2:
                        q = parts[0].replace("Question:", "").strip().lstrip("0123456789. \n")
                        a = parts[1].strip()
                        rk = f"fc_{idx}"
                        if rk not in st.session_state:
                            st.session_state[rk] = False
                        st.markdown(
                            f'<div class="fc-card"><div class="fc-num">CARD {idx} / 5</div><div class="fc-q">{q}</div></div>',
                            unsafe_allow_html=True)
                        if st.button("👁 Reveal" if not st.session_state[rk] else "🙈 Hide", key=f"fcb_{idx}"):
                            st.session_state[rk] = not st.session_state[rk]
                        if st.session_state[rk]:
                            st.success(f"**Answer:** {a}")
                        idx += 1

        with tab2:
            st.caption("Answer all 5 questions then submit for your score.")
            if st.button("Generate AI Quiz", use_container_width=True, type="primary", key="qz_gen"):
                run_gen("AI Quiz", **G)
                st.session_state.quiz_score = None
            if st.session_state.generated_heading == "AI Quiz" and st.session_state.generated_output:
                blocks = re.split(r'Question\s*\d+:', st.session_state.generated_output, flags=re.IGNORECASE)
                blocks = [b.strip() for b in blocks[1:] if b.strip()]
                u_ans, c_ans, qi = [], [], 1
                for blk in blocks[:5]:
                    lines = [l.strip() for l in blk.split("\n") if l.strip()]
                    if not lines:
                        continue
                    qtxt = lines[0]
                    opts = [l for l in lines if re.match(r'^[A-D]\.\s+', l)]
                    cline = [l for l in lines if "Correct Answer:" in l]
                    if opts and qtxt and len(opts) >= 2:
                        st.markdown(f"**Q{qi}.** {qtxt}")
                        sel = st.radio("", opts, key=f"q_{qi}", index=None, label_visibility="collapsed")
                        u_ans.append(sel)
                        if cline:
                            m = re.search(r'[A-D]', cline[0])
                            if m:
                                c_ans.append(m.group(0))
                        st.markdown("---")
                        qi += 1
                if u_ans:
                    if st.button("📝 Submit Quiz", use_container_width=True, type="primary"):
                        if None in u_ans:
                            st.warning("⚠️ Answer all questions first!")
                        else:
                            score = sum(1 for i in range(min(len(u_ans), len(c_ans))) if
                                        u_ans[i] and c_ans[i] and c_ans[i] in u_ans[i])
                            st.session_state.quiz_score = score
                    if st.session_state.quiz_score is not None:
                        sc = st.session_state.quiz_score
                        tot = len(c_ans) if c_ans else 5
                        pct = int(sc / tot * 100)
                        st.markdown("---")
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.metric("Score", f"{sc}/{tot}")
                        with m2:
                            st.metric("Percentage", f"{pct}%")
                        with m3:
                            st.metric("Exam Ready", f"{min(100, pct + 10)}%")
                        st.progress(min(1.0, (pct + 10) / 100))
                        if pct >= 80:
                            st.success("🎉 Excellent! You are exam ready.")
                        elif pct >= 50:
                            st.warning("👍 Good effort — review weak areas.")
                        else:
                            st.error("📚 Keep going — re-read notes and retry.")

        with tab3:
            rc1, rc2 = st.columns(2)
            with rc1:
                if st.button("Reflection Questions", use_container_width=True, key="ref_gen"):
                    run_gen("Study Plan", **G)
            with rc2:
                if st.button("Generate Exam Paper", use_container_width=True, key="exam_gen"):
                    run_gen("Exam Mode", **G)
            if st.session_state.generated_heading in ["Study Plan", "Exam Mode"] and st.session_state.generated_output:
                st.markdown(st.session_state.generated_output)
                st.download_button("📥 Download", data=st.session_state.generated_output,
                                   file_name=f"{st.session_state.generated_heading}.txt", mime="text/plain",
                                   key="dl_ref")
            st.markdown("---")
            st.markdown("#### 🧪 Feynman Technique Checker")
            st.caption("Explain the topic in your own words. AI scores your understanding.")
            fi = st.text_area("Your explanation:", height=120, key="feynman_ta",
                              placeholder="In simple terms, this topic is about...")
            if st.button("✅ Analyse My Understanding", use_container_width=True, type="primary"):
                if not fi.strip():
                    st.warning("Write your explanation first!")
                else:
                    cp = f"Topic: {manual if manual.strip() else 'the uploaded content'}\n\nStudent explanation:\n{fi}\n\nEvaluate this explanation."
                    fp, _ = build_prompt(cp, difficulty, persona, "Feynman Check")
                    with st.spinner("Analysing..."):
                        fr = generate(fp, 0.3)
                    if fr in ("QUOTA_EXCEEDED", "NO_KEYS"):
                        quota_ui()
                    else:
                        st.session_state.feynman_feedback = fr
            if st.session_state.feynman_feedback:
                st.markdown(st.session_state.feynman_feedback)

        with tab4:
            st.caption("AI asks deep Socratic questions — challenges real understanding, not just memory.")
            if st.button("🤔 Ask Me a Question", use_container_width=True, type="primary"):
                sp, _ = build_prompt(content, difficulty, "Analytical", "Socratic Tutor")
                with st.spinner("Thinking..."):
                    sr = generate(sp, 0.6)
                if sr in ("QUOTA_EXCEEDED", "NO_KEYS"):
                    quota_ui()
                else:
                    st.session_state.tutor_history.append({"role": "tutor", "msg": sr})
            for msg in st.session_state.tutor_history:
                if msg["role"] == "tutor":
                    st.markdown(
                        f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:0.8rem;margin:0.5rem 0;color:{TEXT2};font-size:0.85rem;">🤖 <strong>Tutor:</strong> {msg["msg"]}</div>',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:0.8rem;margin:0.5rem 0;color:#34d399;font-size:0.85rem;text-align:right;">👤 <strong>You:</strong> {msg["msg"]}</div>',
                        unsafe_allow_html=True)
            if st.session_state.tutor_history:
                reply = st.text_input("Your answer:", key="tutor_in", placeholder="Type your answer...")
                tc1, tc2 = st.columns([4, 1])
                with tc1:
                    if st.button("Send ➡️", use_container_width=True):
                        if reply.strip():
                            st.session_state.tutor_history.append({"role": "student", "msg": reply})
                            fup = f"Original topic: {manual or 'the uploaded content'}\nStudent answered: {reply}\n\nAsk a deeper Socratic follow-up question. Make it thought-provoking. Short."
                            fp2, _ = build_prompt(fup, difficulty, "Analytical", "Socratic Tutor")
                            with st.spinner("Thinking..."):
                                fur = generate(fp2, 0.6)
                            if fur not in ("QUOTA_EXCEEDED", "NO_KEYS"):
                                st.session_state.tutor_history.append({"role": "tutor", "msg": fur})
                            st.rerun()
                with tc2:
                    if st.button("Reset", use_container_width=True):
                        st.session_state.tutor_history = []
                        st.rerun()

    else:
        st.markdown(
            f"""<div class='empty-state'><div class='empty-icon'>📖</div><div style='font-size:0.9rem;font-weight:700;color:{TEXT2};margin-bottom:0.3rem;'>Generate Notes first to unlock all testing features</div><div style='font-size:0.8rem;color:{TEXT3};'>Enter a topic above and click "📝 Notes" to get started</div></div>""",
            unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown(
            f"<div style='display:flex;align-items:flex-start;gap:1rem;margin:2rem 0 1rem;'><div style='width:32px;height:32px;background:linear-gradient(135deg,#0f766e,#0891b2);border-radius:6px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:0.9rem;flex-shrink:0;'>📜</div><div><div class='step-title'>Session History</div><div class='step-sub'>All generated content from this session</div></div></div>",
            unsafe_allow_html=True)
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"**{item['format']}** — {item['topic']} | {item['ts']}"):
                st.markdown(item.get("output", ""))
                st.download_button("📥 Download", data=item.get("output", ""), file_name=f"{item['format']}_{i}.txt",
                                   mime="text/plain", key=f"hl_{i}")