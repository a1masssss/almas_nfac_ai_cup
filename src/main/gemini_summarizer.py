import os
from dotenv import load_dotenv
import openai
import json

# Загружаем переменные из .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_with_chatgpt(transcript: str, model: str = "gpt-4o-mini") -> str:
    system_prompt = (
        "Ты опытный редактор онлайн-курсов. "
        "Твоя задача — сжать стенограмму лекции до ключевых идей, "
        "ясных примеров и контрольных вопросов. "
        "Стиль — ясный, лаконичный, без воды. "
        "Язык — Summarize in English\n\n"
        "Формат:\n"
        "1. Ключевые идеи (до 8 буллетов)\n"
        "2. Пояснения и примеры (2-3 предложения)\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": transcript}
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.7
    )

    return response['choices'][0]['message']['content'].strip()

def generate_quiz_questions(summary: str, video_title: str = "", model: str = "gpt-4o-mini") -> str:
    """
    Generate quiz questions based on video summary using OpenAI API
    """
    system_prompt = (
        "You are an expert educational assessment designer with 10+ years of experience creating high-quality quiz questions. "
        "Your task is to create engaging, challenging, and pedagogically sound questions that test deep understanding.\n\n"
        
        "CRITICAL REQUIREMENTS:\n"
        "1. Create EXACTLY 4 questions - no more, no less\n"
        "2. Each question must have EXACTLY 3 options - one correct, two incorrect\n"
        "3. Questions must test different cognitive levels: knowledge recall, comprehension, application, and analysis\n"
        "4. Incorrect options must be plausible but clearly wrong to someone who understands the material\n"
        "5. Use clear, concise language appropriate for the subject matter\n"
        "6. Avoid trick questions or ambiguous wording\n\n"
        
        "QUESTION TYPES TO INCLUDE:\n"
        "- Question 1: Key concept identification (What is...?)\n"
        "- Question 2: Process understanding (How does...?)\n"
        "- Question 3: Application (In what scenario would...?)\n"
        "- Question 4: Analysis/Evaluation (Why is... important?)\n\n"
        
        "JSON FORMAT - FOLLOW EXACTLY:\n"
        "{\n"
        '  "questions": [\n'
        "    {\n"
        '      "question": "Clear, specific question text ending with question mark?",\n'
        '      "options": [\n'
        '        {"text": "Correct answer that directly addresses the question", "correct": true},\n'
        '        {"text": "Plausible but incorrect option A", "correct": false},\n'
        '        {"text": "Plausible but incorrect option B", "correct": false}\n'
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        
        "CRITICAL: Respond with ONLY valid JSON. No explanations, no markdown, no extra text. "
        "Start with { and end with }. Use proper JSON syntax with double quotes for all strings."
    )

    user_content = (
        f"VIDEO TITLE: {video_title}\n\n"
        f"CONTENT SUMMARY:\n{summary}\n\n"
        f"Create 4 high-quality quiz questions based on this content. "
        f"Focus on the most important concepts and learning objectives. "
        f"Make sure questions are challenging but fair, and test real understanding rather than memorization."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.3,  # Lower temperature for more consistent JSON output
            max_tokens=1500,
            top_p=0.9
        )
        
        result = response['choices'][0]['message']['content'].strip()
        
        # Clean up common JSON formatting issues
        result = result.replace('```json', '').replace('```', '').strip()
        
        # Validate JSON before returning
        import json
        try:
            parsed = json.loads(result)
            # Ensure structure is correct
            if not isinstance(parsed, dict) or 'questions' not in parsed:
                raise ValueError("Invalid structure")
            if not isinstance(parsed['questions'], list) or len(parsed['questions']) != 4:
                raise ValueError("Must have exactly 4 questions")
            
            # Validate each question
            for i, q in enumerate(parsed['questions']):
                if not isinstance(q, dict) or 'question' not in q or 'options' not in q:
                    raise ValueError(f"Question {i+1} missing required fields")
                if not isinstance(q['options'], list) or len(q['options']) != 3:
                    raise ValueError(f"Question {i+1} must have exactly 3 options")
                
                correct_count = sum(1 for opt in q['options'] if opt.get('correct', False))
                if correct_count != 1:
                    raise ValueError(f"Question {i+1} must have exactly 1 correct answer")
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON validation failed: {e}")
            print(f"Raw response: {result}")
            raise
            
    except Exception as e:
        print(f"Error in generate_quiz_questions: {e}")
        # Return a fallback quiz with proper structure
        fallback_quiz = {
            "questions": [
                {
                    "question": f"What is the main topic covered in the lesson '{video_title}'?",
                    "options": [
                        {"text": "The primary subject matter discussed in this educational content", "correct": True},
                        {"text": "Advanced mathematical concepts", "correct": False},
                        {"text": "Historical events from the 19th century", "correct": False}
                    ]
                },
                {
                    "question": "Based on the lesson content, which approach would be most effective for learning this material?",
                    "options": [
                        {"text": "Active engagement with the concepts and practical application", "correct": True},
                        {"text": "Passive listening without taking notes", "correct": False},
                        {"text": "Memorizing facts without understanding context", "correct": False}
                    ]
                },
                {
                    "question": "What type of knowledge does this lesson primarily focus on?",
                    "options": [
                        {"text": "Educational content relevant to the video topic", "correct": True},
                        {"text": "Cooking recipes and culinary techniques", "correct": False},
                        {"text": "Sports statistics and game rules", "correct": False}
                    ]
                },
                {
                    "question": "Why is understanding this lesson content important?",
                    "options": [
                        {"text": "It provides valuable knowledge and skills for personal or professional development", "correct": True},
                        {"text": "It helps with memorizing random trivia facts", "correct": False},
                        {"text": "It teaches outdated information with no practical value", "correct": False}
                    ]
                }
            ]
        }
        return json.dumps(fallback_quiz)

# Пример использования
if __name__ == "__main__":
    transcript_text = "Here should your text"
    summary = summarize_with_chatgpt(transcript_text)
    print(summary)
