import os
from dotenv import load_dotenv
import google.generativeai as genai

# Загружаем API_KEY из .env
load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY not found in .env")

# Конфигурация SDK
genai.configure(api_key=api_key)

# Создаем модель Gemini 1.5 Pro
model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

def summarize_with_gemini_1_5(transcript: str) -> str:
    system_prompt = (
        "Ты опытный редактор онлайн-курсов. "
        "Твоя задача — сжать стенограмму лекции до ключевых идей, "
        "ясных примеров и контрольных вопросов. "
        "Стиль — ясный, лаконичный, без воды. Язык — такой же, как и у входного текста.\n\n"
        "Формат:\n"
        "1. Ключевые идеи (до 8 буллетов)\n"
        "2. Пояснения и примеры\n"
        "3. Напиши очень развернуто"
    )

    full_prompt = (
        system_prompt
        + "\n\n--- СТЕНОГРАММА НИЖЕ ---\n"
        + transcript.strip()
    )

    response = model.generate_content(full_prompt)
    return response.text.strip()


# Пример использования
if __name__ == "__main__":
    transcript = """
    Сегодня мы обсуждали, как работает нейросеть. 
    Основные блоки: входной слой, скрытые слои, выходной слой.
    Обсудили функцию активации ReLU и её преимущества. 
    Примером служила нейросеть, распознающая рукописные цифры (MNIST).
    """
    summary = summarize_with_gemini_1_5(transcript)
    print(summary)

