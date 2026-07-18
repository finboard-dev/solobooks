---
type: entity
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
tags: [duckdb, reports, sql]
---

# Reports & Analytics (DuckDB)

> Load path: GL sheets + COA sheet → DuckDB tables `gl_lines` + `accounts` → report SQL → token-budget renderer. **Every report is a SQL view over `gl_lines`; each concept defined exactly once.**

Cache validity via `ledger_version` ([[company-object]]); lost cache rebuilds in milliseconds ([[point-in-time-balances]]).

| Tool | Answers |
|---|---|
| `profit_and_loss` | range, monthly columns, prior compare, by class/customer, **cash or accrual** ([[compliance]]) |
| `balance_sheet` | as-of any date; Retained Earnings **computed** (cumulative prior-year net income — no closing entries, [[period-locking-month-close]]) |
| `trial_balance` | CPA sanity check |
| `account_ledger` | one account's lines + running balance (bank-statement view) |
| `ar_aging` / `ap_aging` | open ref sums bucketed 0/30/60/90 via `due_date` ([[general-ledger-sheet]]) |
| `income_by_customer` / `spend_by_vendor` / `project_profitability` | [[dimensions]] rollups |
| `cash_flow` | v1 simple: net change per money account + inflow/outflow categories (indirect method deferred) |
| `sales_tax_liability` / `1099_payments` | [[compliance]] |
| `list_uncategorized` | cleanup queue ([[safety-nets]]) |
| `customer_statement` | open items per customer (v1 if trivial) |
| `query_books` | **power tool** — read-only SQL on `gl_lines`, sqlglot-guarded SELECT-only |

**Accountant packet (expanded 2026-07-18, [[professional-review-findings]]):** TB + GL + 1099 CSV, plus: **by-Schedule-C-tax-line grouping** (COA `tax_line`, [[chart-of-accounts]]), **accrual-to-cash bridge** (ΔAR/ΔAP/Δunearned/non-cash — the [[testing-strategy]] assertion shipped as a report), open AR/AP item detail with refs, customer/vendor/project masters, **categorization review** (every agent account choice + `memo_verbatim`), approval-mode-per-period disclosure with auto-posted entries flagged, tolerance write-off list, fixed-asset additions, exportable audit log.

Rendering reuses FinBoard mcp-server patterns: compact CSV tables under a token budget, drop zero rows, collapse depth, never silently truncate ([[platform]]).

**Cash vs accrual:** cash basis recognizes on payment lines instead of invoice/bill lines — same ledger, per-report toggle, default from [[company-object]].
