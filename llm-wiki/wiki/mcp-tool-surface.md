---
type: entity
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-18-scope-calls.md, raw/2026-07-30-process-aware-objects.md]
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
- **Context assembly (reads, Mongo side):** `get_object(ref, lens)` — `lens` = `SETTLEMENT | TREATMENT | DECISION | EVIDENCE | FULL`; `get_audit_trail(ref)`; `attach_evidence(subject_ref, evidence)`. The `lens` enum, the dossier contract and the section renderer are owned by [[context-assembly]] / [[evidence]]. **(proposed 2026-07-30)**
- **Processes:** `list_processes(type, state)` and `get_process(process_id)` over one generic object — import runs, rec runs, closes, amendments, onboarding ([[process-instance]]). No per-domain read tools. **(proposed 2026-07-30)**

## Tenant scope — the argument test is not enough

The rule above is enforced today by a grep-test proving **no tool takes a `company_id` argument**. That is structural for writes and for aggregate reports, and it proves nothing about `get_object(ref="INV-0042")`: document numbers are minted per company, not globally, so INV-0042 exists in every tenant's books. **(proposed 2026-07-30)**

- Every context read filters `{company_id, ref}`, with `company_id` from the token ([[auth-wiring]]) and `ref` treated as untrusted caller input. **(proposed 2026-07-30)**
- A foreign or non-existent ref returns **not-found** — never data, never a different tenant's object, and never a distinguishable error. The isolation test asserts exactly that ([[context-assembly]]). **(proposed 2026-07-30)**
- Same rule for `process_id`, `decision_id` and any `DRIVE_FILE` evidence ref, which must resolve inside this company's folder registry ([[evidence]]). **(proposed 2026-07-30)**

Agent behavior guidance lives in [[the-skill]].
