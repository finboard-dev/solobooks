---
type: concept
created: 2026-07-17
modified: 2026-07-18
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-18-bucket1-fixes.md, raw/2026-07-18-scope-calls.md]
tags: [locking, close, retained-earnings]
---

# Period Locking & Month Close

> One field (`locked_through` on [[company-object]]) enforces immutability: every posting validates `date > locked_through`. Corrections to locked periods land in the current open month ([[general-ledger-sheet]] rule 4) — a locked month's sheet never changes.

## Month-close ritual (agent-guided checklist)

1. `verify_books` — trial balance ties, no pending drafts, unapplied credits / uncategorized / nonzero OBE / rec discrepancies resolved or acknowledged ([[safety-nets]])
2. **Reconcile each money account** — statement-based rec per [[bank-reconciliation]]. If no statement was imported for the month, fall back to the balance tie-out question ("books say Checking = $8,412 — does your bank agree?"), with any unexplained difference posted only to Reconciliation Discrepancies — never a silent plug.
3. Mini review: P&L, ending balances, unusual entries
4. `lock_period(through)` — audited (who/when/conversation)

## Unlock

Allowed in v1 (`unlock_period`), loudly audited, always requires approval ([[approval-flow]]); agent warns that shared reports may change. A re-opened month re-renders its sheet on re-lock — the one place re-rendering exists. **Artifact permanence:** before any re-render, the current sheet is archived ("General Ledger (as locked YYYY-MM-DD)" in `archive/` — never deleted) and the audit log records a diff summary (txn_ids added/removed/changed). Every rendering a banker or accountant may have seen survives ([[sheets-layer]]).

## Year-end close: nothing to do

No closing entries ever — **Retained Earnings is computed** in balance-sheet SQL (cumulative prior-year net income; current-year net income shown as its own equity line). `fiscal_year_start` just tells reports where years cut ([[reports-and-analytics]], [[dates-and-timezones]]).
