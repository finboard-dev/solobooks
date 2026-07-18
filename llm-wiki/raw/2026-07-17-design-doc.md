# SoloBooks (working name) — Lightweight Accounting for Solopreneurs

**Status:** Draft for review — product/flow design only, no implementation decisions locked.
**Date:** 2026-07-17
**Repo model:** Single new repo (separate from FinBoard monorepo), containing FastAPI + MCP server, Next.js frontend, and the agent skill.

---

## 1. Product Vision

A headless accounting system for solopreneurs where:

- **The books physically live in Google Sheets** — human-readable, shareable with an accountant, exportable by construction.
- **The brain is an MCP server** — all bookkeeping happens conversationally through Claude (or any MCP client). The MCP tools ARE the API.
- **The web UI is minimal** — login, connect-your-agent, and a view of the Drive folder. It never renders a ledger.

**The pitch:** "Your books are yours — plain spreadsheets you can open, share, and keep forever. We add the discipline (double-entry, numbering, audit trail, approvals) and the intelligence (chat-driven bookkeeping and analytics)."

**Target user:** one-person businesses — freelancers, consultants, creators. US-first (1099s, sales tax as flat rate, cash-basis tax filing).

### Non-negotiable principles (inherited from FinBoard CLAUDE.md)

1. Core infrastructure knows nothing about accounting; domain logic lives in tools + the skill.
2. Pure functions, composable steps, inspectable input→output.
3. Reason from accounting first: debits = credits, polarity, flow vs point-in-time.
4. Extension without modification (new document type = new config/emitter, not new tables).
5. Every step queryable; every mutation auditable (who/what/when/which conversation).
6. No magic strings — enums defined once.
7. **One concept, one implementation** — every derived value (open balance, net income, aging) traces to a single ledger-grain definition.

---

## 2. Architecture Overview — Three Stores, One Truth Chain

| Store | Role | Holds |
|---|---|---|
| **MongoDB** | Operational truth | Company object, customers, vendors (projects under customers), documents (invoices, bills, payments…), drafts, ID sequence counters, audit log, users/sessions (Better Auth) |
| **Google Sheets** | The translated ledger (the "books") | Monthly General Ledger sheets + Chart of Accounts sheet. Written ONLY by our service account. Shared **view-only** with the user |
| **DuckDB** | Stateless calculator | Nothing persistent. Loads GL + COA sheets on demand per company, runs report SQL, dies. Rebuildable in milliseconds |

**Truth chain:** Documents are created/edited in Mongo → on approval, translated into journal lines appended to the monthly GL sheet → DuckDB reads the sheets for all reports and queries.

- Sheets are a **projection** of Mongo events, but the GL sheet is the canonical *ledger*: if a cached value in Mongo (e.g., invoice status) ever disagrees with the ledger, the ledger wins.
- The user cannot edit sheets (view-only share from our service account) → no drift detection needed; integrity is enforced by construction.
- Freshness is trivial: we are the only writer. Mongo tracks a `ledger_version` per company, bumped on every posting; the DuckDB cache is valid until it changes.

### Drive folder structure (owned by service account, shared view-only)

```
<Company Name>/
  Chart of Accounts          (sheet — rendered from Mongo COA)
  2026/
    07-July/
      General Ledger         (sheet — one row per journal line)
      attachments/           (folder convention from day one; receipts live here later)
    08-August/
      General Ledger
      ...
  invoices/                  (generated invoice Docs/PDFs — see §13)
```

**Self-sufficiency rule:** the folder must contain everything needed to read the books without our system. That is the exportability promise, and it drives sheet schema decisions (e.g., `due_date` on AR/AP lines, COA as a sheet).

---

## 3. The Company Object (Mongo, editable via MCP)

```json
{
  "legal_name": "...",
  "name": "...",
  "contact_info": { "email": "...", "phone": "...", "address": "..." },
  "fiscal_year_start": "01-01",
  "company_start_date": "2023-04-01",
  "books_start_date": "2026-01-01",
  "accounting_basis": "cash | accrual",
  "approval_mode": "all | none",
  "locked_through": "2026-06-30",
  "sales_tax": { "enabled": true, "flat_rate": 0.0875 },
  "ledger_version": 1234
}
```

- `books_start_date` — "we keep your books from here forward"; opening balances anchor here.
- `accounting_basis` — drives the default report basis (both always computable from the same ledger).
- `approval_mode` — see §15.
- `locked_through` — see §14.

---

## 4. Chart of Accounts

Per company, stored in Mongo, **rendered as a sheet** at the company root.

| Field | Notes |
|---|---|
| `account_number` | CPA conventions: 1xxx assets, 2xxx liabilities, 3xxx equity, 4xxx income, 5xxx COGS, 6xxx expenses |
| `name` | |
| `parent_account` | hierarchy (Bank → Checking / Savings); reports roll up the tree |
| `type` | Asset / Liability / Equity / Income / Expense — drives sign rules and statement placement |
| `detail_type` | Bank, AR, AP, Fixed Asset, Credit Card, COGS, Other Income, … — drives report grouping |
| `normal_balance` | derived from type |
| `active` | accounts with activity are deactivated, never deleted |

**Seed COA (created at onboarding)** must include every account the documented scenarios post to:
Checking, Savings, Cash, Accounts Receivable, Fixed Assets, Accumulated Depreciation, Accounts Payable, Credit Card, **Sales Tax Payable**, **Unearned Revenue**, **Opening Balance Equity**, **Owner's Contributions**, **Owner's Draw**, Retained Earnings (computed, see §14), Sales, Sales Discounts, **Uncategorized Income**, ~10 solopreneur expense accounts (Software, Processing Fees, Contractors, …), **Bad Debt Expense**, **Uncategorized Expense**.

---

## 5. Dimensions (on every GL line)

| Dimension | Why |
|---|---|
| `customer` | income by client, AR |
| `project` | **nested under customer** (QuickBooks-jobs style); engagement profitability |
| `vendor` | spend by vendor, AP, 1099 prep |
| `class` | line of business (consulting vs courses) — P&L by segment |
| `location` | **column exists from day one**, nullable; rarely used by target user |
| `memo` | free text, always |

Dimensions are Mongo collections referenced by id on documents, rendered **by name** in the GL sheet (sheets are for humans; ids live in Mongo).

---

## 6. Document Model — 9 Types, One Pattern

Everything financial is a document in Mongo that validates and **emits a GL line pattern**. Documents are thin; the ledger is the truth.

| Document | GL pattern (happy path) |
|---|---|
| **Invoice** | DR Accounts Receivable / CR Sales (+ CR Sales Tax Payable if taxed) |
| **Payment** (customer) | DR money account / CR AR — one CR line **per applied invoice**, each with `ref` |
| **Bill** | DR Expense (or asset) / CR Accounts Payable |
| **BillPayment** | DR AP (per applied bill, with `ref`) / CR money account |
| **SalesReceipt** | DR money account / CR Sales — cash sale, skips AR entirely |
| **CreditNote** | DR Sales / CR AR `ref` |
| **VendorCredit** | DR AP `ref` / CR Expense |
| **Transfer** | DR account / CR account — never touches P&L (Checking→Savings, paying credit card) |
| **JournalEntry** | **N lines, must balance** — the escape hatch for everything else (opening balances, depreciation, owner-paid expenses, offsets) |

Document lifecycle: `draft` → (approval) → `posted` → optionally `voided` (via reversal). Invoice/bill **status is always derived** from the ledger (paid = ref sum reaches zero), never stored as truth (Mongo may cache it for listing speed).

**Numbering:** Mongo atomic counters per company per type (INV-0042, BILL-0017, PAY-0117, JE-2026-000187). Sequences never reused; gaps are audited (voided drafts).

---

## 7. The General Ledger Sheets

One spreadsheet per month: `<Company>/<Year>/<MM-Month>/General Ledger`.

### Columns (one row per journal line)

| Column | Example |
|---|---|
| `txn_id` | JE-2026-000187 |
| `date` | 2026-07-14 |
| `type` | Invoice / Payment / Bill / BillPayment / SalesReceipt / CreditNote / VendorCredit / Transfer / JournalEntry / Reversal |
| `ref` | INV-0042 |
| `account_number` / `account_name` | 1200 / Accounts Receivable |
| `debit` / `credit` | 1,500.00 / — |
| `customer` / `project` / `vendor` / `class` / `location` | Acme / Website / — / Consulting / — |
| `due_date` | **populated only on the AR/AP lines of invoice and bill postings** — makes aging computable from the sheet alone |
| `memo` | July consulting, net 30 |
| `posted_at` / `posted_by` | timestamp / "agent via MCP (user@…)" |

- Sorted by date, then txn_id. Protected `TOTALS` row on top: total debits, total credits, difference (always 0.00 — a human glancing at the sheet sees the month balances).
- Deliberately denormalized — DuckDB loads the columns 1:1, joins only COA.
- No running-balance column in the GL (noise); the `account_ledger` report provides it per account.

### Append-only rules (the crux of integrity)

1. **Rows are never edited or deleted.** Mistakes are corrected by new entries.
2. **Edit a posted document** → append a **reversal** of the original lines + a **repost** of the new version (same ref, versioned in Mongo). The GL shows the full story.
3. **Void** → reversal only; document status `voided`.
4. **Cross-month corrections:** a document posted in July but corrected in September posts its reversal + repost into **September's GL** (the current open month). Locked months are physically immutable forever.
5. **Failure safety:** Mongo commits first; GL lines go through a pending outbox appended to the sheet with retry. A tool call never half-posts.

---

## 8. Pairing — How Money Gets Matched (THE crux)

No bank feeds in v1: money events enter as the user telling the agent ("$2,000 landed in checking from Acme"). The **matching engine** proposes; the **human approves** (per §15). Matching order:

1. **Exact** — one open invoice for that customer with open balance == amount → propose applying to it.
2. **Combination** — amount equals a subset of open invoices (oldest-first) → propose the split application.
3. **Partial** — amount < a single open invoice → propose partial application; remainder stays open.
4. **Overpayment** — amount > total open → apply all + remainder becomes an **unapplied customer credit** (never lost; surfaced in cleanup report).
5. **Deposit for a project with no invoice yet** → it is a **retainer**: `DR Bank / CR Unearned Revenue (customer, project)`. When the invoice is later raised, apply: `DR Unearned Revenue / CR AR ref:INV-xxxx`. Income is never recognized early.
6. **No match, no context** → unapplied customer credit on AR; listed until resolved.

Every proposed match is a draft whose preview shows the exact applications; approval posts it. The AP side mirrors all of this for bills.

### The universal ref rule

> **Anything that credits AR (or debits AP) carrying a document ref settles that document — regardless of what created it.**

Payments, credit notes, write-offs, offset JEs, discounts — all reduce open balance through the same mechanism:

```
open_balance(INV-0042) = Σ debits − Σ credits   on AR lines where ref = INV-0042
```

Derived, never stored. Applies point-in-time too: filter `date ≤ D` to get "what did Acme owe me on Aug 31".

### Scenario catalog (all just ref-carrying journal lines)

**Money-in (AR):**

| Scenario | Treatment |
|---|---|
| Overpayment | remainder = customer credit (negative AR by ref), apply later |
| Retainer before work exists | `DR Bank / CR Unearned Revenue`; applied on invoicing |
| Processor fees (Stripe nets 970 of 1,000) | `DR Bank 970 / DR Processing Fees 30 / CR AR 1,000 ref` — invoice fully paid |
| Bounced payment (NSF) | reversal of payment lines (invoice reopens automatically) + optional NSF fee entry |
| Refund | `DR AR ref / CR Bank` |
| Chargeback | refund + fee line |
| Early-payment discount | `CR AR ref` full, `DR Sales Discounts` for the discount |
| Cash sale, no invoice | SalesReceipt: `DR Bank / CR Sales` |
| Bad debt write-off | `DR Bad Debt Expense / CR AR ref` |

**Money-out (AP):** vendor credits, partial bill payments, vendor refunds — identical, signs flipped.

**Solopreneur-specific (first-class tools):**

| Scenario | Treatment |
|---|---|
| Owner pays business expense personally | `DR Expense / CR Owner's Contributions` — the #1 solopreneur transaction |
| Owner draws money out | `DR Owner's Draw / CR Bank` |
| Transfer between accounts / pay credit card | Transfer doc — never touches P&L |
| Customer is also a vendor — offset | JE: `DR AP ref:BILL / CR AR ref:INV` — both balances close |

---

## 9. Balances at Any Date

Because the ledger is complete, any balance is a filtered sum — no snapshots, nothing to go stale:

- **Account balance as of D:** `Σ debit − Σ credit where account = X and date ≤ D`
- **Balance sheet as of D:** same, grouped by type (point-in-time)
- **P&L for a range:** `date between start and end` (flow)
- **Open balance as of D:** the ref sum with `date ≤ D`

Volume reality: a busy solopreneur ≈ 5k GL lines/year. DuckDB loads everything since inception in milliseconds.

---

## 10. Reports & Analytics (DuckDB)

**Load path:** GL sheets + COA sheet → DuckDB tables `gl_lines` + `accounts` → report SQL → token-budget renderer (compact CSV tables; reuse FinBoard mcp-server renderer patterns: drop zero rows, collapse depth, never silently truncate).

**Every report is a SQL view over `gl_lines`; each concept defined exactly once.**

| Tool | Answers |
|---|---|
| `profit_and_loss` | range, monthly columns, prior-period compare, by class / by customer, **cash or accrual basis** |
| `balance_sheet` | as-of any date; Retained Earnings computed (cumulative prior-year net income) |
| `trial_balance` | every account, debits/credits — the CPA sanity check |
| `account_ledger` | one account's lines + running balance (bank-statement view) |
| `ar_aging` / `ap_aging` | open ref sums bucketed 0/30/60/90 via `due_date` |
| `income_by_customer` / `spend_by_vendor` / `project_profitability` | dimension rollups |
| `cash_flow` | v1 simple: net change per money account + inflow/outflow categories (indirect method deferred) |
| `sales_tax_liability` | balance of Sales Tax Payable by period |
| `1099_payments` | payments by vendor for year, `track_1099` vendors |
| `list_uncategorized` | everything parked in Uncategorized accounts — the cleanup queue |
| `customer_statement` | all open items for one customer (v1 if trivial, else v1.5) |
| `query_books` | **the power tool** — read-only SQL against `gl_lines`, sqlglot-guarded (SELECT only) |

**Cash vs accrual:** cash-basis P&L recognizes income/expense on payment lines rather than invoice/bill lines — computed from the same ledger, toggled per report, default from company object.

---

## 11. Sales Tax & 1099 (v1 scope)

- **Sales tax:** single flat rate on the company object; optional per invoice → extra `CR Sales Tax Payable` line; liability report. No jurisdictions, no filings.
- **1099:** `track_1099` boolean on vendor + `1099_payments` report. Nearly free, big CPA goodwill.

---

## 12. Onboarding & Opening Balances

1. Create company object → set `books_start_date`.
2. **Opening balance JE** dated books-start-minus-one-day, posted to the first GL sheet. Agent-guided: either simple ("what was your checking balance?") or **full prior trial balance** for users migrating from QuickBooks — same JE, any accounts.
3. Whatever doesn't balance plugs to **Opening Balance Equity** (accountant reclassifies later). Debits always equal credits even with partial info.
4. **Historical open invoices/bills** entered individually (real dates, posting to opening period) so aging and future payments work with proper refs.
5. Until the opening JE posts, books are `incomplete` — reports run but carry a warning.

---

## 13. Invoice Artifact (the sendable thing)

Recording an invoice is not enough — the solopreneur must have something to give the client. v1:

- On posting, render the invoice as a **Google Doc from a template** in `<Company>/invoices/`, auto-export PDF, return the link in chat.
- Includes company contact info (from company object), customer, lines, tax, due date, payment instructions (free-text field on company object).
- **No email sending in v1** — the artifact + link only.

---

## 14. Period Locking & Month Close

**Lock:** one field, `locked_through`, on the company object. Every posting validates `date > locked_through`. Corrections to locked periods land in the current open month (§7.4) — a locked month's sheet never changes.

**Month-close ritual (agent-guided checklist):**
1. `verify_books` — trial balance ties, no pending drafts, no unapplied credits/uncategorized (or acknowledged)
2. **Balance check** — "Books say Checking = $8,412 on Jul 31 — does your bank agree?" Mismatch → agent helps find it or posts an adjustment. (Poor man's bank reconciliation until bank feeds exist.)
3. Mini review: P&L, ending balances, unusual entries
4. `lock_period(through)` — audited

**Unlock:** allowed in v1 (`unlock_period`), loudly audited, agent warns that shared reports may change. If anything posts to a re-opened month, that month's sheet re-renders on re-lock.

**Year-end close: nothing to do.** No closing entries ever — Retained Earnings is computed in the balance sheet SQL (cumulative prior-year net income). Fiscal year start just tells reports where years cut.

---

## 15. Approval Flow

**Mechanism: draft → preview → approve** (not MCP elicitation — spotty client support, not durable, not separately auditable).

1. Posting tools create the document as `draft` and return a preview of the **exact GL lines** it will post.
2. User approves in chat → `approve_document(id)` → validation re-runs → lines append → audit records who/when/which conversation.
3. `reject_draft`, `list_drafts` (drafts are durable across conversations), `approve_all_drafts` for batches.

**Policy — `approval_mode` on company object:**
- `all` (default at onboarding) — every posting needs approval
- `none` — agent posts directly (still fully audited + reversible)

**Always require approval regardless of mode:** voiding a posted document, editing a posted document (reversal + repost), unlocking a period.

---

## 16. Safety Nets

- **Uncategorized accounts** — agents may park unknowns in Uncategorized Income/Expense; `list_uncategorized` is the cleanup queue. Never block a posting on classification.
- **Duplicate warning** — posting tools warn on same vendor/customer + amount + date ±3 days.
- **`verify_books`** — trial balance check + pending drafts + unapplied credits + uncategorized, on demand and at close.
- **Outbox retry** — no half-posted documents (§7.5).
- **Audit log (Mongo, append-only)** — every tool call and mutation: who, what, before/after, when, conversation id.

---

## 17. MCP Tool Surface (v1)

**Context/setup:** `whoami`, `get_books_status`, `get_company` / `update_company`, `lock_period`, `unlock_period`
**COA:** `list_accounts`, `add_account`, `update_account` (deactivate)
**Contacts:** `add_customer` (+projects), `add_vendor`, `update_contact`, `list_contacts`
**Sales:** `create_invoice`, `record_payment` (matching engine), `create_sales_receipt`, `create_credit_note`
**Purchases:** `record_bill`, `pay_bill`, `create_vendor_credit`
**Ledger:** `post_journal_entry` (N lines), `record_transfer`, `record_owner_expense`
**Approval:** `list_drafts`, `approve_document`, `reject_draft`, `approve_all_drafts`
**Reports:** everything in §10.

Writes return confirmation + a link to the exact GL sheet range. All tools scoped by the auth token — **tenant scope never comes from tool arguments** (FinBoard mcp-server rule).

---

## 18. The Skill

Ships with the product; written per "The Art of Writing Skills" (`~/Downloads/The Art of Writing Skills.md`) — the same methodology as all FinBoard skills. Teaches the agent:

- The accounting vocabulary and the 9 document types
- Tool sequences (e.g., money arrives → try matching → retainer path → approval)
- When to use `query_books` vs pre-built reports
- The approval etiquette and close ritual
- What NOT to do (never book transfers as income/expense; never recognize retainers as income; park unknowns in Uncategorized rather than guessing)

---

## 19. Platform

- **Auth:** Better Auth in Next.js (Mongo adapter — same DB). Google social login for convenience but **zero Google scopes needed from users** (sheets use our service account); email/password fine. Better Auth **MCP plugin** makes it the OAuth provider for MCP clients; **JWT plugin + JWKS** lets FastAPI verify tokens statelessly. Fallback if the MCP plugin is immature: API-key flow.
- **Sheets access:** one Google **service account** owns all folders/sheets; per-company folder shared view-only with the user's email.
- **Next.js UI (all of it):** login, "connect Claude" page (MCP URL + auth), folder view linking into the user's view-only Drive folder.
- **Billing: none in v1.** Nothing gated.
- **Reused from FinBoard mcp-server:** FastMCP server skeleton, core/tools separation, `@audit` decorator pattern (→ Mongo), token-budget table renderer, sqlglot SQL guard, rate-limit middleware.

---

## 20. v1 Scope Summary

**In:** double-entry ledger in monthly GL sheets + COA sheet; 9 document types; matching engine with retainer path; approval flow (all/none); opening balances incl. full TB; period locking + close ritual with balance check; cash/accrual toggle; flat sales tax; 1099 tracking; invoice Doc/PDF artifact; uncategorized + duplicate + verify safety nets; all §10 reports incl. `query_books`; Better Auth; minimal Next.js UI; the skill.

**Out (deliberately):** multi-currency, bank feeds/reconciliation & CSV import, receipts UI (folder convention only), depreciation register (manual JE only), estimates/quotes, recurring transactions, billable-expense rebilling (v1.5), customer statements (v1.5 unless trivial), email sending, payroll, inventory, batch deposits, multi-user/teams, billing/Stripe.

**Open questions (not yet decided):**
1. Multi-company per user — in v1 or hard-scoped to one company?
2. Product name.
3. Repo location/name.
