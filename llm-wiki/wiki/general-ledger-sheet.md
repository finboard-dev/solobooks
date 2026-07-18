---
type: entity
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
tags: [gl, sheets, append-only]
---

# General Ledger Sheet

> One spreadsheet per month (`<Company>/<Year>/<MM-Month>/General Ledger`), one row per journal line, **append-only forever**. Written only by our service account through the [[sheets-layer]] ([[three-store-architecture]]).

## Columns

`txn_id`, `date`, `type` (document type or Reversal — [[document-model]]), `ref`, `account_number`/`account_name`, `debit`/`credit`, `customer`/`project`/`vendor`/`class`/`location` ([[dimensions]]), `due_date` (**only on AR/AP lines of invoice/bill postings** — makes aging computable from the sheet alone), `memo`, `posted_at`/`posted_by`.

- Sorted by date then txn_id; protected `TOTALS` row on top (debits, credits, difference — always 0.00, human-glanceable balance proof).
- Names not ids (sheets are for humans); deliberately denormalized — DuckDB loads 1:1, joins only [[chart-of-accounts]].
- No running-balance column (the `account_ledger` report provides it — [[reports-and-analytics]]).

## Append-only rules (integrity crux)

1. Rows are **never edited or deleted** — mistakes are corrected by new entries.
2. Edit a posted document → append **reversal** of original lines + **repost** of new version (same ref, versioned in Mongo). The GL shows the full story.
3. Void → reversal only.
4. **Cross-month corrections land in the current open month** — a locked month's sheet is physically immutable forever ([[period-locking-month-close]]).
5. **Failure safety:** Mongo commits first; GL lines go through a pending outbox with retry and txn_id tail-check dedupe — a tool call never half-posts. Full write path: [[posting-pipeline]].

Trade accepted: corrections are visible forever (reversal noise) instead of silently re-rendered clean sheets. Accountants prefer this. Exception: a month re-opened via unlock re-renders on re-lock.
