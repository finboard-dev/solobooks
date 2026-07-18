---
type: synthesis
created: 2026-07-18
modified: 2026-07-18
status: verified
sources: [raw/2026-07-18-cpa-firm-review.md, raw/2026-07-18-cas-firm-review.md]
tags: [research, cpa, advisors, validation, scope]
---

# Professional Review Findings (CPA firm + CAS firm)

> Two in-depth persona reviews: Dan (tax/CAS partner, receives the books in January) and Priya (CAS founder, would operate or refer). Verdicts: engine praised — "more disciplined than most QBO files I inherit" / "cleanest DIY books I've ever received, I'd rather inherit this than QBSE or Wave" — but reliance gated on specific fixes. Full verbatims in the raw files.

## Fixed 2026-07-18 (bucket 1 — correctness, no scope change)

- [[cash-basis-recognition]] rewritten to rules R1–R9 (v1 page had: internal contradiction on owner-paid expenses, Owner's Draw in the P&L, no asset-leg carve-out, no fee-leg rule).
- [[onboarding-opening-balances]] double-count rule: opening JE never carries AR/AP; historical docs offset OBE not Sales; pre-migration invoices recognize nothing on cash basis.
- [[compliance]] 1099 method exclusion: card/processor payments out of 1099-NEC; `method` is accounting-relevant ([[pairing-and-matching]]).
- [[period-locking-month-close]] artifact permanence: pre-unlock renderings archived, re-render diff audited.

## Convergent findings (both reviewers, independently)

1. **Statement-based bank reconciliation is the trust floor** — the balance-check ritual passes offsetting errors and invites plugs. Dan: the single biggest gap to reliance. Priya: caps everything downstream. Third independent confirmation of the panel's advisor objection ([[buyer-panel-findings]]).
2. **Chat is a poor batch interface** — 60 CSV drafts in chat previews → `approve_all_drafts` theater. Priya: bend the no-ledger-UI rule for ONE batch review grid.
3. **The accountant channel keeps scoring highest** — Priya: "your buyer panel already told you who scored highest — it wasn't the solopreneurs, it was people like me." But firm operation is architecturally absent (no accountant seat, no multi-client view, no close tracking).

## Scope calls — DECIDED 2026-07-18 (raw/2026-07-18-scope-calls.md)

- **v1:** statement-based [[bank-reconciliation]]; batch review grid ([[platform]] exception); expanded accountant packet ([[reports-and-analytics]]: tax_line grouping, bridge, open items, masters, categorization review, approval disclosure, write-offs, asset additions); seed COA loans + Reconciliation Discrepancies + principal/interest skill rule ([[chart-of-accounts]]); verify_books additions ([[safety-nets]]).
- **v1.1 committed fast-follow:** recurring/retainer auto-billing.
- **v1.5:** 1099 completions (W-9/TIN, NEC/MISC, corp exemption); mid-year historical backfill.
- **v2 thesis adopted:** accountant seat (multi-company role, per-user attribution, cross-client console, REST read API) — timing after Phase-6 dogfooding. All reflected in [[v1-scope]] and the implementation plan.
