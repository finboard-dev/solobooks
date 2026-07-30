---
type: entity
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
tags: [mongo, settings]
---

# Company Object

> Per-company settings JSON in Mongo, readable/editable via MCP. Carries the switches that drive accounting behavior.

**Policy-bearing fields are a pointer, not free-standing scalars (proposed 2026-07-30).** `accounting_basis`, `approval_mode`, `sales_tax`, `fiscal_year_start` and `timezone` are held by the current versioned [[policy-set]]; the company object carries `policy_version_current` and resolves them **as-of a date**, never as-of now. Editing one mints a new policy version — an in-place mutation is the silent-restatement class [[policy-set]] enumerates. `locked_through` stays a scalar here: it is books *state*, not policy.

| Field | Drives |
|---|---|
| `legal_name`, `name`, `contact_info` | [[invoice-artifact]] header |
| `fiscal_year_start` | *policy-borne (proposed 2026-07-30)* — "MM-DD", v1 requires day==01 ([[dates-and-timezones]]); where reports cut years ([[reports-and-analytics]]); no closing entries needed ([[period-locking-month-close]]) |
| `timezone` (IANA) | *policy-borne (proposed 2026-07-30)* — relative-date resolution, audit-instant rendering, and instant→period mapping ONLY; document dates are plain dates ([[dates-and-timezones]]) |
| `company_start_date` | history context |
| `books_start_date` | "we keep books from here" — anchors [[onboarding-opening-balances]] |
| `accounting_basis` (cash \| accrual) | *policy-borne (proposed 2026-07-30)* — default report basis, stated on every report header ([[compliance]]) |
| `approval_mode` (all \| none) | *policy-borne (proposed 2026-07-30)* — [[approval-flow]] policy; stamped per posting in `provenance` ([[decision-record]]) |
| `locked_through` | [[period-locking-month-close]] — postings must be dated after it |
| `sales_tax` {enabled, flat_rate} | *policy-borne (proposed 2026-07-30)* — invoice tax line ([[compliance]]); a rate change must not restate an issued [[invoice-artifact]] |
| `policy_version_current` | pointer to the in-force [[policy-set]]; all rows marked *policy-borne* resolve through it **(proposed 2026-07-30)** |
| `books_version` (was `ledger_version`) | DuckDB cache invalidation — bump rule owned by [[duckdb-layer]] **(proposed 2026-07-30)** |
| payment instructions (free text) | printed on [[invoice-artifact]] |
