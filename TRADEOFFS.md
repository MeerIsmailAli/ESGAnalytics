# Tradeoffs — three things we did NOT build

## 1. Live SAP / Concur / utility APIs

**What we skipped:** OAuth pulls, OData, Concur expense API, utility Green Button APIs.

**Why:** Integration and credentials eat the whole week. File upload matches how messy first onboardings actually happen (email attachments, portal exports).

**Cost:** Manual re-upload when data changes; no automatic sync.

---

## 2. Real emission factors and UoM conversion

**What we skipped:** Factor libraries (DEFRA, EPA eGRID), plant/material master lookups, currency, proper unit conversion tables.

**Why:** Carbon math is a product on its own. We needed ingest + review + audit trail first.

**Cost:** `emissions_kg_co2e` is illustrative only — not auditor-ready. German SAP units and plant codes stay opaque.

---

## 3. Lock-after-approve and full edit history

**What we skipped:** Immutable approved rows, field-level diff, analyst edit with re-approval workflow.

**Why:** Status + flagged_by/approved_by + AuditLog is enough to show intent. Full immutability needs more UI and API rules.

**Cost:** Approved rows can still be deleted or status-changed in prototype — would need hard locks before real audit export.
