---
type: concept
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
tags: [architecture, mongo, sheets, duckdb]
---

# Three-Store Architecture

> Mongo = operational truth. Google Sheets = the translated ledger (the "books"). DuckDB = stateless calculator. One truth chain: Mongo documents → approved → journal lines appended to Sheets → DuckDB reads Sheets for all analytics.

| Store | Role | Holds |
|---|---|---|
| **MongoDB** | Operational truth | [[company-object]], contacts ([[dimensions]]), documents ([[document-model]]), drafts, ID counters, audit log, users/sessions |
| **Google Sheets** | The books | Monthly [[general-ledger-sheet]] + [[chart-of-accounts]] sheet, in Workspace **Shared Drives** ([[sheets-layer]]). Written ONLY by our service account; shared **view-only** with the user |
| **DuckDB** | Compute | Nothing persistent — loads GL+COA sheets per company on demand ([[reports-and-analytics]]) |

Key consequences:

- **Sheets are a projection of Mongo events, but the GL is the canonical ledger** — if a Mongo cache (e.g., invoice status) disagrees with the ledger, the ledger wins.
- **Users cannot edit sheets** (view-only share from service account) → integrity by construction, no drift detection needed.
- **Freshness is trivial:** we are the only writer. `ledger_version` on [[company-object]] bumps on every posting; DuckDB cache valid until it changes. No polling, no sync jobs.
- **Self-sufficiency rule:** the Drive folder must contain everything needed to read the books without our system (drives `due_date` column, COA-as-sheet). This is the exportability promise.

Drive folder layout: `<Company>/Chart of Accounts`, `<Company>/<Year>/<MM-Month>/General Ledger` (+ `attachments/` convention + `archive/` for pre-unlock renderings, [[period-locking-month-close]]), `<Company>/invoices/` for [[invoice-artifact]].
