---
type: concept
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-testing-strategy.md]
tags: [testing, ci, fixtures, implementation]
---

# Testing Strategy

> The [[scenario-catalog]] IS the test suite — every accounting claim becomes a cent-exact executable fixture. Eight layers, from property tests to a Golden Company e2e.

1. **Domain invariants** (property tests): every [[document-model]] emitter balances for ANY valid input; polarity never violated; compose pure.
2. **Golden scenario fixtures** — one YAML (`given/when/expect`, exact GL lines + open balances + report deltas) per catalog scenario, incl. transfers asserted NOT touching P&L, cross-month correction, locked-period rejection ([[period-locking-month-close]]).
3. **[[matching-engine]] table tests** — every cascade rule + tolerance boundary ($0.99/$1.00), equal balances → ambiguous (never guess), cited-invoice hint wins.
4. **[[posting-pipeline]] failure injection** (fake Sheets client) — crash between COMMIT/PROJECT → exactly one copy after drain (tail-check proven); no counter reuse; approve-after-lock rejected at re-compose.
5. **[[duckdb-layer]] / reports** — trial balance always ties; BS==cumulative; cash vs accrual differ exactly by unpaid docs; corrupted sheet value → hard parse error (the alarm test).
6. **Golden Company** — scripted solopreneur year (~200 txns, every scenario) through the real pipeline vs fake Sheets: TOTALS 0.00 every month, TB ties, every report cent-exact vs hand-verified file. The gate for every change (FinBoard reconciliation-harness equivalent).
7. **Guards & auth** — `query_books` guard rejections; JWT expiry/audience; tenant isolation ([[auth-wiring]]).
8. **Skill eval** — paired eval loop ([[the-skill]]): ambiguous payment → ask; transfers never income; retainers never early-recognized.

**Spec:** fixtures in `server/tests/fixtures/scenarios/*.yaml`, one parameterized runner. CI: layers 1–5,7 every commit; Golden Company every PR; real-Sheets smoke nightly (test service account).
