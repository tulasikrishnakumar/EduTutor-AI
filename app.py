import streamlit as st
import time
import io # For handling file streams
from utils import (
    extract_text_from_pdf, extract_text_from_docx, # For file processing
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
# General
if 'user_role' not in st.session_state: st.session_state.user_role = None

# Teacher related
if 'teacher_input_method' not in st.session_state: st.session_state.teacher_input_method = "Paste Text"
if 'teacher_content_input_value' not in st.session_state: st.session_state.teacher_content_input_value = ""
if 'teacher_generated_questions' not in st.session_state: st.session_state.teacher_generated_questions = []
if 'teacher_personalized_content_preview' not in st.session_state: st.session_state.teacher_personalized_content_preview = ""
if 'teacher_file_uploader_key' not in st.session_state: st.session_state.teacher_file_uploader_key = 0 # To reset file uploader

# Student related
if 'student_input_method' not in st.session_state: st.session_state.student_input_method = "Paste Text"
if 'student_main_input_text_value' not in st.session_state: st.session_state.student_main_input_text_value = ""
if 'processed_text_for_qna_context' not in st.session_state: st.session_state.processed_text_for_qna_context = ""
if 'simplified_student_text' not in st.session_state: st.session_state.simplified_student_text = ""
if 'student_custom_questions' not in st.session_state: st.session_state.student_custom_questions = []
if 'student_custom_answers' not in st.session_state: st.session_state.student_custom_answers = {}
if 'student_custom_quiz_submitted' not in st.session_state: st.session_state.student_custom_quiz_submitted = False
if 'student_conversation_history' not in st.session_state: st.session_state.student_conversation_history = []
if 'student_file_uploader_key' not in st.session_state: st.session_state.student_file_uploader_key = 0 # To reset file uploader


# --- Switch Role Logic ---
def switch_role(new_role):
    # Reset relevant states when switching roles
    st.session_state.teacher_input_method = "Paste Text"
    st.session_state.teacher_content_input_value = ""
    st.session_state.teacher_generated_questions = []
    st.session_state.teacher_personalized_content_preview = ""
    st.session_state.teacher_file_uploader_key +=1


    st.session_state.student_input_method = "Paste Text"
    st.session_state.student_main_input_text_value = ""
    st.session_state.processed_text_for_qna_context = ""
    st.session_state.simplified_student_text = ""
    st.session_state.student_custom_questions = []
    st.session_state.student_custom_answers = {}
    st.session_state.student_custom_quiz_submitted = False
    st.session_state.student_conversation_history = []
    st.session_state.student_file_uploader_key +=1

    st.session_state.user_role = new_role
    st.rerun()

# --- Role Selection UI ---
if not st.session_state.user_role:
    st.info("Welcome! Please select your role to begin.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("I am a Student", use_container_width=True, key="role_student_button"):
            switch_role("Student")
    with col2:
        if st.button("I am a Teacher", use_container_width=True, key="role_teacher_button"):
            switch_role("Teacher")

# --- TEACHER VIEW ---
elif st.session_state.user_role == "Teacher":
    st.sidebar.header("Teacher Tools")
    if st.sidebar.button("Switch to Student View", key="teacher_switch_to_student_button"):
        switch_role("Student")

    st.header("Teacher Dashboard")
    st.subheader("1. Provide Content & Generate Resources")

    st.session_state.teacher_input_method = st.radio(
        "How would you like to provide content?",
        ("Paste Text", "Upload File"),
        key="teacher_input_method_radio",
        horizontal=True,
        index=["Paste Text", "Upload File"].index(st.session_state.teacher_input_method) # Persist choice
    )

    teacher_text_from_file = ""

    if st.session_state.teacher_input_method == "Upload File":
        uploaded_file_teacher = st.file_uploader(
            "Upload a PDF or DOCX file",
            type=["pdf", "docx"],
            key=f"teacher_file_uploader_widget_{st.session_state.teacher_file_uploader_key}" # Reset uploader
        )
        if uploaded_file_teacher is not None:
            file_bytes = io.BytesIO(uploaded_file_teacher.getvalue())
            file_type = uploaded_file_teacher.type
            
            with st.spinner(f"Extracting text from {uploaded_file_teacher.name}..."):
                if file_type == "application/pdf":
                    teacher_text_from_file = extract_text_from_pdf(file_bytes)
                elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    teacher_text_from_file = extract_text_from_docx(file_bytes)
            
            if teacher_text_from_file:
                st.success("Text extracted successfully!")
                st.session_state.teacher_content_input_value = teacher_text_from_file
                # No rerun here, let text_area update and user proceed
            else:
                st.warning("Could not extract text. File might be empty, image-based (scanned), or corrupted.")
            # To allow re-uploading the same file if needed after an action
            st.session_state.teacher_file_uploader_key += 1
            st.rerun() # Rerun to update text_area with extracted text and reset uploader


    current_teacher_input = st.text_area(
        "Educational content (paste or will be filled from upload):",
        value=st.session_state.teacher_content_input_value,
        height=200,
        key="teacher_content_area_widget_key"
    )
    if current_teacher_input != st.session_state.teacher_content_input_value: # Sync if user types
        st.session_state.teacher_content_input_value = current_teacher_input


    if st.button("✨ Preview Personalized Content", key="teacher_preview_button"):
        if current_teacher_input.strip():
            with st.spinner("Generating personalized version..."):
                content = generate_personalized_content_for_teacher(current_teacher_input)
                st.session_state.teacher_personalized_content_preview = content
            # Don't clear input_value here, teacher might want to generate quiz next
            st.rerun()
        else:
            st.warning("Please provide content via paste or upload.")
            st.session_state.teacher_personalized_content_preview = ""

    if st.session_state.teacher_personalized_content_preview:
        st.markdown("### Personalized Content Preview:")
        st.markdown(st.session_state.teacher_personalized_content_preview)
        st.markdown("---")

    st.subheader("2. Generate Quiz from Your Content")
    num_questions = st.number_input("Number of Quiz Questions:", min_value=1, max_value=10, value=3, key="teacher_num_q_widget_key")
    
    if st.button("📝 Generate Quiz from My Content", key="teacher_generate_quiz_bttn"):
        if current_teacher_input.strip():
            with st.spinner("Generating quiz..."):
                questions = generate_quiz_for_teacher(current_teacher_input, num_questions)
                st.session_state.teacher_generated_questions = questions
                if questions: st.success(f"{len(questions)} questions generated.")
                else: st.warning("Could not generate questions. AI might need different text.")
            
            st.session_state.teacher_content_input_value = "" # Clear for next input
            st.session_state.teacher_personalized_content_preview = "" 
            st.session_state.teacher_file_uploader_key += 1 # Reset uploader for next time
            st.rerun()
        else:
            st.warning("Please provide content to generate a quiz.")
            st.session_state.teacher_generated_questions = []

    if st.session_state.teacher_generated_questions:
        with st.expander("View Generated Quiz", expanded=True):
            for i, q in enumerate(st.session_state.teacher_generated_questions):
                st.markdown(f"**Q{i+1}: {q.get('question_text', 'N/A')}**")
                if isinstance(q.get("options"), list):
                    for opt_text in q["options"]: st.write(f"- {opt_text}")
                else: st.warning(f"Options for Q{i+1} not in list format.")
                st.write(f"✅ Correct Answer: {q.get('correct_answer', 'Not specified')}")
                st.divider()

# --- STUDENT VIEW ---
elif st.session_state.user_role == "Student":
    st.sidebar.header("Student Tools")
    if st.sidebar.button("Switch to Teacher View", key="student_switch_button"):
        switch_role("Teacher")

    st.header("Explore, Understand, and Quiz Yourself!")
    
    st.session_state.student_input_method = st.radio(
        "How would you like to provide text?",
        ("Paste Text", "Upload File (PDF/DOCX)"),
        key="student_input_method_radio_key",
        horizontal=True,
        index=["Paste Text", "Upload File (PDF/DOCX)"].index(st.session_state.student_input_method) # Persist choice
    )

    student_text_from_file = ""

    if st.session_state.student_input_method == "Upload File (PDF/DOCX)":
        uploaded_file_student = st.file_uploader(
            "Upload your study material (PDF or DOCX)",
            type=["pdf", "docx"],
            key=f"student_file_uploader_widget_{st.session_state.student_file_uploader_key}" # Reset uploader
        )
        if uploaded_file_student is not None:
            file_bytes_student = io.BytesIO(uploaded_file_student.getvalue())
            file_type_student = uploaded_file_student.type

            with st.spinner(f"Extracting text from {uploaded_file_student.name}..."):
                if file_type_student == "application/pdf":
                    student_text_from_file = extract_text_from_pdf(file_bytes_student)
                elif file_type_student == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    student_text_from_file = extract_text_from_docx(file_bytes_student)
            
            if student_text_from_file:
                st.success("Text extracted successfully!")
                st.session_state.student_main_input_text_value = student_text_from_file
            else:
                st.warning("Could not extract text. File might be empty, image-based (scanned), or corrupted.")
            # Increment key to allow re-upload of the same file name triggering a change
            st.session_state.student_file_uploader_key += 1
            st.rerun() # Rerun to update text_area and reset uploader widget

    current_student_input = st.text_area(
        "📚 Your text (paste here or will be filled from upload):",
        value=st.session_state.student_main_input_text_value,
        height=200,
        key="student_main_input_widget_key"
    )
    if current_student_input != st.session_state.student_main_input_text_value: # Sync if user types
        st.session_state.student_main_input_text_value = current_student_input

    if st.button("🧠 Process My Text (Explain & Create Quiz)", key="student_process_button"):
        if current_student_input.strip():
            with st.spinner("Analyzing your text..."):
                text_to_process = current_student_input
                st.session_state.processed_text_for_qna_context = text_to_process
                st.session_state.simplified_student_text = simplify_student_text(text_to_process)
                st.session_state.student_custom_questions = generate_quiz_from_student_text(text_to_process, 3)
                if not st.session_state.simplified_student_text and not st.session_state.student_custom_questions:
                    st.warning("AI couldn't process the text well. Try different text or ensure good extraction.")
            
            st.session_state.student_custom_answers = {}
            st.session_state.student_custom_quiz_submitted = False
            st.session_state.student_conversation_history = []
            st.session_state.student_main_input_text_value = "" # Clear for next input
            st.session_state.student_file_uploader_key += 1 # Reset uploader for next time
            st.rerun()
        else:
            st.warning("Please paste text or upload a file first.")
    
    if st.session_state.simplified_student_text:
        st.markdown("---")
        st.markdown("### 💡 AI's Explanation of Your Text:")
        st.markdown(st.session_state.simplified_student_text)

    if st.session_state.processed_text_for_qna_context: 
        st.markdown("---")
        st.subheader("💬 Chat with AI about Your Text")
        chat_container = st.container()
        with chat_container:
            for q_text, a_text in st.session_state.student_conversation_history:
                st.markdown(f"**You:** {q_text}")
                st.markdown(f"**AI:** {a_text}")
                st.markdown("---")

        with st.form(key="student_qna_form_key"):
            user_q_input_form = st.text_input("Your question:", key="student_qna_input_widget_key")
            submit_q = st.form_submit_button("💬 Ask AI")
            if submit_q:
                if user_q_input_form.strip():
                    with st.spinner("Thinking..."):
                        a = answer_follow_up_question(user_q_input_form, st.session_state.processed_text_for_qna_context)
                        st.session_state.student_conversation_history.append((user_q_input_form, a))
                        st.rerun() 
                else:
                    st.warning("Please type a question.")

    if st.session_state.student_custom_questions:
        st.markdown("---")
        st.subheader("📝 Quiz on Your Text")
        if not st.session_state.student_custom_quiz_submitted:
            with st.form(key="student_quiz_form_key"):
                answers = {}
                for i, q_data in enumerate(st.session_state.student_custom_questions):
                    q_id = q_data.get('id', f"s_q_{i}_{int(time.time())}") 
                    options = q_data.get("options", [])
                    if not isinstance(options, list): options = []
                    answers[q_id] = st.radio(
                        f"{i+1}. {q_data.get('question_text', 'Missing question text')}",
                        options, index=None, key=f"s_q_radio_{q_id}" 
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
                for f_item in feedback: st.info(f_item)

            if st.button("Process New Text / Re-Quiz", key="student_new_text_bttn"):
                st.session_state.student_main_input_text_value = "" 
                st.session_state.processed_text_for_qna_context = ""
                st.session_state.simplified_student_text = ""
                st.session_state.student_custom_questions = []
                st.session_state.student_custom_answers = {}
                st.session_state.student_custom_quiz_submitted = False
                st.session_state.student_conversation_history = []
                st.session_state.student_file_uploader_key += 1 # Reset uploader
                st.rerun()