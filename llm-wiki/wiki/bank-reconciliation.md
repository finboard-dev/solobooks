---
type: concept
created: 2026-07-18
modified: 2026-07-30
status: verified
sources: [raw/2026-07-18-scope-calls.md, raw/2026-07-18-cpa-firm-review.md, raw/2026-07-18-cas-firm-review.md, raw/2026-07-30-process-aware-objects.md]
tags: [reconciliation, controls, v1]
---

# Bank Reconciliation (v1 — the trust floor)

> Statement-based reconciliation per money account per month, built on the CSV import. Demanded independently by the buyer panel's advisors, the CPA review, and the CAS review — "the single biggest gap between this design and reliance."

- **A `REC_RUN`** ([[process-instance]]), one per money account × statement period — inputs: the imported statement rows ([[mcp-tool-surface]] `import_bank_csv`); outputs: cleared pairings, outstanding items, discrepancy amount. This replaces the ad-hoc Mongo "Rec object"; import and rec stop being two shapes of one loop. **(proposed 2026-07-30)**
- **Each statement-row-to-GL-line pairing is a `CLEARING` [[decision-record]]** — rule fired, alternatives not taken, confidence, actor ([[matching-engine]] cascade, unchanged). This is what makes a rec **re-performable**: today only a `cleared` boolean survives, so the pairing that produced it is lost and no reviewer can re-do the month. **(proposed 2026-07-30)**
- **`cleared` is an appended row, never a mutated cell** — written to the `Reconciliations` sheet ([[sheets-layer]]). It is not a [[general-ledger-sheet]] column (rejected by the column-admission rule) and never a cell edit on a posted GL row. **(proposed 2026-07-30)**
- **Statement rows are [[evidence]] at zero capture cost** — `STATEMENT_ROW` refs `{rec_id, row_no}` already exist in the run; linking them backs every clearing and every discrepancy without asking the user for anything. **(proposed 2026-07-30)**
- **Outstanding-items report**: uncleared checks/deposits (book-side lines with no statement match) — the reason book balance ≠ bank balance on most days, now shown instead of hand-waved.
- **No silent plugs**: an unexplained difference can only post to a dedicated **Reconciliation Discrepancies** account ([[chart-of-accounts]] seed), which [[safety-nets]] `verify_books` flags whenever nonzero.
- **Rec history**: each month's completed rec is stored and referenced by the close ([[period-locking-month-close]] step 2 upgrades from balance-check to statement rec when a statement exists; the balance-check remains the no-statement fallback).
- Statement rows that match *nothing* in the books feed the import draft queue — reconciliation and [[matching-engine]]-driven import are the same loop, reviewed in the batch grid ([[platform]]).

Cent-exact rec fixtures join [[testing-strategy]] layer 2.
