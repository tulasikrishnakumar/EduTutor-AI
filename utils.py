import re
import time
import streamlit as st
from api_service import call_openrouter_api
import pdfplumber # For PDF text extraction
from docx import Document # For DOCX text extraction
import io # To handle byte streams from Streamlit's uploader

# --- TEXT EXTRACTION UTILITIES ---
def extract_text_from_pdf(file_like_object):
    """Extracts text from a PDF file-like object."""
    text = ""
    try:
        with pdfplumber.open(file_like_object) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n" # Add newline between pages
        return text.strip() if text else None
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def extract_text_from_docx(file_like_object):
    """Extracts text from a DOCX file-like object."""
    text = ""
    try:
        doc = Document(file_like_object)
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text.strip() if text else None
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return None

# --- EXISTING UTILS FUNCTIONS (KEEP THEM AS THEY ARE) ---
def generate_personalized_content_for_teacher(topic_content, difficulty="medium"):
    # (Your existing code)
    prompt = f"Rewrite the following content for a {difficulty} level student. Make it engaging and include analogies or relevant examples if possible:\n\n{topic_content}"
    return call_openrouter_api(prompt)

def generate_quiz_for_teacher(content, num_questions=3):
    # (Your existing code)
    return generate_quiz_from_paragraph(content, num_questions)

def simplify_student_text(original_text):
    # (Your existing code)
    prompt = f"Please explain this text in simpler terms, suitable for a student who might be finding it difficult. Break down complex ideas and use clear language:\n\n{original_text}"
    return call_openrouter_api(prompt)

def generate_quiz_from_student_text(text_input, num_questions=3):
    # (Your existing code)
    return generate_quiz_from_paragraph(text_input, num_questions)

def answer_follow_up_question(student_question, context_text):
    # (Your existing code)
    prompt = (
        f"You are a helpful AI Tutor. Based on the following context text provided by a student:\n\n"
        f"--- CONTEXT START ---\n{context_text}\n--- CONTEXT END ---\n\n"
        f"Please answer the student's follow-up question concisely and clearly: '{student_question}'"
    )
    return call_openrouter_api(prompt)

def grade_assessment(student_answers, questions_list):
    # (Your existing code - ensure it's the robust version)
    score = 0
    feedback = []
    if not isinstance(questions_list, list):
        st.error("Grading error: Questions data is not a list.")
        return 0, 0, ["Error: Could not load questions for grading."]
        
    for q_data in questions_list:
        if not isinstance(q_data, dict):
            feedback.append(f"Skipping an invalid question item.")
            continue

        q_id = q_data.get('id')
        correct_ans_text = q_data.get('correct_answer')
        question_text = q_data.get('question_text', 'N/A')

        if q_id is None or correct_ans_text is None:
            feedback.append(f"Q: {question_text} — Error: Question data incomplete for grading.")
            continue
            
        selected_ans_text = student_answers.get(q_id)

        if selected_ans_text == correct_ans_text:
            score += 1
            feedback.append(f"Q: {question_text} — ✅ Correct!")
        elif selected_ans_text is None:
            feedback.append(f"Q: {question_text} — ❌ Not answered. The correct answer was: {correct_ans_text}")
        else:
            feedback.append(f"Q: {question_text} — ❌ Your answer: {selected_ans_text}. The correct answer was: {correct_ans_text}")
            
    return score, len(questions_list), feedback


def generate_quiz_from_paragraph(paragraph, num_questions=5):
    # (Your existing code - ensure it's the robust version with correct answer parsing)
    prompt = (
        f"Generate exactly {num_questions} multiple-choice questions based on the following paragraph.\n"
        f"For each question:\n"
        f"1. Provide the question text.\n"
        f"2. Provide 4 distinct answer options, labeled A), B), C), and D).\n"
        f"3. IMPORTANT: On a new line immediately after the D) option, specify the correct answer by writing 'ANSWER: ' followed by the letter of the correct option (e.g., 'ANSWER: C').\n\n"
        f"Example Format for ONE question:\n"
        f"Q1: What is the primary color made by mixing red and yellow?\n"
        f"A) Blue\n"
        f"B) Green\n"
        f"C) Orange\n"
        f"D) Purple\n"
        f"ANSWER: C\n\n"
        f"Now, generate the questions from this paragraph:\n"
        f"--- PARAGRAPH START ---\n{paragraph}\n--- PARAGRAPH END ---"
    )

    raw_output = call_openrouter_api(prompt)
    
    pattern = re.compile(
        r"Q\d+[:\.]\s*(.*?)\s*\nA\)\s*(.*?)\s*\nB\)\s*(.*?)\s*\nC\)\s*(.*?)\s*\nD\)\s*(.*?)\s*\nANSWER:\s*([A-D])",
        re.DOTALL | re.IGNORECASE
    )
    
    matches = pattern.findall(raw_output)
    questions = []

    if not matches and raw_output:
        st.warning(f"Primary regex failed to parse LLM output for quiz. Attempting simpler parse or showing raw. Raw output:\n{raw_output}")

    for i, match in enumerate(matches):
        try:
            q_text, opt_a_text, opt_b_text, opt_c_text, opt_d_text, correct_letter = [x.strip() for x in match]
            
            option_a_full = f"A) {opt_a_text}"
            option_b_full = f"B) {opt_b_text}"
            option_c_full = f"C) {opt_c_text}"
            option_d_full = f"D) {opt_d_text}"

            options_list = [option_a_full, option_b_full, option_c_full, option_d_full]
            
            correct_answer_full_text = ""
            if correct_letter.upper() == 'A':
                correct_answer_full_text = option_a_full
            elif correct_letter.upper() == 'B':
                correct_answer_full_text = option_b_full
            elif correct_letter.upper() == 'C':
                correct_answer_full_text = option_c_full
            elif correct_letter.upper() == 'D':
                correct_answer_full_text = option_d_full
            else:
                st.warning(f"Could not map correct answer letter '{correct_letter}' for Q: {q_text}. Defaulting to A.")
                correct_answer_full_text = option_a_full 

            questions.append({
                "question_text": q_text,
                "options": options_list,
                "correct_answer": correct_answer_full_text,
                "id": f"q_{i+1}_{int(time.time())}"
            })
        except Exception as e:
            st.error(f"Error parsing a specific question from LLM output: {e}. Match was: {match}")
            continue

    if not questions and raw_output:
        st.info(f"No questions could be parsed from the AI's response. Please try rephrasing your input text or try again. The AI said: {raw_output[:300]}...")

    return questions