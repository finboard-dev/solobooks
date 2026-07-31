---
type: concept
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md, raw/2026-07-30-tri-persona-review.md]
tags: [onboarding, opening-balances]
---

# Onboarding & Opening Balances

> A solopreneur arriving mid-life of their business gets a clean starting point via one journal entry — never settings fields.

1. Create [[company-object]] → set `books_start_date`.
2. **Opening balance JE** dated books-start-minus-one-day, posted to the first [[general-ledger-sheet]]. Agent-guided, two depths: simple ("what was your checking balance on Jan 1?") or **full prior trial balance** for QuickBooks migrators — same JE, any accounts.
3. Whatever doesn't balance plugs to **Opening Balance Equity** ([[chart-of-accounts]]) — debits always equal credits even with partial info; accountant reclassifies later.
4. **Historical open invoices/bills** entered individually (real dates, posted to opening period) so aging and future payments work with proper refs ([[pairing-and-matching]]).
5. **Double-count rule:** the opening JE **never includes AR/AP lines** — compose rejects them; AR/AP at books start is built exclusively from the historical open documents. No AR twice, no phantom income, no double taxation. **It must equally never include a balance-sheet account that a historical open document's own composition will post. (proposed 2026-07-31)** Under `ACCRUAL` the historical document's offsetting leg is OBE, which cancels the opening JE's plug **by construction**, so nothing can double. Under `CASH` the offsetting leg is a real account — and a prior trial balance already carries every balance-sheet account, because only P&L accounts were closed to equity. A $12,000 machine on a pre-conversion unpaid bill otherwise lands **twice**: the trial balance still ties, net book value still looks plausible, and R11 depreciates the duplicate for seven years.
6. **Composition of a historical open document depends on `prior_return_basis` — asked once, at onboarding. (proposed 2026-07-30)**

The question is **"on the last return you filed, was business income reported on the cash method or the accrual method?"** — *not* what software the books were in. Under the cash method an unpaid invoice is never reported however the books were kept, so **"I had no books" can never mean "already reported"**; absent an accrual return the answer is `CASH`.

| `prior_return_basis` | Historical open invoice | Why |
|---|---|---|
| `ACCRUAL` | `DR AR / CR OBE` (bills `DR OBE / CR AP`) — recognizes **nothing** on collection ([[cash-basis-recognition]] R4) | the prior return already reported that income; recognizing again would double-tax |
| `CASH` (the default, and the answer whenever no accrual return was filed) | `DR AR / CR` **the account the sale actually was** (bills `DR` **the account the purchase actually was** `/ CR AP`), dated pre-`books_start_date` — R4 fires normally at settlement | the taxpayer has **never** reported it, so collecting it after conversion is income in the year received |

- **Do not hardcode `Sales` and `Expense`.** The credit on a historical invoice is whatever the sale was, and the debit on a historical bill is whatever the purchase was — including a **balance-sheet** account. A $12,000 unpaid bill for a machine composes `DR Machinery & Equipment / CR AP`; forcing it to `DR Equipment Expense` deducts the machine in full at settlement **and again** through §179/MACRS ([[cash-basis-recognition]] R11) — the same $12,000 twice. R4's balance-sheet carve-out must survive this branch intact. **(proposed 2026-07-30)**
- **Under `CASH`, a historical open document carries its real composition only where that composition is a P&L account. (proposed 2026-07-31)** Where it is a **balance-sheet** account the prior trial balance already carries it, so the document offsets **OBE** instead (`DR OBE 12,000 / CR AP 12,000` for the machine). The recognized result is identical either way — R4's balance-sheet carve-out and R2's OBE exclusion both recognize nothing — so this changes only the balance sheet, and it is the difference between one machine and two.
- Under `CASH` the pre-`books_start_date` date keeps the line out of every reported period, and each historical document is self-balancing on its own. **Self-balancing is not the same as non-duplicative (proposed 2026-07-31):** a P&L-composed document adds an account the prior trial balance never carried, so it cannot double; a balance-sheet-composed one would, which is why it offsets OBE instead.
- **Under `CASH`, OBE does not net to zero after migration. (proposed 2026-07-31)** The plug offsets pre-period P&L that flows to computed Retained Earnings, so equity is correct in total but split across two lines. `NONZERO_OBE` ([[safety-nets]]) fires on this branch and not on `ACCRUAL` — that is expected, not a missed check.
- The rule as originally written applied the `ACCRUAL` treatment to **everyone**, which for a prior cash-basis filer silently dropped both the income on collection and the deduction on payment — on the first return filed from these books, against a 1099 the payer did file. **(proposed 2026-07-30)**
- `prior_return_basis` is **not** a [[policy-set]] field. It is a `HUMAN` [[decision-record]] on this process instance, and its effect is then carried permanently by the composition of the posted documents. R4 keys off that composition, never off a resolved policy value, so nothing reads a field after onboarding day — a second copy on an effective-dated object could later contradict the ledger with no report able to tell. Correcting it is an `AMENDMENT` over the documents, not a new policy version. **(proposed 2026-07-30)**
7. Books are `incomplete` — reports run with a warning banner — until the **whole onboarding completes**, not until the JE posts. **(proposed 2026-07-30)**

Seed [[chart-of-accounts]] is created here too. The opening JE anchors all [[point-in-time-balances]].

## Onboarding is an `ONBOARDING` [[process-instance]]

The sequence above had no artifact: mid-migration state lived nowhere, so a user who stopped after step 2 could not be resumed and could not be asked what was left. It becomes one process instance, `ONBOARDING-0001`, with steps `SEED_COA → OPENING_JE → HISTORICAL_OPEN_DOCS → BOOKS_COMPLETE`. **(proposed 2026-07-30)**

**The defect this fixes.** `books_state` flipped to `complete` when the opening JE posted — but by rule 5 that JE can **never** carry AR/AP lines, so books flipped to complete *before* the historical open documents that carry all AR/AP had been entered. The banner dropped exactly when it was still needed, and every report in between understated AR and AP. **(proposed 2026-07-30)**

- The flip depends on the **process instance completing** — opening JE posted **and** historical open documents declared done (or explicitly declared none) — never on the JE alone. **(proposed 2026-07-30)**
- "Declared done" is a `HUMAN` [[decision-record]]: the user asserts the migration is complete, and the assertion is the recorded fact. The system cannot know how many prior-system invoices existed. **(proposed 2026-07-30)**
- `books_state` is a report-header field, not a lock ([[policy-set]]): `incomplete` never blocks a posting. **(proposed 2026-07-30)**
