---
type: entity
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
tags: [documents, journal, accounting]
---

# Document Model — 9 Types, One Pattern

> Everything financial is a thin Mongo document that validates and **emits a GL line pattern**. The ledger is the truth; documents are wrappers. Lifecycle: `draft` → (approval) → `posted` → optionally `voided` (via reversal).

| Document | GL pattern (happy path) |
|---|---|
| **Invoice** | DR AR / CR Sales (+ CR Sales Tax Payable if taxed — [[compliance]]) |
| **Payment** | DR money account / CR AR — one CR **per applied invoice**, each with `ref` ([[pairing-and-matching]]) |
| **Bill** | DR Expense (or asset) / CR AP |
| **BillPayment** | DR AP (per applied bill, `ref`) / CR money account |
| **SalesReceipt** | DR money account / CR Sales — cash sale, skips AR |
| **CreditNote** | DR Sales / CR AR `ref` |
| **VendorCredit** | DR AP `ref` / CR Expense |
| **Transfer** | DR account / CR account — **never touches P&L** (Checking→Savings, credit-card payoff) |
| **JournalEntry** | **N lines, must balance** — escape hatch (opening balances, depreciation, owner-paid expenses, offsets) |

Rules:

- **Status is derived, never stored as truth** — an invoice is "paid" because ref'd AR credits sum to its debits ([[pairing-and-matching]]). Mongo may cache for listing speed; ledger wins on disagreement.
- **Numbering:** Mongo atomic counters per company per type (INV-0042, BILL-0017, PAY-0117, JE-2026-000187). Never reused; gaps audited.
- New document type = new emitter config, not new tables (extension without modification).
- Posting writes append-only lines to the [[general-ledger-sheet]]; edits/voids are reversal + repost.
- All postings flow through [[approval-flow]].
