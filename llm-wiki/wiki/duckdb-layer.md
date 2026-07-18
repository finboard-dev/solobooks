---
type: entity
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-duckdb-layer-design.md]
tags: [duckdb, analytics, views, implementation]
---

# DuckDB Layer (read side)

> Stateless calculator with a per-company LRU cache keyed by `ledger_version`. Money is DECIMAL, never float; a parse failure is a hard alarm, not a warning. The view stack is where principle #9 (one concept, one implementation) becomes code.

- **Cache:** `{company_id → (connection, ledger_version)}`; rebuild when Mongo's version differs ([[company-object]]); LRU cap (config, ~32). Rebuild = batch-fetch GL + COA sheets → Arrow → DuckDB, milliseconds at 5k lines/year ([[point-in-time-balances]]).
- **Tables:** `gl_lines` ([[general-ledger-sheet]] columns 1:1) + `accounts` ([[chart-of-accounts]] sheet).
- **View stack, created at load:** `v_lines` (⋈ accounts, signed amount) → `v_balances` (cumulative) → `v_open_items` (the ref sums, [[pairing-and-matching]]) → `v_pnl` (accrual) → `v_pnl_cash` — implements the canonical algorithm in [[cash-basis-recognition]] (money-movement recategorization; the one non-trivial view).
- **Every report tool AND `query_books` run over the same views** — agent ad-hoc SQL can only mean the canonical definitions ([[reports-and-analytics]]). Raw `gl_lines` stays queryable; views are the documented surface in [[the-skill]].
- **Guard:** sqlglot → single SELECT, table whitelist, row cap, timeout (FinBoard mcp-server pattern, [[platform]]).
