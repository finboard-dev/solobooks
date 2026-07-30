---
type: entity
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
tags: [coa, accounting]
---

# Chart of Accounts

> Per-company COA in Mongo, rendered as a sheet at the Drive folder root (self-sufficiency rule, [[three-store-architecture]]). Accounts are deactivated, never deleted once they have activity.

Fields: `account_number` (1xxx assets / 2xxx liabilities / 3xxx equity / 4xxx income / 5xxx COGS / 6xxx expenses), `name`, `parent_account` (hierarchy; reports roll up the tree), `type` (Asset/Liability/Equity/Income/Expense — sign rules + statement placement), `detail_type` (Bank, AR, AP, Fixed Asset, Credit Card, COGS… — report grouping), `normal_balance` (derived), `active`.

Accounts also carry an optional **`tax_line`** (Schedule C mapping) — drives the accountant packet's by-tax-line grouping ([[reports-and-analytics]]).

- The account→line map is **not** stored here: it lives as `coa_tax_line_map` on the append-only [[policy-set]] and resolves as-of the report's period, because the COA is rewritten destructively. **(proposed 2026-07-30)**
- A COA rewrite bumps `books_version` ([[duckdb-layer]]) like any other cached-sheet write — otherwise `add_account` / `update_account` serves a stale `accounts` table. **(proposed 2026-07-30)**

**Seed COA must cover every account the [[scenario-catalog]] posts to:**
Checking, Savings, Cash, Accounts Receivable, Fixed Assets, Accumulated Depreciation, Accounts Payable, Credit Card, **Notes Payable**, Sales Tax Payable, Unearned Revenue, Opening Balance Equity, Owner's Contributions, Owner's Draw, Retained Earnings (computed — see [[period-locking-month-close]]), Sales, Sales Discounts, Uncategorized Income, ~10 solopreneur expense accounts (Software, Processing Fees, Contractors, **Interest Expense**…), Bad Debt Expense, Uncategorized Expense, **Reconciliation Discrepancies** ([[bank-reconciliation]]). The skill carries the principal/interest split rule for loan payments ([[the-skill]]).

Uncategorized accounts are a deliberate safety net — see [[safety-nets]].
