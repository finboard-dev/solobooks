---
type: concept
created: 2026-07-17
modified: 2026-07-18
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-18-scope-calls.md]
tags: [safety, audit, validation]
---

# Safety Nets

> The forgiveness layer — real users are messy; nothing should be lost, blocked, or silently wrong.

- **Uncategorized accounts** — agents may park unknowns in Uncategorized Income/Expense ([[chart-of-accounts]]); `list_uncategorized` is the cleanup queue. Never block a posting on classification.
- **Unapplied credits** — over/unmatched payments sit as customer credits, always listed until resolved ([[pairing-and-matching]]).
- **Duplicate warning** — posting tools warn on same vendor/customer + amount + date ±3 days (import dedupe checks drafts too).
- **`verify_books`** — trial balance ties; pending drafts; unapplied credits; uncategorized; nonzero OBE at close; stale Unearned Revenue; nonzero Reconciliation Discrepancies ([[bank-reconciliation]]). On demand and at close ([[period-locking-month-close]]).
- **Completeness nudges** — a money account silent >2 weeks triggers the agent to ask; surfaced in `get_books_status`.
- **Outbox retry** — Mongo commits first, GL lines append with tail-check dedupe; no half-posted documents ([[posting-pipeline]]).
- **Audit log** (Mongo, append-only) — every tool call and mutation: who, what, before/after, when, conversation id.

The monthly reconciliation itself lives in [[bank-reconciliation]]; the close checklist in [[period-locking-month-close]].
