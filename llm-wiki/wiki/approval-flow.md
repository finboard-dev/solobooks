---
type: concept
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
tags: [approval, hitl, audit]
---

# Approval Flow

> Mechanism: **draft → preview of exact GL lines → approve**. Not MCP elicitation (spotty client support, not durable, not separately auditable).

1. Posting tools create the document as `draft` in Mongo and return a preview of the exact journal lines it will post (DR/CR, accounts, dimensions).
2. User approves in chat → `approve_document(id)` → the full [[posting-pipeline]] runs (compose re-validates at approval time) → lines append to [[general-ledger-sheet]] → audit records who/when/which conversation.
3. `reject_draft`, `list_drafts` (drafts are durable across conversations), `approve_all_drafts` for batches ("yes, post all 5 bills").

## An approval is a decision, not a status transition

- Approving emits an `APPROVAL` [[decision-record]] — approver, `rule_id`, `reason_verbatim` (the user's own words, stored never parsed), `evidence[]`, `exception`, `decided_at`, `alternatives[]` (what else was offered and not taken). `reject_draft` emits `REJECTION` the same way. Status stays derived ([[document-model]]); the decision is the durable fact. **(proposed 2026-07-30)**
- **Not a workflow engine.** Multi-party routing is refused for a single-actor product; the refusal and its reasoning live in [[process-instance]]. **(proposed 2026-07-30)**

## `preview_hash` — proving what the human consented to (this page owns it)

Step 2 re-validates at approval time and posts whatever compose produces **then**. If a tax rate, the COA or a duplicate moved in between, the user consented to one set of lines and the ledger recorded another, with nothing to prove which. **(proposed 2026-07-30)**

- The APPROVAL decision stores `preview_hash` — a hash of the exact DR/CR lines shown in step 1. **(proposed 2026-07-30)**
- At COMMIT a mismatch is never a silent overwrite: it raises `PREVIEW_DRIFT` and **re-presents** the new preview for a fresh approval ([[posting-pipeline]]). **(proposed 2026-07-30)**
- `approval_mode_at_post` is stamped into the PostingRecord `provenance` ([[decision-record]]), which is what makes the packet's per-period auto-posted disclosure a filter ([[reports-and-analytics]]). **(proposed 2026-07-30)**

## Policy — `approval_mode` on [[company-object]]

- `all` — every posting needs approval. **Default at onboarding** (builds trust).
- `none` — agent posts directly; still fully audited and reversible (append-only reversals, [[general-ledger-sheet]]).
- Threshold/per-type middle modes deferred ([[v1-scope]]).
- The mode in force is **resolved as-of from the versioned [[policy-set]]**, never read as a mutable scalar — the packet discloses the mode that applied *then*, not today's. **(proposed 2026-07-30)**

**Always require approval regardless of mode:** voiding a posted document, editing a posted document (reversal + repost), unlocking a period ([[period-locking-month-close]]).

Matching proposals from [[pairing-and-matching]] ride this same flow — the system proposes the pairing, the human confirms it.
