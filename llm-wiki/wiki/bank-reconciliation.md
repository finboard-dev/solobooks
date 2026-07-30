---
type: concept
created: 2026-07-18
modified: 2026-07-30
status: verified
sources: [raw/2026-07-18-scope-calls.md, raw/2026-07-18-cpa-firm-review.md, raw/2026-07-18-cas-firm-review.md, raw/2026-07-30-process-aware-objects.md, raw/2026-07-30-tri-persona-review.md]
tags: [reconciliation, controls, v1]
---

# Bank Reconciliation (v1 — the trust floor)

> Statement-based reconciliation per money account per month, built on the CSV import. Demanded independently by the buyer panel's advisors, the CPA review, and the CAS review — "the single biggest gap between this design and reliance."

- **A `REC_RUN`** ([[process-instance]]), one per money account × statement period — inputs: `statement_period {start, end}`, **`statement_beginning_balance`, `statement_ending_balance`**, and the imported statement rows ([[mcp-tool-surface]] `import_bank_csv`); outputs: cleared pairings, outstanding items, the residual. This replaces the ad-hoc Mongo "Rec object"; import and rec stop being two shapes of one loop. **(proposed 2026-07-30)**

## The rec must tie to a balance, not just match rows (proposed 2026-07-30)

Matching rows proves nothing about **completeness**: a transaction absent from the books *and* unnoticed on the statement is invisible to row-matching. The defining arithmetic was missing, and the balance-check *fallback* this was meant to upgrade ("books say Checking = $8,412 — does your bank agree?") actually captured the bank balance that the upgrade did not.

```
    signed_statement_balance      (+ for asset accounts; − for credit-card/liability, i.e. owed is negative)
  + Σ uncleared book DEBITS  to the account   (date ≤ period end)
  − Σ uncleared book CREDITS to the account   (date ≤ period end)
  = adjusted balance
  residual = adjusted balance − signed book balance (Σ DR − Σ CR) at period end   → must be 0.00
```

**Stated in signed terms deliberately (proposed 2026-07-30).** On a bank account an uncleared debit is a deposit in transit and an uncleared credit is an outstanding cheque — but a **credit card is a money account too** ([[cash-basis-recognition]] R1) and both labels invert there: a debit is a payment, a credit is a charge. The deposit-in-transit / outstanding-cheque wording is bank presentation only; one signed definition holds for every money account. Getting this wrong makes every clean credit-card rec fail and then invites a monthly plug into Reconciliation Discrepancies.

**Clearing is a property of a `(txn_id, account_number, side)` triple, not of a transaction (proposed 2026-07-30).** One transaction clears on as many statements as it has money legs: a Checking→Savings transfer clears on the Checking statement in January and the Savings statement in February. A `txn_id`-only key marks it cleared everywhere at once and drives the second account's residual off by the whole transfer amount. **"Uncleared *as at a period end*"** means: no `rec_clears` row for that triple whose `statement_period` ends on or before that period end ([[sheets-layer]]). The qualification is not optional — unqualified, a December residual of 0.00 silently becomes the outstanding-cheque amount the moment the January run appends its rows, and a completed rec stops being reproducible. **Every residual is a function of a period, never of the sheet's current state. (proposed 2026-07-31)**

**The residual is computed after unmatched statement rows are dispositioned. (proposed 2026-07-30)** A bank fee on the statement but not yet in the books is not a discrepancy — it is a missing entry, and it routes to the import draft queue like any other unmatched row. Only what survives that pass is unexplained.

- `discrepancy_amount` **is that residual** — not leftover unmatched rows. A nonzero residual is the only thing that may post to **Reconciliation Discrepancies**, unchanged, and `verify_books` still flags it.
- **Period continuity:** `statement_beginning_balance` must equal the prior completed run's `statement_ending_balance` for that account. A mismatch means a skipped or overlapping statement and raises `REC_PERIOD_DISCONTINUITY` ([[safety-nets]]) — it is not silently absorbed into the residual.
- **Base case — the only free audit the opening balance ever gets. (proposed 2026-07-30)** The *first* run on an account has no prior run, so `statement_beginning_balance` is asserted against the book balance at `books_start_date − 1`, i.e. against the opening JE ([[onboarding-opening-balances]]). The user is already typing that number to do the rec at all, and the opening balance is otherwise never verified by anything. A mismatch names the opening JE rather than becoming an anonymous plug.
- **Statement periods are not calendar months. (proposed 2026-07-30)** Card statements routinely run 12/16→01/15. The close takes the run whose `statement_period` **contains** the month end, not one bounded by it ([[period-locking-month-close]]) — otherwise no card can ever produce a run for December and close step 2 is acknowledged away every month.
- **Clearings never reach a locked period. (proposed 2026-07-31)** A `CLEARING` is tested against the **accounting date of the GL line it pairs** — never against `cleared_at`, which is a decision instant and by [[dates-and-timezones]] never faces `locked_through`. Compared against `cleared_at` the rule would never fire for any clearing ever. A clearing on a line dated at or before `locked_through` is refused ([[period-locking-month-close]]); correcting a closed month's reconciled state is an `AMENDMENT` ([[process-instance]]) like any other post-lock change.
- **The `Reconciliations` sheet carries a `state` (CLEARED|UNCLEARED) column** and the effective state of a triple for a period is its **latest row**. Without it an erroneous pairing is permanent: the sheet is append-only, so a superseding row can only restate *which* statement cleared a line — never that it is **not** cleared — and a mis-pairing silently removes that line from every future outstanding-items term. **(proposed 2026-07-31)**
- Cutoff interacts here: where a statement row clears an entry already in the books, **the book date governs** and clearing only sets `cleared` ([[cash-basis-recognition]] R10). A misdated December cheque is invisible to this rec, which is why the rec is a control and not *the* control.
- **Each statement-row-to-GL-line pairing is a `CLEARING` [[decision-record]]** — rule fired, alternatives not taken, confidence, actor ([[matching-engine]] cascade, unchanged). This is what makes a rec **re-performable**: today only a `cleared` boolean survives, so the pairing that produced it is lost and no reviewer can re-do the month. **(proposed 2026-07-30)**
- **`cleared` is an appended row, never a mutated cell** — written to the `Reconciliations` sheet ([[sheets-layer]]). It is not a [[general-ledger-sheet]] column (rejected by the column-admission rule) and never a cell edit on a posted GL row. **(proposed 2026-07-30)**
- **Statement rows are [[evidence]] at zero capture cost** — `STATEMENT_ROW` refs `{rec_id, row_no}` already exist in the run; linking them backs every clearing and every discrepancy without asking the user for anything. **(proposed 2026-07-30)**
- **Outstanding-items report**: uncleared checks/deposits (book-side lines with no statement match) — the reason book balance ≠ bank balance on most days, now shown instead of hand-waved.
- **No silent plugs**: an unexplained difference can only post to a dedicated **Reconciliation Discrepancies** account ([[chart-of-accounts]] seed), which [[safety-nets]] `verify_books` flags whenever nonzero.
- **Rec history**: each month's completed rec is stored and referenced by the close ([[period-locking-month-close]] step 2 upgrades from balance-check to statement rec when a statement exists; the balance-check remains the no-statement fallback).
- Statement rows that match *nothing* in the books feed the import draft queue — reconciliation and [[matching-engine]]-driven import are the same loop, reviewed in the batch grid ([[platform]]).

Cent-exact rec fixtures join [[testing-strategy]] layer 2.
