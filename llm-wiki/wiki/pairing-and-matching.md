---
type: concept
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
tags: [pairing, payments, open-balance, crux]
---

# Pairing & Matching (the crux)

> How money gets paired to documents. The system proposes, the human approves ([[approval-flow]]). Everything reduces to the **universal ref rule**.

## Universal ref rule — the single definition of settlement

> **Anything that credits AR (or debits AP) carrying a document ref settles that document — regardless of what created it.**

```
open_balance(INV-0042) = Σ debits − Σ credits   on AR lines where ref = INV-0042
```

Derived, **never stored**. Payments, credit notes, write-offs, offset JEs, discounts all settle through this one mechanism. Point-in-time: filter `date ≤ D` ("what did Acme owe me on Aug 31") — see [[point-in-time-balances]].

## Matching engine (money arrives, no bank feeds in v1 — user tells the agent)

In order:

1. **Exact** — one open invoice for the customer, balance == amount → propose.
2. **Combination** — amount = subset of open invoices (oldest-first) → propose split application.
3. **Partial** — amount < one invoice → partial application, remainder stays open.
4. **Overpayment** — apply all open + remainder becomes **unapplied customer credit** (never lost; surfaced by [[safety-nets]] cleanup).
5. **Deposit for a project with no invoice** → **retainer**: `DR Bank / CR Unearned Revenue (customer, project)`. On later invoicing: `DR Unearned Revenue / CR AR ref`. Income never recognized early.
6. **No context** → unapplied credit on the customer, listed until resolved.

Every match is a draft showing proposed `applications[]`; approval posts it. Implementation internals (deterministic rule cascade, MatchProposal, $0.99 tolerance): [[matching-engine]]. Payment doc carries `deposit_account`, `method` (accounting-relevant — drives the 1099-NEC exclusion, [[compliance]], and recognition events, [[cash-basis-recognition]]), `applications[] = [{invoice, amount}…]` — many-to-many both directions ([[document-model]]). AP mirrors everything for bills.

Concrete GL example — one payment, two invoices:

```
DR Checking 1,400                      (ref: PAY-0117)
CR AR 1,000   ref: INV-0042
CR AR   400   ref: INV-0043
```

Full edge-case treatments: [[scenario-catalog]].
