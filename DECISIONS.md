# Decisions

Stuff we had to guess. What we picked and why.

## Multi-tenancy

**Chose:** Shared schema, `client_name` on Source, all analysts see everything.

**Why:** Assignment workflow is internal review, not client self-serve portals.

**Ignored:** Per-tenant DB, row-level security, client login.

**Ask PM:** Do clients ever log in, or only Breathe analysts?

---

## SAP

**Chose:** Semicolon **flat file CSV** upload (German-friendly headers OK).

**Why:** Real SAP teams often send Z-report / ME export as CSV/TXT, not raw IDoc. IDoc/OData/BAPI are heavier than we had time for.

**Subset we handle:**

- Fuel lines (plant, qty, L)
- Procurement lines (KG, material type)
- Dates like `28.05.2026`
- Plant codes without lookup table (shown as-is)

**Ignored:** IDoc, OData, BAPI, currency, GR/IR, proper UoM master data.

**Ask PM:** Which SAP report name do they actually export today?

---

## Utility

**Chose:** **Portal CSV** upload.

**Why:** Facilities teams usually download CSV from utility portal monthly. PDF needs OCR; APIs are rare on day one.

**Subset:**

- Account, meter, period start/end, kWh

**Ignored:** PDF bills, tariff breakdown, time-of-use, green certificates.

**Ask PM:** Which utility portals / countries for this client?

---

## Travel

**Chose:** **JSON file** shaped like a trimmed Concur expense list (simulates API payload).

**Why:** Real Concur API needs OAuth and paging. JSON lets us show "API-shaped" data without integration time. Still uploaded as a file for same UX as CSV.

**Subset:**

- Air / hotel / ground categories
- Airport codes, optional `distanceKm`
- Estimate km from airport pair if missing (stub table)

**Ignored:** Live Concur/Navan API, per-diem, hotel nights, rail detail.

**Ask PM:** Do they have Concur API credentials or only exports?

---

## Ingestion mechanism

**Chose:** One endpoint `POST /api/sources/upload` for all three types.

**Why:** Same analyst flow: pick type, client, file → rows appear.

**Ignored:** Scheduled jobs, SFTP, email inbox, manual paste UI.

---

## Emissions

**Chose:** Simple factors at ingest (diesel L, grid kWh, km, trip fallback).

**Why:** Assignment wants normalized data + something to review, not full GHG Protocol engine.

**Ignored:** DEFRA/EPA libraries, market vs location based Scope 2, biogenic carbon.

---

## Suspicious rows

**Chose:** Rule-based flags at parse time (zero qty, bad period, missing distance, weird unit).

**Why:** Dashboard needs "what looks wrong" without ML.

**Ignored:** Full validation rule engine UI.

---

## Auth

**Chose:** Token auth, demo users `alice` / `bob`, seeded on deploy via `build.sh`.

**Ignored:** SSO, password reset, role-based approve permissions.
