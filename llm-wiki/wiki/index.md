# SoloBooks Wiki — Index

One entry per page. Update on every ingest.

## Vision & Architecture

- [[product-vision]] — headless accounting for solopreneurs; MCP is the API, sheets are the books, UI is minimal
- [[three-store-architecture]] — Mongo = truth, Sheets = translated ledger (view-only, service-account-owned), DuckDB = stateless calculator; self-sufficiency/exportability rule
- [[platform]] — Better Auth (MCP plugin + JWKS), service-account Sheets, minimal Next.js UI, no billing; FinBoard mcp-server reuse list

## Accounting Core

- [[dates-and-timezones]] — plain calendar dates, no tz math; company timezone for relative dates + audit rendering only; fiscal year day==01 in v1
- [[company-object]] — per-company settings JSON: fiscal year, books start, basis, approval mode, locked_through, sales tax, ledger_version
- [[chart-of-accounts]] — numbered, typed, hierarchical COA; rendered as a sheet; seed chart covers every scenario account
- [[dimensions]] — customer, project (under customer), vendor, class, location (day-one column), memo on every GL line
- [[document-model]] — 9 document types, each a thin validator emitting a GL line pattern; derived status; atomic numbering
- [[general-ledger-sheet]] — monthly sheets, column schema, TOTALS row, append-only rules, cross-month corrections, outbox safety

## The Crux

- [[cash-basis-recognition]] — canonical cash-basis algorithm: money-movement recategorization, pro-rata settlements, card-charge-date rule, retainers-at-receipt

- [[posting-pipeline]] — the write path: COMPOSE→RESERVE→COMMIT→PROJECT→FINALIZE; embedded outbox, tail-check idempotency, no balance caches
- [[pairing-and-matching]] — universal ref rule (single definition of settlement/open balance) + matching flow incl. retainer path
- [[matching-engine]] — deterministic rule cascade, LLM-extracts-facts-only, MatchProposal, ambiguity as outcome, $0.99 tolerance
- [[scenario-catalog]] — every CPA edge case (overpayment, retainers, processor fees, NSF, write-offs, owner expenses, transfers, offsets) as ref'd journal lines
- [[point-in-time-balances]] — any balance at any date is a filtered sum; no snapshots anywhere

## Operations & Trust

- [[bank-reconciliation]] — v1 statement-based rec: cleared flags, outstanding items, no silent plugs (Reconciliation Discrepancies), rec history; the trust floor

- [[approval-flow]] — draft → GL-line preview → approve; approval_mode all/none; destructive actions always gated
- [[period-locking-month-close]] — locked_through, close ritual (statement rec + fallback tie-out), unlock with artifact archiving, no year-end closing entries (RE computed)
- [[onboarding-opening-balances]] — opening JE with OBE plug, full-TB migration path, historical open documents
- [[safety-nets]] — uncategorized parking, unapplied credits, duplicate warnings, expanded verify_books, completeness nudges, outbox retry, append-only audit log

## Implementation (drafted, not built)

- [[sheets-layer]] — Shared-Drive storage, lazy provisioning, one-append-per-txn, tail-check dedupe, formula TOTALS, archive-then-swap re-render
- [[duckdb-layer]] — per-company LRU cache keyed by ledger_version, DECIMAL-only typing, canonical view stack, query_books guard
- [[auth-wiring]] — Better Auth OAuth Provider plugin as auth server; offline JWKS verification; API-key fallback
- [[invoice-artifact]] — template copy → placeholder fill → PDF export; revised artifacts append-only
- [[testing-strategy]] — scenario catalog as cent-exact fixtures; Golden Company e2e gate; 8 layers

## Product Surface

- [[mcp-tool-surface]] — full v1 tool list; tenant scope from token, never from arguments
- [[reports-and-analytics]] — DuckDB load path, all reports as single-definition SQL views, query_books power tool, cash/accrual toggle
- [[compliance]] — cash vs accrual, flat sales tax, 1099 tracking (US-first)
- [[invoice-artifact]] — Google Doc → PDF in Drive; the sendable thing
- [[the-skill]] — agent behavior guide shipped with the product (Art of Writing Skills methodology)
- [[professional-review-findings]] — CPA + CAS persona reviews: cash-basis v1 errors (fixed), bank-rec = trust floor, batch-review need, accountant-channel signal; open scope calls
- [[buyer-panel-findings]] — 15-respondent SSR panel: advisors rank highest, "data pipe" objection 11/15, price bands, scope consequences
- [[v1-scope]] — the authoritative cut: v1 / v1.1 (recurring) / v1.5 / v2 thesis (accountant seat) / out; resolved questions
