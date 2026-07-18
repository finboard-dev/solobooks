---
type: concept
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-matching-engine-design.md]
tags: [matching, payments, deterministic, implementation]
---

# Matching Engine (implementation of pairing)

> Deterministic pure function in `app/domain/` implementing [[pairing-and-matching]]. **The LLM only extracts facts** ({customer, amount, date, deposit_account, hints}); the engine decides — same inputs, same proposal, no LLM inside the server.

## Rule cascade (first hit wins)

1. **Invoice cited** — hint names INV-xxxx with open balance → exact
2. **Exact single** — one open invoice, balance == amount (cents) → exact
3. **Exact subset** — unique subset sums to amount (DP over cents; prefer fewest, then oldest) → high
4. **Partial** — apply oldest-first → medium
5. **Overpay** — apply all + remainder = customer credit → medium
6. **Retainer** — no open invoices + project hint → Unearned Revenue path → medium
7. **Unapplied** — fallback customer credit → low

**Ambiguity is a first-class outcome:** equal balances / multiple valid subsets → return ALL candidates (`confidence: ambiguous`); the agent asks the user instead of guessing. Tie-breaks (oldest-first) only when one answer is objectively canonical.

## Hints schema (the LLM↔engine contract)

`record_payment` / `pay_bill` accept a structured `hints` object — the ONLY channel from agent extraction to the engine:
`{ invoice_refs: ["INV-0042"], project: "Website" | null, memo_verbatim: "<user's words>" }`.
Unknown or closed refs → validation error naming the valid open refs (the agent corrects; the engine never guesses). `memo_verbatim` is stored for audit, never parsed by the engine.

## Output

`MatchProposal {rule, applications[], remainder: {treatment, amount}, alternatives, explanation}` — never a posting. Stored on the draft Payment doc → [[approval-flow]] → [[posting-pipeline]]. The `explanation` appears in both the approval preview and the audit log ([[safety-nets]]).

## Tolerance

`match_tolerance` config, default $0.99: within it, propose full settlement with the difference auto-lined to Bank Fees / Sales Discounts, shown in the preview. Avoids penny-crumb open balances; CPA-standard. Cent-exact-only was rejected.

AP side mirrors everything for bills ([[document-model]]).
