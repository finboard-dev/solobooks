# SoloBooks v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Design authority:** the knowledge base at `finboard/solobooks/llm-wiki/wiki/index.md` (36 pages). Where this plan and the wiki disagree, the wiki wins — flag the conflict, don't improvise.
> **2026-07-30 realignment:** the process-aware object model (`financial-object-model`, `process-instance`, `decision-record`, `evidence`, `policy-set`, `context-assembly`) is folded into the tasks below. Those pages are `status: draft` pending founder confirmation — **do not start Phase 1 until they are confirmed**, because Tasks 1.1/1.4/1.8 and 2.1/2.3 freeze enums, dataclasses and an append-only record shape that cannot be changed afterwards. Provenance is **unbackfillable**: what COMMIT does not capture is gone.

**Goal:** Ship SoloBooks v1 — chat-driven double-entry accounting for solopreneurs: MCP tools over a FastAPI service, operational truth in MongoDB, the ledger projected to view-only Google Sheets, analytics via DuckDB, minimal Next.js web app with Better Auth.

**Architecture:** One Python service (FastMCP mounted on FastAPI) with a pure accounting domain layer (`app/domain/` — zero I/O imports), a 5-step posting pipeline (COMPOSE→RESERVE→COMMIT→PROJECT→FINALIZE, outbox embedded in the PostingRecord, sheet tail-check idempotency), a stateless DuckDB read side keyed by `books_version`, a Mongo context read side (`app/reads/`), and thin MCP tools. Auth is API-key until Phase 8, then Better Auth OAuth Provider plugin. See wiki: `three-store-architecture`, `posting-pipeline`, `duckdb-layer`, `auth-wiring`.

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
│   │   │   ├── renderer.py       # token-budget CSV table renderer + section renderer (wiki: context-assembly)
│   │   │   ├── process.py        # NEW — generic ProcessInstance store, domain-blind (principle #1)
│   │   │   ├── decisions.py      # NEW — generic DecisionRecord + EvidenceRef store, domain-blind
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
│   │   │   ├── policy.py         # NEW — PolicySet resolution as-of a date (wiki: policy-set)
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
│   │   ├── reads/                # NEW — Mongo read side (context, not ledger; wiki: context-assembly)
│   │   │   ├── objects.py        # get_object(ref, lens) — the dossier assembler
│   │   │   └── trails.py         # get_audit_trail(ref) over the audit subject_ref edge
│   │   ├── analytics/            # read side (LEDGER only — context is unreachable from here)
│   │   │   ├── loader.py         # sheets → arrow → duckdb tables (gl_lines, accounts, rec_clears)
│   │   │   ├── cache.py          # {company: (conn, books_version)} LRU
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
- [ ] `AccountType` (ASSET/LIABILITY/EQUITY/INCOME/EXPENSE), `DetailType` (BANK, AR, AP, FIXED_ASSET, CREDIT_CARD, COGS, …), `DocType` (INVOICE, PAYMENT, BILL, BILL_PAYMENT, SALES_RECEIPT, CREDIT_NOTE, VENDOR_CREDIT, TRANSFER, JOURNAL_ENTRY), `DocStatus` (DRAFT/POSTED/VOIDED), `GLColumn` (ordered — TXN_ID, DATE, TYPE, REF, **REVERSES_TXN_ID**, ACCOUNT_NUMBER, ACCOUNT_NAME, DEBIT, CREDIT, CUSTOMER, PROJECT, VENDOR, CLASS, LOCATION, DUE_DATE, **LINE_REASON**, MEMO, POSTED_AT, POSTED_BY). Test: GLColumn order matches wiki `general-ledger-sheet`.
- [ ] **Process-aware vocabulary (2026-07-30 realignment — these freeze here, add them now):** `ProcessType` (IMPORT_RUN, REC_RUN, CLOSE_RUN, AMENDMENT, ONBOARDING), `TriggerKind` (USER_CHAT, SCHEDULE, IMPORT, CLOSE, SYSTEM), `ProcessState` (OPEN, COMPLETED, ABANDONED), `DecisionKind` (MATCH, APPROVAL, REJECTION, CATEGORIZATION, TOLERANCE_WRITE_OFF, DUPLICATE_DISPOSITION, UNCATEGORIZED_PARKING, CLEARING, LOCK, UNLOCK, VOID, AMENDMENT), `ActorKind` (HUMAN, AGENT, RULE, SYSTEM), `Confidence` (EXACT, HIGH, MEDIUM, LOW, AMBIGUOUS), `ExceptionKind` (UNCATEGORIZED, UNAPPLIED_CREDIT, STALE_UNEARNED, NONZERO_OBE, RECONCILIATION_DISCREPANCY, PENDING_DRAFT, TRIAL_BALANCE_BREAK, DUPLICATE_SUSPECTED, IMPORT_ROW_REJECTED, PREVIEW_DRIFT, OUTSTANDING_ITEM_AGED, EVIDENCE_MISSING, **REC_PERIOD_DISCONTINUITY, CUTOFF_DATE_UNCONFIRMED**), `PriorReturnBasis` (CASH, ACCRUAL — no NONE: absent an accrual return the answer is CASH), `Disposition` (OPEN, RESOLVED, ACKNOWLEDGED), `EvidenceKind` (DRIVE_FILE, STATEMENT_ROW, CONVERSATION, IMPORT_ROW, ARTIFACT), `OriginType`, `LineReason`, `PostingSource` (CHAT, CSV_IMPORT, RECURRING, RECONCILIATION), `ObjectLens` (SETTLEMENT, TREATMENT, DECISION, EVIDENCE, FULL). Wiki: `decision-record`, `process-instance`, `safety-nets`, `context-assembly`. Commit `feat: domain enums`.

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
- [ ] 9 frozen dataclasses; Invoice has lines[] (desc, qty, rate, account, dims) + due_date + optional tax; Payment has deposit_account, method, applications[]; JournalEntry has N lines. Validation: required fields, positive amounts, JE lines ≥ 2.
- [ ] **Context seams (2026-07-30 realignment — nullable, free-capture only, but they freeze here):** every document gains `origin {type, ref}` (causation — a *different edge* from `ref`, which stays settlement-only) `evidence[]` and `process_refs[]`; Invoice lines gain `service_period {start, end}`; Invoice gains `delivered_at` / `delivery_channel`. Test: all default to None and no emitter reads them (they are context, not effect). Per-field required/optional column documented for the skill's capture rule. Wiki: `financial-object-model`, `invoice-artifact`, `evidence`. Commit `feat: document models`.

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
- [ ] Runner parameterized over all files; `expect` supports `gl_lines`, `open_balance` (computed in Phase 1 by a test-helper ref-sum — the same arithmetic `v_open_items` implements in Phase 4), and optional `report_deltas` (asserted once Phase 4 lands; ignored before). **Plus `provenance`, `decision`, `exceptions` and `policy_header` blocks (2026-07-30 realignment) — without them no fixture can express any provenance, decision or policy fact and the entire realignment ships with zero deterministic coverage. This schema must be right BEFORE the 25+ YAMLs below are written against it** (wiki: `testing-strategy`). Write the first 8 fixtures: invoice_post, invoice_edit (reversal+repost), invoice_void, partial_payment, overpayment_credit, processor_fee, transfer_not_pnl, owner_expense. Commit `test: scenario fixtures batch 1`.

### Task 1.9: Remaining catalog fixtures
- [ ] **Ruleset fixtures (R1–R11, 2026-07-30 tri-persona review) — these encode the rule changes and must exist before any posting:** `ar_ap_offset` **retargeted to the unequal-amounts + residual-cash-leg variant** (R5a: the offset leg recognizes on the JE date, the cash remainder when it settles — the fixture as previously scoped would have encoded the *wrong* answer); `prior_return_cash_migration` and `prior_return_accrual_migration` (R4 branch), plus `prior_return_cash_capitalized_bill` (a historical unpaid bill for a $12,000 machine must compose `DR Machinery & Equipment`, NOT `DR Equipment Expense` — hardcoding the expense deducts it at settlement and again via §179/MACRS), and `depreciation_and_179` (R11 — the manual depreciation JE that v1-scope mandates must hit BOTH bases); `cutoff_december_check` (R10 — a cheque written 12/28 clearing 01/04 deducts in the earlier year, and the rec still ties).
- [ ] retainer_to_unearned + apply_on_invoice, nsf_reopen, early_discount, bad_debt_writeoff, ar_ap_offset, sales_receipt, credit_note, vendor_credit, opening_balance_obe_plug, cross_month_correction, locked_period_rejected, **refund** (DR AR ref / CR Bank), **chargeback** (refund + fee), **owner_draw** (DR Owner's Draw / CR Bank), **bill_partial_payment**, **vendor_refund** (AP mirrors). Gate: all pass cent-exact — one YAML per scenario-catalog row, no omissions. Commit `test: scenario fixtures complete`.

---

## Phase 2 — Posting pipeline (Mongo + outbox, fake sheets)

**Exit gate:** failure-injection suite green — process killed between COMMIT and PROJECT leaves exactly one copy of every txn in the (fake) sheet after drain; approve-after-lock rejected.

### Task 2.1: Mongo core + indexes
**Files:** `app/core/mongo.py`, `scripts/seed.py`, `tests/test_mongo.py` (mongomock-motor)
- [ ] Collections: companies, contacts, documents, posting_records, counters, audit_log, **policy_sets, process_instances, decisions, evidence_refs** (2026-07-30 realignment). Contact model includes **`track_1099` boolean on vendors** (feeds the 1099 report + packet). `ensure_indexes()`: unique (company_id, doc_number), (company_id, outbox.status), audit append-only (no update ops exposed), **(company_id, subject_ref) on audit_log and decisions — the edge that makes a decision path queryable rather than greppable; an append-only entry written without it never gains one**, (company_id, type, state) on process_instances, unique (company_id, type, idempotency_key) on process_instances. Commit `feat: mongo layer`.

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
  "audit": {"who": ..., "conversation_id": ..., "at": ...},
  # 2026-07-30 realignment — UNBACKFILLABLE. Not captured here means gone forever.
  "provenance": {"approval_mode_at_post": ..., "approved_by": ..., "approval_decision_id": ...,
                 "decided_by": ActorKind, "rule_id": ..., "policy_version": ...,
                 "skill_version": ..., "source": PostingSource, "process_ref": ...} }
```
- [ ] `post(doc, ctx)`: compose → reserve → single insert → audit (**deliberate divergence from wiki step 5: audit written at COMMIT, not FINALIZE — safer, the record exists even if projection lags; log this supersession at Task 9.4 wiki ingest**). **`books_version` is NOT bumped here** — it bumps in the drainer after a successful sheet append (FINALIZE, per wiki posting-pipeline step 5); bumping at COMMIT would let DuckDB cache a sheet that doesn't yet contain the txn. (Renamed from `ledger_version` 2026-07-30: the COA and `Reconciliations` writers are bump sites too — see Task 3.4.) Crash-before-insert test: nothing anywhere. **Test that `provenance` is populated on every path (chat, import, recurring, reconciliation) — a null field here is a permanent data loss, not a TODO.** Commit `feat: commit step`.

### Task 2.4: Fake Sheets + ledger writer core + outbox drainer
**Files:** `tests/fakes/fake_sheets.py`, `app/sheets/ledger_writer.py` (`append_txn`, `tail_check` — built HERE against the fake; Phase 3 adds real-API concerns), `app/pipeline/outbox.py`, `tests/test_outbox.py`
- [ ] Drainer: scan `outbox.state=pending` ordered by txn_id → `append_txn` → mark appended + row_range → **bump `books_version`** (FINALIZE). **Tail-check first on every attempt** (last 50 rows contain txn_id → mark appended, don't re-append). Lifespan task + drain-on-startup. Failure injection: fake raises after write → retry → exactly one copy; assert books_version bumps only after successful append.
- [ ] **Generalize the outbox out of the PostingRecord (2026-07-30 realignment).** It is currently a subdocument of a posting, so it cannot carry the non-posting sheet writes v1 now needs — reconciliation clear rows, archive copies, close exports. Make it a standalone durable queue with the same at-least-once + dedupe guarantees; the PostingRecord holds a reference. Wiki: `sheets-layer`. Commit `feat: outbox drainer with tail-check`.

### Task 2.5: Approval flow
**Files:** `app/pipeline/posting.py` (draft path), `tests/test_approval.py`
- [ ] `create_draft`, `approve(doc_id)` (re-runs compose at approval time), `reject`, `approve_all`. Tests: approval_mode none skips draft; void/edit-posted/unlock ALWAYS draft-gated; draft approved after lock_period → ComposeError.
- [ ] **Approval emits an `APPROVAL` DecisionRecord, not a status flip (2026-07-30 realignment):** approver, rule, `reason_verbatim`, evidence, alternatives, `decided_at`. **`preview_hash` is the load-bearing part** — the draft stores a hash of the exact GL lines previewed; because compose re-validates at approval time, a mismatch means the human consented to one thing and the ledger recorded another. Test: mutate a rate/COA/duplicate between preview and approve → raises `PREVIEW_DRIFT`, re-presents, does NOT post. This must exist at the first approval ever written or the claim is unprovable forever. Wiki: `approval-flow`, `decision-record`. Commit `feat: approval flow`.

### Task 2.6: Period locking
**Files:** `app/domain/locking.py` (extend), `tests/test_locking.py`
- [ ] `lock_period/unlock_period` on company; corrections to locked months emit into current open month (asserted via scenario fixture cross_month_correction now running through the REAL pipeline). Commit `feat: period locking`.

### Task 2.7: Books state (onboarding)
**Files:** `app/pipeline/posting.py`, `tests/test_books_state.py`
- [ ] Company carries `books_state: incomplete|complete`; reports (Phase 4) and `get_books_status` (Phase 6) surface a warning banner while incomplete (wiki onboarding-opening-balances #5). **Fix (2026-07-30 realignment): the flip depends on the `ONBOARDING` ProcessInstance completing — opening JE AND historical open documents — not on the JE alone.** The opening JE by rule can never contain AR/AP, so flipping on it drops the banner precisely while the AR/AP migration is still outstanding. Test: opening JE posted + open documents pending → still `incomplete`. Commit `feat: incomplete-books state`.

### Task 2.8: Process, decision, policy and evidence stores (2026-07-30 realignment)
**Files:** `app/core/process.py`, `app/core/decisions.py`, `app/domain/policy.py`, `tests/test_process.py`, `tests/test_policy.py`
- [ ] Generic **domain-blind** stores (principle #1 — they must know nothing about accounting): `ProcessInstance` (counter-minted human-quotable ids — `CLOSE-2026-07`, not a UUID, per the document-model numbering doctrine; idempotency key so re-uploading the same statement does not mint a second run), `DecisionRecord` (one shape, all `DecisionKind`s), `EvidenceRef` (tenant-scoped: a `DRIVE_FILE` must resolve inside this company's folder registry, an arbitrary id is rejected). `policy.py` is PURE: `resolve(company, as_of_date) -> PolicySet` — **as-of a date, never as-of now**. **`prior_return_basis` is deliberately NOT a policy field** (2026-07-30 ruleset review): it is a HUMAN DecisionRecord on the ONBOARDING instance and its effect is carried by the composition of the posted historical documents, which `v_pnl_cash` reads directly — a second copy on an effective-dated object could later contradict the ledger undetectably; statutory thresholds effective-dated by tax year. Tests: process idempotency; a decision with no `subject_ref` is rejected; policy resolution for a date before/after a change returns different sets; a foreign-company evidence ref is rejected. Wiki: `process-instance`, `decision-record`, `policy-set`, `evidence`. Commit `feat: process, decision and policy stores`.

---

## Phase 3 — Sheets layer (real Google)

**Exit gate:** contract suite green against fake AND `@real_google` smoke: provision → post → row visible in the actual sheet, TOTALS difference cell = 0.00, file shared view-only.

### Task 3.1: Authorized clients
**Files:** `app/sheets/client.py`, `tests/test_sheets_client.py`
- [ ] Service-account creds from config; sheets/drive/docs builders; retry with exponential backoff on 429/5xx. Commit `feat: google clients`.

### Task 3.2: Provisioning
**Files:** `app/sheets/provision.py`, `tests/test_provision.py` (against fake; one real smoke)
- [ ] **All files created in Shared Drives** (SA as Manager member; `shared_drive_id` in the provisioning registry — wiki sheets-layer storage architecture). `ensure_company_folder`, `ensure_month_file(company, yyyy_mm)` (lazy, from template: **protected TOTALS row on top** with `=SUM(...)` formulas + difference cell, header row from GLColumn enum below it, frozen), share view-only with user email, register ids in Mongo. Never resolve by name at runtime. **Plus `ensure_reconciliations_sheet(company)`** — a third per-company sheet at the company folder root: `txn_id`, **`account_number`**, **`side`** (DEBIT|CREDIT), `statement_period`, `rec_id`, **`state`** (CLEARED|UNCLEARED), `cleared_at` — **keyed by the `(txn_id, account_number, side)` triple** (wiki `sheets-layer`, `bank-reconciliation`). Written by APPEND only; `cleared` is not a GL column and never a cell edit, because the sheets layer has no method for mutating an existing row and the tail-check cannot make one effectively-once. **This schema freezes HERE — the sheet is append-only, so a missing key column is unfixable after the first company is provisioned.** A `txn_id`-only key marks a Transfer cleared on both its accounts at once and drives the second account's residual off by the whole transfer amount; without `state`, an erroneous pairing is permanent. Test: a Transfer cleared on account A leaves its account-B leg uncleared. **(2026-07-31 second-pass W16)** Wiki: `sheets-layer`, `general-ledger-sheet`. Commit `feat: drive provisioning`.

### Task 3.3: Ledger writer — real-API concerns
**Files:** `app/sheets/ledger_writer.py` (extend the Phase-2 core), `tests/test_ledger_writer.py`
- [ ] Real-API semantics for the existing `append_txn`/`tail_check`: ONE `values.append` RAW per txn, retry/backoff wiring; `re_render_month` (unlock case): fresh tab → verify counts+totals → swap → delete. Wire the real client into the drainer behind the same interface as the fake. Commit `feat: ledger writer real API`.

### Task 3.4: COA writer + real smoke
**Files:** `app/sheets/coa_writer.py`, `tests/test_real_smoke.py` (@real_google)
- [ ] Full COA rewrite on change. **The rewrite MUST bump `books_version` (2026-07-30 realignment) — this is a live bug in the current design, not a new capability: DuckDB caches the `accounts` table too, and `ledger_version` bumped only on GL append, so a `tax_line` edit, rename or deactivation served stale account data until an unrelated posting happened.** Test: `update_account` → cached connection is invalidated without any posting. Smoke: fresh test company end-to-end → assert via API read-back. Commit `feat: coa writer + real smoke`.

---

## Phase 4 — Read side (DuckDB + reports)

**Exit gate:** trial balance ties on every fixture ledger; BS(as-of) == cumulative sums; cash vs accrual differ exactly by unpaid documents; corrupted cell → hard error.

### Task 4.1: Loader + typing
**Files:** `app/analytics/loader.py`, `tests/test_loader.py`
- [ ] batchGet all month sheets + COA **+ the company-root `Reconciliations` sheet** → arrow → duckdb `gl_lines`, `accounts`, `rec_clears`; DECIMAL(18,2)/DATE enforced; any parse failure raises `LedgerCorruptionError` (test with a poisoned fixture). Commit `feat: duckdb loader`.

### Task 4.2: Cache
**Files:** `app/analytics/cache.py`, `tests/test_cache.py`
- [ ] `{company: (conn, books_version)}`, rebuild on version mismatch, LRU cap from config. **Test both bump triggers: a GL append AND a COA rewrite each invalidate the cache** (the COA half is the bug fix from Task 3.4; no existing test layer catches it because they all build fresh connections). Commit `feat: analytics cache`.

### Task 4.3: View stack
**Files:** `app/analytics/views.py`, `tests/test_views.py`
- [ ] `v_lines` (⋈ accounts, signed amount by normal balance) → `v_balances` → `v_open_items` (ref sums) → `v_pnl` → `v_pnl_cash` — implements **R1–R11** ([[cash-basis-recognition]]) incl. **R5a** (offset amount = `min(Σ AP debits w/ ref, Σ AR credits w/ ref)`; every other leg of that posting recognizes nothing), **R11** (cost recovery — a P&L line whose contra is a contra-asset/accumulated-amortization/prepaid account recognizes on BOTH bases; without it Schedule C line 13 is $0 forever) and R4's **OBE-composition test** (an AR/AP settlement whose settled document's offsetting composition is Opening Balance Equity recognizes nothing; every other composition recognizes pro-rata). **There is deliberately NO `prior_return_basis` branch in this view** — the answer was baked into the posted documents' composition at onboarding, and Task 2.8 makes the value unreachable from PolicySet by design (2026-07-31 second-pass, regression 5). Grep-test: `views.py` references no field outside `gl_lines` / `accounts` / `rec_clears`. Tests on fixture ledgers, incl. the cash-basis delta assertion. Commit `feat: canonical view stack`.

### Task 4.4a: Core statements
**Files:** `app/analytics/reports.py`, `tests/test_reports_core.py`
- [ ] profit_and_loss (range, basis toggle, **monthly columns**, **prior-period/prior-year compare**, by class/customer), balance_sheet (as-of; RE computed), trial_balance, account_ledger (running balance). Reports carry the `books_state` warning banner while incomplete (Task 2.7). Every report = parameterized SELECT over views only (grep-test: no raw table refs outside views.py except loader).
- [ ] **Policy header on every report (2026-07-30 realignment):** basis, `policy_version`, ruleset versions (cash-basis R1–R11 id, matching), period, books_state — resolved **as-of the report's period, not as-of now**. A report without a header is a number with no meaning; `compliance` already required this of the sales-tax report and it generalizes. Test: the same period rendered under two policy versions produces two different headers. Wiki: `policy-set`. Commit `feat: core statements`.

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
- [ ] **Statement balances + the four-term residual (2026-07-30 tri-persona review):** `REC_RUN.inputs` gains `statement_period{start,end}`, `statement_beginning_balance`, `statement_ending_balance` (signed: + for asset accounts, − for credit cards). `discrepancy_amount` is **redefined as the residual**, stated in **signed terms** — never "deposits in transit" / "outstanding cheques", both of which invert on a credit card, which is a money account too (2026-07-31 second-pass W17):

```
  signed_statement_ending_balance          (+ asset; − credit-card/liability)
+ Σ uncleared book DEBITS  to the account  (date ≤ period end)
− Σ uncleared book CREDITS to the account  (date ≤ period end)
− signed book balance (Σ DR − Σ CR) at period end
= 0.00
```

"Uncleared" is qualified **by period**: no `rec_clears` row for the triple whose `statement_period` ends on or before this period end — otherwise a December residual of 0.00 becomes nonzero the moment the January run appends its rows. Not leftover unmatched rows; without a balance the rec proves nothing about completeness. Cent-exact fixtures assert 0.00 on a clean month for **both a checking account and a credit card**, the exact residual on a seeded omission, and **reproducibility** (run December → run January → re-run December, still 0.00). `statement_beginning_balance` must equal the prior completed run's ending balance or raise `REC_PERIOD_DISCONTINUITY`; on the FIRST run for an account it is asserted against the opening JE instead (the only verification the opening balance ever receives). Residual is computed only AFTER unmatched statement rows are dispositioned — a bank fee not yet booked is a missing entry, not a discrepancy. A `CLEARING` dated ≤ `locked_through` is refused. Cent-exact fixture asserts a residual of 0.00 on a clean month and the exact residual on a seeded omission.
- [ ] **A `REC_RUN` ProcessInstance** per money account × statement period (2026-07-30 realignment — replaces the ad-hoc "Rec object"): statement rows matched to posted GL lines, **each pairing recorded as a `CLEARING` DecisionRecord so the rec is re-performable** (a bare `cleared` boolean loses the pairing that produced it), cleared state appended to the Reconciliations sheet (Task 3.2), outstanding-items report (uncleared book-side lines), rec history = the process instances themselves; unexplained differences post ONLY to Reconciliation Discrepancies (verify_books flags nonzero); statement rows are `EvidenceKind.STATEMENT_ROW` at zero capture cost; unmatched statement rows feed the import draft queue — which is an `IMPORT_RUN` process instance, making "reconciliation and import are the same loop" literally true (one object, two type entries). Close ritual step 2 upgrades to statement rec when a statement exists (balance-check = fallback). Cent-exact rec fixtures. Commit `feat: bank reconciliation`.

---

## Phase 6 — MCP surface (first dogfood)

**Exit gate (MILESTONE):** a real test company's books kept entirely from Claude via API key — invoice → payment → reports, links to real sheets. **Plus (2026-07-30 realignment): ask "why is this invoice still outstanding?" and get an assembled, correct answer that names what it does not know.** The gate was write-path only; a system that can post perfectly and explain nothing would have passed it.

### Task 6.1: API-key auth + tenant
**Files:** `app/core/auth.py`, `app/tools/_shared.py`, `tests/test_auth.py`
- [ ] Per-user API keys in Mongo (hashed); middleware resolves key → user → company; tools never accept tenant args (grep-test over tool signatures). **Extend the isolation rule (2026-07-30 realignment): the grep-test proves no tool takes a `company_id`, but proves nothing about a tool taking `ref="INV-0042"` — document numbers are unique PER COMPANY, not globally, and the new context reads are the first surfaces that accept a caller-supplied id. Every context read filters `{company_id, ref}`; test asserts a foreign ref returns not-found, not data.** Wiki: `context-assembly`. Commit `feat: api-key auth`.

### Task 6.2: Audit decorator + renderer
**Files:** `app/core/audit.py`, `app/core/renderer.py`, `tests/test_renderer.py`
- [ ] `@audited` wraps every tool (who/args/duration/result-size/conversation), append-only, **plus the `subject_ref` edge on every entry (2026-07-30 realignment) — an append-only entry written without it never gains one, and without it a decision path can be grepped but never queried.** Renderer: CSV-style tables under token budget — drop zero rows, collapse depth, explicit truncation marker (port FinBoard mcp-server pattern).
- [ ] **Section renderer alongside the table renderer.** All three table-budget levers are row operations, so a dossier that exceeds the budget gets truncated by dropping the OLDEST audit rows — i.e. the original approval, the most load-bearing fact in the answer — while a marker at the bottom satisfies "never silently truncate" and the agent explains confidently from a mutilated trail. Contract: an ordered list of named sections, each with a minimum guaranteed allocation and its own `(N earlier entries not shown)` marker; sections are dropped whole and named, never thinned silently. Wiki: `context-assembly`. Commit `feat: audit + renderer`.

### Task 6.3a: Tools — context, COA, contacts
**Files:** `app/tools/{context,coa,contacts}.py`, `app/main.py`, `tests/test_tools_context.py`
- [ ] whoami, get_books_status (incl. incomplete-books banner; silent-account nudges **stub until 7.3**), get/update_company, lock/unlock_period; list/add/update_account; add_customer(+projects), add_vendor (**with track_1099**), update_contact, list_contacts. Pattern: resolve tenant → call domain/pipeline → render. One happy-path test per tool (fakes + mongomock). Commit `feat: tools batch 1`.

### Task 6.3b: Tools — documents, approval, reports, imports
**Files:** `app/tools/{sales,purchases,ledger,approval,reports,imports}.py`, `tests/test_tools_documents.py`
- [ ] create_invoice, record_payment (matching), create_sales_receipt, create_credit_note; record_bill, pay_bill, create_vendor_credit; post_journal_entry, record_transfer, record_owner_expense; list_drafts/approve/reject/approve_all; all report tools + query_books + verify_books (**stub until 7.3; final home `tools/context.py`**); import_bank_csv, export_accountant_packet (stub until 7.2). Every write returns its sheet-range link. One happy-path test per tool. Commit `feat: tools batch 2`.

### Task 6.3c: Tools — context assembly (2026-07-30 realignment)
**Files:** `app/reads/{objects,trails}.py`, `app/tools/context.py`, `tests/test_context_assembly.py`
- [ ] `get_object(ref, lens)` — assembles the financial object from Mongo per `ObjectLens` (SETTLEMENT / TREATMENT / DECISION / EVIDENCE / FULL), joining document + ledger facts + process refs + decision path + policy in force + evidence, rendered through the section renderer. `get_audit_trail(ref)` over the `subject_ref` edge. `attach_evidence(subject_ref, evidence)`. `list_processes` / `get_process(process_id)`.
- [ ] **Read-only, no new truth store, no snapshots.** Tests: the two founder-source questions end-to-end on a fixture ledger — "why is this still outstanding" (SETTLEMENT) and "why did this recognize when it did" (TREATMENT); **a null field renders as "not recorded", never as a fact** (a null `delivered_at` must not read as "not delivered"); out-of-scope context returns an explicit "not applicable in this scope" rather than an empty section; foreign-company ref → not-found (Task 6.1). Wiki: `context-assembly`, `financial-object-model`. Commit `feat: context assembly tools`.

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
- [ ] One tool → bundle in Drive folder: TB, GL, 1099 CSV (method-excluded, **$600 threshold resolved as-of the report's tax year, never as-of now**), **by-tax-line grouping** (Schedule C, using the `tax_line` map **effective for that year** — a destructive COA rewrite would otherwise regroup a filed return under today's map), **accrual-to-cash bridge** (ΔAR/ΔAP/Δunearned/non-cash), open AR/AP item detail with refs, customer/vendor/project masters, **categorization review**, approval-mode-per-period disclosure + auto-posted flags, tolerance write-off list, fixed-asset additions, audit log export.
- [ ] **The three previously-undeliverable sections become filters over `PostingRecord.provenance` (2026-07-30 realignment)** — categorization review (`decided_by=AGENT` + rule + memo_verbatim), tolerance write-off list (`rule_id=RULE_TOLERANCE_WRITEOFF`, previously indistinguishable from a real bank fee), approval disclosure (`approval_mode_at_post`, previously derivable only by replaying an unindexed audit stream). Plus: **the packet and any explicitly exported report are retained as immutable timestamped copies in the Drive folder with their policy header**, and the close writes the Tier-2 self-sufficiency export (CloseRun, decision trail, policy header, evidence index) into the month folder. Wiki: `policy-set`, `three-store-architecture`. Commit `feat: accountant packet`.

### Task 7.3: Close ritual + nudges
**Files:** `app/tools/context.py` (verify_books, close checklist), `app/pipeline/nudges.py`
- [ ] `verify_books` (TB ties, drafts pending, unapplied, uncategorized, **nonzero OBE, stale unearned, aged unapplied credits, nonzero Reconciliation Discrepancies**); close flow prompts statement rec (Task 5.4) with balance tie-out as no-statement fallback; nudge query: money account with no lines >14 days → surfaced in get_books_status (threshold from the versioned policy set, not a literal — the wiki carried two spellings of this one number).
- [ ] **The close is a `CLOSE_RUN` ProcessInstance (2026-07-30 realignment)** with per-step state and every exception carrying an `ExceptionKind` + `Disposition` (OPEN / RESOLVED / ACKNOWLEDGED) with actor and reason — today the profession's core control ritual is a chat checklist that persists one scalar, and the adopted v2 accountant-seat thesis needs close state to be a queryable object. Unlock becomes a bounded `AMENDMENT` process instance (today reopening one month mutates a scalar that unlocks every month after it, with nothing bounding the amendment). Wiki: `process-instance`, `period-locking-month-close`, `safety-nets`. Commit `feat: close ritual + nudges`.

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
**Files:** `tests/fixtures/golden_company/script.yaml` (~200 txns exercising every scenario), `expected/{trial_balance.csv, pnl_accrual.csv, pnl_cash.csv, bs.csv, aging.csv, context.yaml}`
- [ ] Author the fictional solopreneur year and hand-verify the expected files (this is accounting work — budget it as its own sitting; verify TB ties by hand before committing). **`context.yaml` is hand-verified too (2026-07-30 realignment): for a chosen invoice, the exact facts `get_object(ref, lens)` must return per lens AND the exact set it must report as not-recorded / not-applicable. Without it every one of the eight existing layers can pass while the system is unable to explain anything** — they are all write-path or ledger-arithmetic assertions. Commit `test: golden company fixture`.

### Task 9.1b: Golden Company runner
**Files:** `tests/test_golden_company.py`
- [ ] Posts the scripted year through the REAL pipeline vs fake sheets; every month TOTALS 0.00; every expected file matches to the cent. Wired into CI on every PR. Commit `test: golden company runner`.

### Task 9.2: Hardening
- [ ] Rate-limit middleware (auth 30/min IP, MCP 120/min token); request logging with conversation id; Dockerfile (server) + web build; compose prod profile. Commit `chore: hardening + docker`.

### Task 9.3: Skill eval + final skill
- [ ] Paired eval loop: scripted conversations (ambiguous payment → asks; transfer never income; retainer never early income; CSV import flow) against live agent; iterate skill until pass.
- [ ] **Explanation + capture evals (2026-07-30 realignment):** the skill and this gate are entry-shaped throughout, so nothing today would detect that the system cannot answer a "why" question. Add: "why is this invoice still outstanding" routes to the SETTLEMENT lens and states what is not recorded rather than guessing; "why did this recognize then" routes to TREATMENT; **and the capture rule holds — "I got paid $1,400 from Acme" must NOT turn into a five-question interrogation** (free capture mandatory, paid capture opt-in or retroactive). Wiki: `the-skill`, `context-assembly`. Commit `feat: skill v1`.

### Task 9.4: Docs + wiki sync
- [ ] Move `llm-wiki/` into the repo; README quickstart; ingest "as-built" deltas into the wiki (any place implementation diverged from design gets a logged supersession). Commit `docs: v1`.

---

## Deferred by design (do NOT build in v1)

**v1.1 committed fast-follow:** recurring/retainer auto-billing. **v1.5:** Stripe payment links, billable expenses, sendable customer-statement **artifact** (the open-items *report* ships in v1, Task 4.4b), 1099 completions (W-9/TIN, NEC/MISC, corp exemption), mid-year historical backfill. **v2 thesis (adopted):** accountant seat — multi-company role, per-user audit attribution, cross-client console, REST read API. **Later:** Plaid feeds, receipts OCR, time tracking, mileage, quarterly tax estimates, payroll, multi-currency. Pricing must be **announced** at launch (business decision, no billing code).

**From the process-aware object model — decided out, not overlooked (2026-07-30):** ASC-606 performance obligations and revenue schedules; contract / sales-order / subscription objects (the `origin` field is the seam; recurring billing is v1.1); `billing_method`, rate cards and list-price-and-override capture (no pricing engine, so "why is this 15% lower than expected?" is out of scope by construction); multi-party approval routing (there is no second party — a `DecisionRecord`, not a workflow engine); collections and dispute workflows; receipt substantiation and OCR; **and a server-side attention layer — attention is the skill plus the `lens` parameter, never a question classifier in the server ("no LLM inside the server" is load-bearing).** Full reasoning in wiki `v1-scope`.
