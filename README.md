# 🎓 AI Cup — Interactive YouTube Course Platform

Turn any YouTube playlist into an interactive course with AI-generated quizzes, progress tracking, and sequential unlocking.

## 🚀 What It Does

1. **Paste a YouTube playlist URL** — the app fetches all videos and their metadata.
2. **AI generates quizzes** for each video using Gemini.
3. **Watch & learn** — videos are presented as lessons.
4. **Pass quizzes to unlock** — score 60% or above to unlock the next lesson.
5. **Track your progress** — see which courses you've started, how many quizzes you've passed, and your scores.

## 🧠 Features

- 🔗 YouTube playlist parsing via WebSockets (real-time progress)
- 🤖 AI-powered quiz generation with Gemini
- 🔒 Sequential lesson unlocking (must pass previous quiz)
- 📊 Progress tracking across all courses
- 📝 Quiz history with per-question review
- 📱 Responsive UI (works on mobile and desktop)
- 🚢 Deployable to Render.com with one click

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5.x |
| Database | PostgreSQL |
| Async / WebSockets | Django Channels + Redis |
| AI | Google Gemini API |
| Frontend | Django templates + vanilla JS |
| Deployment | Render.com (Web Service + PostgreSQL + Redis) |
| Static files | Whitenoise |

## 📁 Project Structure

```
├── build.sh                  # Render build script
├── start.sh                  # Render start script
├── render.yaml               # Render Blueprint (infrastructure as code)
├── requirements.txt          # Python dependencies
├── DEPLOY.md                 # Deployment guide (Russian)
├── RENDER_ENV_SETUP.md       # Render environment variables setup
└── src/
    ├── manage.py             # Django management
    ├── fetch_playlist.py     # YouTube playlist fetching
    ├── config/               # Django project settings (settings, urls, asgi, wsgi, routing)
    ├── main/                 # Core app: views, models, quiz logic, WebSocket consumers, Gemini summarizer
    └── users/                # User management app
```

## 🏃 Running Locally

### Prerequisites

- Python 3.10+
- PostgreSQL (or SQLite for quick testing)
- Redis (for WebSocket support)

### Setup

```bash
# Clone the repo
git clone https://github.com/a1masssss/almas_nfac_ai_cup.git
cd almas_nfac_ai_cup

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DEBUG=True
export SECRET_KEY=your-secret-key-here
export DATABASE_URL=sqlite:///db.sqlite3  # or PostgreSQL URL
export GEMINI_API_KEY=your-gemini-api-key
export YOUTUBE_API_KEY=your-youtube-api-key
export REDIS_URL=redis://localhost:6379

# Run migrations
cd src
python manage.py migrate

# Start the server
python manage.py runserver
```

Then open **http://localhost:8000** and paste a YouTube playlist URL.

## ☁️ Deploying to Render

This project includes a `render.yaml` for one-click deployment:

1. Push the repo to GitHub
2. In Render, click **New → Blueprint** and select the repo
3. Render provisions the Web Service, PostgreSQL, and Redis automatically

See [`DEPLOY.md`](DEPLOY.md) and [`RENDER_ENV_SETUP.md`](RENDER_ENV_SETUP.md) for detailed instructions (in Russian).

### Required Environment Variables on Render

| Variable | Description |
|----------|-------------|
| `DEBUG` | Set to `False` |
| `SECRET_KEY` | Django secret key |
| `ALLOWED_HOSTS` | Your Render domain |
| `DATABASE_URL` | PostgreSQL connection string (auto-provisioned by Render) |
| `REDIS_URL` | Redis connection string |
| `GEMINI_API_KEY` | Google Gemini API key |
| `DJANGO_SETTINGS_MODULE` | `config.settings` |

## 🎮 How It Works

1. User submits a YouTube playlist URL on the homepage
2. A WebSocket connection streams video metadata in real time as the playlist is fetched
3. Each video is saved to the database along with AI-generated quiz questions
4. The user watches the first video (unlocked), then takes the quiz
5. **Score ≥ 60%** → next video unlocks. Below 60% → retry!
6. Progress is tracked per user session; quiz history is saved for review

## 📄 License

This project was built for the **nFactorial AI Cup** hackathon.