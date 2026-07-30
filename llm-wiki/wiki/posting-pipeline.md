---
type: concept
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-posting-pipeline-research.md, raw/2026-07-30-process-aware-objects.md]
tags: [write-path, outbox, idempotency, implementation]
---

# Posting Pipeline (the write path)

> Five steps: COMPOSE (pure) → RESERVE (counters) → COMMIT (atomic Mongo insert, outbox embedded) → PROJECT (drainer appends to sheet, effectively-once) → FINALIZE (audit + `books_version` + link). Validated against Modern Treasury ledger practice and outbox literature.

1. **COMPOSE** — pure function in `app/domain/`: document payload → business validation (accounts exist, `date > locked_through` [[period-locking-month-close]], duplicate check [[safety-nets]]) → emitter ([[document-model]]) → balanced lines. **Hard invariant Σdebits == Σcredits enforced here or never.**
2. **RESERVE** — Mongo atomic counters → `txn_id` + document number.
3. **COMMIT** — one atomic insert of the **PostingRecord** `{txn_id, doc snapshot, gl_lines[], status, idempotency_key, outbox: pending}`. Single-document atomicity — no multi-doc transactions. The entry legally exists at this instant. COMMIT is also where `provenance` is written ([[decision-record]]) and where a `preview_hash` mismatch raises `PREVIEW_DRIFT` instead of posting ([[approval-flow]]). **(proposed 2026-07-30)**
4. **PROJECT** — outbox drainer (lifespan worker) appends lines to the month's [[general-ledger-sheet]]. Outbox = at-least-once; **dedupe = read sheet tail, check txn_id before any retry** (Sheets API has no idempotency keys). Row range written back (powers "view in sheet" links).
5. **FINALIZE** — audit entry → bump `books_version` ([[duckdb-layer]], invalidates the DuckDB cache) → confirmation + sheet link.

**Failure matrix:** crash before COMMIT → nothing happened. After COMMIT → drainer re-projects on startup, tail-check prevents double rows. No state where money exists in one store and not eventually the other.

**Approval:** drafts stop before step 1; `approve_document` runs the full pipeline — compose re-validates at approval time, not draft time ([[approval-flow]]).

**Deliberate divergence from Modern Treasury:** no balance caches — DuckDB recomputes any balance in milliseconds at solopreneur volume ([[point-in-time-balances]]); ledger stays the single definition.

**Ordering:** single drainer in one process = per-company FIFO for free (single-replica deployment).
