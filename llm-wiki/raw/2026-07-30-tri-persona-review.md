# Tri-Persona Review — CFO / Shopify solopreneur / CPA firm (2026-07-30)

> Immutable source. Three independent in-character reviews of the design *after* the process-aware object-model realignment, each adversarially verified against file text. 43 findings → 5 refuted → **0 blocking, 6 serious**, remainder minor or scope-confirming.
>
> Method note recorded for honesty: the first verification pass keyed verdicts by finding id, and the seller and CFO had both numbered findings `F1…`. Their verdicts collided and the pass was re-run with namespaced ids. Only the re-run is authoritative. The persona verdicts, headlines and realignment assessments were never affected — they come from the reviewers, not the verifiers.

## Verdicts

**Shopify solopreneur** (~$40k/mo gross, ~900 orders/mo, sole prop, Schedule C, cash basis) — *would not adopt today.*
> "It is not because of anything on the 'Out of v1' list — it is because there is no correct entry path for the only way money reaches my business."

Every dollar arrives as a net settlement batch: a $3,812.44 payout = gross $4,150.00 − refunds $180.00 − fees $157.56, spanning 2–3 days of orders. Booking it as a `SalesReceipt` hides $17,160/yr of deductible fees and under-reports gross receipts by $36,360 against the 1099-K. **Verifier reversal:** `post_journal_entry` already expresses the correct compound entry, so his net income ties today — the harm is *labor, not error*. Downgraded blocking → serious; the fix is seed accounts + a skill rule, **not** a tenth document type.

**Fractional CFO** (8 clients, $2M–$30M) — *(b): not a system I would put a client on, but the bones are right and I would not have to tear them out.*
> "The audit layer you just designed is genuinely ahead of QuickBooks and worth building first."

All findings downgraded to minor. His substantive point is strategic, not defect-shaped: none of the realignment touches the numbers, and his money is on budget-vs-actual, an indirect cash flow statement that ties, and a formatted deliverable. Sharpening on the v2 thesis: **the wedge is the cross-client exceptions/close console, not multi-company bookkeeping** — "nobody moves 20 clients off QuickBooks."

**CPA firm (Dan, 2nd pass)** — *conditionally yes.*
> "I would rather inherit these books than any QBSE or Wave file I get today, but not until [the two numbers I sign] are fixed."

Gate 2 (who decided what, re-performably) is won and he says so. Gate 1 (arithmetic that ties to the bank) has two open defects and three recognition rules.

## The six serious findings

1. **Processor payouts have no seed accounts or skill rule** (seller). Fix: seed `Merchant Clearing` (1xxx) and `Sales Returns & Allowances` (4xxx contra) + one skill rule — *a processor payout is never revenue; decompose it.* No new document type.
2. **The opening-balance fix over-corrected** (CPA). Historical open documents offset to OBE, and OBE-composition documents recognize nothing (R4) — correct for a prior *accrual* filer, a **double omission** for a prior *cash* filer, dropping real income and deductions off the migration-year return. Fix: `prior_books_basis`.
3. **The "statement-based" reconciliation never captures the statement's ending balance** (CPA), so it proves nothing about completeness — a transaction missing from both sides is invisible. Note the balance-check *fallback* it replaces does capture the bank balance. Fix: statement balances on `REC_RUN` + a four-term residual.
4. **R5 wrongly says offset JEs recognize nothing** (CPA). On cash basis a mutual offset is constructive receipt *and* constructive payment. Fix: carve out **R5a**.
5. **Processor-net deposits are unreachable from the matching cascade** (CPA). A Stripe/PayPal deposit short of the invoice by the fee falls to rule 7 and leaves a permanent AR stub — for consultants and creators taking cards, i.e. the *stated* market. Fix: a `NET_SETTLEMENT` cascade rule.
6. **No cutoff rule** (CPA). The import path dates payments at the clearing date — the wrong year for December checks, and invisible in the rec. Fix: **R10**.

## Strategic calls the review forces

- **Refuse the ecommerce batch market in `v1-scope` — and build finding 5 anyway.** Findings 1 and 5 share a root cause but only one is in-market. Building 5 while refusing the batch is what makes the refusal honest rather than evasive. The currently-recorded reason for the exclusion is **stale**: `scenario-catalog` defers batch deposits because they "matter only with bank feeds", written one day before CSV import and statement rec were pulled *into* v1.
- **Ship at "signable numbers", not "a better file."** The accountant channel is the adopted distribution channel; if the packet's promise is false on the two numbers Dan signs, the highest-scoring segment is lost to a fixable bug.
- **v2 leads with the exceptions/close console**, then a REST read API, then multi-company.

## Realignment scorecard (from the reviewers' own assessments)

| Element | Verdict |
|---|---|
| `provenance` at COMMIT | **Earned, unanimous.** Dan: 10–12 h → 3–4 h per client; the only unbackfillable item |
| `policy-set` (effective-dated, tax-line map, report header) | **Earned, unanimous.** Dan: "quiet E&O protection I would not have thought to ask for" |
| `ExceptionKind` + `Disposition` | **Earned.** "QuickBooks has no vocabulary for this at all" |
| `preview_hash` / `PREVIEW_DRIFT` | **Earned**, claim needs narrowing — it proves the ledger recorded what the server offered, not what the human saw. CFO: "if the founder builds exactly one thing, build this" |
| `process-instance` / `CLOSE_RUN` | **Earned for the v2 thesis, not the v1 buyer.** `REC_RUN` alone justifies the store |
| `evidence` (link seam) | Neutral, cheap, unobjectionable |
| `context-assembly` / `get_object(ref, lens)` | **Did not earn its keep — all three reviewers independently rated it irrelevant to their decision.** Dan: "five lenses of design surface aimed at a conversational user, and I will use exactly none of them" |

**Net: a good pass aimed at the wrong axis.** It fixed the file Dan inherits and moved none of the numbers he signs. All three reviewers said so independently.

## Sequencing constraint

Findings 2, 4 and 6 change R1–R9. `ruleset_versions {cash_basis: …}` is stamped into every policy set and every retained report header. **Close the ruleset before the first posting**, or the design commits the exact silent restatement `policy-set` was written to prevent — for the second time; `log.md` already records one R1–R9 rewrite.
