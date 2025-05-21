import streamlit as st
import time
from utils import (
    generate_personalized_content_for_teacher,
    generate_quiz_for_teacher,
    simplify_student_text,
    generate_quiz_from_student_text,
    answer_follow_up_question,
    grade_assessment
)

# Page Configuration
st.set_page_config(page_title="EduTutor AI", layout="wide", initial_sidebar_state="expanded")
st.title("🎓 EduTutor AI")
st.caption("Personalized Learning and Assessment System")

# --- Session State Initialization ---
if 'user_role' not in st.session_state: st.session_state.user_role = None
if 'teacher_content_input' not in st.session_state: st.session_state.teacher_content_input = ""
if 'teacher_generated_questions' not in st.session_state: st.session_state.teacher_generated_questions = []
if 'student_main_input_text' not in st.session_state: st.session_state.student_main_input_text = ""
if 'processed_text_for_qna_context' not in st.session_state: st.session_state.processed_text_for_qna_context = ""
if 'simplified_student_text' not in st.session_state: st.session_state.simplified_student_text = ""
if 'student_custom_questions' not in st.session_state: st.session_state.student_custom_questions = []
if 'student_custom_answers' not in st.session_state: st.session_state.student_custom_answers = {}
if 'student_custom_quiz_submitted' not in st.session_state: st.session_state.student_custom_quiz_submitted = False
if 'student_follow_up_question_input' not in st.session_state: st.session_state.student_follow_up_question_input = ""
if 'student_conversation_history' not in st.session_state: st.session_state.student_conversation_history = []

# --- Switch Role Logic ---
def switch_role(new_role):
    st.session_state.teacher_content_input = ""
    st.session_state.teacher_generated_questions = []
    st.session_state.student_main_input_text = ""
    st.session_state.processed_text_for_qna_context = ""
    st.session_state.simplified_student_text = ""
    st.session_state.student_custom_questions = []
    st.session_state.student_custom_answers = {}
    st.session_state.student_custom_quiz_submitted = False
    st.session_state.student_follow_up_question_input = ""
    st.session_state.student_conversation_history = []
    st.session_state.user_role = new_role
    st.rerun()

# --- Role Selection UI ---
if not st.session_state.user_role:
    st.info("Welcome! Please select your role to begin.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("I am a Student", use_container_width=True):
            switch_role("Student")
    with col2:
        if st.button("I am a Teacher", use_container_width=True):
            switch_role("Teacher")

# --- TEACHER VIEW ---
elif st.session_state.user_role == "Teacher":
    st.sidebar.header("Teacher Tools")
    if st.sidebar.button("Switch to Student View"):
        switch_role("Student")

    st.header("Teacher Dashboard")
    st.subheader("1. Input Content for Personalization/Assessment")
    st.session_state.teacher_content_input = st.text_area(
        "Paste educational content here:",
        value=st.session_state.teacher_content_input,
        height=200
    )

    col_teach1, col_teach2 = st.columns(2)
    with col_teach1:
        if st.button("✨ Preview Personalized Content"):
            if st.session_state.teacher_content_input.strip():
                st.markdown("### Personalized Content Preview:")
                with st.spinner("Generating personalized version..."):
                    content = generate_personalized_content_for_teacher(
                        st.session_state.teacher_content_input[:70]
                    )
                    st.markdown(content)
            else:
                st.warning("Please input content first.")
    with col_teach2:
        num_questions = st.number_input("Number of Quiz Questions:", min_value=1, max_value=10, value=3)
        if st.button("📝 Generate Quiz from My Content"):
            if st.session_state.teacher_content_input.strip():
                with st.spinner("Generating quiz..."):
                    questions = generate_quiz_for_teacher(st.session_state.teacher_content_input, num_questions)
                    st.session_state.teacher_generated_questions = questions
                    st.success(f"{len(questions)} questions generated.")
                    with st.expander("View Generated Quiz", expanded=False):
                        for i, q in enumerate(questions):
                            st.markdown(f"**Q{i+1}: {q['question_text']}**")
                            for opt in q["options"]:
                                st.write(opt)
                            st.write(f"✅ Correct Answer: {q['correct_answer']}")
                            st.divider()
            else:
                st.warning("Please input content first to generate a quiz.")
    st.markdown("---")
    st.subheader("2. View Student Progress (Placeholder)")
    st.info("Student analytics will appear here in the future.")

# --- STUDENT VIEW ---
elif st.session_state.user_role == "Student":
    st.sidebar.header("Student Tools")
    if st.sidebar.button("Switch to Teacher View"):
        switch_role("Teacher")

    st.header("Explore, Understand, and Quiz Yourself!")
    st.write("Paste any text you're studying. The AI will explain it in simpler terms, create a quiz, and you can ask follow-up questions!")

    st.session_state.student_main_input_text = st.text_area(
        "📚 Paste your text paragraph here:",
        value=st.session_state.student_main_input_text,
        height=200
    )

    if st.button("🧠 Process My Text (Explain & Create Quiz)"):
        if st.session_state.student_main_input_text.strip():
            with st.spinner("Analyzing your text..."):
                st.session_state.processed_text_for_qna_context = st.session_state.student_main_input_text
                st.session_state.simplified_student_text = simplify_student_text(
                    st.session_state.processed_text_for_qna_context
                )
                st.session_state.student_custom_questions = generate_quiz_from_student_text(
                    st.session_state.processed_text_for_qna_context, 3
                )
            st.session_state.student_custom_answers = {}
            st.session_state.student_custom_quiz_submitted = False
            st.session_state.student_conversation_history = []
            st.session_state.student_follow_up_question_input = ""
        else:
            st.warning("Please paste some text first.")

    if st.session_state.simplified_student_text:
        st.markdown("---")
        st.markdown("### 💡 AI's Explanation of Your Text:")
        st.markdown(st.session_state.simplified_student_text)

    if st.session_state.processed_text_for_qna_context:
        st.markdown("---")
        st.subheader("💬 Chat with AI about Your Text")
        if st.session_state.student_conversation_history:
            for q, a in st.session_state.student_conversation_history:
                st.markdown(f"**You:** {q}")
                st.markdown(f"**AI:** {a}")
                st.markdown("---")

        with st.form(key="student_follow_up_qna_form"):
            st.session_state.student_follow_up_question_input = st.text_input(
                "Your question:",
                value=st.session_state.student_follow_up_question_input
            )
            submit_q = st.form_submit_button("💬 Ask AI")
            if submit_q:
                q = st.session_state.student_follow_up_question_input
                if q.strip():
                    with st.spinner("Thinking..."):
                        a = answer_follow_up_question(q, st.session_state.processed_text_for_qna_context)
                        st.session_state.student_conversation_history.append((q, a))
                        st.session_state.student_follow_up_question_input = ""
                        st.rerun()
                else:
                    st.warning("Please type a question.")

    if st.session_state.student_custom_questions:
        st.markdown("---")
        st.subheader("📝 Quiz on Your Text")
        if not st.session_state.student_custom_quiz_submitted:
            with st.form(key="student_custom_text_quiz_form"):
                answers = {}
                for i, q in enumerate(st.session_state.student_custom_questions):
                    answers[q["id"]] = st.radio(
                        f"{i+1}. {q['question_text']}",
                        q["options"],
                        index=None,
                        key=f"student_q_{q['id']}"
                    )
                if st.form_submit_button("Submit My Quiz"):
                    st.session_state.student_custom_answers = answers
                    st.session_state.student_custom_quiz_submitted = True
                    st.rerun()
        else:
            score, total, feedback = grade_assessment(
                st.session_state.student_custom_answers,
                st.session_state.student_custom_questions
            )
            st.success(f"Your Quiz Submitted! Your Score: {score}/{total}")
            with st.expander("View Detailed Feedback", expanded=True):
                for f in feedback:
                    st.info(f)

            if st.button("Process New Text / Re-Quiz"):
                st.session_state.processed_text_for_qna_context = ""
                st.session_state.simplified_student_text = ""
                st.session_state.student_custom_questions = []
                st.session_state.student_custom_answers = {}
                st.session_state.student_custom_quiz_submitted = False
                st.session_state.student_conversation_history = []
                st.session_state.student_follow_up_question_input = ""
                st.rerun()
