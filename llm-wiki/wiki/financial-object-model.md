---
type: concept
created: 2026-07-30
modified: 2026-07-30
status: draft
sources: [raw/2026-07-30-process-aware-objects.md]
tags: [architecture, objects, context, canonical-definition]
---

# Financial Object Model (process-aware objects)

> **SoloBooks does not retrieve records. It reconstructs financial context.** A financial object's *effect* is fixed by the ledger; its *meaning* depends on the process it was in, the policy in force, the evidence behind it, and the question being asked. This page is the root of that model — [[process-instance]], [[decision-record]], [[evidence]], [[policy-set]] and [[context-assembly]] each own one piece of it.

## The correction this page makes

The design previously carried a binary: **ledger = truth, Mongo = cache** ([[three-store-architecture]]). That is right about money and wrong about meaning. Sharpened:

| Domain | Store | Rule |
|---|---|---|
| **Effect** — what money did | GL sheets ([[general-ledger-sheet]]) | Canonical, append-only. Every monetary and settlement fact traces here (FinBoard principle #9). On any *monetary* disagreement, the ledger wins. |
| **Context** — why it did | Mongo | Canonical, append-only, **never a cache**. Origin, decisions, evidence, policy-in-force, process participation, exceptions. The ledger has nothing to say about it, so it can never be "corrected" by the ledger. |

Mongo still caches *derived* ledger facts (invoice paid/unpaid) for listing speed, and there the ledger still wins ([[document-model]]). The narrow claim "Mongo is a cache" applied to context is what this page supersedes.

## The eleven buckets, mapped

The founder source lists eleven buckets an object should carry. Honest status for a one-person cash-basis product:

| Bucket | SoloBooks v1 | Where |
|---|---|---|
| Core attributes | **ships** | Mongo document ([[document-model]]) |
| Commercial context | **seam only** — `origin {type, ref}` nullable on every document; `service_period {start,end}` on invoice lines | [[document-model]], [[invoice-artifact]] |
| Accounting context | **ships** — basis, recognition rule, tax treatment, all resolved as-of | [[cash-basis-recognition]], [[policy-set]] |
| Relationships | **ships** — `ref` (settlement, the universal rule) + `origin` (causation) are two different edges, deliberately | [[pairing-and-matching]] |
| Evidence | **link seam ships**, no capture UI | [[evidence]] |
| Current state | **ships** — derived, never stored ([[point-in-time-balances]]) | [[document-model]] |
| Derived facts | **ships** — the design's strongest area; one ledger-grain definition each | [[reports-and-analytics]] |
| Workflow references | **ships** — `process_refs[]` | [[process-instance]] |
| Policy references | **ships** — `policy_version` stamped at post | [[policy-set]] |
| Exceptions | **ships** — named `ExceptionKind` vocabulary + disposition | [[safety-nets]] |
| Audit history | **ships** — audit entries gain a `subject_ref` edge so a trail is *queryable*, not just chronological | [[context-assembly]] |

The buckets this model deliberately does **not** build — revenue schedules, contract/order objects, pricing capture, approval routing, collections — are enumerated with their reasons in [[v1-scope]], recorded so a future reader can tell a decision from a gap.

## Two consequences that bind the rest of the wiki

- `ref` (settlement) and `origin` (causation) are **two different edges** and must never be conflated; the distinction is defined in [[pairing-and-matching]]. `origin` is a Mongo field, never a GL column — the column-admission rule in [[general-ledger-sheet]] decides that class of question.
- Every context field above is filled under the capture rule in [[the-skill]] — free capture mandatory, paid capture opt-in — and a null renders as "not recorded", never as a fact ([[context-assembly]]).
