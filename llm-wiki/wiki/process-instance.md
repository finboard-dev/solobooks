---
type: entity
created: 2026-07-30
modified: 2026-07-30
status: draft
sources: [raw/2026-07-30-process-aware-objects.md]
tags: [workflow, process, mongo, canonical-definition]
---

# Process Instance (the one workflow object)

> One generic, domain-blind object for "a multi-step process with inputs, steps, decisions, exceptions and outputs". An object **participates in** processes; processes are never embedded in the object. Replaces four ad-hoc representations of the same idea.

## Why it exists

The design had four different shapes for one concept — a Mongo "Rec object" ([[bank-reconciliation]]), a draft queue with no batch identity ([[platform]]), a chat checklist that persisted only `locked_through` ([[period-locking-month-close]]), and an onboarding sequence with no artifact ([[onboarding-opening-balances]]). Four representations of one concept is exactly what FinBoard principles #7 and #9 forbid. The month close was the worst case: the profession's core control ritual left **no durable artifact at all**, and the adopted v2 accountant-seat thesis ([[v1-scope]]) depends on close state being a queryable object.

## Shape

```
ProcessInstance {
  process_id      # counter-minted, gap-audited, human-quotable: CLOSE-2026-07, IMPORT-0042, REC-2026-07-CHECKING
  type            # ProcessType enum
  trigger         # TriggerKind enum: USER_CHAT | SCHEDULE | IMPORT | CLOSE | SYSTEM
  participants[]  # actor refs — always [the one user] in v1; non-null seam for the v2 accountant seat
  state           # ProcessState enum: OPEN | COMPLETED | ABANDONED
  steps[]         # {key, state, at, decisions[] -> decision_id, exceptions[] -> ExceptionKind + disposition}
  inputs          # e.g. {source_file_ref, statement_period, account}
  outputs         # e.g. {posting_txn_ids[], artifact_refs[]}
  idempotency_key # re-running the same input must not mint a second instance
  opened_at / closed_at
}
```

**Domain-blind (principle #1).** The object knows nothing about accounting. Process *types* are config; a new process is a new type entry, never a new table or a new code path.

**Ids are minted, not opaque.** Anything a human or an accountant will quote gets a counter-minted, never-reused, gap-audited id, exactly as documents do ([[document-model]]) — `CLOSE-2026-07`, not a UUID.

**Idempotency.** Re-uploading the same bank statement must not mint a second ImportRun; the natural key is the source file ref. Re-running a close for a month that already has a completed CloseRun resumes it rather than duplicating it.

## v1 types

| Type | Replaces | Outputs |
|---|---|---|
| `IMPORT_RUN` | the anonymous CSV draft queue | drafts created, rows rejected, dedupe hits ([[matching-engine]]) |
| `REC_RUN` | the ad-hoc "Rec object" | cleared pairings, outstanding items, discrepancy amount ([[bank-reconciliation]]) |
| `CLOSE_RUN` | a chat checklist with no artifact | the four close steps with per-step state, the exceptions resolved or acknowledged, the lock decision ([[period-locking-month-close]]) |
| `AMENDMENT` | an unbounded `locked_through` rollback | the unlock scope, what changed, the re-lock ([[period-locking-month-close]]) |
| `ONBOARDING` | an untracked sequence | opening JE, historical open documents, the `books_state` flip ([[onboarding-opening-balances]]) |

Import and reconciliation are described in the design as "the same loop" — as process instances they finally *are* one, with two type entries over one object.

## What is deliberately NOT a process instance

**Approval is not a workflow.** The founder source models approval as multi-party routing (controller requests a document, sales uploads it, controller approves). SoloBooks has one actor who is simultaneously the salesperson, the approver and the bookkeeper. An approval here needs a **[[decision-record]]** — who decided, under which rule, why, against what alternatives, on what evidence — not a routing engine. Building step-routing for a single actor would be pure ceremony. This refusal is recorded in [[v1-scope]].

**Posting is not a process instance.** The [[posting-pipeline]] is a five-step *function* (COMPOSE→RESERVE→COMMIT→PROJECT→FINALIZE) with a durable PostingRecord already. It is not a human-time process and gains nothing from a second wrapper.

Process instances live in Mongo only; their close-time export into the Drive folder is governed by the two-tier self-sufficiency rule in [[three-store-architecture]].
