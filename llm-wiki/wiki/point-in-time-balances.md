---
type: concept
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
tags: [balances, reporting, accounting]
---

# Point-in-Time Balances

> Because the ledger is complete and append-only, any balance at any date is a filtered sum. No snapshots stored anywhere — nothing to go stale or disagree.

- **Account balance as of D:** `Σ debit − Σ credit where account = X and date ≤ D`
- **Balance sheet as of D:** same, grouped by account type (point-in-time / stock)
- **P&L for a range:** `date between start and end` (flow) — the flow-vs-stock distinction is fundamental
- **Open balance as of D:** the ref sum of [[pairing-and-matching]] with `date ≤ D`

Anchored by the opening-balance JE at [[onboarding-opening-balances]] — day-one balances are posted as a journal entry, never typed in as settings.

Volume reality: a busy solopreneur ≈ 5k GL lines/year; DuckDB loads everything since inception in milliseconds ([[reports-and-analytics]]).
