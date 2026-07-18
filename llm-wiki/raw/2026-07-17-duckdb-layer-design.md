# DuckDB Analytics Layer — approved design (2026-07-17)

## Cache lifecycle
- One in-memory DuckDB per company: {company_id → (connection, ledger_version)}.
- On any read: cached version ≠ Mongo ledger_version → rebuild. LRU eviction beyond config cap (e.g. 32 resident).
- Rebuild = batch-fetch all monthly GL sheets + COA sheet → Arrow → DuckDB. Milliseconds at 5k lines/year.

## Typing discipline
- Money = DECIMAL(18,2), never float. Dates = DATE. Sheets were written RAW by us so the parse is
  deterministic; a parse failure is a HARD error (means ledger corruption — we want the alarm).
- Tables: gl_lines (sheet columns 1:1) + accounts (from COA sheet: type/detail_type/parent).

## View stack (principle #9 as code) — created at load
- v_lines       gl_lines ⋈ accounts (+ signed amount by normal balance)
- v_balances    cumulative per account (balance_sheet, account_ledger)
- v_open_items  the ref sums (aging, open balances, statements)
- v_pnl         income/expense by period — accrual
- v_pnl_cash    cash basis: recognizes an invoice's income lines proportionally when payments settle it
                (via refs). The one non-trivial view — written once, used everywhere.

Every report tool = parameterized SELECT over these views. query_books runs against the SAME views
(agent ad-hoc SQL can only mean the canonical definitions). Raw gl_lines stays queryable; views are
the documented surface in the skill.

## query_books guard
- sqlglot parse → single SELECT only, table whitelist, row cap, statement timeout
  (same design as FinBoard mcp-server execute_sql guard).
