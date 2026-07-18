# Matching Engine — approved design (2026-07-17)

Founder-approved internals for payment↔document pairing.

## Core call

The LLM never decides the match — it only extracts facts. Agent produces a structured event
{customer, amount, date, deposit_account, hints: {project?, invoice_numbers?}}. The engine is a
deterministic pure function in app/domain/ — same inputs, same proposal; no LLM inside the server.

Inputs: event + customer's open items (open balances by ref from the ledger — single canonical definition).

## Rule cascade (first hit wins)

1. Invoice cited (hint names INV-xxxx with open balance) — exact
2. Exact single (one open invoice, balance == amount in cents) — exact
3. Exact subset (unique subset sums to amount; DP over cents, fine at ≤20 open invoices; prefer fewest then oldest) — high
4. Partial (amount < oldest open invoice → apply oldest-first) — medium
5. Overpay (amount > total open → apply all + remainder = customer credit) — medium
6. Retainer (no open invoices, project hint → Unearned Revenue path) — medium
7. Unapplied (fallback → customer credit) — low

Ambiguity is a first-class outcome: equal open balances or multiple valid subsets → return ALL candidates
with confidence: ambiguous; agent asks the user rather than guessing. Deterministic tie-breaks (oldest first)
only when one answer is objectively canonical.

## Output

MatchProposal { rule, applications: [{ref, amount}…], remainder: {treatment: credit|retainer, amount},
alternatives, explanation }. Never a posting. Stored on the draft Payment doc, rides approval flow →
posting pipeline. The explanation string appears in the approval preview AND the audit log.

## Tolerance (decision: option b)

Config match_tolerance (default $0.99): if |amount − open| ≤ tolerance, propose full settlement with the
difference auto-lined to Bank Fees (short) / Sales Discounts, clearly shown in the preview. CPA-standard;
avoids penny-crumb open balances. Cent-exact-only rejected.

AP side mirrors everything for bills.
