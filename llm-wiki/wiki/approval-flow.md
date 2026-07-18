---
type: concept
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
tags: [approval, hitl, audit]
---

# Approval Flow

> Mechanism: **draft → preview of exact GL lines → approve**. Not MCP elicitation (spotty client support, not durable, not separately auditable).

1. Posting tools create the document as `draft` in Mongo and return a preview of the exact journal lines it will post (DR/CR, accounts, dimensions).
2. User approves in chat → `approve_document(id)` → the full [[posting-pipeline]] runs (compose re-validates at approval time) → lines append to [[general-ledger-sheet]] → audit records who/when/which conversation.
3. `reject_draft`, `list_drafts` (drafts are durable across conversations), `approve_all_drafts` for batches ("yes, post all 5 bills").

## Policy — `approval_mode` on [[company-object]]

- `all` — every posting needs approval. **Default at onboarding** (builds trust).
- `none` — agent posts directly; still fully audited and reversible (append-only reversals, [[general-ledger-sheet]]).
- Threshold/per-type middle modes deferred ([[v1-scope]]).

**Always require approval regardless of mode:** voiding a posted document, editing a posted document (reversal + repost), unlocking a period ([[period-locking-month-close]]).

Matching proposals from [[pairing-and-matching]] ride this same flow — the system proposes the pairing, the human confirms it.
