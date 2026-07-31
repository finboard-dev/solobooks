---
type: entity
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
tags: [gl, sheets, append-only]
---

# General Ledger Sheet

> One spreadsheet per month (`<Company>/<Year>/<MM-Month>/General Ledger`), one row per journal line, **append-only forever**. Written only by our service account through the [[sheets-layer]] ([[three-store-architecture]]).

## Columns

`txn_id`, `date`, `type` (document type or Reversal — [[document-model]]), `reverses_txn_id` (**proposed 2026-07-30** — Reversal lines only, blank elsewhere), `ref`, `account_number`/`account_name`, `debit`/`credit`, `customer`/`project`/`vendor`/`class`/`location` ([[dimensions]]), `due_date` (**only on AR/AP lines of invoice/bill postings** — makes aging computable from the sheet alone), `line_reason` (**proposed 2026-07-30** — machine-set `LineReason` enum), `memo`, `posted_at`/`posted_by`.

- Sorted by date then txn_id; protected `TOTALS` row on top (debits, credits, difference — always 0.00, human-glanceable balance proof).
- Names not ids (sheets are for humans); deliberately denormalized — DuckDB loads 1:1, joins only [[chart-of-accounts]].
- No running-balance column (the `account_ledger` report provides it — [[reports-and-analytics]]).
- The set is an **ordered enum** (`GLColumn`, principle #7) and a locked month's sheet is immutable forever — admitting a column is effectively irreversible. **(proposed 2026-07-30)**

## The column-admission rule (proposed 2026-07-30)

> A field earns a GL column **if and only if** a competent human reading the Drive folder with no software running cannot correctly interpret the ledger without it. Everything else is Mongo provenance ([[financial-object-model]]).

Applied once, here, publicly: six separate findings each proposed columns, and nine columns each justified on their own page would destroy the human-legible ledger the buyer panel actually liked ([[buyer-panel-findings]]).

| Field | Verdict | Why |
|---|---|---|
| `reverses_txn_id` | **ADMIT** (proposed 2026-07-30) | Repeated reversal/repost cycles on one `ref` are genuinely ambiguous on paper — same ref, same accounts, mirrored amounts, and nothing saying which repost a given reversal undid. Rule 2's claim "the GL shows the full story" is **not true today**; this column is what makes it true. |
| `line_reason` | **ADMIT** (proposed 2026-07-30) | A DR $0.40 to Sales Discounts written by the `$0.99` tolerance rule ([[matching-engine]]) is otherwise indistinguishable from a discount the user granted. Machine-set `LineReason` enum (`TOLERANCE_WRITE_OFF`, `ROUNDING`, `OPENING_BALANCE`, `NSF_REVERSAL`, **`COST_RECOVERY`**, **`OFFSET_SETTLEMENT`**, **`PREPAID_12_MONTH`**, **`PRINCIPAL_WRITE_OFF`** — the last is R5a's intent predicate, without which an account+ref pattern fabricates receipts out of a month-end JE; the set freezes at the first posting — a member missing on this page after go-live is unfixable except by AMENDMENT over every affected document). **Reversal lines inherit the reversed line's `line_reason` unchanged; reversal-ness is carried by `type = Reversal` + `reverses_txn_id`, never by `line_reason` (proposed 2026-08-01)** — otherwise voiding a recognized prepayment leaves its deduction standing forever **(proposed 2026-07-31)** — **distinct from `memo`**, which is user prose and stays user prose. No FX value: multi-currency is out of v1 ([[v1-scope]]). |
| `origin_type` / `origin_ref` | **REJECT** (proposed 2026-07-30) | Causation is a Mongo edge ([[financial-object-model]]); which schedule or import run minted an entry changes nothing about how a human reads it. |
| `cleared` | **REJECT** (proposed 2026-07-30) | Rec state is an appended row on the `Reconciliations` sheet ([[sheets-layer]], [[bank-reconciliation]]). A `cleared` column would require mutating a posted row — rule 1 forbids it. |
| every other id (`decision_id`, `process_id`, `policy_version`, `evidence_ref`) | **REJECT** (proposed 2026-07-30) | Names not ids. All reachable via `get_object` ([[context-assembly]]). |

## Append-only rules (integrity crux)

1. Rows are **never edited or deleted** — mistakes are corrected by new entries.
2. Edit a posted document → append **reversal** of original lines + **repost** of new version (same ref, versioned in Mongo). The GL shows the full story.
3. Void → reversal only.
4. **Cross-month corrections land in the current open month** — a locked month's sheet is physically immutable forever ([[period-locking-month-close]]).
5. **Failure safety:** Mongo commits first; GL lines go through a pending outbox with retry and txn_id tail-check dedupe — a tool call never half-posts. Full write path: [[posting-pipeline]].

Trade accepted: corrections are visible forever (reversal noise) instead of silently re-rendered clean sheets. Accountants prefer this. Exception: a month re-opened via unlock re-renders on re-lock.
