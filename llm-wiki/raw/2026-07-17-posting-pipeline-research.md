# Posting Pipeline — research + approved design (2026-07-17)

Founder-approved design for the SoloBooks write path, informed by online research.

## Research findings

- Modern Treasury ledger series: transactions mutable while pending, **immutable once posted**; corrections = reversal or delta transactions; clients create transactions only, never entries (the ledger creates entries); MT maintains O(1) balance caches.
  - https://www.moderntreasury.com/journal/enforcing-immutability-in-your-double-entry-ledger
  - https://www.moderntreasury.com/journal/how-to-scale-a-ledger-part-v
  - https://www.moderntreasury.com/journal/behind-the-scenes-how-we-built-ledgers-for-high-throughput
- Outbox literature: outbox = **at-least-once**, never exactly-once; consumer-side idempotency key dedupe achieves effectively-once; in MongoDB, embed outbox state in the same document for single-document atomicity (no multi-doc transaction).
  - https://event-driven.io/en/outbox_inbox_patterns_and_delivery_guarantees_explained/
  - https://ash-mageed.medium.com/re-implementing-the-outbox-pattern-in-mongodb-b7fdc9a2523d

## Approved pipeline (5 steps)

1. **COMPOSE** (pure, app/domain/): document payload → business validation (accounts exist, date > locked_through, duplicate check) → emitter → balanced JournalEntry lines. Hard invariant Σdebits == Σcredits enforced here or never.
2. **RESERVE**: Mongo atomic counters ($inc) → txn_id + document number.
3. **COMMIT**: one atomic Mongo insert of the PostingRecord {txn_id, document snapshot, gl_lines[], status: committed, idempotency_key, outbox: pending}. Entry legally exists at this instant.
4. **PROJECT**: outbox drainer (FastAPI lifespan worker) appends gl_lines to month GL sheet. Retry dedupe = read sheet tail, check txn_id (effectively-once). Row range written back to PostingRecord.
5. **FINALIZE**: audit entry (who/what/when/conversation) → bump ledger_version → return confirmation + sheet link.

Failure matrix: crash before COMMIT = nothing happened; after COMMIT = drainer re-projects on startup with tail-check dedupe; ambiguous Sheets error = tail-check before retry. No state where money exists in one store and not eventually the other.

Approval: drafts stop before step 1; approve_document runs the full pipeline; compose re-validates at approval time.

Divergence from MT: **no balance caches** — DuckDB recomputes (5k lines/year, milliseconds); removes a class of drift bugs; ledger stays the single definition.

Ordering: single drainer in one process = per-company FIFO free; outbox partitioning concerns apply only beyond one replica.
