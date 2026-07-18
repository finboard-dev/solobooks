# Scope calls decided (2026-07-18)

Founder approved all eight recommendations from the professional-review scope discussion.

1. **Statement-based bank reconciliation → v1.** Rec object per money account per month off the CSV
   import: per-line cleared/matched status against statement rows, outstanding-items report
   (uncleared checks/deposits), rec history, any plug forced to a dedicated Reconciliation
   Discrepancies account that verify_books flags. Close ritual step 2 upgrades from balance-check to
   statement rec when a statement is imported (balance-check remains the no-statement fallback).
2. **Batch review grid → v1, narrowly.** ONE read-only web grid for reviewing/approving/rejecting
   import drafts (columns: date, description, proposed account, amount, dup-flag; approve/reject per
   row + select-all). Explicit exception to "UI never renders a ledger" — it renders a DRAFT QUEUE,
   not the ledger. No other ledger UI.
3. **Recurring/retainer auto-billing → v1.1 first fast-follow** (not v1 gate): scheduler + auto-draft
   riding the existing approval flow.
4. **Accountant packet upgrades → v1:** COA gains optional `tax_line` (Schedule C mapping) + packet
   report grouped by tax line; accrual-to-cash bridge report (ΔAR/ΔAP/Δunearned/non-cash); open AR/AP
   item detail with refs; customer/vendor/project masters; categorization review report (account
   choice + memo_verbatim); approval-mode-per-period disclosure with auto-posted entries flagged;
   tolerance write-off list; fixed-asset additions listing; exportable audit log.
5. **Seed COA + verify_books → v1:** add Notes Payable + Interest Expense to seed chart + agent rule
   for principal/interest splits (skill); verify_books adds: nonzero OBE at close, stale unearned
   revenue, aged unapplied credits, nonzero Reconciliation Discrepancies.
6. **1099 completions (W-9/TIN capture, NEC vs MISC, corp exemption) → v1.5.**
7. **Mid-year historical transaction backfill → v1.5** (opening TB + open items is the v1 floor).
8. **Accountant seat / multi-client console → adopted as the v2 thesis** (not v1): multi-company
   accountant role, per-user audit attribution, cross-client close/exceptions console, REST read API.
   Decide timing after Phase-6 dogfooding.

## Plan impact (applied to 2026-07-17-solobooks-v1-plan.md)

- New Task 5.4: bank reconciliation (rec object, cleared flags, outstanding items, discrepancies
  account, rec report) + fixtures.
- Task 1.3 seed COA: + Notes Payable, Interest Expense, Reconciliation Discrepancies; accounts model
  gains optional tax_line.
- Task 7.2 accountant packet expanded per call #4; Task 7.3 verify_books additions per call #5.
- New Task 8.4: batch review grid (import-draft queue page, approve/reject wired to approval tools).
- Deferred list updated: recurring → v1.1 fast-follow; 1099 completions + historical backfill → v1.5;
  accountant seat → v2 thesis.
