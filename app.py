import streamlit as st
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# -----------------------------
# LOAD API KEY
# -----------------------------
load_dotenv()

api_key = os.getenv("LATENTSTACK_API_KEY")

if not api_key:
    st.error("LATENTSTACK_API_KEY not found in .env file.")
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://latentstack.dev/v1"
)

MODEL = "gemini-3.1-pro"

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Physics Misconception Detector",
    page_icon="🧠",
    layout="wide"
)


# -----------------------------
# PHYSICS SYLLABUS
# -----------------------------
SYLLABUS = {
    "First Year": {
        "Physics": {
            "Mechanics": [
                "Motion in One Dimension",
                "Velocity and Acceleration",
                "Newton's Laws of Motion",
                "Work, Energy and Power",
                "Momentum and Collisions",
                "Circular Motion"
            ],
            "Waves": [
                "Simple Harmonic Motion",
                "Wave Motion",
                "Sound Waves"
            ],
            "Thermodynamics": [
                "Temperature and Heat",
                "Laws of Thermodynamics",
                "Heat Engines"
            ]
        }
    },

    "Second Year": {
        "Physics": {
            "Electromagnetism": [
                "Electric Field",
                "Electric Potential",
                "Current Electricity",
                "Magnetic Field",
                "Electromagnetic Induction"
            ],
            "Optics": [
                "Ray Optics",
                "Wave Optics",
                "Interference",
                "Diffraction"
            ],
            "Modern Physics": [
                "Photoelectric Effect",
                "Atomic Physics",
                "Nuclear Physics",
                "Semiconductors"
            ]
        }
    }
}


# -----------------------------
# SESSION STATE
# -----------------------------
defaults = {
    "page": "home",
    "year": None,
    "subject": None,
    "chapter": None,
    "subtopic": None,
    "questions": [],
    "answers": {},
    "reasoning": {},
    "current_question": 0,
    "results": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -----------------------------
# AI FUNCTION
# -----------------------------
def ask_ai(prompt):

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert Physics teacher and misconception detector. "
                    "Focus on understanding the student's reasoning, not just whether "
                    "the final answer is correct."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4,
        max_completion_tokens=6000
    )

    return response.choices[0].message.content


# -----------------------------
# GENERATE 20 QUESTIONS
# -----------------------------
def generate_assignment(year, subject, chapter, subtopic):

    prompt = f"""
Create a Physics assignment for:

Year: {year}
Subject: {subject}
Chapter: {chapter}
Subtopic: {subtopic}

Generate EXACTLY 20 multiple-choice questions.

The questions should test conceptual understanding and should contain
common student misconceptions.

For each question provide:

1. question
2. options with exactly four choices A, B, C, D
3. correct_answer
4. misconception

Return ONLY valid JSON in this format:

[
  {{
    "question": "...",
    "options": {{
      "A": "...",
      "B": "...",
      "C": "...",
      "D": "..."
    }},
    "correct_answer": "A",
    "misconception": "..."
  }}
]

Do not add markdown.
Do not add explanations outside the JSON.
"""

    result = ask_ai(prompt)

    # Remove accidental markdown fences
    result = result.replace("```json", "").replace("```", "").strip()

    questions = json.loads(result)

    return questions[:20]


# -----------------------------
# ANALYZE STUDENT ANSWERS
# -----------------------------
def analyze_assignment():

    data = []

    for i, question in enumerate(st.session_state.questions):

        data.append({
            "question": question["question"],
            "options": question["options"],
            "correct_answer": question["correct_answer"],
            "student_answer": st.session_state.answers.get(i, ""),
            "student_reasoning": st.session_state.reasoning.get(i, "")
        })

    prompt = f"""
Analyze this student's Physics assignment.

Topic:
Year: {st.session_state.year}
Subject: {st.session_state.subject}
Chapter: {st.session_state.chapter}
Subtopic: {st.session_state.subtopic}

Student responses:

{json.dumps(data, indent=2)}

Provide a detailed but student-friendly report.

Include:

1. Total score out of 20
2. Percentage
3. Questions answered incorrectly
4. The student's major misconceptions
5. Evidence from the student's reasoning
6. Correct Physics concepts
7. Simple intuitive explanations
8. Suggestions for improvement

IMPORTANT:
Do not simply say "wrong".
Identify WHY the student's thinking may be wrong.

Format the response with clear headings and bullet points.
"""

    return ask_ai(prompt)


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    st.title("🧠 Physics Misconception Detector")

    st.subheader(
        "Don't just find the wrong answer. Find the wrong thinking."
    )

    st.write(
        "An AI-powered Physics learning platform that analyzes "
        "how students think."
    )

    st.write("")

    if st.button("🚀 Start Learning", use_container_width=True):

        st.session_state.page = "year"
        st.rerun()


# ============================================================
# YEAR SELECTION
# ============================================================

elif st.session_state.page == "year":

    st.title("🎓 Select Your Year")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📘 First Year", use_container_width=True):

            st.session_state.year = "First Year"
            st.session_state.page = "subject"
            st.rerun()

    with col2:
        if st.button("📗 Second Year", use_container_width=True):

            st.session_state.year = "Second Year"
            st.session_state.page = "subject"
            st.rerun()


# ============================================================
# SUBJECT SELECTION
# ============================================================

elif st.session_state.page == "subject":

    st.title(f"📚 {st.session_state.year}")

    subjects = list(
        SYLLABUS[st.session_state.year].keys()
    )

    st.subheader("Select Subject")

    for subject in subjects:

        if st.button(
            f"📖 {subject}",
            use_container_width=True
        ):

            st.session_state.subject = subject
            st.session_state.page = "chapter"
            st.rerun()

    if st.button("⬅ Back"):

        st.session_state.page = "year"
        st.rerun()


# ============================================================
# CHAPTER SELECTION
# ============================================================

elif st.session_state.page == "chapter":

    st.title("📑 Select Chapter")

    chapters = list(
        SYLLABUS[
            st.session_state.year
        ][
            st.session_state.subject
        ].keys()
    )

    for chapter in chapters:

        if st.button(
            f"📘 {chapter}",
            use_container_width=True
        ):

            st.session_state.chapter = chapter
            st.session_state.page = "subtopic"
            st.rerun()

    if st.button("⬅ Back"):

        st.session_state.page = "subject"
        st.rerun()


# ============================================================
# SUBTOPIC SELECTION
# ============================================================

elif st.session_state.page == "subtopic":

    st.title(
        f"📖 {st.session_state.chapter}"
    )

    subtopics = SYLLABUS[
        st.session_state.year
    ][
        st.session_state.subject
    ][
        st.session_state.chapter
    ]

    st.subheader("Select Subtopic")

    for subtopic in subtopics:

        if st.button(
            f"🔹 {subtopic}",
            use_container_width=True
        ):

            st.session_state.subtopic = subtopic
            st.session_state.page = "assignment_start"
            st.rerun()

    if st.button("⬅ Back"):

        st.session_state.page = "chapter"
        st.rerun()


# ============================================================
# ASSIGNMENT START
# ============================================================

elif st.session_state.page == "assignment_start":

    st.title("📝 Assignment")

    st.success(
        f"{st.session_state.year} → "
        f"{st.session_state.subject} → "
        f"{st.session_state.chapter} → "
        f"{st.session_state.subtopic}"
    )

    st.write("### Your assignment contains 20 questions.")

    st.write(
        "Each question is designed to test conceptual understanding "
        "and identify possible misconceptions."
    )

    if st.button(
        "🚀 Generate 20 Questions",
        use_container_width=True
    ):

        with st.spinner(
            "AI is preparing your 20-question assignment..."
        ):

            try:

                questions = generate_assignment(
                    st.session_state.year,
                    st.session_state.subject,
                    st.session_state.chapter,
                    st.session_state.subtopic
                )

                st.session_state.questions = questions
                st.session_state.answers = {}
                st.session_state.reasoning = {}
                st.session_state.current_question = 0
                st.session_state.page = "assignment"

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not generate assignment: {e}"
                )

    if st.button("⬅ Back"):

        st.session_state.page = "subtopic"
        st.rerun()

# ============================================================
# ASSIGNMENT
# ============================================================

elif st.session_state.page == "assignment":

    questions = st.session_state.questions
    total = len(questions)
    current = st.session_state.current_question
    question = questions[current]

    st.title("📝 Physics Assignment")

    st.progress((current + 1) / total)

    st.write(
        f"### Question {current + 1} of {total}"
    )

    st.write(
        f"**{question['question']}**"
    )

    # -----------------------------
    # OPTIONS
    # -----------------------------

    options = question["options"]

    answer = st.radio(
        "Choose your answer:",
        [
            f"A. {options['A']}",
            f"B. {options['B']}",
            f"C. {options['C']}",
            f"D. {options['D']}"
        ],
        key=f"answer_{current}"
    )

    # -----------------------------
    # REASONING
    # -----------------------------

    st.write("### 🧠 Explain your thinking")

    reasoning = st.text_area(
        "Why did you choose this answer?",
        placeholder=(
            "Explain why you selected this answer. "
            "Write your formula, concept, calculation, "
            "or reasoning in your own words."
        ),
        height=150,
        key=f"reasoning_{current}"
    )

    st.write("")

    # -----------------------------
    # ANALYZE THINKING BUTTON
    # -----------------------------

    if st.button(
        "🔍 Analyze My Thinking",
        use_container_width=True
    ):

        if not answer:

            st.warning(
                "⚠️ Please select an answer first."
            )

        elif not reasoning.strip():

            st.warning(
                "⚠️ Please explain your thinking first."
            )

        else:

            student_answer = answer[0]

            analysis_prompt = f"""
You are a Physics Misconception Detector.

Analyze the student's reasoning for this question.

Question:
{question['question']}

Options:
A. {options['A']}
B. {options['B']}
C. {options['C']}
D. {options['D']}

Correct answer:
{question['correct_answer']}

Student selected:
{student_answer}

Student's reasoning:
{reasoning}

Expected possible misconception:
{question.get('misconception', 'Not provided')}

IMPORTANT:

Do NOT judge only the final answer.

Analyze the student's actual thinking.

Identify:

1. Whether the student's answer is correct or incorrect.
2. What the student appears to believe.
3. The specific physics misconception, if any.
4. Evidence from the student's reasoning.
5. The correct physics principle.
6. A simple intuitive explanation.
7. How the student should think about this type of problem next time.

If the student's reasoning is too short or unclear,
say that the reasoning does not provide enough evidence
to identify a specific misconception.

Be supportive and student-friendly.

Use clear headings.
"""

            with st.spinner(
                "🧠 AI is analyzing your thinking..."
            ):

                try:

                    analysis = ask_ai(analysis_prompt)

                    st.session_state[
                        f"analysis_{current}"
                    ] = analysis

                except Exception as e:

                    st.error(
                        f"AI analysis error: {e}"
                    )

    # -----------------------------
    # SHOW AI ANALYSIS
    # -----------------------------

    if f"analysis_{current}" in st.session_state:

        st.divider()

        st.subheader("🤖 AI Analysis of Your Thinking")

        st.markdown(
            st.session_state[
                f"analysis_{current}"
            ]
        )

    st.write("")

    # -----------------------------
    # SAVE & NEXT
    # -----------------------------

    if st.button(
        "💾 Save & Next ➡️",
        use_container_width=True
    ):

        if not answer:

            st.warning(
                "⚠️ Please select an answer."
            )

        elif not reasoning.strip():

            st.warning(
                "⚠️ Please explain your thinking."
            )

        else:

            # Save answer
            st.session_state.answers[current] = answer[0]

            # Save reasoning
            st.session_state.reasoning[current] = reasoning

            # Move to next question
            if current < total - 1:

                st.session_state.current_question += 1

                st.rerun()

            else:

                # All questions completed
                st.session_state.page = "analyzing"

                st.rerun()





# ============================================================
# ANALYZING
# ============================================================

elif st.session_state.page == "analyzing":

    st.title("🤖 AI Analysis")

    st.write(
        "Your assignment is complete."
    )

    with st.spinner(
        "AI is analyzing your reasoning and detecting misconceptions..."
    ):

        try:

            result = analyze_assignment()

            st.session_state.results = result
            st.session_state.page = "results"

            st.rerun()

        except Exception as e:

            st.error(
                f"AI analysis error: {e}"
            )

            if st.button("Try Again"):

                st.rerun()


# ============================================================
# RESULTS
# ============================================================

elif st.session_state.page == "results":

    st.title("📊 Assignment Results")

    st.success("Your assignment has been analyzed!")

    st.write(
        f"**Year:** {st.session_state.year}"
    )

    st.write(
        f"**Subject:** {st.session_state.subject}"
    )

    st.write(
        f"**Chapter:** {st.session_state.chapter}"
    )

    st.write(
        f"**Subtopic:** {st.session_state.subtopic}"
    )

    st.divider()

    st.markdown(
        st.session_state.results
    )

    st.divider()

    if st.button(
        "🔄 Start Another Assignment",
        use_container_width=True
    ):

        st.session_state.questions = []
        st.session_state.answers = {}
        st.session_state.reasoning = {}
        st.session_state.results = None
        st.session_state.page = "year"

        st.rerun()