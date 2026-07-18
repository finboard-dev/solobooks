---
type: entity
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-sheets-layer-design.md]
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
