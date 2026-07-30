---
type: entity
created: 2026-07-30
modified: 2026-07-30
status: draft
sources: [raw/2026-07-30-process-aware-objects.md]
tags: [evidence, audit, drive, seam]
---

# Evidence (a link, not a store)

> "Retrieve connected evidence" had no target: `attachments/` was a **Drive folder naming convention** with no field on any document, decision or process, and no tool. v1 ships the *link* and nothing else.

## The narrow v1 decision

Receipt capture, OCR and substantiation are out of v1 and stay out — that cut was made three times independently ([[v1-scope]], [[professional-review-findings]]) and the CPA persona accepted it. What was never decided is that evidence should be **unlinkable**, and that is the part this page fixes. The cost is one nullable array and one tool; the cost of adding it after documents, decisions and process instances are frozen is a migration across all three.

```
EvidenceRef {
  kind          # EvidenceKind: DRIVE_FILE | STATEMENT_ROW | CONVERSATION | IMPORT_ROW | ARTIFACT
  ref           # drive_file_id | {rec_id, row_no} | conversation_id | {import_id, row_no} | artifact link
  label
  added_by / added_at
}
```

`evidence[]` is a nullable field on documents ([[document-model]]), decisions ([[decision-record]]) and process steps ([[process-instance]]). One tool, `attach_evidence(subject_ref, evidence)`, plus `evidence[]` surfacing in the `EVIDENCE` lens of `get_object` ([[context-assembly]]).

## Rules

- **Never a store.** SoloBooks does not host, copy or parse evidence. A `DRIVE_FILE` is a pointer into the company's own Drive folder ([[three-store-architecture]]); the bytes are the user's, exactly like the ledger.
- **Never blocks a posting.** Missing evidence is at most an `ExceptionKind` surfaced by `verify_books` ([[safety-nets]]) — never a validation error. This follows the existing forgiveness doctrine: nothing is blocked on classification, and nothing is blocked on paperwork either.
- **Tenant-scoped, validated.** A `DRIVE_FILE` ref must resolve inside *this company's* folder registry. An arbitrary Drive id is rejected: unvalidated it could point at another tenant's folder, or at a file the service account can read and the user cannot. It is a caller-supplied id, so the sharpened tenant rule in [[mcp-tool-surface]] applies.
- **Append-only.** Evidence is detached by superseding, never deleted — consistent with [[general-ledger-sheet]] and the artifact-permanence rule in [[period-locking-month-close]].
- **Free capture only.** The agent never interrogates the user for evidence; it links what the user volunteers or references ([[the-skill]]).

## What this unlocks later

The v1.5/v2 items that need evidence — 1099 W-9/TIN capture, receipt substantiation, the accountant seat's review console ([[v1-scope]]) — become additive because the link exists. Statement rows already produced by [[bank-reconciliation]] and import rows from [[matching-engine]] are evidence on day one at zero capture cost: the system already has them.
