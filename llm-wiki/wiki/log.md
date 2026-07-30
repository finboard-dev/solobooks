---
type: synthesis
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
tags: [log, provenance]
---

# Log (append-only)

## [2026-07-17] ingest | Product design discussion → design doc v1

- Source: `raw/2026-07-17-design-doc.md` (distilled from founder design session, 2026-07-17)
- Pages created: product-vision, three-store-architecture, platform, company-object, chart-of-accounts, dimensions, document-model, general-ledger-sheet, pairing-and-matching, scenario-catalog, point-in-time-balances, approval-flow, period-locking-month-close, onboarding-opening-balances, safety-nets, mcp-tool-surface, reports-and-analytics, compliance, invoice-artifact, the-skill, v1-scope
- Contradictions flagged: none (first ingest)
- Notes: design supersedes two ideas rejected during discussion — (1) user-editable sheets with drift detection (rejected for service-account-owned view-only sheets), (2) re-render-on-demand ledger, option (b) (rejected for append-only immediate posting, option (a); re-render survives only for unlocked-month re-lock). Open questions tracked in v1-scope.

## [2026-07-17] decision | Open questions resolved
- Multi-company: one company v1, company_id-keyed schema from day one
- Name: SoloBooks (confirmed)
- Repo: new standalone repo, patterns copied from finboard/mcp-server
- Pages updated: v1-scope

## [2026-07-17] ingest | Posting pipeline research + approved design
- Source: raw/2026-07-17-posting-pipeline-research.md (Modern Treasury ledger series, outbox literature)
- Pages created: posting-pipeline
- Pages updated: index, general-ledger-sheet, approval-flow (cross-links)
- Contradictions flagged: none; confirms existing append-only/reversal design. Notable divergence from MT recorded: no balance caches.

## [2026-07-17] ingest | Matching engine internals approved
- Source: raw/2026-07-17-matching-engine-design.md
- Pages created: matching-engine
- Pages updated: pairing-and-matching, index (cross-links)
- Decisions: LLM extracts facts only (engine deterministic); tolerance option (b) $0.99 write-off to Bank Fees/Sales Discounts; ambiguity returns all candidates

## [2026-07-17] ingest | Sheets layer approved
- Source: raw/2026-07-17-sheets-layer-design.md
- Pages created: sheets-layer
- Pages updated: index (cross-link)
- Decisions: lazy month creation; formula TOTALS; one append per txn; swap-tab re-render

## [2026-07-17] ingest | DuckDB layer approved
- Source: raw/2026-07-17-duckdb-layer-design.md
- Pages created: duckdb-layer
- Pages updated: index
- Decisions: reports AND query_books share one view stack; parse failure = hard error; LRU cap on resident companies

## [2026-07-17] ingest | Auth wiring approved (supersession)
- Source: raw/2026-07-17-auth-wiring-design.md
- Pages created: auth-wiring
- Pages updated: platform (MCP plugin reference superseded — CONTRADICTION resolved: Better Auth MCP plugin deprecated in favor of OAuth Provider plugin), index

## [2026-07-17] ingest | Testing strategy + invoice artifact details; index reorganized
- Sources: raw/2026-07-17-testing-strategy.md (+ invoice artifact generation details folded into invoice-artifact context)
- Pages created: testing-strategy
- Pages updated: index (new "Implementation (drafted, not built)" section consolidating posting-pipeline, matching-engine, sheets-layer, duckdb-layer, auth-wiring, invoice-artifact, testing-strategy)
- Drafting phase COMPLETE — all implementation topics documented; no code written

## [2026-07-17] ingest | Buyer panel (SSR, 15 respondents) → scope revision
- Sources: raw/2026-07-17-buyer-panel-report.md, raw/2026-07-17-buyer-panel.json
- Pages created: buyer-panel-findings
- Pages updated: v1-scope (CSV import INTO v1 — REVERSES earlier "no import" cut; accountant packet, completeness nudges, pricing ≤$29 pre-launch), mcp-tool-surface (import_bank_csv, export_accountant_packet), safety-nets (nudges), index
- Contradiction resolved: "bank feeds/CSV import out of v1" superseded by panel evidence (11/15 top objection); full Plaid feeds remain out

## [2026-07-17] plan | Phased v1 implementation plan written + reviewer-approved
- Artifact: solobooks/plans/2026-07-17-solobooks-v1-plan.md (10 phases, 40+ tasks, exit gates)
- Review loop: round 1 found 11 issues (worst: ledger_version bumped at COMMIT would stale the DuckDB cache — moved to FINALIZE per posting-pipeline) — all fixed; round 2 approved
- Deliberate divergence to log at ingest (Task 9.4): audit written at COMMIT not FINALIZE; customer_statement = report in v1, artifact v1.5
- NO code written — plan is a document pending founder review

## [2026-07-18] ingest | Self-review gap fixes (7 gaps)
- Source: raw/2026-07-18-gap-fixes.md
- Pages created: cash-basis-recognition (canonical v_pnl_cash algorithm incl. sales-tax-on-cash + card-charge-date + retainers-at-receipt), dates-and-timezones
- Pages updated: sheets-layer (**CRITICAL SUPERSESSION: SA My-Drive storage → Google Workspace Shared Drives — post-2025-04-15 SAs have ZERO Drive quota, original design would not work**; row_range invalidation on re-render), matching-engine (hints schema — the LLM↔engine contract), buyer-panel-findings (sober framing: no segment above "might or might not"), company-object (timezone field, fiscal day==01), duckdb-layer + compliance (point to canonical cash-basis page), platform (Shared Drives + exportability mechanism), general-ledger-sheet + scenario-catalog (orphan-fixing inbound links)
- Plan updated: new Task 0.4 integration spike (shared drives, append read-after-write, FastMCP mount, PDF export; purity contract renumbered 0.5); Task 3.2 shared-drive provisioning; Task 5.3 split into 5.3a parse / 5.3b classify
- Lint: orphans sheets-layer + testing-strategy resolved

## [2026-07-18] ingest | Professional reviews (CPA + CAS personas) → bucket-1 correctness fixes
- Sources: raw/2026-07-18-cpa-firm-review.md, raw/2026-07-18-cas-firm-review.md, raw/2026-07-18-bucket1-fixes.md
- Pages created: professional-review-findings
- Pages updated: cash-basis-recognition (**REWRITTEN to rules R1–R9 — v1 page had REAL ERRORS: internal contradiction on owner-paid expenses, Owner's Draw in P&L, uncapitalized asset legs, unstated fee-leg rule; caught by CPA persona review**), onboarding-opening-balances (double-count rule: opening JE never carries AR/AP, historical docs offset OBE), compliance (1099 method exclusion + sales-tax basis disclosure), pairing-and-matching (method now accounting-relevant — SUPERSEDES "metadata only"), period-locking-month-close + sheets-layer (pre-unlock artifact archiving + audited diff), index
- Scope calls deliberately NOT decided — listed as OPEN on professional-review-findings

## [2026-07-18] decision | Scope calls applied (all 8 recommendations approved)
- Source: raw/2026-07-18-scope-calls.md
- Pages created: bank-reconciliation
- Pages updated: v1-scope (rec + grid + packet + COA/verify additions into v1; NEW v1.1 section = recurring billing; 1099 completions + backfill → v1.5; v2 thesis = accountant seat), platform (batch grid = the one ledger-UI exception), chart-of-accounts (tax_line field; Notes Payable, Interest Expense, Reconciliation Discrepancies; principal/interest skill rule), safety-nets (verify_books additions), reports-and-analytics (expanded packet contents), professional-review-findings (open calls → decided), index
- Plan updated: new Task 5.4 (bank reconciliation) + Task 8.4 (batch review grid); Tasks 1.3/7.2/7.3 expanded; deferred section restructured (v1.1/v1.5/v2 thesis/later)

## [2026-07-30] ingest | Process-aware financial objects (founder) → object-model realignment

- Source: `raw/2026-07-30-process-aware-objects.md` — founder architecture position, framed through the invoice. Directive: "review this and use this ideology and update full stack which conflicts with that."
- Method: six-lens conflict audit (object model, workflow-as-object, decision trail, policy versioning, retrieval-as-attention, adversarial scope counter-lens) over all 30 wiki pages, all raw sources and the implementation plan; every candidate adversarially verified against file text; completeness critic pass. **62 candidates → 32 refuted → 27 verified conflicts + 15 second-order findings.**
- Pages created (all `status: draft`): financial-object-model, process-instance, decision-record, evidence, policy-set, context-assembly
- Pages updated: three-store-architecture, product-vision, company-object, duckdb-layer, dates-and-timezones, general-ledger-sheet, sheets-layer, bank-reconciliation, period-locking-month-close, document-model, approval-flow, matching-engine, pairing-and-matching, invoice-artifact, onboarding-opening-balances, mcp-tool-surface, reports-and-analytics, safety-nets, compliance, chart-of-accounts, the-skill, testing-strategy, v1-scope, index

### GOVERNANCE — read before treating any of this as decided

`CLAUDE.md` defines `verified` as "confirmed by the founder in design discussion **and** present in a raw source". The source is founder-authored; the ~20 design decisions derived from it are **not**. Therefore: new pages are `draft`, and every new or changed claim on an existing page carries the inline marker **(proposed 2026-07-30)** so the founder can confirm them in one pass. Precedent: `raw/2026-07-18-scope-calls.md` was the founder confirming a review's recommendations *before* pages moved. **The supersession rule is also explicitly narrowed here: recency does not outrank correctness.** This source does NOT override CPA-validated accounting decisions the founder never revisited — cash-basis R1–R9, the AR/AP opening double-count rule, the 1099 method exclusion, deterministic matching.

### CONTRADICTIONS FLAGGED (not silently overwritten)

1. **`three-store-architecture`: "Mongo = cache, ledger wins."** Correct for money, wrong for meaning. Narrowed to two truth domains — effect (ledger, canonical for monetary/settlement facts) vs context (Mongo, canonical and append-only, never a cache). Mongo remains a cache of *derived ledger* facts (invoice status) and the ledger still wins there.
2. **`invoice-artifact`: "line-item prose isn't accounting data."** True of description/qty/rate; false of `service_period`, which is accounting context. Scope-corrected, not reversed.
3. **`general-ledger-sheet`: "The GL shows the full story."** False today — no column links a reversal to what it reverses. Fixed by admitting `reverses_txn_id` under a new column-admission rule.
4. **`bank-reconciliation`: GL lines "carry `cleared` status."** Unimplementable as written: the sheets layer has one primitive (append, never edit), so a `cleared` cell update has no method, violates append-only, and cannot be made effectively-once by the tail-check. Superseded by append rows to a `Reconciliations` sheet.
5. **`onboarding-opening-balances`: `books_state` flips `complete` on the opening JE**, which by rule 5 can never contain AR/AP — the banner drops while the migration is still incomplete. Flip now depends on the onboarding process completing.
6. **`period-locking-month-close`: "every rendering a banker or accountant may have seen survives."** Mechanism only archives the GL sheet; outsiders see P&Ls, agings and packets. Extended to retained exported renderings.
7. **`reports-and-analytics`: three packet sections were not producible** — approval-mode-per-period disclosure (derivable only by replaying an unindexed audit stream), the tolerance write-off list (indistinguishable from real fee/discount lines), and categorization review (specified over `memo_verbatim`, captured only on the two matching tools). Fixed by `PostingRecord.provenance`.
8. **`approval-flow`: the approved preview is not provably the posted lines** — compose re-validates at approval time. Fixed by `preview_hash` + `PREVIEW_DRIFT`.
9. **LIVE BUG (no ideology needed): `ledger_version` bumps only on a GL append**, but DuckDB also caches the `accounts` table and the COA is "fully rewritten on change" with no bump. A `tax_line` edit, rename or deactivation serves stale data until an unrelated posting happens. Renamed `books_version`; bumps on any change to anything DuckDB caches.

### REFUTED — do not resurrect without new file evidence

Enterprise machinery correctly refused: contract/order objects, revenue schedules, collections/dispute workflows, multi-party approval routing, a server-side attention classifier, receipt substantiation. Already-satisfied claims wrongly flagged: derived status and point-in-time balances already answer the "current state" and "derived facts" buckets better than the source asks; the cash/accrual toggle is already one object read two ways; `query_books` already exposes prior treatment over `gl_lines`. Recorded in `v1-scope` so the next reviewer does not burn a cycle rediscovering them.

## [2026-07-18] maintenance | Redundancy + contradiction sweep
- Contradictions removed: period-locking step 2 taught balance-check-with-plug (now: statement rec per bank-reconciliation, fallback tie-out posts only to Reconciliation Discrepancies); safety-nets "poor man's bank reconciliation" bullet deleted; product-vision "never renders a ledger" now names the one grid exception; three-store-architecture aligned to Shared Drives + archive/ folder; mcp-tool-surface packet description updated (was stale TB+GL+1099-only) + reconcile_account added; onboarding duplicate step numbering fixed
- Redundancy removed: v1-scope rewritten as single authoritative cut (accretion layers folded); buyer-panel-findings scope list → pointer to v1-scope; dated "(added 2026-07-18…)"/"SUPERSEDES" annotations stripped from 10 pages (provenance lives in frontmatter sources + this log); auth-wiring supersedes-footnote removed; index Implementation stubs replaced
- Coherence added: the-skill now carries principal/interest + reconciliation flows; cash-basis history note moved to log; original features/ design doc marked SUPERSEDED with pointer to wiki

## [2026-07-30] maintenance | Coherence + lint sweep after the parallel object-model update

- Trigger: six new pages and 24 edited pages were written by five agents that could not see each other's work. Links and orphans were clean; duplication and two contradictions were not.
- **Single-owner assignments made explicit** (one concept, one page): `books_version` → duckdb-layer · capture rule → the-skill · null-renders-as-"not recorded" → context-assembly · `provenance` → decision-record · `preview_hash`/`PREVIEW_DRIFT` → approval-flow · policy header + retained renderings + statutory/operational thresholds → policy-set · `ExceptionKind` → safety-nets · column-admission rule → general-ledger-sheet · `ref` vs `origin` → pairing-and-matching · tenant rule for caller-supplied refs → mcp-tool-surface · audit `subject_ref` edge → safety-nets · ledger-vs-context read boundary → duckdb-layer · "approval is not a workflow" → process-instance · packet-section diagnosis → reports-and-analytics · decided-out register → v1-scope. Every other mention reduced to a one-line consequence plus a link.
- **Contradictions fixed:** `ledger_version` survived on posting-pipeline, sheets-layer, reports-and-analytics and index → all now `books_version`; three-store-architecture placed the `Reconciliations` sheet in the month folder while sheets-layer placed it at the company root (company root wins — it carries a `statement_period` column); duckdb-layer called its table `reconciliations` and hedged it as conditional while sheets-layer named it `rec_clears` and committed to it (`rec_clears`, committed); index still described rec as "cleared flags".
- posting-pipeline had been missed entirely by the parallel pass despite three pages pointing at it for COMMIT-time `provenance` and `PREVIEW_DRIFT` — source, `modified`, marker and the two hooks added.
- Frontmatter added to index and log (lint rule requires it on every page; they were exempt only from the orphan rule).
- **One duplication left undecided and escalated:** pairing-and-matching's 6-rule ordered list vs matching-engine's 7-rule cascade — pre-existing (both 2026-07-17), CPA-validated content, not agent-introduced. Resolved separately below on founder instruction.

## [2026-07-30] decision | Matching rules: one cascade, one page (founder-approved)

- **Contradiction, not granularity.** The two lists had already drifted three ways, all provable from file text: (1) `matching-engine` rule 1 **"Invoice cited"** — the user naming INV-0042 — was **absent** from pairing-and-matching, and since both lists were explicitly ordered ("In order" / "first hit wins"), the missing rule was the highest-precedence one, so implementing from that page would override the user's own explicit instruction; (2) the subset **tie-break disagreed** — `oldest-first` vs `prefer fewest, then oldest`: on open invoices of $100/$400/$500 a $500 payment settles `{$100,$400}` under one and `{$500}` under the other, producing different refs, different aging and a different cash-basis composition (R4 recognizes pro-rata *per settled document*); (3) **confidence and ambiguity-as-an-outcome** — the "return ALL candidates and ask the user" safety rule — existed only on matching-engine, so the other page read as "always propose", i.e. always guess.
- Why it mattered beyond tidiness: the plan states "where this plan and the wiki disagree, **the wiki wins**", which assumes the wiki gives one answer. Both pages were `status: verified` and gave two. (Plan Task 5.1 does cite matching-engine, so live risk was low; the exposure was the next edit to either page going uncaught.)
- **Resolution:** pairing-and-matching's ordered list → an **unordered outcome table** ("treatments, not a cascade"), keeping every journal entry verbatim — retainer `DR Bank / CR Unearned Revenue (customer, project)` and `DR Unearned Revenue / CR AR ref` with "income never recognized early" (R6), the overpayment→unapplied-credit treatment, partial-remainder-stays-open, no-context→listed credit. **[[matching-engine]] is now the sole owner of precedence, tie-breaks, confidence and ambiguity.** The cited-invoice rule is correctly absent from the outcome table: it is a *selection* rule, not a distinct ledger outcome — which is exactly why the outcome/precedence split is the right seam.
- **No accounting changed.** Zero CPA-validated treatments were altered, reworded or dropped; only the ordering framing was removed. Verified: both retainer JEs, the R6 claim, the overpayment treatment and the universal ref rule all still present; no numbered rule list remains on pairing-and-matching; matching-engine still carries all 7; all links resolve.
