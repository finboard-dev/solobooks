# Bucket-1 fixes from professional reviews (2026-07-18)

Founder-directed corrections (no scope changes) from the CPA-firm review (Dan) and CAS-firm review
(Priya). Sources: raw/2026-07-18-cpa-firm-review.md, raw/2026-07-18-cas-firm-review.md.

## 1. Cash-basis spec rewritten to one consistent rule set (fixes Dan #1–#5)

R1 RECOGNITION EVENTS — a document recognizes on cash basis when it (a) moves a money account
   (Bank/Cash/Credit Card), (b) charges a credit card (charge date = payment, Rev. Rul. 78-38), or
   (c) records an owner-paid business expense (sole prop: owner's personal payment IS the taxpayer
   paying; DR Expense / CR Owner's Contributions recognizes at transaction date).
R2 EQUITY LINES NEVER RECOGNIZE — Owner's Draw, Owner's Contributions, OBE are equity, excluded from
   P&L on both bases. A draw is not an expense. (Fixes the draw-in-P&L error.)
R3 DIRECT P&L LEGS ON A RECOGNITION EVENT recognize as-is at that document's date — including
   processing-fee legs on payments, NSF fees, and $0.99-tolerance write-off lines (they accompany
   real cash). Ensures cash income ties to bank deposits.
R4 AR/AP SETTLEMENT — a recognition event settling a document recognizes that document's line
   composition pro-rata (applied ÷ document total) at settlement date, across ALL its lines, with:
   tax lines → liability-collected (never P&L); **balance-sheet lines stay balance-sheet** — an asset
   leg on a bill capitalizes (§263 still applies on cash basis; no laptop in the P&L).
R5 NON-CASH SETTLEMENTS RECOGNIZE NOTHING EVER — standalone CreditNote, VendorCredit, bad-debt
   write-off, offset JEs. (Distinction from R3: a discount line inside a payment document recognizes;
   a standalone credit note does not.)
R6 RETAINERS — recognized at receipt under "Customer deposits received"; later application non-cash.
R7 REFUNDS/NSF — negative recognition at their money-moving date.
R8 TRANSFERS — excluded both bases (incl. credit-card payoff).
R9 SALES-TAX REPORT BASIS DISCLOSURE — cash figure = tax portion of cash received; the report must
   state its basis on its face and warn that many states require accrual-basis remittance regardless
   of the taxpayer's income-tax basis; accrual figure available via toggle.

## 2. Opening-balance double-count rule (fixes Dan #6)

- The opening JE NEVER includes AR/AP control lines. AR/AP at books start is built exclusively from
  historical open documents.
- Historical open invoices offset to **Opening Balance Equity, not Sales** (DR AR / CR OBE);
  historical bills DR OBE / CR AP. The income/expense belonged to the prior system's books.
- Cash-basis interaction: when a pre-books-start invoice is paid post-migration, its composition is
  an OBE (balance-sheet) line → per R4, recognizes NOTHING in cash P&L. No phantom income, no double
  taxation. Validation: compose rejects opening JEs containing AR/AP lines.

## 3. 1099 method exclusion (fixes Dan #11 correctness core)

- Payment `method` is now ACCOUNTING-RELEVANT (supersedes "metadata for humans"): card and
  third-party-processor payments are EXCLUDED from 1099-NEC totals (processor's 1099-K territory).
- 1099 report = cash/check/ACH-transfer payments only, to track_1099 vendors, with the $600 threshold
  applied and per-vendor method breakdown shown.
- Still open as SCOPE decisions (not fixed here): W-9/TIN capture, NEC vs MISC classification,
  corporate-payee exemption flag.

## 4. Locked-artifact permanence on unlock (fixes Dan #8 / Priya finding 1-adjacent)

- Before any month re-render: the current sheet is archived in place (tab copy or file copy named
  "General Ledger (as locked YYYY-MM-DD)") in an `archive/` folder — never deleted.
- The audit log records a re-render diff summary (txn_ids added/removed/changed vs the archived
  rendering).
- The Drive folder therefore preserves every rendering a third party may have seen.

## 5. Synthesis page

professional-review-findings created (mirror of buyer-panel-findings) so scope discussion can cite
one page. Scope calls NOT decided here: statement-based bank rec in v1, batch review grid, recurring
billing pull-forward, Schedule C tax_line + bridge report in packet, accountant-seat v2 thesis —
listed as OPEN on the page.
