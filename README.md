# Breathe ESG Prototype - Phase 1

Simple shared-schema CRUD:

- **Sources** — register an ingestion source (SAP / utility / travel)
- **Entries** — rows under a source; analysts can flag, approve, or delete
- All analysts see all data (no tenant isolation)
- `created_by` / `approved_by` tracked on entries

## API

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/auth/login` | Login |
| GET/POST | `/api/sources` | List / add sources |
| GET/POST | `/api/entries` | List / add entries |
| PATCH | `/api/entries/:id` | Update status (`new`, `flagged`, `approved`) |
| DELETE | `/api/entries/:id` | Delete entry |

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
