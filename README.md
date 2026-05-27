# CinematchAI

Public layout & architecture snapshot of **Cinematch**, an AI-powered movie recommendation web application.



A live portfolio page is published from this repo at:
**https://tedrubin80.github.io/CinematchAI/**

---

## What's in this repository

```
.
├── app.py              Flask application factory, error handlers, health check, CLI commands
├── auth.py             Login / register / OAuth flow (blueprint)
├── config.py           Environment-driven configuration (dev / prod / test)
├── models.py           Core SQLAlchemy schema (User, Session, APIKey, MovieDocument, ChatLog, …)
├── celery_config.py    Celery broker / scheduler config
├── gunicorn.conf.py    Production WSGI server config
├── requirements.txt    Python dependencies (Flask, SQLAlchemy, Celery, LangChain, pgvector, …)
│
├── templates/          Jinja2 page templates — the visual layout of the application
│   ├── base.html, index.html, about.html, help.html, maintance.html
│   ├── auth/           login, register, password reset, forgot password
│   ├── admin/          dashboard, analytics, API keys, routes, AI instructions
│   ├── cinebot/        chat UI, AI disclosure
│   ├── components/     age-verification modal, consent modal, parameter controls
│   ├── email/          transactional email templates
│   ├── errors/         400 / 401 / 403 / 404 / 405 / 429 / 500 / 502 / 503
│   ├── help/           parameter explainer pages (temperature, top_k)
│   └── subscription/   pricing, dashboard, parental consent, age verification
│
├── static/             CSS / JS / image asset folders + custom error pages
│
├── portfolio/          Standalone developer-portfolio page (single HTML/CSS/JS bundle)
└── docs/               Same portfolio, served by GitHub Pages from /docs
```



## Running the layout demo locally

```bash
git clone https://github.com/tedrubin80/CinematchAI.git
cd CinematchAI

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env — set SECRET_KEY, DATABASE_URL, REDIS_URL, ADMIN_SECRET_PATH

flask db upgrade
flask --app app init_db

flask --app app run
```

Open http://localhost:5000/ — the homepage, about page, error pages, and template flow are wired up. The recommendation backend is intentionally absent, so AI features will not respond.

## License

MIT — see [LICENSE](LICENSE).
