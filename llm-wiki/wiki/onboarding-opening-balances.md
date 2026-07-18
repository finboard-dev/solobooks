---
type: concept
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
tags: [onboarding, opening-balances]
---

# Onboarding & Opening Balances

> A solopreneur arriving mid-life of their business gets a clean starting point via one journal entry — never settings fields.

1. Create [[company-object]] → set `books_start_date`.
2. **Opening balance JE** dated books-start-minus-one-day, posted to the first [[general-ledger-sheet]]. Agent-guided, two depths: simple ("what was your checking balance on Jan 1?") or **full prior trial balance** for QuickBooks migrators — same JE, any accounts.
3. Whatever doesn't balance plugs to **Opening Balance Equity** ([[chart-of-accounts]]) — debits always equal credits even with partial info; accountant reclassifies later.
4. **Historical open invoices/bills** entered individually (real dates, posted to opening period) so aging and future payments work with proper refs ([[pairing-and-matching]]).
5. **Double-count rule:** the opening JE **never includes AR/AP lines** — compose rejects them; AR/AP at books start is built exclusively from the historical open documents. Historical invoices offset to **OBE, not Sales** (`DR AR / CR OBE`; bills `DR OBE / CR AP`) — the income belonged to the prior system's books. When a pre-books-start invoice is paid later, its OBE composition is a balance-sheet line → recognizes **nothing** in cash-basis P&L ([[cash-basis-recognition]] R4). No AR twice, no phantom income, no double taxation.
6. Until the opening JE posts, books are `incomplete` — reports run with a warning banner.

Seed [[chart-of-accounts]] is created here too. The opening JE anchors all [[point-in-time-balances]].
