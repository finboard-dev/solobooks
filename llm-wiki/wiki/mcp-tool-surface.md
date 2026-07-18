---
type: entity
created: 2026-07-17
modified: 2026-07-18
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-18-scope-calls.md]
tags: [mcp, tools, api]
---

# MCP Tool Surface (v1)

> The MCP tools ARE the API. Writes return confirmation + a link to the exact GL sheet range. **Tenant scope comes from the auth token, never from tool arguments** ([[auth-wiring]]).

- **Context/setup:** `whoami`, `get_books_status` (incl. incomplete-books banner + silence nudges), `get_company` / `update_company`, `lock_period`, `unlock_period` ([[period-locking-month-close]])
- **COA:** `list_accounts`, `add_account`, `update_account` (deactivate, `tax_line`) ([[chart-of-accounts]])
- **Contacts:** `add_customer` (+projects), `add_vendor` (`track_1099`), `update_contact`, `list_contacts` ([[dimensions]])
- **Sales:** `create_invoice` ([[invoice-artifact]]), `record_payment` (matching engine + hints — [[matching-engine]]), `create_sales_receipt`, `create_credit_note`
- **Purchases:** `record_bill`, `pay_bill`, `create_vendor_credit`
- **Ledger:** `post_journal_entry` (N lines), `record_transfer`, `record_owner_expense` ([[scenario-catalog]])
- **Import & reconciliation:** `import_bank_csv` (statement rows → categorized drafts, approval-gated; reviewed in the batch grid — [[platform]]), `reconcile_account` ([[bank-reconciliation]])
- **Approval:** `list_drafts`, `approve_document`, `reject_draft`, `approve_all_drafts` ([[approval-flow]])
- **Reports & export:** everything in [[reports-and-analytics]] incl. `query_books`, `verify_books`, and `export_accountant_packet` (the expanded packet)

Agent behavior guidance lives in [[the-skill]].
