---
type: concept
created: 2026-07-17
modified: 2026-07-31
status: verified
sources: [raw/2026-07-17-testing-strategy.md, raw/2026-07-30-process-aware-objects.md, raw/2026-07-30-tri-persona-review.md]
tags: [testing, ci, fixtures, implementation]
---

# Testing Strategy

> The [[scenario-catalog]] IS the test suite — every accounting claim becomes a cent-exact executable fixture. Eight layers, from property tests to a Golden Company e2e — plus a ninth that asserts the system can *explain* what it posted **(proposed 2026-07-30)**.

1. **Domain invariants** (property tests): every [[document-model]] emitter balances for ANY valid input; polarity never violated; compose pure.
2. **Golden scenario fixtures** — one YAML (`given/when/expect`, exact GL lines + open balances + report deltas) per catalog scenario, incl. transfers asserted NOT touching P&L, cross-month correction, locked-period rejection ([[period-locking-month-close]]).
3. **[[matching-engine]] table tests** — every cascade rule + tolerance boundary ($0.99/$1.00), equal balances → ambiguous (never guess), cited-invoice hint wins.
4. **[[posting-pipeline]] failure injection** (fake Sheets client) — crash between COMMIT/PROJECT → exactly one copy after drain (tail-check proven); no counter reuse; approve-after-lock rejected at re-compose.
5. **[[duckdb-layer]] / reports** — trial balance always ties; BS==cumulative; On any fixture ledger the accrual-vs-cash delta must reconcile **line by line to an enumerated set that is a PARTITION of R1–R12 (proposed 2026-08-01)** — unpaid documents (R4), retainers recognized at receipt (R6), non-cash settlements such as a bad-debt write-off (R5), **prepaid timing (R12), which must be signed and self-reversing: Σ of a prepayment's attributions over its life = 0.00, or a permanent disallowance is wearing a timing label**, and **disposal gain/loss (Form 4797 — in `v_pnl`, never in `v_pnl_cash`)** — **with an unattributed cent failing the gate, and every rule that cannot produce a delta named as contributing exactly 0.00 (R11 cost recovery, R8 transfers, R2 equity).** Every rule that can produce a delta appears here by name. Both earlier wordings were wrong: "unpaid/non-cash items" licensed the R11 cost-recovery bug; "unpaid documents only" failed a correct ledger by the retainer and the write-off.; corrupted sheet value → hard parse error (the alarm test).
6. **Golden Company** — scripted solopreneur year (~200 txns, every scenario) through the real pipeline vs fake Sheets: TOTALS 0.00 every month, TB ties, every report cent-exact vs hand-verified file. The gate for every change (FinBoard reconciliation-harness equivalent). Gains one **hand-verified expected context file** alongside the hand-verified ledger CSVs: for a named set of refs, the exact facts `get_object` must return per lens and the exact set it must report as unknown. **(proposed 2026-07-30)**
7. **Guards & auth** — `query_books` guard rejections; JWT expiry/audience; tenant isolation ([[auth-wiring]]).
8. **Skill eval** — paired eval loop ([[the-skill]]): ambiguous payment → ask; transfers never income; retainers never early-recognized. Adds: never interrogates for a paid-capture field at entry; renders a null as "not recorded", never as a fact. **(proposed 2026-07-30)**
9. **Explanation** — given a fixture ledger, `get_object(ref, lens)` returns exactly this set of facts **and explicitly enumerates what is unknown** ([[context-assembly]]). Layers 1–8 are write-path or ledger-arithmetic assertions: all eight can pass while the system is unable to explain anything. Asserted value-exact, same doctrine — a section dropped by the section renderer must be named, and a `not recorded` must never read as a fact. **(proposed 2026-07-30)**

## The `expect` block — six added slots (proposed 2026-08-01: `recognized` and `balances` complete it)

`gl_lines`, `open_balance`, `report_deltas` are all money. No fixture can therefore express a provenance, decision, exception or policy fact — meaning every change in the 2026-07-30 update ships with **zero deterministic coverage**. Six blocks are added, asserted in the same cent-exact/set-exact style. This lands **before** the 25-plus scenario YAMLs are written against the schema; afterwards it is a 25-file rewrite. **(proposed 2026-07-30)**

| Block | Asserts | Definition owner |
|---|---|---|
| `provenance` | the PostingRecord sub-document written at COMMIT — `approval_mode_at_post`, `approved_by`, `rule_id`, `policy_version`, `skill_version`, `source`; plus `preview_hash` equality across approve→post, and `PREVIEW_DRIFT` raised when the lines moved | [[decision-record]] **(proposed 2026-07-30)** |
| `decision` | `kind`, `rule_id`, `chosen`, `confidence`, and `alternatives[]` as an exact set — the omitted-everywhere field is the one most worth asserting | [[decision-record]] **(proposed 2026-07-30)** |
| `exceptions` | the `ExceptionKind` set raised and each disposition; an expected-clean fixture asserts the set is explicitly empty, never absent | [[safety-nets]] **(proposed 2026-07-30)** |
| `policy_header` | the header on the report's face — basis, policy version, ruleset versions, period, `books_state`; and that a policy mutation restates nothing already stamped | [[policy-set]] **(proposed 2026-07-30)** |
| `recognized` | `{period, cash:{account:amount}, accrual:{account:amount}, attribution}` — **the slot 12 of the 13 ruleset fixtures need and none had**. Without it `prepaid_12_month`'s "never both, never neither", `bundled_yearend_je`'s "$500 not $1,700" and `depreciation_and_179`'s "both bases" cannot be asserted at all. Evaluated in **Phase 1** by the same helper pattern as `open_balance`, not deferred to Phase 4 | [[cash-basis-recognition]] **(proposed 2026-08-01)** |
| `balances` | `{account: amount}` — an **account balance**, not a document's own lines. `prior_return_cash_capitalized_bill` passes whether Machinery ends at $12,000, $24,000 or $0 if it asserts only `gl_lines`, because the bill's lines are identical in all three | [[onboarding-opening-balances]] **(proposed 2026-08-01)** |

**Spec:** fixtures in `server/tests/fixtures/scenarios/*.yaml`, one parameterized runner. CI: layers 1–5,7,9 every commit **(proposed 2026-07-30)**; Golden Company every PR; real-Sheets smoke nightly (test service account).
