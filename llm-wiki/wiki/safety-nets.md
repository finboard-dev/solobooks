---
type: concept
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-18-scope-calls.md, raw/2026-07-30-process-aware-objects.md]
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
- **Audit log** (Mongo, append-only) — every tool call and mutation: who, what, before/after, when, conversation id, **plus a `subject_ref` edge** so a decision path can be *queried* rather than grepped ([[context-assembly]]). An append-only entry written without the edge never gains one, so the edge ships with the first entry ever written. **(proposed 2026-07-30)**

## `ExceptionKind` — this page owns the vocabulary **(proposed 2026-07-30)**

The conditions above appear across five future call sites — `verify_books`, the close ritual, the import reject report, the rec check, the packet — under nine different names and **zero identifiers**. That is exactly the failure principle #7 exists to prevent, and un-named it silently defeats the v2 cross-client exceptions console ([[v1-scope]]), which has nothing to group by. The enum and every row below are new; it is defined once in `app/domain/enums.py` and imported everywhere.

| `ExceptionKind` | Condition | Surfaced by |
|---|---|---|
| `UNCATEGORIZED` | posting parked in Uncategorized Income/Expense | posting tools, `list_uncategorized` |
| `UNAPPLIED_CREDIT` | credit with no ref application | [[pairing-and-matching]] |
| `STALE_UNEARNED` | Unearned Revenue un-drawn past its policy age | `verify_books` |
| `NONZERO_OBE` | Opening Balance Equity ≠ 0 at close | `verify_books`, [[onboarding-opening-balances]] |
| `RECONCILIATION_DISCREPANCY` | nonzero Reconciliation Discrepancies balance | [[bank-reconciliation]] |
| `PENDING_DRAFT` | draft still unapproved at close | [[approval-flow]] |
| `TRIAL_BALANCE_BREAK` | total DR ≠ total CR | `verify_books` |
| `DUPLICATE_SUSPECTED` | same payee + amount + date ± `duplicate_window_days` | posting tools, import dedupe |
| `IMPORT_ROW_REJECTED` | statement row could not become a draft | `IMPORT_RUN` ([[process-instance]]) |
| `PREVIEW_DRIFT` | posted lines ≠ the approved `preview_hash` | [[decision-record]] |
| `OUTSTANDING_ITEM_AGED` | rec item uncleared beyond its policy age | `REC_RUN` ([[bank-reconciliation]]) |
| `EVIDENCE_MISSING` | subject has no linked evidence | [[evidence]] |

Every exception carries a `Disposition` — `OPEN | RESOLVED | ACKNOWLEDGED` — with **actor and reason**. `ACKNOWLEDGED` is how a close proceeds over a known exception without pretending it was fixed ([[period-locking-month-close]] step 1). Ages and windows are thresholds on the versioned [[policy-set]], not constants. **(proposed 2026-07-30)**

**Exceptions never block.** They are raised, listed and disposed — never turned into validation errors. Nothing is blocked on classification, and nothing is blocked on paperwork ([[evidence]]). **(proposed 2026-07-30)**

The monthly reconciliation itself lives in [[bank-reconciliation]]; the close checklist in [[period-locking-month-close]].
