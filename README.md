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

## What's intentionally **not** in this repository

The following parts of the production system are excluded — either because they are proprietary, NDA-covered, or contain credentials:

- The recommendation engine, conversation-intelligence, and personality system
- All AI-provider routing logic (Ollama → Claude → OpenAI fallback)
- Web-scraping and data-acquisition pipelines
- Payment processing, subscription billing, fraud detection
- Age-verification and PCI-compliance modules
- Admin tooling, monitoring, analytics, scraping daemons
- All `.env` files, API keys, encryption keys, and OAuth secrets
- Internal documentation, patent disclosures, and survey data
- Database backups, training notebooks, and ops scripts

If you are evaluating this codebase for a hiring decision and want to see additional material under NDA, contact the author.

## Tech stack (visible from this excerpt)

- **Backend:** Python 3.8+, Flask 3, SQLAlchemy, Flask-Login, Flask-Migrate, Flask-Limiter, Celery
- **Database:** PostgreSQL with `pgvector` for embeddings
- **Cache / queue:** Redis
- **AI / ML:** LangChain (Anthropic, OpenAI, Google Generative AI), `sentence-transformers`, spaCy
- **Front-end:** Server-rendered Jinja2 templates, Bootstrap, vanilla JS for the portfolio page
- **Infra:** Gunicorn behind nginx, Docker-friendly, S3-compatible object storage for backups

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
