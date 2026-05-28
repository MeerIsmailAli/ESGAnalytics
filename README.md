# Breathe ESG Prototype

ESG data ingest + analyst review dashboard.

- **SAP** — semicolon flat file CSV upload
- **Utility** — portal-style CSV upload  
- **Travel** — JSON file (Concur-like API shape)
- **Entries** — scope, emissions estimate, flag / approve / delete
- **Docs:** `MODEL.md`, `DECISIONS.md`, `TRADEOFFS.md`, `SOURCES.md`

## API

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/auth/login` | Login |
| GET/POST | `/api/sources` | List / add sources |
| POST | `/api/sources/upload` | Upload file (multipart: `source_type`, `client_name`, `file`) |
| GET/POST | `/api/entries` | List / add entries |
| PATCH | `/api/entries/:id` | Update status (`new`, `flagged`, `approved`) |
| DELETE | `/api/entries/:id` | Delete entry |

Sample files: `backend/sample_files/` (loaded by `seed_demo` on deploy).

Approving sets `approved_by` and `approved_at` automatically.

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
rm -f db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

## Demo login

- `alice / password123`
- `bob / password123`

Both are analysts and see the same shared data.

## Render deployment

### Backend (Web Service)

- **Root directory:** `backend`
- **Build command:** `./build.sh`
- **Start command:** `gunicorn config.wsgi:application`

`build.sh` runs: `migrate` → `seed_demo` → `collectstatic`

**Environment variables:**

| Variable | Example |
|----------|---------|
| `DATABASE_URL` | (from Render Postgres — auto if linked) |
| `SECRET_KEY` | long random string |
| `CORS_ALLOWED_ORIGINS` | `https://esganalytics-1.onrender.com` |

### Frontend (Static Site)

- **Root directory:** `frontend`
- **Build command:** `npm install && npm run build`
- **Publish directory:** `dist`

**Environment variable (required at build time):**

| Variable | Example |
|----------|---------|
| `VITE_API_URL` | `https://YOUR-BACKEND.onrender.com/api` |

Use your **backend** Render URL (not the frontend URL). After changing `VITE_API_URL`, trigger a **manual redeploy** of the frontend.

### Demo login (production)

- `alice / password123`
- `bob / password123`
