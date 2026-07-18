---
type: concept
created: 2026-07-18
modified: 2026-07-18
status: verified
sources: [raw/2026-07-18-gap-fixes.md]
tags: [dates, timezone, semantics]
---

# Dates & Timezones

> Document dates are **plain calendar dates** — no time component, no timezone math, ever. Fills the gap flagged in the 2026-07-18 self-review.

- The date the user states is the date; month-file assignment ([[general-ledger-sheet]]) = month of that plain date. Deterministic — no midnight-boundary ambiguity.
- [[company-object]] gains `timezone` (IANA, set at onboarding, default America/New_York), used ONLY to: resolve relative dates in chat ("today", "last month" — [[the-skill]] documents this), and render `posted_at` audit timestamps (stored UTC).
- `fiscal_year_start` = "MM-DD"; **v1 validates day == 01** (first-of-month fiscal years only; mid-month rejected with a clear error, deferred).
- Period locking compares plain dates: `date > locked_through` ([[period-locking-month-close]]).
