# Breathe ESG Prototype - Phase 1

Minimal multi-tenant scaffold with:
- Django + DRF backend
- React frontend
- `POST /api/auth/login`
- `GET /api/analysis` (protected, tenant-filtered)

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Backend runs on `http://localhost:8000`.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`.

## Demo credentials

- `alice / password123` (Tenant: Acme Corp)
- `bob / password123` (Tenant: Globex)

## Multi-tenancy rule in code

Protected analysis endpoint filters by current user tenant:

`AnalysisRecord.objects.filter(tenant=request.user.tenant)`
