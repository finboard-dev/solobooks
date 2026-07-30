---
type: concept
created: 2026-07-18
modified: 2026-07-30
status: verified
sources: [raw/2026-07-18-gap-fixes.md, raw/2026-07-30-process-aware-objects.md]
tags: [dates, timezone, semantics]
---

# Dates & Timezones

> Document dates are **plain calendar dates** — no time component, no timezone math, ever. Fills the gap flagged in the 2026-07-18 self-review.

- The date the user states is the date; month-file assignment ([[general-ledger-sheet]]) = month of that plain date. Deterministic — no midnight-boundary ambiguity.
- [[company-object]] gains `timezone` (IANA, set at onboarding, default America/New_York), used ONLY to: resolve relative dates in chat ("today", "last month" — [[the-skill]] documents this), and render `posted_at` audit timestamps (stored UTC).
- `fiscal_year_start` = "MM-DD"; **v1 validates day == 01** (first-of-month fiscal years only; mid-month rejected with a clear error, deferred).
- Period locking compares plain dates: `date > locked_through` ([[period-locking-month-close]]).

## Three time categories, named (proposed 2026-07-30)

| Category | Examples | Semantics |
|---|---|---|
| **Accounting date** | document date, posting date, `locked_through`, period boundary | plain calendar date; sets the month file; no timezone math, ever |
| **Effective date** | `effective_from` on a [[policy-set]], `service_period_start` / `service_period_end` on an invoice line ([[invoice-artifact]]) | **plain calendar date**, resolved as-of exactly like an accounting date **(proposed 2026-07-30)** |
| **Decision instant** | `decided_at` / `approved_at` ([[decision-record]]), `cleared_at` ([[bank-reconciliation]]), `opened_at` / `closed_at` ([[process-instance]]) | **UTC instant**, stored UTC, rendered in the company `timezone` **(proposed 2026-07-30)** |

- **Mapping an instant to an accounting period uses the company timezone, explicitly (proposed 2026-07-30).** An approval at `2026-08-01T02:14Z` by a user in `America/Los_Angeles` is disclosed under **July** — when the human actually did it. Left implicit, the packet's per-period approval disclosure ([[policy-set]], [[reports-and-analytics]]) is ambiguous by construction.
- An instant is never a substitute for an accounting date: it never sets the month file and never faces `locked_through` **(proposed 2026-07-30)**.
