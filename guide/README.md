# Draftspot Development Workflow

This guide describes how to develop Draftspot without touching production by accident.

## Environments

| Environment | Git branch | Frontend | Backend | Database | Telegram bot |
| --- | --- | --- | --- | --- | --- |
| Local | feature branches | `http://127.0.0.1:5173` | `http://127.0.0.1:8000` | Supabase dev | Dev bot via ngrok |
| Staging | `develop` | Vercel Preview | Render `draftspot-backend-dev` | Supabase dev | Dev bot |
| Production | `main` | Vercel Production | Render production backend | Supabase production | Main bot |

Production data must not be used for UI experiments, seed data, or manual SQL tests.

## Git Flow

Use `main` only for production-ready code.

```bash
git switch develop
git pull origin develop
git switch -c feature/short-task-name
```

After testing locally, merge the feature into `develop`. Vercel creates a Preview deployment and Render dev deploys the backend from `develop`. Test in the dev Telegram bot before merging to `main`.

## Local Backend

Create `backend/.env` from `backend/.env.example` and point `DATABASE_URL` to the Supabase dev project.

Run the backend without changing Telegram webhook:

```bash
cd backend
SERVERLESS=true ../.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If you need Telegram webhook locally, run ngrok and set `WEBHOOK_BASE_URL` to the ngrok HTTPS URL:

```bash
ngrok http 8000
```

Then set the dev bot webhook to:

```text
https://api.telegram.org/botDEV_BOT_TOKEN/setWebhook?url=https://NGROK_URL/bot/webhook
```

## Local Frontend

Create `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

Run:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

For real Telegram authentication, test through the dev bot. Browser-only local testing can verify layout, but protected API calls require signed Telegram `initData`.

## Supabase Dev Database

Run SQL in this order in the dev Supabase project:

1. `backend/sql/schema.sql`
2. `backend/sql/dev_seed.sql`

The seed is idempotent. It clears only rows created by the seed marker and recreates demo venues, users, events, applications, and favorites.

## Render Dev Backend

Render dev service:

```text
Name: draftspot-backend-dev
Branch: develop
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

```env
BOT_TOKEN=dev-bot-token
DATABASE_URL=postgresql+asyncpg://...
WEBHOOK_BASE_URL=https://draftspot-backend-dev.onrender.com
MINI_APP_URL=https://vercel-preview-url
WEBHOOK_PATH=/bot/webhook
PYTHON_VERSION=3.10.14
```

`DATABASE_URL` must start with `postgresql+asyncpg://`. If a password contains special characters, URL-encode them.

## Vercel Environments

Use one Vercel project with different environment values:

```text
Production VITE_API_BASE_URL = https://production-backend.onrender.com/api
Preview    VITE_API_BASE_URL = https://draftspot-backend-dev.onrender.com/api
```

Preview deployments must be publicly accessible for Telegram Mini App testing. If Telegram opens a Vercel login screen, disable Deployment Protection for Preview or use a public staging deployment.

## Promotion Checklist

Before merging `develop` into `main`:

- Frontend build passes.
- Backend starts on Render dev.
- Dev bot `/start` works.
- Mini App opens Vercel Preview without login.
- Create event works against Supabase dev.
- Feed, favorites, applications, and profile behave correctly.
- Any required SQL migration has been run on dev first.

Only after this checklist is clean should the change move to production.
