# Testing Strategy — approved draft (2026-07-17)

Philosophy: the scenario catalog IS the test suite — every accounting claim becomes an executable
fixture, cent-exact.

## Layers

1. Domain invariants (property tests, hypothesis): every emitter balances (Σd==Σc) for ANY valid
   document of the 9 types; polarity never violated; compose pure (same input → same lines, no mutation).
2. Golden scenario fixtures: one YAML per catalog scenario — given/when/expect (exact GL lines, open
   balances, report deltas, cents). Covers: invoice lifecycle (post/edit/void/pay/partial/overpay),
   retainer→apply, processor fee, NSF reopen, early discount, write-off, AR/AP offset, transfers
   (asserted NOT touching P&L), owner expense/draw, sales receipt, credit/vendor notes, opening JE with
   OBE plug, cross-month correction, locked-period posting rejected.
3. Matching engine table tests: one per cascade rule + tolerance boundary ($0.99 in / $1.00 out),
   equal balances → ambiguous (never guess), multiple subsets → ambiguous, cited-invoice hint wins.
4. Posting pipeline failure injection (fake Sheets client): kill between COMMIT and PROJECT → drain on
   restart, exactly one copy (tail-check proven); ambiguous append error → no double-post; counters
   never reuse; draft approved after period lock → rejected at re-compose.
5. DuckDB/reports on fixture ledgers: trial balance always ties; BS(as-of)==cumulative; cash vs accrual
   differ exactly by unpaid docs; aging buckets; v_pnl_cash proportional recognition; corrupted sheet
   value → HARD parse error (the alarm test).
6. Golden Company (flagship e2e): scripted fictional solopreneur year (~200 txns, every scenario) →
   real pipeline vs fake Sheets → TOTALS 0.00 every month, TB ties, every report cent-exact vs
   hand-verified expected file. Equivalent of FinBoard's reconciliation harness; the gate for every change.
7. Guards & auth: query_books rejects non-SELECT/DDL/multi-statement/over-cap; JWT expired/wrong
   audience; tenant isolation (user A never touches company B).
8. Skill eval (paired eval loop, Art of Writing Skills methodology): scripted conversations — ambiguous
   payment → agent asks; transfer never booked income; retainer never recognized early.

## Spec

- Fixtures: server/tests/fixtures/scenarios/*.yaml (given/when/expect); one parameterized runner.
- CI: layers 1–5,7 every commit; Golden Company every PR; real-Sheets smoke (test service account) nightly.
