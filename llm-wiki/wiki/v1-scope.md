---
type: synthesis
created: 2026-07-17
modified: 2026-07-18
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-17-buyer-panel-report.md, raw/2026-07-18-scope-calls.md]
tags: [scope, roadmap]
---

# v1 Scope

> The single authoritative scope list. Provenance of each decision lives in `log.md` and the research pages ([[buyer-panel-findings]], [[professional-review-findings]]); this page states only the current cut.

## v1

- Double-entry **append-only ledger** in monthly GL sheets + COA sheet ([[general-ledger-sheet]], [[chart-of-accounts]] incl. `tax_line`, loan accounts, Reconciliation Discrepancies)
- **9 document types** ([[document-model]]) with the full [[scenario-catalog]]
- **Matching engine** with retainer path and hints contract ([[matching-engine]])
- **CSV bank-statement import** (agent-categorized, approval-gated) + **statement-based [[bank-reconciliation]]**
- **Approval flow** all/none ([[approval-flow]]) + **batch review grid** for import drafts — the one ledger-UI exception ([[platform]])
- **Opening balances** incl. full prior trial balance, AR/AP-from-documents-only rule ([[onboarding-opening-balances]])
- **Period locking + month close** with statement rec (balance-check fallback) and artifact archiving ([[period-locking-month-close]])
- **Cash/accrual** from one ledger ([[cash-basis-recognition]]); flat **sales tax** with basis disclosure; **1099 tracking** with payment-method exclusion ([[compliance]])
- **Invoice Doc/PDF artifact** ([[invoice-artifact]])
- **Safety nets**: uncategorized parking, duplicate warnings, unapplied-credit tracking, `verify_books`, completeness nudges ([[safety-nets]])
- **All reports** incl. `query_books` + the **expanded accountant packet** ([[reports-and-analytics]])
- **Better Auth** + minimal Next.js UI ([[platform]], [[auth-wiring]]); **the skill** ([[the-skill]])
- **Pricing announced at launch** (anchor ≤$29/mo) — no billing infrastructure, but never ship unpriced

## v1.1 (committed fast-follow)

Recurring/retainer auto-billing — scheduler + auto-draft riding the existing [[approval-flow]].

## v1.5

Stripe payment link on the invoice artifact; billable-expense rebilling; sendable customer-statement artifact (the open-items *report* is v1); 1099 completions (W-9/TIN capture, NEC vs MISC, corp exemption); mid-year historical transaction backfill.

## v2 thesis (adopted; timing decided after Phase-6 dogfooding)

**The accountant seat**: multi-company accountant role, per-user audit attribution, cross-client close/exceptions console, REST read API. Three independent signals converge here ([[professional-review-findings]]).

## Out of v1 (deliberately)

Multi-currency; full bank feeds (Plaid); receipts UI (folder convention only); depreciation register (manual JE only; packet lists asset additions); estimates/quotes; time tracking; mileage; quarterly tax estimates; email sending; payroll; inventory; batch deposits; multi-user/teams (the accountant seat is the v2 thesis, not a v1 feature).

## Resolved questions

1. **Multi-company:** v1 is one company per user, but everything is `company_id`-keyed from day one — multi-company later is a `select_company` tool + UI, zero migration.
2. **Product name:** **SoloBooks**.
3. **Repo:** new standalone repo (`~/solobooks`); patterns copied from `finboard/mcp-server`, not imported.
