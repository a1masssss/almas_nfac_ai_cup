# 🔐 Настройка переменных окружения в Render Dashboard

## ⚠️ ВАЖНО: API ключи нужно добавлять только через Render Dashboard!

### 1. Обязательные переменные окружения для веб-сервиса:

Добавьте в Render Dashboard → Your Web Service → Environment:

```
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=almas-nfac-ai-cup.onrender.com

# 🔑 API Keys (ОБЯЗАТЕЛЬНО добавить!)


# 🗄️ Database URL (автоматически через render.yaml, но можно добавить вручную)
DATABASE_URL=postgresql://ai_cup_user:password@internal-host:5432/ai_cup
```

### 2. Как добавить переменные в Render Dashboard:

1. Зайдите в Render Dashboard
2. Откройте ваш веб-сервис
3. Перейдите в раздел **"Environment"**
4. Нажмите **"Add Environment Variable"**
5. Добавьте каждую переменную по отдельности

### 3. Как найти Internal Database URL:

1. Зайдите в Render Dashboard
2. Откройте вашу PostgreSQL базу данных
3. В разделе "Connections" найдите **"Internal Database URL"**
4. Скопируйте полный URL (например: `postgresql://ai_cup_user:password@dpg-xxx-a:5432/ai_cup`)
5. Добавьте его как `DATABASE_URL` в переменные окружения веб-сервиса

### 4. Build и Start команды:

```
Build Command: ./build.sh
Start Command: ./start.sh
```

### 5. После добавления всех переменных:

1. Сохраните изменения
2. Render автоматически пересоберет приложение
3. Проверьте логи на наличие ошибок 