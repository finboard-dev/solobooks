---
type: concept
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
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

## Two edges — `ref` vs `origin` (this page owns the distinction)

`ref` answers **"what does this settle?"** and remains the single definition of open balance above — unchanged. `origin` ([[document-model]]) answers **"what caused this to exist?"** — a recurring schedule, an import run, an amendment. Conflating them corrupts settlement semantics, because a causal edge would leak into the open-balance sum. `origin` is a Mongo field, never a GL column ([[general-ledger-sheet]]). **(proposed 2026-07-30)**

## Settlement outcomes (money arrives, no bank feeds in v1 — user tells the agent)

**Treatments, not a cascade — deliberately unordered. (proposed 2026-07-30)** Which rule fires, in what precedence, with which tie-break and which confidence, is owned solely by [[matching-engine]]. This page previously restated that as its own ordered list and the two had already drifted: the cited-invoice rule was missing here, the subset tie-break disagreed (`oldest-first` here vs `prefer fewest, then oldest` there — on open invoices of $100/$400/$500 a $500 payment settles a *different* pair under each), and ambiguity-as-an-outcome existed only there. One concept, one page (principle #9).

| Situation | Ledger treatment |
|---|---|
| **Exact** — one open invoice, balance == amount | `DR money account / CR AR ref` — the document closes by the ref rule above |
| **Combination** — the amount settles several open invoices | one `CR AR` line **per invoice**, each carrying its own ref (GL example below) |
| **Partial** — amount < the invoice | `CR AR ref` for the applied amount; the remainder stays open, derived |
| **Overpayment** — amount exceeds everything open | apply all, then the remainder becomes an **unapplied customer credit** — never lost, surfaced by [[safety-nets]] cleanup |
| **Deposit for a project with no invoice** → **retainer** | `DR Bank / CR Unearned Revenue (customer, project)`. On later invoicing: `DR Unearned Revenue / CR AR ref`. **Income never recognized early** ([[cash-basis-recognition]] R6); drawdown defined below |
| **No context** | unapplied credit on the customer, listed until resolved |

Every match is a draft showing proposed `applications[]`; approval posts it. The engine never guesses: equal balances or multiple valid subsets return **all** candidates and the agent asks ([[matching-engine]]). Payment doc carries `deposit_account`, `method` (accounting-relevant — drives the 1099-NEC exclusion, [[compliance]], and recognition events, [[cash-basis-recognition]]), `applications[] = [{invoice, amount}…]` — many-to-many both directions ([[document-model]]). AP mirrors everything for bills.

Concrete GL example — one payment, two invoices:

```
DR Checking 1,400                      (ref: PAY-0117)
CR AR 1,000   ref: INV-0042
CR AR   400   ref: INV-0043
```

## Retainer drawdown — the one deferral v1 ships

Rule 5's obligation spans months and `verify_books` reports it as "stale Unearned Revenue" ([[safety-nets]]), yet it had **no ref rule and no single definition** — a principle-#9 gap in the only deferral v1 ships. Defined at ledger grain, mirroring the universal rule with the polarity reversed (a liability): **(proposed 2026-07-30)**

```
receipt:      DR Bank 5,000 / CR Unearned Revenue 5,000   ref: PAY-0117  (customer, project)
application:  DR Unearned Revenue 2,000  ref: PAY-0117
              CR AR               2,000  ref: INV-0042
unapplied_retainer(PAY-0117) = Σ credits − Σ debits  on Unearned Revenue lines where ref = PAY-0117
```

- One line, one ref: the drawdown debit refs the retainer, its paired AR credit refs the invoice — which is why the same posting both draws down the liability and settles the invoice. **(proposed 2026-07-30)**
- Derived, never stored; point-in-time by `date ≤ D` ([[point-in-time-balances]]). The stale-retainer check and any "unearned by customer/project" report are **filters over this one definition**. Recognition already happened at receipt ([[cash-basis-recognition]] R6), so the drawdown touches no P&L account. **(proposed 2026-07-30)**

Full edge-case treatments: [[scenario-catalog]].
