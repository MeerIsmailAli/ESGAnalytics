# Sources — research, samples, what breaks in prod

## 1. SAP (fuel & procurement)

### What we researched

SAP data often arrives as:

- **Flat files** (CSV/TXT, semicolon in EU), from custom reports
- IDoc / OData / BAPI exist but need SAP team + middleware

Common pain: German headers (`Budat`, `Werk`, `Menge`, `MEINS`), plant codes without names, dates `DD.MM.YYYY`, mixed units.

### What we built

- Upload: `backend/sample_files/sap_acme.csv`
- Semicolon delimiter, columns: posting date, plant, material, qty, unit, material type, document id
- Fuel → Scope 1; procurement type → Scope 3

### Why sample looks like this

Row with `1200 L` diesel is normal. Row with `0 L` is **intentionally bad** (tests suspicious flag). `5000 KG` procurement is typical spend/mass proxy.

### What breaks in real deployment

- Different column names every client
- Need material/plant master to interpret codes
- Multiple plants per file, currencies, corrections/credits
- Files bigger than memory — need chunked parse

---

## 2. Utility (electricity)

### What we researched

Facilities teams usually:

- Log into **utility portal** → download **CSV** (account, meter, billing period, kWh)
- PDF bills are common but need OCR
- Billing periods rarely match calendar months

### What we built

- Upload: `backend/sample_files/utility_globex.csv`
- Columns: account, meter_id, period_start, period_end, consumption, unit
- Scope 2, normalized to kWh

### Why sample looks like this

Normal month ~45k kWh. Zero kWh month flags suspicious. Quarter row has **>90 day period** flag.

### What breaks in real deployment

- Every utility uses different column names
- Multiple tariffs, demand charges, estimated vs actual reads
- PDF-only utilities
- Need Green Button / Arcadia-style API later

---

## 3. Travel (Concur-style)

### What we researched

Concur / Navan expose APIs but onboarding often starts with **expense exports**. Categories map to different emission methods (air vs hotel vs ground). Flights may only have **airport codes**, not km.

### What we built

- Upload JSON: `backend/sample_files/travel_acme.json`
- Shape: `{ "expenses": [ { id, expenseType, origin, destination, distanceKm? } ] }`
- Simulates API body saved as a file
- Scope 3; km from field or small airport-pair stub

### Why sample looks like this

- Flight DEL-BOM with km — clean case
- Hotel — no distance, trip fallback
- Ground — short hop
- LHR-JFK **without** km — tests estimation + suspicious flag

### What breaks in real deployment

- Real API pagination, auth token refresh
- Multi-leg trips, refunds, personal vs business
- Hotel nights need different factor than km
- Need proper great-circle distance DB, not 4 hardcoded pairs

---

## How to test locally

```bash
cd backend
python manage.py seed_demo   # loads all three sample files
```

Or use the dashboard **Upload & ingest** with the same files from `backend/sample_files/`.
