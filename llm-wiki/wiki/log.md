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

## [2026-07-18] maintenance | Redundancy + contradiction sweep
- Contradictions removed: period-locking step 2 taught balance-check-with-plug (now: statement rec per bank-reconciliation, fallback tie-out posts only to Reconciliation Discrepancies); safety-nets "poor man's bank reconciliation" bullet deleted; product-vision "never renders a ledger" now names the one grid exception; three-store-architecture aligned to Shared Drives + archive/ folder; mcp-tool-surface packet description updated (was stale TB+GL+1099-only) + reconcile_account added; onboarding duplicate step numbering fixed
- Redundancy removed: v1-scope rewritten as single authoritative cut (accretion layers folded); buyer-panel-findings scope list → pointer to v1-scope; dated "(added 2026-07-18…)"/"SUPERSEDES" annotations stripped from 10 pages (provenance lives in frontmatter sources + this log); auth-wiring supersedes-footnote removed; index Implementation stubs replaced
- Coherence added: the-skill now carries principal/interest + reconciliation flows; cash-basis history note moved to log; original features/ design doc marked SUPERSEDED with pointer to wiki
