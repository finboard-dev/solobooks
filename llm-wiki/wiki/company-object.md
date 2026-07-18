---
type: entity
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
tags: [mongo, settings]
---

# Company Object

> Per-company settings JSON in Mongo, readable/editable via MCP. Carries the switches that drive accounting behavior.

| Field | Drives |
|---|---|
| `legal_name`, `name`, `contact_info` | [[invoice-artifact]] header |
| `fiscal_year_start` | "MM-DD", v1 requires day==01 ([[dates-and-timezones]]); where reports cut years ([[reports-and-analytics]]); no closing entries needed ([[period-locking-month-close]]) |
| `timezone` (IANA) | relative-date resolution + audit timestamp rendering ONLY — document dates are plain dates ([[dates-and-timezones]]) |
| `company_start_date` | history context |
| `books_start_date` | "we keep books from here" — anchors [[onboarding-opening-balances]] |
| `accounting_basis` (cash \| accrual) | default report basis ([[compliance]]) |
| `approval_mode` (all \| none) | [[approval-flow]] policy |
| `locked_through` | [[period-locking-month-close]] — postings must be dated after it |
| `sales_tax` {enabled, flat_rate} | invoice tax line ([[compliance]]) |
| `ledger_version` | DuckDB cache invalidation ([[three-store-architecture]]) |
| payment instructions (free text) | printed on [[invoice-artifact]] |
