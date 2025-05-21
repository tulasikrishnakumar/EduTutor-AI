# role_handler.py
import streamlit as st
from utils import create_quiz

def teacher_view():
    st.header("👩‍🏫 Teacher Dashboard")
    subject = st.text_input("Enter Subject:", "General")
    content = st.text_area("Paste your teaching content:")
    num_questions = st.slider("Number of Questions", 1, 10, 5)

    if st.button("Generate Quiz"):
        if content.strip():
            with st.spinner("Generating quiz..."):
                quiz = create_quiz(subject, content, num_questions)
                st.session_state.teacher_quiz = quiz
        else:
            st.warning("Please enter content.")

    if 'teacher_quiz' in st.session_state:
        st.subheader("Generated Quiz")
        for i, q in enumerate(st.session_state.teacher_quiz):
            st.markdown(f"**Q{i+1}: {q['question_text']}**")
            for opt in q['options']:
                st.markdown(f"- {opt}")
            st.markdown(f"✅ **Answer**: {q.get('correct_answer', 'Not specified')}")
            st.divider()

def student_view():
    st.header("🎓 Student Assistant")
    subject = st.text_input("Subject:", "General Reading")
    paragraph = st.text_area("Paste a paragraph you'd like to understand or be quizzed on:")
    if st.button("Explain & Quiz Me"):
        if paragraph.strip():
            with st.spinner("Analyzing and generating questions..."):
                quiz = create_quiz(subject, paragraph)
                st.session_state.student_quiz = quiz
        else:
            st.warning("Please enter a paragraph.")

    if 'student_quiz' in st.session_state:
        st.subheader("Take Your Quiz")
        if 'student_answers' not in st.session_state:
            st.session_state.student_answers = {}
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.student_quiz):
                selected = st.radio(q['question_text'], q['options'], key=f"student_q_{i}")
                st.session_state.student_answers[q['question_text']] = selected
            submitted = st.form_submit_button("Submit Answers")
            if submitted:
                st.success("Quiz submitted!")
                st.subheader("Results")
                correct = 0
                for q in st.session_state.student_quiz:
                    ans = st.session_state.student_answers[q['question_text']]
                    if ans.endswith(q.get('correct_answer', '')):
                        correct += 1
                    st.markdown(f"**Q: {q['question_text']}**")
                    st.markdown(f"Your Answer: {ans}")
                    st.markdown(f"Correct Answer: {q.get('correct_answer', 'Not specified')}")
                st.info(f"Your Score: {correct}/{len(st.session_state.student_quiz)}")
