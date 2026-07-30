---
type: entity
created: 2026-07-17
modified: 2026-07-31
status: verified
sources: [raw/2026-07-17-duckdb-layer-design.md, raw/2026-07-30-process-aware-objects.md, raw/2026-07-30-tri-persona-review.md]
tags: [duckdb, analytics, views, implementation]
---

# DuckDB Layer (read side)

> Stateless calculator with a per-company LRU cache keyed by `books_version`. Money is DECIMAL, never float; a parse failure is a hard alarm, not a warning. The view stack is where principle #9 (one concept, one implementation) becomes code.

- **Cache:** `{company_id → (connection, books_version)}`; rebuild when Mongo's version differs ([[company-object]]); LRU cap (config, ~32). Rebuild = batch-fetch GL + COA sheets → Arrow → DuckDB, milliseconds at 5k lines/year ([[point-in-time-balances]]).
- **This page owns `books_version` (proposed 2026-07-30).** Renamed from `ledger_version`, held on [[company-object]], and bumped by **any** write to **any** sheet DuckDB caches — a GL append, a COA rewrite, a `Reconciliations` append. Live bug today: the COA is rewritten with no bump ([[chart-of-accounts]]), so after `update_account` the resident connection serves the stale `accounts` table until an unrelated posting happens. One key, one name, every writer bumps it (principle #7).
- **Tables:** `gl_lines` ([[general-ledger-sheet]] columns 1:1) + `accounts` ([[chart-of-accounts]] sheet) + `rec_clears` (the `Reconciliations` sheet, [[sheets-layer]]; keyed by `(txn_id, account_number, side)`) — all on the one version key **(proposed 2026-07-30)**.
- **Boundary — DuckDB is the LEDGER read side and stays that way (proposed 2026-07-30).** Every canonical *number* is a view over `gl_lines` (principle #9); context — decisions, process participation, evidence, policy — is structurally unreachable by `query_books` and is read from Mongo through [[context-assembly]]. Two read paths, two jobs; neither redefines the other's values.
- **View stack, created at load:** `v_lines` (⋈ accounts, signed amount) → `v_balances` (cumulative) → `v_open_items` (the ref sums, [[pairing-and-matching]]) → `v_pnl` (accrual) → `v_pnl_cash` — implements the canonical algorithm in [[cash-basis-recognition]] (money-movement recategorization; the one non-trivial view).
- **Every report tool AND `query_books` run over the same views** — agent ad-hoc SQL can only mean the canonical definitions ([[reports-and-analytics]]). Raw `gl_lines` stays queryable; views are the documented surface in [[the-skill]].
- **Guard:** sqlglot → single SELECT, table whitelist, row cap, timeout (FinBoard mcp-server pattern, [[platform]]).
