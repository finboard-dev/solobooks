---
type: concept
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
tags: [architecture, mongo, sheets, duckdb]
---

# Three-Store Architecture

> Mongo = operational truth. Google Sheets = the translated ledger (the "books"). DuckDB = stateless calculator. One truth chain: Mongo documents → approved → journal lines appended to Sheets → DuckDB reads Sheets for all analytics.

| Store | Role | Holds |
|---|---|---|
| **MongoDB** | Operational truth | [[company-object]], contacts ([[dimensions]]), documents ([[document-model]]), drafts, ID counters, audit log, users/sessions |
| **Google Sheets** | The books | Monthly [[general-ledger-sheet]] + [[chart-of-accounts]] sheet, in Workspace **Shared Drives** ([[sheets-layer]]). Written ONLY by our service account; shared **view-only** with the user |
| **DuckDB** | Compute | Nothing persistent — loads GL+COA sheets per company on demand ([[reports-and-analytics]]) |

**Truth is two domains, not one store beating another (proposed 2026-07-30).** [[financial-object-model]] owns the split; the local consequence for this page is that "Mongo = cache" is scoped down to *derived ledger facts* (invoice paid/unpaid, open balance) and nothing else. The context Mongo holds — origin, decisions ([[decision-record]]), process participation ([[process-instance]]), evidence links ([[evidence]]), policy in force ([[policy-set]]) — is canonical and append-only, and is **never a cache**: the GL has no opinion on why, so it cannot correct it.

Key consequences:

- **Sheets are a projection of Mongo events, but the GL is the canonical ledger** — if a Mongo cache (e.g., invoice status) disagrees with the ledger, the ledger wins. **"The ledger wins" is scoped to monetary and settlement disagreements (proposed 2026-07-30);** it decides no question of meaning.
- **Users cannot edit sheets** (view-only share from service account) → integrity by construction, no drift detection needed.
- **Freshness is trivial:** we are the only writer — no polling, no sync jobs. Cache invalidation rides one counter, `books_version`, defined in [[duckdb-layer]] **(proposed 2026-07-30)**.
- **Self-sufficiency rule, tier 1 — continuous:** the **ledger** is readable and tie-out-able from the Drive folder at every instant (drives `due_date` column, COA-as-sheet). This is the exportability promise.
- **Self-sufficiency rule, tier 2 — at close (proposed 2026-07-30):** the **record of how it got there** — the CloseRun ([[process-instance]]), its decision trail ([[decision-record]]), the policy header ([[policy-set]]) and the evidence index ([[evidence]]) — is exported into the Drive folder by the close, reusing the packet/bundle machinery in [[period-locking-month-close]]. Without tier 2 the promise silently narrows from "the books" to "the arithmetic", and exportability *is* the pitch ([[product-vision]]).

Drive folder layout: `<Company>/Chart of Accounts`, `<Company>/<Year>/<MM-Month>/General Ledger` (+ `attachments/` convention + `archive/` for pre-unlock renderings, [[period-locking-month-close]]), `<Company>/invoices/` for [[invoice-artifact]], and **`<Company>/Reconciliations` — one per-company sheet, the statement rec's durable human-legible face; layout owned by [[sheets-layer]] (proposed 2026-07-30)**.
