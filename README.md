# 🎵 AI Cup — Playlist Summarizer

Django-приложение для фестиваля **AI Cup**, которое получает плейлисты и генерирует AI-саммари с помощью Gemini.

## 🚀 Возможности

- 🔍 Поиск и загрузка плейлистов
- 🤖 AI-саммаризация треков через Google Gemini
- 👤 Пользовательская система с регистрацией и профилями
- 🔌 WebSocket поддержка (Django Channels + Redis)
- 🐳 Docker для локальной разработки

## 🛠️ Стек

- **Backend:** Django, Django Channels, Redis
- **AI:** Google Gemini API
- **Деплой:** Render.com
- **БД:** PostgreSQL

## ⚡ Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/a1masssss/almas_nfac_ai_cup.git
cd almas_nfac_ai_cup

# Настроить переменные окружения
cp src/.env.example src/.env
# Заполнить src/.env своими ключами

# Установить зависимости
pip install -r requirements.txt

# Запустить миграции
cd src
python manage.py migrate

# Запустить сервер
python manage.py runserver
```

## 🐳 Docker

```bash
docker-compose -f docker-compose.dev.yml up
```

## 📦 Деплой

Подробная инструкция в [DEPLOY.md](DEPLOY.md).

---

*Этот README был создан из Clanker.*