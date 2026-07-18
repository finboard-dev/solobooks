# Professional review — Dan Kowalski, CPA (persona: cpa-firm partner, 22-person Ohio firm)

Deep design review from the accountant who receives the books in January and signs a Schedule C
based on them. Read 19 wiki pages. Status: findings NOT yet ingested/fixed — raw input.

## Findings (numbered, verbatim condensed)

1. **Cash-basis page contradicts itself on the #1 transaction.** Headline rule "only money-account
   transactions drive recognition" vs enumeration listing "owner draw/expense as-is". Owner-paid
   expense (DR Expense / CR Owner's Contributions) touches NO money account. Enumeration is right
   (deduction legitimate when owner pays — same taxpayer); headline rule is wrong. One canonical
   statement needed or v_pnl_cash is a coin flip on real deductions.
2. **Owner's Draw listed as "money↔P&L document" — it is EQUITY, not P&L.** Draw = DR Owner's Draw /
   CR Bank; never deductible, never on Schedule C. As written, draws land in cash-basis P&L as expense.
3. **BillPayment cash recognition has no carve-out for asset legs.** Cash-basis taxpayers still
   capitalize fixed assets; a paid $4,000 laptop bill would flow to cash P&L under the stated rule.
   Pro-rata must stop at balance-sheet accounts. State + fixture-test.
4. **P&L legs riding on Payment documents have no stated cash rule** (Stripe fee 30 in DR Bank 970 /
   DR Fees 30 / CR AR 1000) and "non-cash settlements recognize nothing: early-pay discounts"
   collides with the $0.99 tolerance auto-line. Rule needed: any P&L leg on a document that moves
   money recognizes at that document's date — else cash income never ties to bank deposits.
5. **Rules endorsed on record:** card-charge-date (Rev. Rul. 78-38 — correct), retainers taxable at
   receipt (correct + courageous), pro-rata incl. tax line (QBO convention), bad debt nothing on cash,
   NSF at reversal date. **Flagged:** cash-basis sales-tax liability — several states require
   invoice/accrual-basis remittance regardless of income-tax basis; report can tell an Ohio client to
   underpay the state. Disclose basis on the report face at minimum.
6. **Opening-balance double-count trap:** full prior TB includes AR control AND historical open
   invoices post DR AR / CR Sales → AR twice + phantom income. Needs explicit rule (suppress opening
   JE AR line when documents entered, or historical invoices offset OBE not Sales) + what happens when
   a pre-migration invoice is paid post-migration (Sales vs OBE changes the return). Tested.
7. **The balance check is not a bank reconciliation.** Book balance shouldn't equal bank balance on
   most closing days (outstanding checks, deposits in transit). "Mismatch → post an adjustment" is an
   invitation to plug. Need statement-based rec off the CSV import: matched/unmatched lines,
   outstanding-items list; any plug routed to a Reconciliation Discrepancies account that verify_books
   screams about. THE single biggest gap between design and reliance.
8. **Unlock re-render breaks the immutability promise for shared artifacts.** P&L sent to a banker in
   March, February re-rendered in June — visible artifact changed, no visible trace. Archive
   pre-unlock renderings + emit a diff into the audit trail.
9. **Categorization is the un-audited LLM surface** (matching is well-fenced; categorization isn't).
   Need a categorization review report: every agent account choice with the client's verbatim words
   (memo_verbatim already stored — use it).
10. **approval_mode: none must be visible in the record** — packet states approval mode in force per
    period; auto-posted entries flagged individually. E&O-relevant.
11. **1099 report will over-report:** card/processor payments are excluded from 1099-NEC (1099-K
    problem). Payment `method` must drive the report (currently "metadata only"). Also missing: W-9/TIN
    capture, $600 threshold, NEC vs MISC, corp exemption.
12. **No Schedule C mapping anywhere.** One optional tax_line field on COA + packet report grouped by
    it = "the return practically drafts itself." Cheap. Do it.
13. **No accrual-to-cash bridge report** (ΔAR, ΔAP, Δunearned, non-cash). The testing-strategy
    assertion IS the report — ship it in the packet, not just the test suite.
14. **Seed COA gaps: no loan accounts** (Notes Payable, Interest Expense) — principal/interest split is
    a top-3 miscoding. verify_books should flag nonzero OBE at close.
15. **Computed RE sound.** State that BS shows current-year net income as its own equity line;
    consider presentation-only annual roll of draws.
16. **Substantiation honestly out of scope** — trail proves what was posted, not that it happened.
    Would still test: 12 bank recs, cutoff, uncategorized/unapplied at 12/31, OBE, categorization sample.

## Missing requirements for firm blessing (verbatim list)

1. Statement-based bank/credit-card reconciliation (non-negotiable)
2. One internally consistent cash-basis spec (fixes 1–4) + fixtures
3. Schedule C tax-line mapping on COA + packet report
4. Accrual-to-cash bridge report in packet
5. 1099 workflow: method exclusion, W-9/TIN, threshold, NEC/MISC
6. Migration double-count rule, stated + tested
7. Locked-period artifact permanence (archive + diff)
8. Approval-mode disclosure per period; auto-posted entries flagged
9. Categorization review report (choice + verbatim words, exportable)
10. Exportable audit log + all tolerance write-offs for the year
11. verify_books: nonzero OBE, stale unearned, aged unapplied credits, rec-discrepancy balance
12. Loan accounts in seed COA + principal/interest agent rule
13. Sales-tax basis disclosure on the liability report
14. Fixed-asset additions listing in packet

## Bottom line (verbatim)

Skeleton better than it has any right to be; the crux page (cash-basis) is exactly where he'd sign
his name and currently contains an internal contradiction, an equity account in the P&L, an
uncapitalized-asset leak, and an unstated fee-leg rule — on top of a verbal yes/no "reconciliation"
and an over-reporting 1099. Fix cash-basis to one defensible page, real bank rec, bridge report,
Schedule C lines → "the rare tool I'd hand to my messiest Schedule C clients and thank." As designed
today: "a shoebox with unusually good handwriting — legible, organized, and still fully re-verified
before anything touches a return."
