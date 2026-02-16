import streamlit as st
import google.generativeai as genai
import PyPDF2
from docx import Document
import json
import datetime

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Reflective Learning Studio",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# GEMINI CONFIG
# ==========================================================

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ==========================================================
# STYLING
# ==========================================================

st.markdown("""
<style>
.block-container {
    max-width: 1100px;
    margin: auto;
}
.stButton>button {
    border-radius: 8px;
    height: 3em;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# SESSION STATE
# ==========================================================

if "current_data" not in st.session_state:
    st.session_state.current_data = {}

if "history" not in st.session_state:
    st.session_state.history = []

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def generate_all(text, difficulty, persona, creativity, length):

    prompt = f"""
Return ONLY valid JSON in this structure:

{{
  "notes": "...",
  "flashcards": [{{"question":"...","answer":"..."}}],
  "quiz": [{{"question":"...","options":["A","B","C","D"],"answer":"..."}}],
  "reflection": "...",
  "study_plan": "..."
}}

Content:
{text}

Difficulty: {difficulty}
Style Persona: {persona}
Creativity Level: {creativity}
Response Length: {length}

Adjust vocabulary, depth, and tone accordingly.
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": creativity,
            "max_output_tokens": 1500
        }
    )

    try:
        return json.loads(response.text)
    except:
        st.error("Parsing error. Retry.")
        return {}

def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "\n".join([page.extract_text() for page in reader.pages])

def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def read_txt(file):
    return file.read().decode("utf-8")

# ==========================================================
# SIDEBAR (PROFESSIONAL CONTROLS)
# ==========================================================

st.sidebar.title("⚙ Professional Controls")

difficulty = st.sidebar.radio(
    "Difficulty Level",
    ["Beginner", "Intermediate", "Advanced"]
)

persona = st.sidebar.radio(
    "Explanation Persona",
    [
        "Child-Friendly",
        "School Teacher",
        "University Professor",
        "Scientist",
        "Psychological",
        "Exam-Oriented",
        "Analytical",
        "Conversational",
        "Motivational"
    ]
)

creativity = st.sidebar.slider(
    "Creativity Level",
    0.1, 1.0, 0.6
)

length = st.sidebar.radio(
    "Response Length",
    ["Concise", "Balanced", "Detailed"]
)

st.sidebar.divider()

st.sidebar.subheader("Session Analytics")
st.sidebar.write(f"Total Sessions: {len(st.session_state.history)}")

if st.sidebar.button("Clear History"):
    st.session_state.history = []
    st.success("History Cleared")

# ==========================================================
# MAIN UI
# ==========================================================

st.title("📚 Reflective Learning Studio")
st.caption("Adaptive AI Learning System • Professional Mode")
st.divider()

uploaded = st.file_uploader("Upload PDF, DOCX, TXT", type=["pdf", "docx", "txt"])

file_text = ""

if uploaded:
    if uploaded.type == "application/pdf":
        file_text = read_pdf(uploaded)
    elif "document" in uploaded.type:
        file_text = read_docx(uploaded)
    else:
        file_text = read_txt(uploaded)
    st.success("File loaded successfully.")

manual = st.text_area("Enter Topic or Notes")

content = manual.strip() if manual.strip() else file_text

# ==========================================================
# GENERATE BUTTON
# ==========================================================

if st.button("Generate Learning Content", use_container_width=True):

    if not content:
        st.warning("Enter content first.")
    else:
        with st.spinner("Generating..."):
            result = generate_all(
                content[:9000],
                difficulty,
                persona,
                creativity,
                length
            )

            st.session_state.current_data = result

            # Save to history
            st.session_state.history.append({
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "topic_preview": content[:50],
                "data": result
            })

        st.success("Generation Complete")

# ==========================================================
# HISTORY SECTION
# ==========================================================

if st.session_state.history:

    st.divider()
    st.subheader("🕒 Previous Sessions")

    for i, session in enumerate(reversed(st.session_state.history)):
        if st.button(
            f"{session['timestamp']} — {session['topic_preview']}",
            key=f"history_{i}"
        ):
            st.session_state.current_data = session["data"]

# ==========================================================
# SWITCH FORMATS
# ==========================================================

if st.session_state.current_data:

    st.divider()

    view = st.radio(
        "Switch Format",
        ["Notes", "Flashcards", "Quiz", "Reflection", "Study Plan"],
        horizontal=True
    )

    data = st.session_state.current_data

    # NOTES
    if view == "Notes":
        st.markdown(data.get("notes", ""))

    # FLASHCARDS
    elif view == "Flashcards":
        for i, card in enumerate(data.get("flashcards", [])):
            st.markdown(f"### {card['question']}")
            if st.button("Reveal", key=f"flash_{i}"):
                st.success(card["answer"])

    # QUIZ
    elif view == "Quiz":
        quiz = data.get("quiz", [])
        selections = []
        score = 0

        for i, q in enumerate(quiz):
            st.markdown(f"### {q['question']}")
            choice = st.radio("Select Option", q["options"], key=f"quiz_{i}")
            selections.append(choice)

        if st.button("Submit Quiz"):
            for i, q in enumerate(quiz):
                if selections[i] == q["answer"]:
                    score += 1
            st.success(f"Score: {score} / {len(quiz)}")

    # REFLECTION
    elif view == "Reflection":
        st.markdown(data.get("reflection", ""))

    # STUDY PLAN
    elif view == "Study Plan":
        st.markdown(data.get("study_plan", ""))
