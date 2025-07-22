# PintxoPote

Django web‑app for recording, searching, and sharing pintxo bar notes in San Sebastián.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=pintxopote.settings
python manage.py migrate
python manage.py runserver
```

Set enviornmental variable DJANGO_ALLOWED_HOSTS for allowed hosts.

The app will be available at `http://127.0.0.1:8000/`.

### Deployment

Commit & push to **GitHub → main**. Railway auto‑deploys, mounts a persistent volume for the SQLite DB and `/static/uploads`.

### Admin token

Set `ADMIN_TOKEN` as an environment variable on Railway to enable edit routes. Public visitors have read‑only access.

---

This repository was bootstrapped via ChatGPT “AI‑gen coding” using the dev‑brief in `dev-brief.md`.
