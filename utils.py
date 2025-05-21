import re
from api_service import call_openrouter_api

def generate_personalized_content_for_teacher(topic, difficulty="medium"):
    prompt = f"Rewrite the content on '{topic}' for a {difficulty} level student. Include analogies or examples."
    return call_openrouter_api(prompt)

def generate_quiz_for_teacher(content, num_questions=3):
    return generate_quiz_from_paragraph(content, num_questions)

def simplify_student_text(original_text):
    prompt = f"Please explain this in simpler terms for a student:\n\n{original_text}"
    return call_openrouter_api(prompt)

def generate_quiz_from_student_text(text_input, num_questions=3):
    return generate_quiz_from_paragraph(text_input, num_questions)

def answer_follow_up_question(student_question, context_text):
    prompt = (
        f"Based on this context:\n\n{context_text}\n\n"
        f"Please answer this question:\n{student_question}"
    )
    return call_openrouter_api(prompt)

def grade_assessment(student_answers, questions):
    score = 0
    feedback = []
    for q in questions:
        q_id = q['id']
        correct = q['correct_answer']
        selected = student_answers.get(q_id)
        if selected == correct:
            score += 1
            feedback.append(f"Q: {q['question_text']} — ✅ Correct")
        elif selected is None:
            feedback.append(f"Q: {q['question_text']} — ❌ No answer. Correct: {correct}")
        else:
            feedback.append(f"Q: {q['question_text']} — ❌ Your answer: {selected}. Correct: {correct}")
    return score, len(questions), feedback

def generate_quiz_from_paragraph(paragraph, num_questions=5):
    prompt = (
        f"Generate {num_questions} multiple-choice questions from the following paragraph.\n"
        f"Each question should have 4 options labeled A), B), C), D).\n"
        f"Format:\nQ1: Question here?\nA) Option\nB) Option\nC) Option\nD) Option\n\n"
        f"Paragraph:\n{paragraph}"
    )

    raw_output = call_openrouter_api(prompt)
    pattern = re.compile(r"Q\d+[:\.] (.*?)\nA\) (.*?)\nB\) (.*?)\nC\) (.*?)\nD\) (.*?)(?=\nQ\d+[:\.]|\Z)", re.DOTALL)
    matches = pattern.findall(raw_output)

    questions = []
    for i, match in enumerate(matches):
        q_text, opt_a, opt_b, opt_c, opt_d = [x.strip() for x in match]
        questions.append({
            "question_text": q_text,
            "options": [f"A) {opt_a}", f"B) {opt_b}", f"C) {opt_c}", f"D) {opt_d}"],
            "correct_answer": f"A) {opt_a}",  # Can be updated later if LLM adds correct key
            "id": f"q{i+1}"
        })

    return questions
