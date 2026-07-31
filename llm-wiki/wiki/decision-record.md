---
type: entity
created: 2026-07-30
modified: 2026-07-30
status: draft
sources: [raw/2026-07-30-process-aware-objects.md]
tags: [decisions, audit, provenance, canonical-definition]
---

# Decision Record (one shape for every determination)

> **This page owns the decision vocabulary.** Every determination the system or the user makes — a match, an approval, a categorization, a write-off, a clearing, a lock — is recorded in ONE shape. Where the design previously had this pattern in exactly one place, principle #9 says it is the pattern.

## The pattern already exists — it was just a one-off

[[matching-engine]] already emits `MatchProposal {rule, applications, remainder, alternatives, explanation}` — rule cited, alternatives preserved, human-readable explanation, stored on the draft, surfaced in the approval preview and the audit log. That is a decision record done correctly. Six other determinations produced nothing comparable. Generalizing it costs one shape and deletes six future ad-hoc ones.

## Shape

```
DecisionRecord {
  decision_id
  kind            # DecisionKind enum (below)
  subject_ref     # what it is about: INV-0042 | txn_id | account | CLOSE-2026-07
  process_ref     # nullable -> ProcessInstance
  actor           # ActorKind: HUMAN | AGENT | RULE | SYSTEM  (+ identity)
  rule_id         # the named rule that fired: RULE_EXACT_SINGLE, RULE_TOLERANCE_WRITEOFF, RULE_RETAINER…
  inputs          # what the decision saw
  alternatives[]  # what else was possible and was not chosen  ← the part everyone omits
  chosen
  reason_verbatim # the human's own words, when they gave any; stored, never parsed
  confidence      # exact | high | medium | low | ambiguous  (from the matching cascade)
  evidence[]      # -> [[evidence]]
  policy_version  # -> [[policy-set]], resolved at decision time
  skill_version    # which agent skill produced an AGENT decision
  exception       # nullable ExceptionKind + disposition ([[safety-nets]])
  decided_at      # UTC instant (see time semantics below)
}
```

Every enum value is defined once in `app/domain/enums.py` (principle #7). No decision kind may invent its own actor, reason or timestamp fields.

## v1 decision kinds

`MATCH` (already exists, becomes an instance of this shape) · `APPROVAL` · `REJECTION` · `CATEGORIZATION` (which account the agent chose, and why) · `TOLERANCE_WRITE_OFF` · `DUPLICATE_DISPOSITION` (warned → posted anyway / abandoned) · `UNCATEGORIZED_PARKING` · `CLEARING` (a statement row paired to a GL line) · `LOCK` · `UNLOCK` · `VOID` · `AMENDMENT` · **`PRIOR_RETURN_BASIS`** · **`MIGRATION_COMPLETE`** · **`CUTOFF_DATE_CONFIRMATION`** · **`STATEMENT_ROW_DISPOSITION`** · **`PREPAYMENT_12_MONTH_TEST`** — the first two carry decisions [[onboarding-opening-balances]] already mandates and which previously had no legal `kind` to be written as **(proposed 2026-07-31)**.

## `provenance` — the posting-side projection of a decision

Every **PostingRecord carries a `provenance` sub-document written at COMMIT** ([[posting-pipeline]]):

```
provenance {approval_mode_at_post, approved_by, approval_decision_id, decided_by, rule_id,
            policy_version, skill_version, source: CHAT|CSV_IMPORT|RECURRING|RECONCILIATION}
```

Provenance is **unbackfillable**: what is not captured at COMMIT is gone, so it exists at the first posting ever written or never. That makes it the single most time-sensitive item in this update. Its payoff is that three promised accountant-packet sections stop being stream-replay archaeology and become filters ([[reports-and-analytics]]).

An `APPROVAL` decision additionally carries `preview_hash`, which proves the posted lines are the lines the human saw — defined in [[approval-flow]].

## Time semantics

`decided_at` is a **decision instant**, never an accounting date: it never sets a month file and never faces `locked_through`. The three time categories and the instant→period mapping rule are defined in [[dates-and-timezones]].

## Reads

Decisions are useless if they are write-only. `get_audit_trail` and the decision-path section of `get_object` are defined in [[context-assembly]], over the audit log's `subject_ref` edge ([[safety-nets]]).
