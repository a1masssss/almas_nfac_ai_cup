import os
from dotenv import load_dotenv
import openai

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

# Пример использования
if __name__ == "__main__":
    transcript_text = "Here should your text"
    summary = summarize_with_chatgpt(transcript_text)
    print(summary)
