---
type: concept
created: 2026-07-18
modified: 2026-07-18
status: verified
sources: [raw/2026-07-18-scope-calls.md, raw/2026-07-18-cpa-firm-review.md, raw/2026-07-18-cas-firm-review.md]
tags: [reconciliation, controls, v1]
---

# Bank Reconciliation (v1 — the trust floor)

> Statement-based reconciliation per money account per month, built on the CSV import. Demanded independently by the buyer panel's advisors, the CPA review, and the CAS review — "the single biggest gap between this design and reliance."

- **Rec object** (Mongo): money account × statement period → imported statement rows ([[mcp-tool-surface]] `import_bank_csv`) matched against posted GL lines; each line carries `cleared` status.
- **Outstanding-items report**: uncleared checks/deposits (book-side lines with no statement match) — the reason book balance ≠ bank balance on most days, now shown instead of hand-waved.
- **No silent plugs**: an unexplained difference can only post to a dedicated **Reconciliation Discrepancies** account ([[chart-of-accounts]] seed), which [[safety-nets]] `verify_books` flags whenever nonzero.
- **Rec history**: each month's completed rec is stored and referenced by the close ([[period-locking-month-close]] step 2 upgrades from balance-check to statement rec when a statement exists; the balance-check remains the no-statement fallback).
- Statement rows that match *nothing* in the books feed the import draft queue — reconciliation and [[matching-engine]]-driven import are the same loop, reviewed in the batch grid ([[platform]]).

Cent-exact rec fixtures join [[testing-strategy]] layer 2.
