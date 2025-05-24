# Деплой на Render.com

## Подготовка к деплою

### 1. Обновите переменные окружения

В файле `src/.env` замените `REPLACE_WITH_YOUR_RENDER_PASSWORD` на реальный пароль из Render:

```env
DB_PASSWORD=ваш_реальный_пароль_из_render
```

### 2. Добавьте API ключи

Убедитесь, что в `src/.env` указаны правильные API ключи:
- `OPENAI_API_KEY` - для OpenAI API
- `API_KEY` - для Google Gemini API

## Деплой

### Автоматический деплой (рекомендуется)

1. Пушьте код в GitHub репозиторий
2. Подключите репозиторий к Render
3. Render автоматически использует `render.yaml` для конфигурации

### Ручной деплой

1. В Render Dashboard создайте новый Web Service
2. Подключите ваш GitHub репозиторий
3. Настройте следующие параметры:

**Build Command:**
```bash
./build.sh
```

**Start Command:**
```bash
./start.sh
```

**Environment Variables:**
- `DEBUG=False`
- `SECRET_KEY=your-secret-key`
- `ALLOWED_HOSTS=your-app-name.onrender.com`
- `OPENAI_API_KEY=your-openai-key`
- `API_KEY=your-gemini-key`
- Database variables будут добавлены автоматически при подключении PostgreSQL

### 3. Подключите базу данных

1. Создайте PostgreSQL базу данных в Render
2. Подключите её к вашему Web Service
3. Render автоматически установит переменные окружения для БД

### 4. Настройте Redis (для WebSocket)

1. Создайте Redis instance в Render (или используйте внешний сервис)
2. Добавьте `REDIS_URL` в переменные окружения

## После деплоя

1. Проверьте логи приложения в Render Dashboard
2. Убедитесь, что миграции прошли успешно
3. Проверьте работу статических файлов
4. Протестируйте WebSocket соединения

## Troubleshooting

### Проблемы со статическими файлами
- Проверьте, что `collectstatic` выполнился успешно в логах сборки
- Убедитесь, что `whitenoise` настроен правильно

### Проблемы с базой данных
- Проверьте правильность DATABASE_URL или отдельных переменных БД
- Убедитесь, что миграции выполнились

### Проблемы с WebSocket
- Проверьте настройки Redis
- Убедитесь, что ASGI application настроен правильно 