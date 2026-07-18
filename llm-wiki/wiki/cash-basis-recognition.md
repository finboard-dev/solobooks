---
type: concept
created: 2026-07-18
modified: 2026-07-18
status: verified
sources: [raw/2026-07-18-bucket1-fixes.md, raw/2026-07-18-cpa-firm-review.md]
tags: [cash-basis, accounting, canonical-definition]
---

# Cash-Basis Recognition (canonical rules R1–R9)

> One consistent rule set — THE definition `v_pnl_cash` ([[duckdb-layer]]) implements; fixtures in [[testing-strategy]] derive from these rules. (Revision history in `log.md`.)

- **R1 — Recognition events.** A document recognizes on cash basis when it (a) moves a money account (Bank/Cash/Credit Card), (b) charges a credit card — **charge date = payment** (Rev. Rul. 78-38; paying the card bill is a Transfer, no P&L), or (c) records an **owner-paid business expense** — sole prop: the owner's personal payment IS the taxpayer paying (`DR Expense / CR Owner's Contributions`, recognizes at transaction date, [[scenario-catalog]]).
- **R2 — Equity lines never recognize.** Owner's Draw, Owner's Contributions, OBE are equity — excluded from P&L on both bases. A draw is not an expense.
- **R3 — Direct P&L legs on a recognition event** recognize as-is at that document's date — including processing-fee legs on payments, NSF fees, and $0.99-tolerance write-off lines ([[matching-engine]]): they accompany real cash, so cash income ties to bank deposits.
- **R4 — AR/AP settlement.** A recognition event settling a document ([[pairing-and-matching]]) recognizes the settled document's line composition **pro-rata** (applied ÷ document total) at settlement date, across ALL its lines, where: tax lines → liability-collected, never P&L ([[compliance]]); **balance-sheet lines stay balance-sheet** — an asset leg on a bill capitalizes (§263 applies on cash basis too; no laptop in the P&L), and OBE-offset historical documents ([[onboarding-opening-balances]]) recognize nothing.
- **R5 — Non-cash settlements recognize nothing, ever**: standalone CreditNote, VendorCredit, bad-debt write-off, offset JEs. (Contrast R3: a discount line inside a payment document recognizes; a standalone credit note does not.)
- **R6 — Retainers**: recognized at RECEIPT under "Customer deposits received"; the later application is non-cash → no double count.
- **R7 — Refunds / NSF**: negative recognition at their money-moving date.
- **R8 — Transfers**: excluded, both bases.
- **R9 — Sales-tax basis disclosure**: the cash-basis `sales_tax_liability` figure = tax portion of cash received; the report states its basis on its face and warns that many states require accrual-basis remittance regardless of income-tax basis; accrual figure via toggle.

CPA endorsements on record (Dan review): card-charge-date, retainers-at-receipt, pro-rata incl. tax line, bad-debt-nothing, NSF-at-reversal. Accrual vs cash on any fixture ledger must differ *exactly* by unpaid/non-cash items ([[testing-strategy]] layer-5 gate).
