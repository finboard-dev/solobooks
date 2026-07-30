---
type: concept
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-18-bucket1-fixes.md, raw/2026-07-18-scope-calls.md, raw/2026-07-30-process-aware-objects.md]
tags: [locking, close, retained-earnings]
---

# Period Locking & Month Close

> One field (`locked_through` on [[company-object]]) enforces immutability: every posting validates `date > locked_through`. Corrections to locked periods land in the current open month ([[general-ledger-sheet]] rule 4) — a locked month's sheet never changes.

## Month-close ritual — a `CLOSE_RUN`

The close is a `CLOSE_RUN` [[process-instance]] (`CLOSE-2026-07`), not a chat checklist: four steps with per-step state, and every exception **resolved or acknowledged as a recorded disposition** (`ExceptionKind` + disposition, [[safety-nets]]) instead of a sentence in a conversation. Today the profession's core control ritual persists exactly one scalar; the adopted v2 accountant seat ([[v1-scope]]) depends on close state being queryable. **(proposed 2026-07-30)**

1. `verify_books` — trial balance ties, no pending drafts, unapplied credits / uncategorized / nonzero OBE / rec discrepancies resolved or acknowledged ([[safety-nets]]); each unresolved item is a step exception carrying its disposition **(proposed 2026-07-30)**
2. **Reconcile each money account** — statement-based rec per [[bank-reconciliation]]; the month's `REC_RUN`s are step inputs **(proposed 2026-07-30)**. If no statement was imported for the month, fall back to the balance tie-out question ("books say Checking = $8,412 — does your bank agree?"), with any unexplained difference posted only to Reconciliation Discrepancies — never a silent plug.
3. Mini review: P&L, ending balances, unusual entries
4. `lock_period(through)` — audited (who/when/conversation), recorded as a `LOCK` [[decision-record]] and the run's closing output **(proposed 2026-07-30)**

**Close writes the tier-2 self-sufficiency export** ([[three-store-architecture]]) into the month folder — the completed `CLOSE_RUN` with its steps, exceptions and dispositions, plus the month's `REC_RUN`s — through the generalized outbox ([[sheets-layer]]). **(proposed 2026-07-30)**

## Unlock — a bounded `AMENDMENT`

Allowed in v1 (`unlock_period`), loudly audited, always requires approval ([[approval-flow]]); agent warns that shared reports may change. Unlock opens an `AMENDMENT` [[process-instance]] that **bounds** it — scope (which months), reason, what changed, the re-lock as its closing output — and `UNLOCK`/`LOCK` are decision records. Today rolling `locked_through` back to reopen July silently unlocks every month after it, with no object saying what is being amended or when the amendment ends; `verify_books` flags an OPEN amendment. **(proposed 2026-07-30)**

A re-opened month re-renders its sheet on re-lock — the one place re-rendering exists. **Artifact permanence:** before any re-render, the current sheet is archived ("General Ledger (as locked YYYY-MM-DD)" in `archive/` — never deleted) and the audit log records a diff summary (txn_ids added/removed/changed). That covers the GL sheet only, and the renderings outsiders actually see are P&Ls, agings and packets — those are governed by the retained-renderings rule in [[policy-set]], which is what makes "every rendering a banker or accountant may have seen survives" true as stated ([[sheets-layer]]). **(proposed 2026-07-30)**

## Year-end close: nothing to do

No closing entries ever — **Retained Earnings is computed** in balance-sheet SQL (cumulative prior-year net income; current-year net income shown as its own equity line). `fiscal_year_start` just tells reports where years cut ([[reports-and-analytics]], [[dates-and-timezones]]).
