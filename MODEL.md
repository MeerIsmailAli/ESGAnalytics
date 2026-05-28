# Data model

Plain English overview of what we store and why.

## Multi-tenancy (how we tag clients)

We use **one database, one schema, shared tables**. We do **not** hide data per analyst login.

- Each **Source** has a `client_name` (e.g. Acme Corp, Globex).
- That is **column-based multi-tenancy**: same tables, filter/report by client when you need to.
- Breathe analysts are internal users; they can see all clients on the review dashboard.

If we needed client-only access later, we'd add permissions per `client_name` — not built in this prototype.

## Main tables

### User (`core.User`)

- Django user + `role` (analyst/admin).
- Used for login and for `created_by` / `flagged_by` / `approved_by`.

### Source

One **ingestion batch** — one file upload or one manual registration.

| Field | Purpose |
|-------|---------|
| name | Label for this batch |
| source_type | `sap`, `utility`, `travel` |
| client_name | Which enterprise client |
| filename | Original file name |
| created_by, created_at | Who uploaded and when |

### Entry

One **normalized row** ready for analyst review (and later audit export).

| Field | Purpose |
|-------|---------|
| source | Which ingestion batch this came from |
| label | Human-readable summary |
| status | `new`, `flagged`, `approved` |
| scope | GHG Scope `1`, `2`, or `3` |
| activity_type | e.g. fuel, procurement, electricity, flight |
| quantity, unit | As parsed from file |
| normalized_quantity, normalized_unit | Simple normalized units (L, KG, KWH, KM, TRIP) |
| emissions_kg_co2e | Prototype estimate at ingest time |
| period_start, period_end | Utility billing window (optional) |
| external_id | Id from source file (dedup helper) |
| raw_data | JSON copy of original row — **source of truth** |
| is_suspicious, suspicion_reason | Auto flags for review |
| created_by, flagged_by, approved_by + timestamps | Who did what |

### AuditLog

Append-only style log of actions: ingested, flagged, approved, deleted.

Tied to `entry` + `user` + `action` + optional `note`.

## Scope rules (prototype)

| Source | Typical scope | Why |
|--------|---------------|-----|
| SAP fuel | 1 | Direct fuel |
| SAP procurement | 3 | Purchased goods |
| Utility electricity | 2 | Purchased energy |
| Travel | 3 | Business travel |

## Unit normalization

We don't do full SAP UoM conversion. Parsers map to a small set:

- Fuel/procurement: keep L or KG from file
- Utility: kWh → `KWH`
- Travel: km if present, else `TRIP` fallback

Emissions = `normalized_quantity × hardcoded factor` (see `parsers/emissions.py`). **Not audit-grade** — documented in TRADEOFFS.md.

## Source-of-truth chain

```
Uploaded file
  → Source record (metadata)
  → Entry rows (parsed + normalized)
  → raw_data JSON (exact parsed fields)
  → Analyst flag/approve (updates status + flagged_by/approved_by)
  → AuditLog entries
```

If a row was edited manually later, we'd extend AuditLog — for now edits are status changes only.

## Audit trail (what reviewers care about)

- **Ingested**: automatic on upload
- **Flagged / Approved**: set user + timestamp on Entry + AuditLog row
- **Deleted**: AuditLog written before row removed

Approved rows are the ones we'd treat as "locked for audit" in a v2 (no edit after approve — not enforced in code yet).
