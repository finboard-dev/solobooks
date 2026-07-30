---
type: synthesis
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-17-buyer-panel-report.md, raw/2026-07-18-scope-calls.md, raw/2026-07-30-process-aware-objects.md]
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

### Process-aware object model (proposed 2026-07-30)

Structural, not features: all of it is cheap while zero code exists and a migration afterwards. Rationale in [[financial-object-model]].

- **Context as a truth domain** — Mongo is canonical and append-only for *meaning*, never a cache of it; two-tier self-sufficiency ([[three-store-architecture]])
- **`provenance` on every PostingRecord** — **unbackfillable**, so it ships with the first posting or never ([[decision-record]])
- **[[decision-record]]** — one shape for every determination (generalizing MatchProposal), incl. `preview_hash` so an approved preview is provably what posted
- **[[process-instance]]** — one generic object for import runs, rec runs, **month close**, amendments, onboarding
- **[[evidence]]** — the link only; no capture UI, no OCR, never blocks a posting
- **[[policy-set]]** — versioned policy, effective-dated; policy header on every report; exported renderings retained
- **[[context-assembly]]** — `get_object(ref, lens)`, `get_audit_trail`, `attach_evidence`; the audit log gains a `subject_ref` edge
- **`ExceptionKind` + `Disposition` enums** ([[safety-nets]]); GL gains `reverses_txn_id` + `line_reason` ([[general-ledger-sheet]]); a third `Reconciliations` sheet ([[sheets-layer]])
- **Nullable seams** — `origin{type,ref}` on documents, `service_period` on invoice lines, `delivered_at` on invoices. Free capture only ([[the-skill]])
- **Bug fix, not a feature:** `ledger_version` → `books_version`, bumping on every cached-sheet write ([[duckdb-layer]])

## v1.1 (committed fast-follow)

Recurring/retainer auto-billing — scheduler + auto-draft riding the existing [[approval-flow]].

## v1.5

Stripe payment link on the invoice artifact; billable-expense rebilling; sendable customer-statement artifact (the open-items *report* is v1); 1099 completions (W-9/TIN capture, NEC vs MISC, corp exemption); mid-year historical transaction backfill.

## v2 thesis (adopted; timing decided after Phase-6 dogfooding)

**The accountant seat**: multi-company accountant role, per-user audit attribution, cross-client close/exceptions console, REST read API. Three independent signals converge here ([[professional-review-findings]]).

## Out of v1 (deliberately)

Multi-currency; full bank feeds (Plaid); receipts UI (folder convention only); depreciation register (manual JE only; packet lists asset additions); estimates/quotes; time tracking; mileage; quarterly tax estimates; email sending; payroll; inventory; batch deposits; multi-user/teams (the accountant seat is the v2 thesis, not a v1 feature).

**From the process-aware object model — decided out, not overlooked (proposed 2026-07-30).** The founder source is written in enterprise-finance vocabulary; these are the parts that are wrong for a one-person cash-basis US business, recorded here so the next reader can tell a decision from a gap:

- **Performance obligations and revenue schedules** (ASC-606 shaped) — a cash-basis solopreneur recognizes retainers at receipt ([[cash-basis-recognition]] R6); a schedule engine would overturn a CPA-endorsed rule, not extend it.
- **Contract / sales-order / subscription objects** — recurring billing is the committed **v1.1** fast-follow; upstream commercial objects would preempt that decision. `origin{type,ref}` is the seam.
- **`billing_method`, rate cards, list-price-and-override capture** — no pricing engine exists, so the source's own example question ("why is this invoice 15% lower than expected?") is out of scope by construction. A discount is simply a lower rate and nets correctly; only the analytical *why* is unavailable.
- **Multi-party approval routing** — there is no second party; the correct shape is a [[decision-record]], and [[process-instance]] records why it is not a workflow.
- **Collections and dispute workflows** — enterprise AR machinery. The panel bought AR *visibility*, which already ships ([[reports-and-analytics]]).
- **A server-side attention layer** — attention is the skill plus the `lens` parameter, never a question classifier in the server; "no LLM inside the server" is load-bearing ([[context-assembly]]).

## Resolved questions

1. **Multi-company:** v1 is one company per user, but everything is `company_id`-keyed from day one — multi-company later is a `select_company` tool + UI, zero migration.
2. **Product name:** **SoloBooks**.
3. **Repo:** new standalone repo (`~/solobooks`); patterns copied from `finboard/mcp-server`, not imported.
