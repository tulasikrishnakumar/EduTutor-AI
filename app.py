import streamlit as st
import time # For st.spinner

# Page Configuration
st.set_page_config(page_title="EduTutor AI", layout="wide", initial_sidebar_state="expanded")

st.title("🎓 EduTutor AI")
st.caption("Personalized Learning and Assessment System")

# --- MOCK BACKEND FUNCTIONS ---
def mock_generate_personalized_content_for_teacher(topic, difficulty="medium"):
    return (f"This is a *mock personalized content preview* for the teacher regarding '{topic}' at {difficulty} level. "
            f"The actual LLM would adapt the teacher's input text for different student needs or learning styles. "
            f"For example, it might provide more analogies for a 'basic' understanding, or deeper technical details for 'advanced'.")

def mock_generate_quiz_for_teacher(content_topic, num_questions=3):
    questions = []
    for i in range(num_questions):
        questions.append({
            "question_text": f"Teacher's Quiz: What is a key point in '{content_topic[:30]}...'? (Q{i+1})",
            "options": [f"Teacher Opt A", f"Teacher Opt B", f"Teacher Opt C", f"Teacher Opt D"],
            "correct_answer": f"Teacher Opt A",
            "id": f"teacher_q{i}{content_topic.replace(' ', '').lower()}"
        })
    return questions

def mock_simplify_student_text(original_text):
    if not original_text.strip():
        return "Please provide some text to simplify."
    # Make it sound a bit more like a real simplification
    text_snippet = original_text[:70].replace('*','').replace('\n', ' ') + "..."
    return (f"*AI's Explanation of Your Text (mock):*\n\n"
            f"Okay, let's break down your text starting with \"{text_snippet}\".\n\n"
            f"Essentially, the main idea seems to be about [mock main idea related to the text, e.g., 'the process of X' or 'the importance of Y']. "
            f"Key points include [mock key point 1] and [mock key point 2]. "
            f"To put it simply, imagine [mock analogy]. This helps to illustrate how [mock concept] works. "
            f"The author emphasizes that [mock emphasis]. This simplified version aims to make these concepts more accessible. "
            f"Feel free to ask specific questions about parts you're still unsure of!")

def mock_generate_quiz_from_student_text(text_input, num_questions=3):
    if not text_input.strip():
        return []
    questions = []
    text_snippet = text_input[:50].replace('*','').replace('\n', ' ') + "..."
    for i in range(num_questions):
        q_text = ""
        if i == 0:
            q_text = f"Based on your text (\"{text_snippet}\"), what is the primary subject discussed?"
        elif i == 1:
            q_text = f"According to your text, what is one implication of [mock concept from text]?"
        else:
            q_text = f"Which of the following statements best summarizes a point made in your text?"

        options = [
            f"Option A (related to \"{text_snippet}\")",
            f"Option B (a plausible distractor)",
            f"Option C (another detail)",
            f"Option D (a conclusion)"
        ]
        questions.append({
            "question_text": q_text,
            "options": options,
            "correct_answer": options[0], # Mock correct answer
            "id": f"student_custom_q{i}"
        })
    return questions

def mock_answer_follow_up_question(student_question, context_text):
    if not student_question.strip():
        return "It looks like you didn't type a question. Try asking something specific!"
    context_snippet = context_text[:70].replace('*','').replace('\n', ' ') + "..."
    # Simulate AI thinking and responding to the question based on context
    answer = (f"Regarding your question: \"{student_question}\"\n\n"
              f"Considering the text you provided (starting with \"{context_snippet}\"), "
              f"my understanding is that [mock specific answer related to the question and context]. "
              f"For instance, the part about [mock detail from context_text if LLM was real] seems relevant here. "
              f"Is there another aspect of this you'd like to explore or a different part of your text you're curious about?")
    return answer

def mock_grade_assessment(student_answers, questions):
    score = 0
    feedback_items = []
    if not questions: return 0, 0, ["No questions found for grading."]
    if not student_answers:
        for q_data in questions:
             feedback_items.append(f"Question '{q_data['question_text']}': No answer. Correct: {q_data.get('correct_answer', 'N/A')}.")
        return score, len(questions), feedback_items
    for q_data in questions:
        q_id = q_data["id"]
        ans_given = student_answers.get(q_id)
        if ans_given == q_data["correct_answer"]:
            score += 1
            feedback_items.append(f"Q: '{q_data['question_text'][:50]}...': Correct!")
        elif ans_given is None:
            feedback_items.append(f"Q: '{q_data['question_text'][:50]}...': No answer. Correct: {q_data.get('correct_answer', 'N/A')}.")
        else:
            feedback_items.append(f"Q: '{q_data['question_text'][:50]}...': Incorrect. You said '{ans_given}'. Correct: {q_data.get('correct_answer', 'N/A')}.")
    return score, len(questions), feedback_items
# --- END MOCK BACKEND FUNCTIONS ---


# --- Session State Initialization ---
if 'user_role' not in st.session_state: st.session_state.user_role = None
# Teacher related
if 'teacher_content_input' not in st.session_state: st.session_state.teacher_content_input = ""
if 'teacher_generated_questions' not in st.session_state: st.session_state.teacher_generated_questions = []
# Student - Custom Text & Q&A
if 'student_main_input_text' not in st.session_state: st.session_state.student_main_input_text = "" # The primary text from student
if 'processed_text_for_qna_context' not in st.session_state: st.session_state.processed_text_for_qna_context = "" # Stores the text used for current Q&A
if 'simplified_student_text' not in st.session_state: st.session_state.simplified_student_text = ""
if 'student_custom_questions' not in st.session_state: st.session_state.student_custom_questions = []
if 'student_custom_answers' not in st.session_state: st.session_state.student_custom_answers = {}
if 'student_custom_quiz_submitted' not in st.session_state: st.session_state.student_custom_quiz_submitted = False
if 'student_follow_up_question_input' not in st.session_state: st.session_state.student_follow_up_question_input = ""
if 'student_conversation_history' not in st.session_state: st.session_state.student_conversation_history = []
# --- End Session State Initialization ---

def switch_role(new_role):
    # Reset states when switching roles
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

# --- UI Logic ---
if not st.session_state.user_role:
    st.info("Welcome! Please select your role to begin.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("I am a Student", key="student_role_btn", use_container_width=True):
            switch_role("Student")
    with col2:
        if st.button("I am a Teacher", key="teacher_role_btn", use_container_width=True):
            switch_role("Teacher")

# --- TEACHER VIEW ---
elif st.session_state.user_role == "Teacher":
    st.sidebar.header("Teacher Tools")
    if st.sidebar.button("Switch to Student View", key="teacher_switch_to_student"):
        switch_role("Student")
    st.header("Teacher Dashboard")
    st.subheader("1. Input Content for Personalization/Assessment")
    st.session_state.teacher_content_input = st.text_area(
        "Paste educational content here:",
        value=st.session_state.teacher_content_input,
        height=200,
        key="teacher_content_area"
    )
    col_teach1, col_teach2 = st.columns(2)
    with col_teach1:
        if st.button("✨ Preview Personalized Content", key="teacher_personalize_btn"):
            if st.session_state.teacher_content_input.strip():
                st.markdown("### Mock Personalized Content Preview:")
                st.markdown(mock_generate_personalized_content_for_teacher(st.session_state.teacher_content_input[:50] + "...", "medium"))
            else:
                st.warning("Please input content first.")
    with col_teach2:
        num_questions_to_generate = st.number_input("Number of Quiz Questions:", min_value=1, max_value=10, value=3, key="teacher_num_questions")
        if st.button("📝 Generate Quiz from My Content", key="teacher_generate_quiz_btn"):
            if st.session_state.teacher_content_input.strip():
                st.session_state.teacher_generated_questions = mock_generate_quiz_for_teacher(
                    st.session_state.teacher_content_input, num_questions_to_generate
                )
                st.success(f"{len(st.session_state.teacher_generated_questions)} questions generated (mock).")
                if st.session_state.teacher_generated_questions:
                    with st.expander("View Generated Quiz (for Teacher)", expanded=False):
                        for i, q_data in enumerate(st.session_state.teacher_generated_questions):
                            st.markdown(f"*Q{i+1}: {q_data['question_text']}*")
                            st.write(f"Options: {', '.join(q_data['options'])}")
                            st.write(f"Correct Answer: {q_data['correct_answer']}")
                            st.divider()
            else:
                st.warning("Please input content first to generate a quiz.")
    st.markdown("---")
    st.subheader("2. View Student Progress (Placeholder)")
    st.info("Teacher analytics and student progress tracking would appear here.")

# --- STUDENT VIEW ---
elif st.session_state.user_role == "Student":
    st.sidebar.header("Student Tools")
    if st.sidebar.button("Switch to Teacher View", key="student_switch_to_teacher"):
        switch_role("Teacher")

    st.header("Explore, Understand, and Quiz Yourself!")
    st.write("Paste any text you're studying. The AI will explain it in simpler terms, create a quiz, and then you can ask follow-up questions!")

    # Main text input area for the student
    st.session_state.student_main_input_text = st.text_area(
        "📚 Paste your text paragraph here:",
        value=st.session_state.student_main_input_text,
        height=200,
        key="student_main_text_input_area"
    )

    if st.button("🧠 Process My Text (Explain & Create Quiz)", key="student_process_text_btn"):
        if st.session_state.student_main_input_text.strip():
            with st.spinner("AI is analyzing your text..."):
                # Store the current text as the context for Q&A
                st.session_state.processed_text_for_qna_context = st.session_state.student_main_input_text
                st.session_state.simplified_student_text = mock_simplify_student_text(st.session_state.processed_text_for_qna_context)
                st.session_state.student_custom_questions = mock_generate_quiz_from_student_text(st.session_state.processed_text_for_qna_context, 3)
            # Reset quiz state and Q&A history for this new processing run
            st.session_state.student_custom_answers = {}
            st.session_state.student_custom_quiz_submitted = False
            st.session_state.student_conversation_history = [] # Clear old Q&A
            st.session_state.student_follow_up_question_input = "" # Clear any lingering follow-up question
            # No rerun needed here, conditional display below will update
        else:
            st.warning("Please paste some text before processing.")

    # Display simplified text if available
    if st.session_state.simplified_student_text:
        st.markdown("---")
        st.markdown("### 💡 AI's Explanation of Your Text:")
        st.markdown(st.session_state.simplified_student_text)

    # Display Q&A section if text has been processed
    if st.session_state.processed_text_for_qna_context:
        st.markdown("---")
        st.subheader("💬 Chat with AI about Your Text")
        st.write("Ask any specific questions you have about the text you pasted above.")

        # Display conversation history
        if st.session_state.student_conversation_history:
            for i, (q, a) in enumerate(st.session_state.student_conversation_history):
                st.markdown(f"*You:* {q}")
                st.markdown(f"*AI:* {a}")
                if i < len(st.session_state.student_conversation_history) -1:
                    st.markdown("---") # Divider between Q&A pairs

        # Q&A input form
        with st.form(key="student_follow_up_qna_form"):
            st.session_state.student_follow_up_question_input = st.text_input(
                "Your question:",
                value=st.session_state.student_follow_up_question_input, # Keeps value if form resubmits without this question
                key="follow_up_input_bar"
            )
            submit_follow_up_q = st.form_submit_button("💬 Ask AI")

            if submit_follow_up_q:
                if st.session_state.student_follow_up_question_input.strip():
                    question_to_ask = st.session_state.student_follow_up_question_input
                    with st.spinner("AI is thinking about your question..."):
                        ai_answer = mock_answer_follow_up_question(
                            question_to_ask,
                            st.session_state.processed_text_for_qna_context # Use the originally processed text
                        )
                    st.session_state.student_conversation_history.append((question_to_ask, ai_answer))
                    st.session_state.student_follow_up_question_input = "" # Clear input bar after submission
                    st.rerun() # Rerun to display the new Q&A and clear the input bar in the UI
                else:
                    st.warning("Please type a question before asking the AI.")

    # Display quiz if questions are generated
    if st.session_state.student_custom_questions:
        st.markdown("---")
        st.subheader("📝 Quiz on Your Text")
        if not st.session_state.student_custom_quiz_submitted:
            with st.form(key="student_custom_text_quiz_form"):
                temp_custom_answers = {}
                for i, q_data in enumerate(st.session_state.student_custom_questions):
                    temp_custom_answers[q_data["id"]] = st.radio(
                        f"{i+1}. {q_data['question_text']}",
                        options=q_data["options"],
                        key=f"student_q_{q_data['id']}_custom",
                        index=None
                    )
                submit_custom_quiz = st.form_submit_button("Submit My Quiz")
                if submit_custom_quiz:
                    st.session_state.student_custom_answers = temp_custom_answers
                    st.session_state.student_custom_quiz_submitted = True
                    st.rerun()
        else: # Student custom quiz submitted
            score, total_questions, feedback_items = mock_grade_assessment(
                st.session_state.student_custom_answers,
                st.session_state.student_custom_questions
            )
            st.success(f"Your Quiz Submitted! Your Score: {score}/{total_questions}")
            with st.expander("View Detailed Feedback", expanded=True):
                for item in feedback_items:
                    st.info(item)

            if st.button("Process New Text / Re-Quiz", key="student_retry_custom_quiz_or_new_text"):
                # This button effectively resets the student's interaction for new text
                # The text in student_main_input_text area will remain for them to edit or replace.
                st.session_state.processed_text_for_qna_context = ""
                st.session_state.simplified_student_text = ""
                st.session_state.student_custom_questions = []
                st.session_state.student_custom_answers = {}
                st.session_state.student_custom_quiz_submitted = False
                st.session_state.student_conversation_history = []
                st.session_state.student_follow_up_question_input = ""
                st.rerun()
    elif st.session_state.student_main_input_text.strip() and not st.session_state.simplified_student_text:
        # This message appears if they've typed text but not yet clicked "Process"
        st.info("Click 'Process My Text' above to get an explanation, a quiz, and to enable Q&A with the AI.")

# Fallback if no role is selected
elif not st.session_state.user_role:
    st.info("Please select a role using the buttons above to get started.")