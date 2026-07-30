---
type: concept
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
tags: [onboarding, opening-balances]
---

# Onboarding & Opening Balances

> A solopreneur arriving mid-life of their business gets a clean starting point via one journal entry — never settings fields.

1. Create [[company-object]] → set `books_start_date`.
2. **Opening balance JE** dated books-start-minus-one-day, posted to the first [[general-ledger-sheet]]. Agent-guided, two depths: simple ("what was your checking balance on Jan 1?") or **full prior trial balance** for QuickBooks migrators — same JE, any accounts.
3. Whatever doesn't balance plugs to **Opening Balance Equity** ([[chart-of-accounts]]) — debits always equal credits even with partial info; accountant reclassifies later.
4. **Historical open invoices/bills** entered individually (real dates, posted to opening period) so aging and future payments work with proper refs ([[pairing-and-matching]]).
5. **Double-count rule:** the opening JE **never includes AR/AP lines** — compose rejects them; AR/AP at books start is built exclusively from the historical open documents. Historical invoices offset to **OBE, not Sales** (`DR AR / CR OBE`; bills `DR OBE / CR AP`) — the income belonged to the prior system's books. When a pre-books-start invoice is paid later, its OBE composition is a balance-sheet line → recognizes **nothing** in cash-basis P&L ([[cash-basis-recognition]] R4). No AR twice, no phantom income, no double taxation.
6. Books are `incomplete` — reports run with a warning banner — until the **whole onboarding completes**, not until the JE posts. **(proposed 2026-07-30)**

Seed [[chart-of-accounts]] is created here too. The opening JE anchors all [[point-in-time-balances]].

## Onboarding is an `ONBOARDING` [[process-instance]]

The sequence above had no artifact: mid-migration state lived nowhere, so a user who stopped after step 2 could not be resumed and could not be asked what was left. It becomes one process instance, `ONBOARDING-0001`, with steps `SEED_COA → OPENING_JE → HISTORICAL_OPEN_DOCS → BOOKS_COMPLETE`. **(proposed 2026-07-30)**

**The defect this fixes.** `books_state` flipped to `complete` when the opening JE posted — but by rule 5 that JE can **never** carry AR/AP lines, so books flipped to complete *before* the historical open documents that carry all AR/AP had been entered. The banner dropped exactly when it was still needed, and every report in between understated AR and AP. **(proposed 2026-07-30)**

- The flip depends on the **process instance completing** — opening JE posted **and** historical open documents declared done (or explicitly declared none) — never on the JE alone. **(proposed 2026-07-30)**
- "Declared done" is a `HUMAN` [[decision-record]]: the user asserts the migration is complete, and the assertion is the recorded fact. The system cannot know how many prior-system invoices existed. **(proposed 2026-07-30)**
- `books_state` is a report-header field, not a lock ([[policy-set]]): `incomplete` never blocks a posting. **(proposed 2026-07-30)**
