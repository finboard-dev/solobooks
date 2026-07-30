---
type: entity
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-sheets-layer-design.md, raw/2026-07-30-process-aware-objects.md]
tags: [sheets, drive, implementation]
---

# Sheets Layer

> The only external dependency in the write path. Rules: lazy month creation, one append per txn, tail-check dedupe, formula TOTALS, never edit in place.

- **Storage architecture:** service accounts created after 2025-04-15 have **zero** Drive storage quota — SA-owned files are impossible. SoloBooks runs under a Google Workspace tenant; all files live in **Shared Drives** (files belong to the drive, not the SA), SA as Manager member. Sharding: many companies per shared drive (400k-item cap; a company-year ≈ 15 files); `shared_drive_id` in the provisioning registry; new drives created as caps approach. Domain-wide delegation rejected. Verified in the Phase-0 spike.
- **Provisioning:** company folder + [[chart-of-accounts]] sheet at onboarding; monthly GL files created **lazily** on first posting to that month, from a template. Every file shared view-only, ids registered in Mongo — never resolved by name at runtime ([[three-store-architecture]]).
- **Appends** ([[posting-pipeline]] PROJECT): one `values.append` per transaction (a txn never splits across a failure boundary); tail-check `txn_id` dedupe before any retry; `RAW` input — Sheets never interprets ledger data.
- **TOTALS row is formulas** (`=SUM…` + difference cell): the [[general-ledger-sheet]] self-verifies — a writer bug is visible to any human with no system running. Self-sufficiency applied to integrity.
- **Quotas:** ~60 writes/min/user vs handful of txns/day; drainer serializes with backoff on 429/5xx — pressure means "seconds later", never "lost".
- **COA sheet:** fully rewritten on change.
- **Re-render** (unlock case only, [[period-locking-month-close]]): archive the current sheet first ("as locked YYYY-MM-DD", `archive/` folder — prior renderings never deleted) → fresh tab → verify counts+totals → swap. Never edit in place. **Invalidates every affected PostingRecord's `row_range`** (null + `rerendered: true`), recomputed from the rebuild ordering; "view in sheet" links resolve lazily by txn_id search when row_range is null ([[posting-pipeline]]).

## One primitive, one durability mechanism (proposed 2026-07-30)

The layer has exactly **one write primitive** — append, never edit — and exactly **one durability mechanism**: an outbox *embedded in a PostingRecord*, indexed and drained as such ([[posting-pipeline]]). Every non-posting sheet write the object model now requires has **neither**. Closing the gap without weakening either rule:

- **A cell update is not a supported operation.** Flipping a `cleared` cell mutates an existing row: rule 1 of [[general-ledger-sheet]] forbids it, the layer has no method for it, and tail-check dedupe cannot make it effectively-once — tail-check works because a `txn_id` is either present or absent, and "was this cell already flipped" has no equivalent test. **(proposed 2026-07-30)**
- **Reconciliation state is appended**, to a third per-company sheet **`Reconciliations`** at the company folder root (`txn_id`, `statement_period`, `rec_id`, `cleared_at`; one row per clearing, superseded by a later row, never overwritten), loaded 1:1 as a third DuckDB table `rec_clears` ([[duckdb-layer]]). Append-only, self-sufficient (a human sees which lines cleared in which statement period with no system running), 1:1 loader preserved, no new GL column ([[bank-reconciliation]]). Appending bumps `books_version` ([[duckdb-layer]]) like any other cached-sheet write. **(proposed 2026-07-30)**
- **The outbox is generalized out of the PostingRecord** into a standalone durable queue keyed `{company_id, target_sheet, idempotency_key}`, drained by the same single-drainer FIFO worker. Non-posting writes — rec clears, `archive/` copies, close-time exports ([[period-locking-month-close]]) — then get the same at-least-once + dedupe guarantee as postings; dedupe is `idempotency_key` tail-checked in the target sheet. The PostingRecord keeps an enqueue, not a queue. **(proposed 2026-07-30)**
