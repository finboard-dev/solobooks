# SoloBooks v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Design authority:** the knowledge base at `finboard/solobooks/llm-wiki/wiki/index.md` (28 pages). Where this plan and the wiki disagree, the wiki wins — flag the conflict, don't improvise.

**Goal:** Ship SoloBooks v1 — chat-driven double-entry accounting for solopreneurs: MCP tools over a FastAPI service, operational truth in MongoDB, the ledger projected to view-only Google Sheets, analytics via DuckDB, minimal Next.js web app with Better Auth.

**Architecture:** One Python service (FastMCP mounted on FastAPI) with a pure accounting domain layer (`app/domain/` — zero I/O imports), a 5-step posting pipeline (COMPOSE→RESERVE→COMMIT→PROJECT→FINALIZE, outbox embedded in the PostingRecord, sheet tail-check idempotency), a stateless DuckDB read side keyed by `ledger_version`, and thin MCP tools. Auth is API-key until Phase 8, then Better Auth OAuth Provider plugin. See wiki: `three-store-architecture`, `posting-pipeline`, `duckdb-layer`, `auth-wiring`.

**Tech Stack:** Python 3.13, uv, FastAPI, FastMCP v3, motor (async Mongo), DuckDB, pandas/pyarrow, sqlglot, hypothesis, pytest; Next.js 15 + Better Auth (Mongo adapter, OAuth Provider plugin); Google Sheets/Drive/Docs APIs via a service account; Docker + docker-compose (Mongo) for local dev.

---

## Conventions (read once, apply to every task)

**The TDD loop is implicit in every task.** Each task means: (1) write the failing test named in the task, (2) run it, confirm it fails for the stated reason, (3) write the minimal implementation, (4) run it green, (5) commit with the stated message. Tasks below list *what* the test asserts and *what* the implementation must do — the loop itself is not restated 90 times.

- **Money is `Decimal` everywhere.** `float` in any money position is a review-rejecting bug. Amounts serialize as strings in Mongo and sheets.
- **No magic strings.** Every meaningful token (account types, document types, GL columns, statuses) is an enum in `app/domain/enums.py`, defined once (FinBoard principle #7).
- **`app/domain/` imports nothing from `app/core/`, `app/sheets/`, `app/pipeline/`, motor, or googleapiclient.** CI enforces this with an import-linter contract. Pure functions only.
- **Commits:** conventional (`feat:`, `test:`, `chore:`), one task = 1-2 commits, always compiling, tests green.
- **Fixtures:** scenario files in `server/tests/fixtures/scenarios/*.yaml` with `given / when / expect` (see Task 1.8 for the schema). The scenario catalog page of the wiki is the source of the list.
- **Fakes over mocks:** `tests/fakes/fake_sheets.py` is a stateful in-memory Sheets API (append, get, batchGet, create) used by all pipeline/report tests. Real-API tests are marked `@pytest.mark.real_google` and excluded from default runs.

## Repo file map (locked decomposition)

```
solobooks/
├── docker-compose.yml            # mongo:7 + server (dev)
├── .github/workflows/ci.yml      # uv sync, ruff, import-linter, pytest (excl. real_google)
├── server/
│   ├── pyproject.toml            # uv-managed
│   ├── app/
│   │   ├── config.py             # pydantic-settings: mongo url, google sa json path, caps
│   │   ├── main.py               # FastAPI + FastMCP mount + lifespan (outbox drainer)
│   │   ├── core/                 # domain-blind infrastructure
│   │   │   ├── mongo.py          # client, collections, indexes
│   │   │   ├── audit.py          # append-only audit writer + @audited decorator
│   │   │   ├── auth.py           # P6: API-key verify; P8: JWKS JWT verify
│   │   │   ├── renderer.py       # token-budget CSV table renderer
│   │   │   ├── sql_guard.py      # sqlglot SELECT-only guard
│   │   │   └── ratelimit.py      # sliding-window middleware (P9)
│   │   ├── domain/               # PURE — the accounting brain
│   │   │   ├── enums.py          # AccountType, DetailType, DocType, Status, GLColumn…
│   │   │   ├── money.py          # Money (Decimal cents), parse/format
│   │   │   ├── accounts.py       # COA model, seed chart, hierarchy
│   │   │   ├── documents.py      # 9 document dataclasses + validation
│   │   │   ├── emitters.py       # doc → balanced JournalLines (the GL patterns)
│   │   │   ├── compose.py        # validation pipeline: accounts exist, lock check, dup check
│   │   │   ├── matching.py       # rule cascade → MatchProposal
│   │   │   ├── csv_import.py     # statement rows → draft document intents
│   │   │   └── locking.py        # locked_through rules, cross-month redirect
│   │   ├── pipeline/             # write path (Mongo + outbox)
│   │   │   ├── counters.py       # atomic $inc sequences
│   │   │   ├── posting.py        # COMPOSE→RESERVE→COMMIT orchestration (+ drafts, books_state)
│   │   │   ├── outbox.py         # drainer: pending PostingRecords → sheets, tail-check, FINALIZE
│   │   │   └── nudges.py         # silent-account detection (>14 days)
│   │   ├── sheets/               # Google API adapters
│   │   │   ├── client.py         # thin authorized clients (sheets/drive/docs)
│   │   │   ├── provision.py      # company folder, lazy month files, sharing
│   │   │   ├── ledger_writer.py  # append txn, tail_check, re_render_month (TOTALS template lives in provision.py)
│   │   │   └── coa_writer.py     # full COA sheet rewrite
│   │   ├── analytics/            # read side
│   │   │   ├── loader.py         # sheets → arrow → duckdb tables
│   │   │   ├── cache.py          # {company: (conn, ledger_version)} LRU
│   │   │   ├── views.py          # v_lines, v_balances, v_open_items, v_pnl, v_pnl_cash
│   │   │   └── reports.py        # parameterized SELECTs per report
│   │   ├── artifacts/
│   │   │   ├── invoice_doc.py    # template copy → placeholder fill → PDF
│   │   │   └── accountant_packet.py
│   │   └── tools/                # MCP registration, thin over domain/pipeline
│   │       ├── _shared.py        # tenant resolution (token → user → company)
│   │       ├── context.py  coa.py  contacts.py  sales.py  purchases.py
│   │       ├── ledger.py  approval.py  reports.py  imports.py
│   ├── scripts/seed.py           # Mongo indexes + demo company
│   └── tests/
│       ├── fakes/fake_sheets.py
│       ├── fixtures/scenarios/*.yaml
│       ├── fixtures/golden_company/   # P9
│       └── test_*.py
├── web/                          # Next.js 15 + Better Auth (P8)
├── skill/SKILL.md                # the agent skill (P6 v0, P9 final)
└── llm-wiki/                     # knowledge base moves in from finboard/solobooks
```

---

## Phase 0 — Bootstrap

**Exit gate:** CI green on an empty suite; `GET /health` returns `{"status":"ok"}`; `docker compose up` gives a working Mongo.

### Task 0.1: Repo scaffold
**Files:** create the tree above (empty modules with docstrings), `server/pyproject.toml` (deps: fastapi, fastmcp, motor, pydantic-settings, duckdb, pyarrow, pandas, sqlglot, google-api-python-client, google-auth, uvicorn; dev: pytest, pytest-asyncio, hypothesis, ruff, import-linter, mongomock-motor).
- [ ] `uv sync` succeeds; `ruff check .` clean. Commit `chore: scaffold solobooks repo`.

### Task 0.2: Config + health
**Files:** `app/config.py`, `app/main.py`, `tests/test_health.py`
- [ ] Test: `GET /health` → 200 `{"status":"ok"}` (httpx AsyncClient). Implement pydantic-settings `Settings` (mongo_url, google_sa_path, duckdb_cache_max=32, token_budget=8000, match_tolerance="0.99") + minimal FastAPI app. Commit `feat: config + health endpoint`.

### Task 0.3: docker-compose + CI
**Files:** `docker-compose.yml`, `.github/workflows/ci.yml`
- [ ] compose: mongo:7 with volume; CI: uv sync → ruff → import-linter → pytest -m "not real_google"; **plus a `schedule:` (nightly) job running `pytest -m real_google` with the test service account secret** (jobs no-op until Phase 3 adds real tests). Commit `chore: compose + CI`.

### Task 0.4: Integration spike (timeboxed, findings → wiki)
**Files:** `spikes/` (throwaway, not shipped), findings ingested to `llm-wiki/raw/`
- [ ] Verify with real Google APIs before any dependent phase: (a) **Shared Drive** file creation by SA member + external view-only sharing (post-2025 SAs have zero My-Drive quota — wiki sheets-layer storage architecture), (b) `values.append` read-after-write consistency (the tail-check depends on it), (c) FastMCP-on-FastAPI mount with auth middleware, (d) Docs template → PDF export quality. Any failed assumption → wiki supersession BEFORE Phase 1. Commit `chore: integration spike findings`.

### Task 0.5: Domain purity contract
**Files:** `pyproject.toml` ([tool.importlinter] forbid `app.domain` → `app.core|app.sheets|app.pipeline|motor|googleapiclient|duckdb`), `tests/test_purity.py`
- [ ] Test runs `lint-imports` and asserts pass. Commit `chore: enforce domain purity`.

---

## Phase 1 — Domain core (pure)

**Exit gate:** hypothesis property — every emitter balances for ANY valid generated document; all Phase-1 scenario fixtures compose to the exact expected GL lines (cents).

### Task 1.1: Enums
**Files:** `app/domain/enums.py`, `tests/test_enums.py`
- [ ] `AccountType` (ASSET/LIABILITY/EQUITY/INCOME/EXPENSE), `DetailType` (BANK, AR, AP, FIXED_ASSET, CREDIT_CARD, COGS, …), `DocType` (INVOICE, PAYMENT, BILL, BILL_PAYMENT, SALES_RECEIPT, CREDIT_NOTE, VENDOR_CREDIT, TRANSFER, JOURNAL_ENTRY), `DocStatus` (DRAFT/POSTED/VOIDED), `GLColumn` (ordered — TXN_ID, DATE, TYPE, REF, ACCOUNT_NUMBER, ACCOUNT_NAME, DEBIT, CREDIT, CUSTOMER, PROJECT, VENDOR, CLASS, LOCATION, DUE_DATE, MEMO, POSTED_AT, POSTED_BY). Test: GLColumn order matches wiki `general-ledger-sheet`. Commit `feat: domain enums`.

### Task 1.2: Money
**Files:** `app/domain/money.py`, `tests/test_money.py`

```python
# the core type — complete, this is load-bearing
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")

def money(v: str | int | Decimal) -> Decimal:
    if isinstance(v, float):
        raise TypeError("float is forbidden in money positions")
    return Decimal(v).quantize(CENT, rounding=ROUND_HALF_UP)
```
- [ ] Tests: float raises; "10.005" → 10.01; string round-trip. Commit `feat: money type`.

### Task 1.3: Chart of accounts + seed
**Files:** `app/domain/accounts.py`, `tests/test_accounts.py`
- [ ] `Account` model (number, name, parent, type, detail_type, active, **optional tax_line** for Schedule C grouping; normal_balance derived from type). `seed_chart()` returns the full starter COA from wiki `chart-of-accounts` — test asserts every account named in the scenario catalog exists (OBE, Owner's Draw/Contributions, Unearned Revenue, Sales Tax Payable, Processing Fees, Bad Debt, Uncategorized ×2, Fixed Assets + Accum Dep, **Notes Payable, Interest Expense, Reconciliation Discrepancies**). Commit `feat: COA model + seed chart`.

### Task 1.4: Documents
**Files:** `app/domain/documents.py`, `tests/test_documents.py`
- [ ] 9 frozen dataclasses; Invoice has lines[] (desc, qty, rate, account, dims) + due_date + optional tax; Payment has deposit_account, method, applications[]; JournalEntry has N lines. Validation: required fields, positive amounts, JE lines ≥ 2. Commit `feat: document models`.

### Task 1.5: Emitters — the GL patterns
**Files:** `app/domain/emitters.py`, `tests/test_emitters.py`
- [ ] `emit(doc, coa) -> list[JournalLine]` per DocType, exactly the patterns in wiki `document-model` (invoice → DR AR / CR Sales [+ CR Sales Tax Payable]; payment → DR deposit / CR AR per application with ref; transfer → never an income/expense account — enforced; etc.). Example-based tests per type, cents exact. Commit `feat: GL emitters`.

### Task 1.6: The invariant (property test)
**Files:** `tests/test_invariants.py`

```python
@given(any_valid_document())          # hypothesis strategy over all 9 types
def test_every_emission_balances(doc):
    lines = emit(doc, SEED_COA)
    assert sum(l.debit for l in lines) == sum(l.credit for l in lines)
```
- [ ] Strategy generates randomized valid documents (amounts, line counts, dims, tax on/off). Also: transfer emissions never touch INCOME/EXPENSE. Commit `test: balance invariant property`.

### Task 1.7: Compose (validation pipeline)
**Files:** `app/domain/compose.py`, `app/domain/locking.py`, `tests/test_compose.py`
- [ ] `compose(doc, ctx) -> ComposedPosting | ComposeError` — pure; ctx carries coa, locked_through, recent_docs (for dup check), sequences preview. Rules: accounts exist+active, `date > locked_through` else redirect-to-current-month for corrections (locking.py), duplicate warning (same party+amount±3d), Σd==Σc re-asserted. Commit `feat: compose validation`.

### Task 1.8: Scenario fixture runner
**Files:** `tests/fixtures/scenarios/*.yaml`, `tests/test_scenarios.py`

```yaml
# fixture schema (example: processor_fee.yaml)
given: {coa: seed, open_invoices: [{ref: INV-0001, customer: Acme, amount: "1000.00"}]}
when:
  - {type: payment, customer: Acme, deposit_account: Checking, amount: "970.00",
     fee: {account: "Processing Fees", amount: "30.00"},
     applications: [{ref: INV-0001, amount: "1000.00"}]}
expect:
  gl_lines:
    - {account: Checking, debit: "970.00"}
    - {account: "Processing Fees", debit: "30.00"}
    - {account: "Accounts Receivable", credit: "1000.00", ref: INV-0001}
  open_balance: {INV-0001: "0.00"}
```
- [ ] Runner parameterized over all files; `expect` supports `gl_lines`, `open_balance` (computed in Phase 1 by a test-helper ref-sum — the same arithmetic `v_open_items` implements in Phase 4), and optional `report_deltas` (asserted once Phase 4 lands; ignored before). Write the first 8 fixtures: invoice_post, invoice_edit (reversal+repost), invoice_void, partial_payment, overpayment_credit, processor_fee, transfer_not_pnl, owner_expense. Commit `test: scenario fixtures batch 1`.

### Task 1.9: Remaining catalog fixtures
- [ ] retainer_to_unearned + apply_on_invoice, nsf_reopen, early_discount, bad_debt_writeoff, ar_ap_offset, sales_receipt, credit_note, vendor_credit, opening_balance_obe_plug, cross_month_correction, locked_period_rejected, **refund** (DR AR ref / CR Bank), **chargeback** (refund + fee), **owner_draw** (DR Owner's Draw / CR Bank), **bill_partial_payment**, **vendor_refund** (AP mirrors). Gate: all pass cent-exact — one YAML per scenario-catalog row, no omissions. Commit `test: scenario fixtures complete`.

---

## Phase 2 — Posting pipeline (Mongo + outbox, fake sheets)

**Exit gate:** failure-injection suite green — process killed between COMMIT and PROJECT leaves exactly one copy of every txn in the (fake) sheet after drain; approve-after-lock rejected.

### Task 2.1: Mongo core + indexes
**Files:** `app/core/mongo.py`, `scripts/seed.py`, `tests/test_mongo.py` (mongomock-motor)
- [ ] Collections: companies, contacts, documents, posting_records, counters, audit_log. Contact model includes **`track_1099` boolean on vendors** (feeds the 1099 report + packet). `ensure_indexes()`: unique (company_id, doc_number), (company_id, outbox.status), audit append-only (no update ops exposed). Commit `feat: mongo layer`.

### Task 2.2: Counters
**Files:** `app/pipeline/counters.py`, `tests/test_counters.py`
- [ ] `next_number(company_id, kind)` via findOneAndUpdate $inc upsert; test: 100 concurrent calls → 100 unique sequential values, no reuse. Commit `feat: atomic counters`.

### Task 2.3: PostingRecord + COMMIT
**Files:** `app/pipeline/posting.py`, `tests/test_posting.py`

```python
# PostingRecord document shape (single atomic insert — outbox embedded)
{ "_id": ..., "company_id": ..., "txn_id": "JE-2026-000187",
  "doc_snapshot": {...}, "gl_lines": [...],          # amounts as strings
  "idempotency_key": ..., "status": "committed",
  "outbox": {"state": "pending", "attempts": 0, "row_range": None},
  "audit": {"who": ..., "conversation_id": ..., "at": ...} }
```
- [ ] `post(doc, ctx)`: compose → reserve → single insert → audit (**deliberate divergence from wiki step 5: audit written at COMMIT, not FINALIZE — safer, the record exists even if projection lags; log this supersession at Task 9.4 wiki ingest**). **`ledger_version` is NOT bumped here** — it bumps in the drainer after a successful sheet append (FINALIZE, per wiki posting-pipeline step 5); bumping at COMMIT would let DuckDB cache a sheet that doesn't yet contain the txn. Crash-before-insert test: nothing anywhere. Commit `feat: commit step`.

### Task 2.4: Fake Sheets + ledger writer core + outbox drainer
**Files:** `tests/fakes/fake_sheets.py`, `app/sheets/ledger_writer.py` (`append_txn`, `tail_check` — built HERE against the fake; Phase 3 adds real-API concerns), `app/pipeline/outbox.py`, `tests/test_outbox.py`
- [ ] Drainer: scan `outbox.state=pending` ordered by txn_id → `append_txn` → mark appended + row_range → **bump `ledger_version`** (FINALIZE). **Tail-check first on every attempt** (last 50 rows contain txn_id → mark appended, don't re-append). Lifespan task + drain-on-startup. Failure injection: fake raises after write → retry → exactly one copy; assert ledger_version bumps only after successful append. Commit `feat: outbox drainer with tail-check`.

### Task 2.5: Approval flow
**Files:** `app/pipeline/posting.py` (draft path), `tests/test_approval.py`
- [ ] `create_draft`, `approve(doc_id)` (re-runs compose at approval time), `reject`, `approve_all`. Tests: approval_mode none skips draft; void/edit-posted/unlock ALWAYS draft-gated; draft approved after lock_period → ComposeError. Commit `feat: approval flow`.

### Task 2.6: Period locking
**Files:** `app/domain/locking.py` (extend), `tests/test_locking.py`
- [ ] `lock_period/unlock_period` on company; corrections to locked months emit into current open month (asserted via scenario fixture cross_month_correction now running through the REAL pipeline). Commit `feat: period locking`.

### Task 2.7: Books state (onboarding)
**Files:** `app/pipeline/posting.py`, `tests/test_books_state.py`
- [ ] Company carries `books_state: incomplete|complete`; flips to complete when the opening-balance JE posts; reports (Phase 4) and `get_books_status` (Phase 6) surface a warning banner while incomplete (wiki onboarding-opening-balances #5). Commit `feat: incomplete-books state`.

---

## Phase 3 — Sheets layer (real Google)

**Exit gate:** contract suite green against fake AND `@real_google` smoke: provision → post → row visible in the actual sheet, TOTALS difference cell = 0.00, file shared view-only.

### Task 3.1: Authorized clients
**Files:** `app/sheets/client.py`, `tests/test_sheets_client.py`
- [ ] Service-account creds from config; sheets/drive/docs builders; retry with exponential backoff on 429/5xx. Commit `feat: google clients`.

### Task 3.2: Provisioning
**Files:** `app/sheets/provision.py`, `tests/test_provision.py` (against fake; one real smoke)
- [ ] **All files created in Shared Drives** (SA as Manager member; `shared_drive_id` in the provisioning registry — wiki sheets-layer storage architecture). `ensure_company_folder`, `ensure_month_file(company, yyyy_mm)` (lazy, from template: **protected TOTALS row on top** with `=SUM(...)` formulas + difference cell, header row from GLColumn enum below it, frozen), share view-only with user email, register ids in Mongo. Never resolve by name at runtime. Commit `feat: drive provisioning`.

### Task 3.3: Ledger writer — real-API concerns
**Files:** `app/sheets/ledger_writer.py` (extend the Phase-2 core), `tests/test_ledger_writer.py`
- [ ] Real-API semantics for the existing `append_txn`/`tail_check`: ONE `values.append` RAW per txn, retry/backoff wiring; `re_render_month` (unlock case): fresh tab → verify counts+totals → swap → delete. Wire the real client into the drainer behind the same interface as the fake. Commit `feat: ledger writer real API`.

### Task 3.4: COA writer + real smoke
**Files:** `app/sheets/coa_writer.py`, `tests/test_real_smoke.py` (@real_google)
- [ ] Full COA rewrite on change. Smoke: fresh test company end-to-end → assert via API read-back. Commit `feat: coa writer + real smoke`.

---

## Phase 4 — Read side (DuckDB + reports)

**Exit gate:** trial balance ties on every fixture ledger; BS(as-of) == cumulative sums; cash vs accrual differ exactly by unpaid documents; corrupted cell → hard error.

### Task 4.1: Loader + typing
**Files:** `app/analytics/loader.py`, `tests/test_loader.py`
- [ ] batchGet all month sheets + COA → arrow → duckdb `gl_lines`, `accounts`; DECIMAL(18,2)/DATE enforced; any parse failure raises `LedgerCorruptionError` (test with a poisoned fixture). Commit `feat: duckdb loader`.

### Task 4.2: Cache
**Files:** `app/analytics/cache.py`, `tests/test_cache.py`
- [ ] `{company: (conn, ledger_version)}`, rebuild on version mismatch, LRU cap from config. Commit `feat: analytics cache`.

### Task 4.3: View stack
**Files:** `app/analytics/views.py`, `tests/test_views.py`
- [ ] `v_lines` (⋈ accounts, signed amount by normal balance) → `v_balances` → `v_open_items` (ref sums) → `v_pnl` → `v_pnl_cash` (settlement-proportional recognition via refs). Tests on fixture ledgers, incl. the cash-basis delta assertion. Commit `feat: canonical view stack`.

### Task 4.4a: Core statements
**Files:** `app/analytics/reports.py`, `tests/test_reports_core.py`
- [ ] profit_and_loss (range, basis toggle, **monthly columns**, **prior-period/prior-year compare**, by class/customer), balance_sheet (as-of; RE computed), trial_balance, account_ledger (running balance). Reports carry the `books_state` warning banner while incomplete (Task 2.7). Every report = parameterized SELECT over views only (grep-test: no raw table refs outside views.py except loader). Commit `feat: core statements`.

### Task 4.4b: Operational reports
**Files:** `app/analytics/reports.py`, `tests/test_reports_ops.py`
- [ ] ar/ap_aging (due_date buckets), income_by_customer, spend_by_vendor, project_profitability, cash_flow (simple), sales_tax_liability, 1099_payments (track_1099 vendors), list_uncategorized, customer_statement (**resolution of the wiki's split: the open-items REPORT ships in v1; a sendable statement ARTIFACT is v1.5** — log this supersession in the wiki at ingest). Commit `feat: operational reports`.

### Task 4.5: query_books guard
**Files:** `app/core/sql_guard.py`, `tests/test_sql_guard.py`
- [ ] sqlglot: single SELECT, whitelist {v_* views, gl_lines, accounts}, row cap, timeout; rejection tests (DDL, multi-statement, JOIN to nothing-listed). Commit `feat: sql guard`.

---

## Phase 5 — Matching + money-in/out

**Exit gate:** rule-cascade table tests green incl. tolerance boundary and ambiguity; CSV file → categorized drafts → approved → books.

### Task 5.1: Matching engine
**Files:** `app/domain/matching.py`, `tests/test_matching.py`
- [ ] `match(event, open_items, tolerance) -> MatchProposal` — cascade per wiki `matching-engine` (cited → exact → unique subset (DP over cents) → partial oldest-first → overpay+credit → retainer-if-project-hint → unapplied). Table tests: one per rule; $0.99 in/$1.00 out (difference auto-lined to fees/discounts); equal balances → `ambiguous` with all candidates; multiple subsets → ambiguous; **at least one AP-mirror test per rule family (bill payments)**. Commit `feat: matching engine`.

### Task 5.2: Payment + applications through pipeline
**Files:** `app/pipeline/posting.py` (payment path), `tests/test_payments_e2e.py`
- [ ] MatchProposal stored on draft Payment; approval posts DR deposit / CR AR per application with refs; open balances update via v_open_items (fixture: one payment, two invoices). Commit `feat: payments e2e`.

### Task 5.3a: Statement parsing
**Files:** `app/domain/csv_import.py`, `tests/test_csv_parse.py`, `tests/fixtures/statements/*.csv`
- [ ] `parse_statement(csv_bytes) -> list[StatementRow]` (date, description, amount, direction) tolerant of real bank variance — fixtures: Chase-shaped, BofA-shaped, generic debit/credit-column CSV; malformed rows collected into a reject report, never silently dropped. Commit `feat: statement parsing`.

### Task 5.3b: Classification → drafts
**Files:** `app/domain/csv_import.py`, `app/tools/imports.py` (Phase 6 registers), `tests/test_csv_classify.py`
- [ ] Rows → draft document intents: deposits route through the [[matching-engine]] hints path, expenses to Uncategorized-or-heuristic accounts, money↔money rows to Transfer candidates; EVERYTHING lands as drafts, approval-gated; **dedupe vs existing postings** (amount+date±3d against posted txns AND pending drafts). Commit `feat: csv classification`.

### Task 5.4: Bank reconciliation (the trust floor — wiki `bank-reconciliation`)
**Files:** `app/domain/reconciliation.py`, `app/pipeline/posting.py` (rec object persistence), `app/analytics/reports.py` (rec + outstanding-items reports), `tests/test_reconciliation.py`
- [ ] Rec object per money account × statement period: statement rows matched to posted GL lines (cleared flags), outstanding-items report (uncleared book-side lines), rec history stored; unexplained differences post ONLY to Reconciliation Discrepancies (verify_books flags nonzero); unmatched statement rows feed the import draft queue (same loop as 5.3b). Close ritual step 2 upgrades to statement rec when a statement exists (balance-check = fallback). Cent-exact rec fixtures. Commit `feat: bank reconciliation`.

---

## Phase 6 — MCP surface (first dogfood)

**Exit gate (MILESTONE):** a real test company's books kept entirely from Claude via API key — invoice → payment → reports, links to real sheets.

### Task 6.1: API-key auth + tenant
**Files:** `app/core/auth.py`, `app/tools/_shared.py`, `tests/test_auth.py`
- [ ] Per-user API keys in Mongo (hashed); middleware resolves key → user → company; tools never accept tenant args (grep-test over tool signatures). Commit `feat: api-key auth`.

### Task 6.2: Audit decorator + renderer
**Files:** `app/core/audit.py`, `app/core/renderer.py`, `tests/test_renderer.py`
- [ ] `@audited` wraps every tool (who/args/duration/result-size/conversation), append-only. Renderer: CSV-style tables under token budget — drop zero rows, collapse depth, explicit truncation marker (port FinBoard mcp-server pattern). Commit `feat: audit + renderer`.

### Task 6.3a: Tools — context, COA, contacts
**Files:** `app/tools/{context,coa,contacts}.py`, `app/main.py`, `tests/test_tools_context.py`
- [ ] whoami, get_books_status (incl. incomplete-books banner; silent-account nudges **stub until 7.3**), get/update_company, lock/unlock_period; list/add/update_account; add_customer(+projects), add_vendor (**with track_1099**), update_contact, list_contacts. Pattern: resolve tenant → call domain/pipeline → render. One happy-path test per tool (fakes + mongomock). Commit `feat: tools batch 1`.

### Task 6.3b: Tools — documents, approval, reports, imports
**Files:** `app/tools/{sales,purchases,ledger,approval,reports,imports}.py`, `tests/test_tools_documents.py`
- [ ] create_invoice, record_payment (matching), create_sales_receipt, create_credit_note; record_bill, pay_bill, create_vendor_credit; post_journal_entry, record_transfer, record_owner_expense; list_drafts/approve/reject/approve_all; all report tools + query_books + verify_books (**stub until 7.3; final home `tools/context.py`**); import_bank_csv, export_accountant_packet (stub until 7.2). Every write returns its sheet-range link. One happy-path test per tool. Commit `feat: tools batch 2`.

### Task 6.4: Skill v0 + dogfood
**Files:** `skill/SKILL.md`
- [ ] Skill v0 per "The Art of Writing Skills": document types, tool sequences (money-arrived flow), never-do list (transfers≠income, retainers≠income, park in Uncategorized). Manual gate: connect Claude with API key, run the milestone script (onboard → opening balance → invoice → payment → P&L → lock month). Record transcript in `llm-wiki/raw/`. Commit `feat: skill v0`.

---

## Phase 7 — Artifacts + close ritual

**Exit gate:** invoice PDF renders from template with correct totals; accountant packet opens in Excel; close checklist runs in chat end-to-end.

### Task 7.1: Invoice artifact
**Files:** `app/artifacts/invoice_doc.py`, `tests/test_invoice_doc.py` (@real_google for render)
- [ ] Template copy → batchUpdate placeholders → PDF export to `<Company>/invoices/`; revised versions append-only (`INV-0042 (revised)`); links on Mongo doc + returned in chat. Commit `feat: invoice artifact`.

### Task 7.2: Accountant packet (expanded scope 2026-07-18)
**Files:** `app/artifacts/accountant_packet.py`, tool in `app/tools/reports.py`, `tests/test_packet.py`
- [ ] One tool → bundle in Drive folder: TB, GL, 1099 CSV (method-excluded), **by-tax-line grouping** (Schedule C), **accrual-to-cash bridge** (ΔAR/ΔAP/Δunearned/non-cash), open AR/AP item detail with refs, customer/vendor/project masters, **categorization review** (account choice + memo_verbatim), approval-mode-per-period disclosure + auto-posted flags, tolerance write-off list, fixed-asset additions, audit log export. Commit `feat: accountant packet`.

### Task 7.3: Close ritual + nudges
**Files:** `app/tools/context.py` (verify_books, close checklist), `app/pipeline/nudges.py`
- [ ] `verify_books` (TB ties, drafts pending, unapplied, uncategorized, **nonzero OBE, stale unearned, aged unapplied credits, nonzero Reconciliation Discrepancies**); close flow prompts statement rec (Task 5.4) with balance tie-out as no-statement fallback; nudge query: money account with no lines >14 days → surfaced in get_books_status. Commit `feat: close ritual + nudges`.

---

## Phase 8 — Web + real OAuth

**Exit gate:** Claude connects via full OAuth (Better Auth OAuth Provider plugin); web login and MCP grant are the same user; API-key path retained as fallback.

### Task 8.1a: Next.js scaffold + Better Auth login
**Files:** `web/` (app router, Better Auth w/ Mongo adapter + Google social + email/password), login page
- [ ] Auth against the same Mongo; login/logout round-trip test (playwright or route-handler test). Commit `feat: web scaffold + login`.

### Task 8.1b: Session-guarded REST
**Files:** `web/` API routes or server actions: me, folder tree, API-key management
- [ ] Session cookie guards all three; unauthenticated → 401 test. Commit `feat: web REST`.

### Task 8.2: OAuth Provider plugin + resource server
**Files:** `web/` (oauth-provider plugin config), `app/core/auth.py` (JWKS verifier), `tests/test_jwt_verify.py`
- [ ] RFC 9728 metadata on the MCP server pointing at web's `/oauth2/*`; FastAPI verifies JWT offline (cached JWKS with rotation), token→user→company; consent ON. **Automated tests: expired token rejected; wrong `aud` rejected; wrong `iss` rejected; garbage signature rejected; valid token resolves tenant** (testing-strategy layer 7). Fallback: API-key still accepted. Manual gate: full Claude connect flow on a fresh account. Commit `feat: oauth wiring`.

### Task 8.3: Folder view + connect page
- [ ] Folder tree from Mongo registry (links open Google Sheets); connect page shows MCP URL + key management. Commit `feat: connect + folder pages`.

### Task 8.4: Batch review grid (the one ledger-UI exception — wiki `platform`)
**Files:** `web/` (import-drafts page), server: reuse approval tools via REST wrappers
- [ ] Read-only draft-queue grid: date, description, proposed account, amount, dup-flag; approve/reject per row + select-all; wired to the same approval flow (audited identically to chat approvals). Renders the DRAFT QUEUE only — no ledger views. Commit `feat: batch review grid`.

---

## Phase 9 — Golden Company + ship

**Exit gate:** Golden Company e2e cent-exact vs hand-verified expected file; rate limits on; Docker images build; skill eval scenarios pass.

### Task 9.1a: Golden Company script + expected files
**Files:** `tests/fixtures/golden_company/script.yaml` (~200 txns exercising every scenario), `expected/{trial_balance.csv, pnl_accrual.csv, pnl_cash.csv, bs.csv, aging.csv}`
- [ ] Author the fictional solopreneur year and hand-verify the expected files (this is accounting work — budget it as its own sitting; verify TB ties by hand before committing). Commit `test: golden company fixture`.

### Task 9.1b: Golden Company runner
**Files:** `tests/test_golden_company.py`
- [ ] Posts the scripted year through the REAL pipeline vs fake sheets; every month TOTALS 0.00; every expected file matches to the cent. Wired into CI on every PR. Commit `test: golden company runner`.

### Task 9.2: Hardening
- [ ] Rate-limit middleware (auth 30/min IP, MCP 120/min token); request logging with conversation id; Dockerfile (server) + web build; compose prod profile. Commit `chore: hardening + docker`.

### Task 9.3: Skill eval + final skill
- [ ] Paired eval loop: scripted conversations (ambiguous payment → asks; transfer never income; retainer never early income; CSV import flow) against live agent; iterate skill until pass. Commit `feat: skill v1`.

### Task 9.4: Docs + wiki sync
- [ ] Move `llm-wiki/` into the repo; README quickstart; ingest "as-built" deltas into the wiki (any place implementation diverged from design gets a logged supersession). Commit `docs: v1`.

---

## Deferred by design (do NOT build in v1)

**v1.1 committed fast-follow:** recurring/retainer auto-billing. **v1.5:** Stripe payment links, billable expenses, sendable customer-statement **artifact** (the open-items *report* ships in v1, Task 4.4b), 1099 completions (W-9/TIN, NEC/MISC, corp exemption), mid-year historical backfill. **v2 thesis (adopted):** accountant seat — multi-company role, per-user audit attribution, cross-client console, REST read API. **Later:** Plaid feeds, receipts OCR, time tracking, mileage, quarterly tax estimates, payroll, multi-currency. Pricing must be **announced** at launch (business decision, no billing code).
