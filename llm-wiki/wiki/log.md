---
type: synthesis
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
tags: [log, provenance]
---

# Log (append-only)

## [2026-07-17] ingest | Product design discussion → design doc v1

- Source: `raw/2026-07-17-design-doc.md` (distilled from founder design session, 2026-07-17)
- Pages created: product-vision, three-store-architecture, platform, company-object, chart-of-accounts, dimensions, document-model, general-ledger-sheet, pairing-and-matching, scenario-catalog, point-in-time-balances, approval-flow, period-locking-month-close, onboarding-opening-balances, safety-nets, mcp-tool-surface, reports-and-analytics, compliance, invoice-artifact, the-skill, v1-scope
- Contradictions flagged: none (first ingest)
- Notes: design supersedes two ideas rejected during discussion — (1) user-editable sheets with drift detection (rejected for service-account-owned view-only sheets), (2) re-render-on-demand ledger, option (b) (rejected for append-only immediate posting, option (a); re-render survives only for unlocked-month re-lock). Open questions tracked in v1-scope.

## [2026-07-17] decision | Open questions resolved
- Multi-company: one company v1, company_id-keyed schema from day one
- Name: SoloBooks (confirmed)
- Repo: new standalone repo, patterns copied from finboard/mcp-server
- Pages updated: v1-scope

## [2026-07-17] ingest | Posting pipeline research + approved design
- Source: raw/2026-07-17-posting-pipeline-research.md (Modern Treasury ledger series, outbox literature)
- Pages created: posting-pipeline
- Pages updated: index, general-ledger-sheet, approval-flow (cross-links)
- Contradictions flagged: none; confirms existing append-only/reversal design. Notable divergence from MT recorded: no balance caches.

## [2026-07-17] ingest | Matching engine internals approved
- Source: raw/2026-07-17-matching-engine-design.md
- Pages created: matching-engine
- Pages updated: pairing-and-matching, index (cross-links)
- Decisions: LLM extracts facts only (engine deterministic); tolerance option (b) $0.99 write-off to Bank Fees/Sales Discounts; ambiguity returns all candidates

## [2026-07-17] ingest | Sheets layer approved
- Source: raw/2026-07-17-sheets-layer-design.md
- Pages created: sheets-layer
- Pages updated: index (cross-link)
- Decisions: lazy month creation; formula TOTALS; one append per txn; swap-tab re-render

## [2026-07-17] ingest | DuckDB layer approved
- Source: raw/2026-07-17-duckdb-layer-design.md
- Pages created: duckdb-layer
- Pages updated: index
- Decisions: reports AND query_books share one view stack; parse failure = hard error; LRU cap on resident companies

## [2026-07-17] ingest | Auth wiring approved (supersession)
- Source: raw/2026-07-17-auth-wiring-design.md
- Pages created: auth-wiring
- Pages updated: platform (MCP plugin reference superseded — CONTRADICTION resolved: Better Auth MCP plugin deprecated in favor of OAuth Provider plugin), index

## [2026-07-17] ingest | Testing strategy + invoice artifact details; index reorganized
- Sources: raw/2026-07-17-testing-strategy.md (+ invoice artifact generation details folded into invoice-artifact context)
- Pages created: testing-strategy
- Pages updated: index (new "Implementation (drafted, not built)" section consolidating posting-pipeline, matching-engine, sheets-layer, duckdb-layer, auth-wiring, invoice-artifact, testing-strategy)
- Drafting phase COMPLETE — all implementation topics documented; no code written

## [2026-07-17] ingest | Buyer panel (SSR, 15 respondents) → scope revision
- Sources: raw/2026-07-17-buyer-panel-report.md, raw/2026-07-17-buyer-panel.json
- Pages created: buyer-panel-findings
- Pages updated: v1-scope (CSV import INTO v1 — REVERSES earlier "no import" cut; accountant packet, completeness nudges, pricing ≤$29 pre-launch), mcp-tool-surface (import_bank_csv, export_accountant_packet), safety-nets (nudges), index
- Contradiction resolved: "bank feeds/CSV import out of v1" superseded by panel evidence (11/15 top objection); full Plaid feeds remain out

## [2026-07-17] plan | Phased v1 implementation plan written + reviewer-approved
- Artifact: solobooks/plans/2026-07-17-solobooks-v1-plan.md (10 phases, 40+ tasks, exit gates)
- Review loop: round 1 found 11 issues (worst: ledger_version bumped at COMMIT would stale the DuckDB cache — moved to FINALIZE per posting-pipeline) — all fixed; round 2 approved
- Deliberate divergence to log at ingest (Task 9.4): audit written at COMMIT not FINALIZE; customer_statement = report in v1, artifact v1.5
- NO code written — plan is a document pending founder review

## [2026-07-18] ingest | Self-review gap fixes (7 gaps)
- Source: raw/2026-07-18-gap-fixes.md
- Pages created: cash-basis-recognition (canonical v_pnl_cash algorithm incl. sales-tax-on-cash + card-charge-date + retainers-at-receipt), dates-and-timezones
- Pages updated: sheets-layer (**CRITICAL SUPERSESSION: SA My-Drive storage → Google Workspace Shared Drives — post-2025-04-15 SAs have ZERO Drive quota, original design would not work**; row_range invalidation on re-render), matching-engine (hints schema — the LLM↔engine contract), buyer-panel-findings (sober framing: no segment above "might or might not"), company-object (timezone field, fiscal day==01), duckdb-layer + compliance (point to canonical cash-basis page), platform (Shared Drives + exportability mechanism), general-ledger-sheet + scenario-catalog (orphan-fixing inbound links)
- Plan updated: new Task 0.4 integration spike (shared drives, append read-after-write, FastMCP mount, PDF export; purity contract renumbered 0.5); Task 3.2 shared-drive provisioning; Task 5.3 split into 5.3a parse / 5.3b classify
- Lint: orphans sheets-layer + testing-strategy resolved

## [2026-07-18] ingest | Professional reviews (CPA + CAS personas) → bucket-1 correctness fixes
- Sources: raw/2026-07-18-cpa-firm-review.md, raw/2026-07-18-cas-firm-review.md, raw/2026-07-18-bucket1-fixes.md
- Pages created: professional-review-findings
- Pages updated: cash-basis-recognition (**REWRITTEN to rules R1–R9 — v1 page had REAL ERRORS: internal contradiction on owner-paid expenses, Owner's Draw in P&L, uncapitalized asset legs, unstated fee-leg rule; caught by CPA persona review**), onboarding-opening-balances (double-count rule: opening JE never carries AR/AP, historical docs offset OBE), compliance (1099 method exclusion + sales-tax basis disclosure), pairing-and-matching (method now accounting-relevant — SUPERSEDES "metadata only"), period-locking-month-close + sheets-layer (pre-unlock artifact archiving + audited diff), index
- Scope calls deliberately NOT decided — listed as OPEN on professional-review-findings

## [2026-07-18] decision | Scope calls applied (all 8 recommendations approved)
- Source: raw/2026-07-18-scope-calls.md
- Pages created: bank-reconciliation
- Pages updated: v1-scope (rec + grid + packet + COA/verify additions into v1; NEW v1.1 section = recurring billing; 1099 completions + backfill → v1.5; v2 thesis = accountant seat), platform (batch grid = the one ledger-UI exception), chart-of-accounts (tax_line field; Notes Payable, Interest Expense, Reconciliation Discrepancies; principal/interest skill rule), safety-nets (verify_books additions), reports-and-analytics (expanded packet contents), professional-review-findings (open calls → decided), index
- Plan updated: new Task 5.4 (bank reconciliation) + Task 8.4 (batch review grid); Tasks 1.3/7.2/7.3 expanded; deferred section restructured (v1.1/v1.5/v2 thesis/later)

## [2026-07-30] ingest | Process-aware financial objects (founder) → object-model realignment

- Source: `raw/2026-07-30-process-aware-objects.md` — founder architecture position, framed through the invoice. Directive: "review this and use this ideology and update full stack which conflicts with that."
- Method: six-lens conflict audit (object model, workflow-as-object, decision trail, policy versioning, retrieval-as-attention, adversarial scope counter-lens) over all 30 wiki pages, all raw sources and the implementation plan; every candidate adversarially verified against file text; completeness critic pass. **62 candidates → 32 refuted → 27 verified conflicts + 15 second-order findings.**
- Pages created (all `status: draft`): financial-object-model, process-instance, decision-record, evidence, policy-set, context-assembly
- Pages updated: three-store-architecture, product-vision, company-object, duckdb-layer, dates-and-timezones, general-ledger-sheet, sheets-layer, bank-reconciliation, period-locking-month-close, document-model, approval-flow, matching-engine, pairing-and-matching, invoice-artifact, onboarding-opening-balances, mcp-tool-surface, reports-and-analytics, safety-nets, compliance, chart-of-accounts, the-skill, testing-strategy, v1-scope, index

### GOVERNANCE — read before treating any of this as decided

`CLAUDE.md` defines `verified` as "confirmed by the founder in design discussion **and** present in a raw source". The source is founder-authored; the ~20 design decisions derived from it are **not**. Therefore: new pages are `draft`, and every new or changed claim on an existing page carries the inline marker **(proposed 2026-07-30)** so the founder can confirm them in one pass. Precedent: `raw/2026-07-18-scope-calls.md` was the founder confirming a review's recommendations *before* pages moved. **The supersession rule is also explicitly narrowed here: recency does not outrank correctness.** This source does NOT override CPA-validated accounting decisions the founder never revisited — cash-basis R1–R9, the AR/AP opening double-count rule, the 1099 method exclusion, deterministic matching.

### CONTRADICTIONS FLAGGED (not silently overwritten)

1. **`three-store-architecture`: "Mongo = cache, ledger wins."** Correct for money, wrong for meaning. Narrowed to two truth domains — effect (ledger, canonical for monetary/settlement facts) vs context (Mongo, canonical and append-only, never a cache). Mongo remains a cache of *derived ledger* facts (invoice status) and the ledger still wins there.
2. **`invoice-artifact`: "line-item prose isn't accounting data."** True of description/qty/rate; false of `service_period`, which is accounting context. Scope-corrected, not reversed.
3. **`general-ledger-sheet`: "The GL shows the full story."** False today — no column links a reversal to what it reverses. Fixed by admitting `reverses_txn_id` under a new column-admission rule.
4. **`bank-reconciliation`: GL lines "carry `cleared` status."** Unimplementable as written: the sheets layer has one primitive (append, never edit), so a `cleared` cell update has no method, violates append-only, and cannot be made effectively-once by the tail-check. Superseded by append rows to a `Reconciliations` sheet.
5. **`onboarding-opening-balances`: `books_state` flips `complete` on the opening JE**, which by rule 5 can never contain AR/AP — the banner drops while the migration is still incomplete. Flip now depends on the onboarding process completing.
6. **`period-locking-month-close`: "every rendering a banker or accountant may have seen survives."** Mechanism only archives the GL sheet; outsiders see P&Ls, agings and packets. Extended to retained exported renderings.
7. **`reports-and-analytics`: three packet sections were not producible** — approval-mode-per-period disclosure (derivable only by replaying an unindexed audit stream), the tolerance write-off list (indistinguishable from real fee/discount lines), and categorization review (specified over `memo_verbatim`, captured only on the two matching tools). Fixed by `PostingRecord.provenance`.
8. **`approval-flow`: the approved preview is not provably the posted lines** — compose re-validates at approval time. Fixed by `preview_hash` + `PREVIEW_DRIFT`.
9. **LIVE BUG (no ideology needed): `ledger_version` bumps only on a GL append**, but DuckDB also caches the `accounts` table and the COA is "fully rewritten on change" with no bump. A `tax_line` edit, rename or deactivation serves stale data until an unrelated posting happens. Renamed `books_version`; bumps on any change to anything DuckDB caches.

### REFUTED — do not resurrect without new file evidence

Enterprise machinery correctly refused: contract/order objects, revenue schedules, collections/dispute workflows, multi-party approval routing, a server-side attention classifier, receipt substantiation. Already-satisfied claims wrongly flagged: derived status and point-in-time balances already answer the "current state" and "derived facts" buckets better than the source asks; the cash/accrual toggle is already one object read two ways; `query_books` already exposes prior treatment over `gl_lines`. Recorded in `v1-scope` so the next reviewer does not burn a cycle rediscovering them.

## [2026-07-18] maintenance | Redundancy + contradiction sweep
- Contradictions removed: period-locking step 2 taught balance-check-with-plug (now: statement rec per bank-reconciliation, fallback tie-out posts only to Reconciliation Discrepancies); safety-nets "poor man's bank reconciliation" bullet deleted; product-vision "never renders a ledger" now names the one grid exception; three-store-architecture aligned to Shared Drives + archive/ folder; mcp-tool-surface packet description updated (was stale TB+GL+1099-only) + reconcile_account added; onboarding duplicate step numbering fixed
- Redundancy removed: v1-scope rewritten as single authoritative cut (accretion layers folded); buyer-panel-findings scope list → pointer to v1-scope; dated "(added 2026-07-18…)"/"SUPERSEDES" annotations stripped from 10 pages (provenance lives in frontmatter sources + this log); auth-wiring supersedes-footnote removed; index Implementation stubs replaced
- Coherence added: the-skill now carries principal/interest + reconciliation flows; cash-basis history note moved to log; original features/ design doc marked SUPERSEDED with pointer to wiki

## [2026-08-01] verify | Mechanical verification pass — **CLEAN**. 68 checks, negative-controlled.

- Artifact: `tools/verify_design.py` — the seven invariants as a **committed, repeatable script**, not a transcript. `python3 tools/verify_design.py` exits 0 clean, 1 with failures.
- **68 checks pass** on the current tree: every carrier read by the specific rule that must read it, every carrier with a named writer and an intent detector, every member mirrored wiki↔plan, every field a rule branches on frozen in its owning page, every recognized non-P&L leg with a `tax_line`-bearing presentation account, ladder 13/13, gate and bridge declared partitions, 40 pages, 0 broken links, every CPA-validated invariant intact.

**The negative control is the part that matters.** A check that cannot fail is worthless, so four historical defects were deliberately reintroduced. The **first version of the script passed two of them** — a live false-negative rate of 50%:

- `INV1` asked "is `COST_RECOVERY` read by *any* rule". Deleting R11's `line_reason` limb — the pass-3 W-1 defect that deducts $0.00 for the life of every multi-year prepaid — **passed**, because R12 still mentioned the same token. Now each carrier is bound to the *specific* rule that must read it.
- `INV4` matched the bare word `recognized`, which appears four times in prose on that page, so **removing the `expect.recognized` slot passed**. Now anchored to a table row.

Retested after tightening: all four defects fail, each against the correct invariant — R11's limb → INV1, R6's missing rung → INV6, the removed slot → INV4, the broken mirror → INV7.

**This is the first instrument in the project with a measured detection rate rather than an asserted one.** Run it before every commit that touches a rule, an enum, or a plan task.

**Scope, stated plainly:** it verifies **encoding, never doctrine**. It cannot tell you whether R12 states the law correctly — only that R12's carriers exist, are read, are written, and are mirrored. Accounting correctness rests on the four adversarial passes in `llm-wiki/raw/`, whose consistent finding was that the doctrine had converged and only the encoding kept breaking.

## [2026-08-01] fix | Batch 4 — the twenty fourth-pass defects, and the ladder becomes a table

> Supersedes the DO-NOT-FREEZE entry below **for the twenty named defects**. Not yet verified by the mechanical pass; see the close.

**Structural change, not just fixes.** The priority ladder is now a **table with one row per rule R1–R12**, each carrying a rung *or* a stated reason for being outside. A rule missing from that table is a defect **by construction**, which is what makes the missing-rung class (W-3, W-16) unrepresentable rather than merely fixed — and it is greppable, so invariant 6 can check it.

- **W-1** (highest EV, third consecutive pass) — plan Task 4.3 still encoded the *pre-batch-3* preamble, R11 and R12 verbatim, and `views.py` is built from that file, so the paraphrase silently outranked the wiki. It now **quotes** the wiki and carries grep-tests including "no date arithmetic on a benefit period".
- **W-2/W-3/W-16** — R11 moved **above** the R5/R5a suppression step (a depreciation leg bundled with an offset recognized $0 and simultaneously failed the layer-5 gate on a correct ledger); R6 gained a rung (the whole retainer was permanently omitted); R7 declared outside with R4; the default rung is now **untyped** (typed to balance-sheet lines, an unpaid invoice's `CR Sales` was claimed by no rung).
- **W-4** — a **regression** batch 3 introduced: the 12-month test had been re-anchored from `benefit_start` to `payment_date`, which admits only policies whose coverage starts the day you pay. Restored to Reg. §1.263(a)-4(f)(1)'s first-realization anchor.
- **W-5 + the cross-carrier invariant** — R12's tag moves to the **settlement** (the prepaid debit leg posts at *bill* date while the test reads the payment, so every bill-borne and pre-conversion prepayment posted untagged and deducted $0.00 forever). And the exclusion is now a **posting-time invariant across both carriers**: `COST_RECOVERY` may never be written on a line relieving a `PREPAID_12_MONTH` leg. Without it both carriers could be set — $2,400 on a $1,200 premium, trial balance tying.
- **W-6** — rule 5 strips at **amount** granularity, not account: a prior-TB Machinery balance of $20,000 of which one bill carries $12,000 must leave $8,000.
- **W-7** — the amount-matching `NONZERO_OBE` signature is **withdrawn**; it fired on every *correct* CASH migration and matched neither real defect. Replaced by two structural detectors, `OPENING_JE_OVERLAP_BREAK` and `HISTORICAL_DOC_POSTS_OBE`.
- **W-8/W-9** — `GAIN_ON_DISPOSAL`/`LOSS_ON_DISPOSAL` existed in no enum and no seed account while the preamble referenced them; seeded with **no `tax_line`**. The layer-5 gate and the packet bridge are now **partitions of R1–R12** with the disposal term and the prepaid **self-reversal bound** (Σ over a prepayment's life = 0.00).
- **W-10** — `Customer Deposits Received` **withdrawn**: every posting rule credits Unearned Revenue, so seeding it split one deferral across two accounts on opposite sides of the balance sheet. Unearned Revenue carries the `tax_line` instead.
- **W-11** — enum mirroring in **both** directions: `general-ledger-sheet` (which owns `line_reason`) was missing two members; plan Task 1.1 was missing eight `ExceptionKind`, five `DecisionKind` including `PREPAYMENT_12_MONTH_TEST` (R12's entire carrier), the `DetailType` residuals, `DocType.REVERSAL`, and `StatementRow`'s `txn_date`/`post_date` split.
- **W-12/W-13/W-14** — `expect.recognized` and `expect.balances` added (12 of 13 ruleset fixtures could not assert their claim; the fixture guarding pass-2's W3 **passed the defect** because a bill's `gl_lines` are identical whether the asset lands once, twice or never). `PRINCIPAL_WRITE_OFF` gained a writer and `WRITE_OFF_INTENT_UNDECLARED`. Reversal lines now inherit `line_reason` unchanged; reversal-ness rides `type` + `reverses_txn_id`.

**The carrier check ran to seven invariants over every enum, and caught two of my own errors mid-batch** — including an unasserted `.replace()` that silently did nothing, the exact failure mode that produced W-7 in batch 3. All seven now pass: ladder 13/13, every carrier read *and* written, every member mirrored wiki↔plan, every `expect` slot present, 40 pages, 0 broken links.

**Close:** batch 4 is bounded — no doctrine reopened, and the doctrine had already converged (twelve attacker-runs never broke R5a's arithmetic, R1(c), R10, R3, R4's pro-rata, R8, R11's line-level test, rule 5's core, or `Σ recognized ≤ line amount`). What remains is a **mechanical verification pass, not an attack pass**: run the seven invariants exhaustively over all 18 enums, diff every wiki enum against its plan twin, confirm the ladder table is a partition, and confirm every Task 1.9 fixture has a slot for the claim its description makes. **Freeze when that returns clean.**

## [2026-07-31] review | Fourth pass (scoped) → **DO NOT FREEZE.** Batch 3 fixed 7 and created ~11.

> **Supersedes the batch-3 entry below.** All four seams returned BROKEN. Do not build from R1–R12.

- Source: `raw/2026-07-31-ruleset-fourth-pass-memo.md`. Scoped to the three seams batch 3 touched, plus an independent re-verification of the carrier check.
- **Defect trend, four passes: ~17 → 9 (5 self-inflicted) → 20 (11 self-inflicted). It is not converging; the self-inflicted share is rising.**

**What held.** `Σ recognized ≤ line amount` per (`gl_line`, recognition event) survived a dedicated four-way assault — partial settlement across tax years, R4 pro-rata, R12 shares, R7 negatives, overpayment. The adjudicator: *"Keep it verbatim; it is the best sentence batch 3 wrote."* Deleting the OBE-substitution bullet was also confirmed correct by all four attackers. R12's **idea** — decide the branch at entry, carry a tag, never let the view guess a benefit period — is a genuine durable fix; only its **placement** is wrong (the tag belongs on the settlement, not the document).

**What broke.** R12's carrier, three independent ways — including a **regression**: batch 3 re-anchored the 12-month test from `benefit_start` to `payment_date`, which admits only policies whose coverage starts the day you pay, i.e. rejects every actual prepayment. The published ladder failed on all three axes (mis-ordered, R6/R7 have no rung, terminal rung mistyped). Rule 5's granularity is account-level where the arithmetic needs amount-level. The re-armed `NONZERO_OBE` signature fires on every *correct* migration and is silent on both defects it was armed against.

**The carrier check: instrument accepted, discharge rejected.** It is real and it is the first thing here to catch this defect class without an adversary — keep it, run it every batch. But the maintainer designed it, ran it over a subset of its own domain, and declared it passing. Invariant 4 never passed at all (`expect.recognized` was never written). Invariant 2 fails in five places. Invariant 3 cannot be discharged statically while `add_account` mints accounts at posting time. Two more invariants are needed (**named writer + undeclared-intent detector**; **every ladder/gate/bridge set must be a partition of R1–R12**) plus a process rule: **no wiki rule edit ships without its plan task in the same commit** — that has failed three passes running and produced the highest-consequence defect in the repo.

**Stop attacking.** Across four passes, twelve attacker-runs hit R5a's arithmetic, R1(c), R10, R3, R4's pro-rata, R8, R11's line-level test and rule 5's core; none broke. A fifth adversary would re-derive the same findings at the same seams, because the seams are wherever the last edit landed and there will always be a new last edit. Run instead: **batch 4** (bounded, no doctrine reopened) → **encode the ladder as a table**, one row per rule stating its rung *or* why it is outside, which makes the missing-rung class unrepresentable rather than merely fixed → **a mechanical verification pass, not an attack pass**. Freeze when that returns clean.

**Risk if frozen today, and who carries it.** `LineReason` and `ExceptionKind` freeze at the first posting and a locked month is immutable forever, so the wiki/plan enum drift is unfixable after go-live except by AMENDMENT over every affected document. The code as planned deducts **$0.00 for the life of every prepaid amortization** and mis-years **every partial settlement**. Both are silent: the trial balance ties, all seven `verify_books` checks pass, and the accrual-to-cash bridge reproduces the error because it is built from the same broken set. That lands on the first customer's first filed Schedule C, and **the taxpayer carries it**.

## [2026-07-31] fix | Batch 3 — carrier check + the seven third-pass defects. R1–R12 stands, with carriers.

> Supersedes the DO-NOT-FREEZE state below **for the seven named defects only**. The ruleset has **not** been re-attacked since; see the stop condition at the end.

**The carrier check ran first, and it works.** Four grep-able invariants, applied mechanically before any editing, reproduced W-1, W-2 and W-5 with no review: `LineReason.COST_RECOVERY` was written by R12 and read by no rule; `PREPAID_ASSET`, `INVENTORY`, `COGS` had no reader at all; R3's haircut carve-out had no predicate token. That is the first time this class of defect was caught without an adversarial pass.

- **W-1** — R11 gains a second limb: `detail_type ∈ CostRecovery` **OR** `line_reason = COST_RECOVERY`. That second limb is the only route by which prepaid amortization reaches R11, and the deduction keeps the *expense* account's `tax_line`, which a CostRecovery account could not give it. R11 and R12 no longer contradict each other.
- **W-2** — R12 rewritten: the 12-month branch is **decided at entry and posted**, carried by `LineReason.PREPAID_12_MONTH` plus a `PREPAYMENT_12_MONTH_TEST` decision record — never inferred by the view, which has no benefit period to read and must not guess. "Exactly one branch fires" is now true *by construction*. Unanswered defaults to capitalized and raises `PREPAYMENT_PERIOD_UNCONFIRMED`. R12 reads **both** `detail_type = PREPAID_ASSET` and the tag, so the tag cannot deduct a leg that is not a prepayment.
- **W-3** — `Prepaid Insurance / Rent / Software` sub-accounts each carrying their own `tax_line` (one generic prepaid cannot carry Sch C lines 15, 20b and 18/27a at once), plus **Customer Deposits Received** — R6 recognized "under Customer deposits received" and that caption was in no seed list.
- **W-4** — the preamble is now per-**(`gl_line`, recognition event)** with `Σ recognized ≤ line amount`. The previous "once per line, on exactly one date" outlawed partial settlement, which is R4's own mechanic and the modal event. **The priority order is now published** rather than asserted, and R4 is explicitly outside the ladder. Disposals are excluded from `v_pnl_cash`, not merely unmapped.
- **W-5** — Inventory and COGS **removed** from the seed COA and `DetailType`, with the refusal stated on the page. They were added on the maintainer's initiative, absent from both source memos, against a `verified` scope page, and no rule recognized either leg. The proposed R13 is rejected: admitting inventory needs a recognition rule, not a seed-account entry.
- **W-6** — the OBE-substitution bullet **deleted**. Onboarding carried two competing fixes for one defect; together the asset was on the books zero times, and OBE-substitution alone destroyed the modal no-prior-TB user's basis. Rule 5 alone is complete, now excepting the plug it depends on, and `NONZERO_OBE` is re-armed: a residual equal to a historical document's own amount is the duplication/deletion signature.
- **W-7** — the bridge terms are now Δ(AR from P&L-composed) / Δ(AP from P&L-composed) / Δunearned / prepaid timing, and nothing else; it ties to `v_pnl_cash` to the cent. The false "cash recognizes on payment lines instead of invoice/bill lines" summary is gone — it was untrue for R1(b), R5a, R10, R11 and R12.
- Consistency: R3's haircut gains `PRINCIPAL_WRITE_OFF` as a hard predicate (a $30 processing fee and a $30 haircut are otherwise identical in every column); R4 defines `applied`; R5a raises `OFFSET_INTENT_UNDECLARED` when the shape matches without the tag; R9 covers constructive receipt through an offset; four `ExceptionKind` and five `DecisionKind` members added — including `PRIOR_RETURN_BASIS`, without which the previous pass's headline fix had no legal kind to be written as.

**Stop condition, unchanged:** batch 3 made three judgment edits at seams (R12, the preamble, deleting one onboarding mechanism), which is exactly the profile that broke in passes 2 and 3. A fourth pass is warranted, **scoped to those three seams only** — re-attacking R5a, R1(c), R10, R3 or batch 1 is negative-value; four attackers hit each and none broke.

## [2026-07-31] review | Third adversarial pass → **DO NOT FREEZE**. R1–R12 is not converging.

> **Read this before building anything from R1–R12 or from commit `baa83dd`.** The entry below it says the ruleset was "closed at R1–R12". It was not. Nine confirmed defects, **five introduced by that very commit**, two of them permanent tax disallowances.

- Source: `raw/2026-07-31-ruleset-third-pass-memo.md`. Four angles + adjudicator, targeting the half of the second pass that had never been attacked.
- **W-1 (worst).** Pre-batch-2 R11's `prepaid-asset` contra clause **worked** — it caught multi-year prepaid amortization and gave the right answer. Batch 2 deleted it, replaced the contra test with an own-account `detail_type` test that cannot match an ordinary expense account, added an explicit "prepaid amortization is excluded" sentence, and then pointed R12's capitalized branch back at R11. A $3,000 three-year premium now deducts **$0.00 forever** — verbatim the outcome R12's own closing sentence claims to prevent. A $1,100 timing error became a $3,000 permanent disallowance. `LineReason.COST_RECOVERY`, added to a frozen enum for this purpose, is **read by no rule**.
- **W-2.** R12's 12-month-rule branch selector has **no evaluator and no carrier**: a 12-month and a 3-year policy post identical rows, and Task 4.3's grep-test forbids the view from reading anything else. Both-branches-fire is also constructible ($6,000 on a $3,000 premium).
- **W-4.** The composition preamble ("once per `gl_line` … at most once, on exactly one date") **outlaws partial settlement** — R4's own mechanic, the modal solopreneur event, and two existing fixtures. Copied verbatim into plan Task 4.3.
- **W-5.** Inventory + COGS were seeded on the maintainer's own initiative, absent from both source memos, **against a `verified` scope page** that puts inventory out of v1 — and no rule in R1–R12 recognizes either leg. Schedule C Part III = $0 forever *and* the purchase is never deducted. **Resolution: delete the accounts; the proposed R13 is a scope expansion smuggled through a seed list and is rejected.**
- **W-6.** Onboarding now carries **two competing fixes for the same defect** (rule 5 strips the account from the opening JE; the `:29` bullet substitutes OBE into the document). Either alone is correct; **together the asset is on the books zero times**, and `:29` alone destroys the modal no-prior-TB user's basis while the same commit disarmed `NONZERO_OBE` for that branch.
- **W-7.** The accrual-to-cash bridge was applied by **neither** batch — it lived in the second memo's section-4 checklist while the work was done from the W-numbers.

### The meta-finding, which matters more than any single defect

Three passes, one failure mode: **mechanical edits land cleanly; judgment edits break the adjacent rule that was written against the old semantics.** More review passes will not fix this. Four **grep-able carrier invariants** would have caught W-1, W-2 and half the outstanding checklist with no review at all: (1) every enum member added must be *read* by some rule; (2) every field a rule reads must exist in a frozen list; (3) every rule that recognizes an amount must name an account carrying a `tax_line`; (4) every fixture must have an `expect` slot able to assert its claim. Currently failing, in order: `LineReason.COST_RECOVERY`; R12's benefit period; R6 and R12; eight fixtures.

**Next action is the carrier check, not another edit sprint.** A fourth pass is worth running only after batch 3, scoped to the three seams the memo names (R12's carrier; the per-(line, event) preamble against the per-document rules; whichever onboarding mechanism survives, against R11/R12). Re-attacking R5a, R1(c), R10, R3 or batch 1 is explicitly negative-value — four attackers hit each and none broke.

## [2026-07-31] ingest | Second adversarial pass → ruleset closed at R1–R12

- Source: `raw/2026-07-31-ruleset-second-pass-memo.md`. Four angles attacked the **revised** R1–R11 (nobody had); adjudicated. **Verdict: FREEZE WITH EDITS** — the architecture held (the allowlist shape, `min()`, composition-carries-basis, the signed residual, the `(txn_id, account_number, side)` triple), but **8 defects put a wrong number on a filed Schedule C** and several were introduced by the *previous* fix.
- Applied in two batches (`fb1a863` mechanical, this commit judgment) so the accounting changes could be verified separately.

### Defects the previous revision INTRODUCED (worth recording as a pattern)

- **W3 — the `prior_return_basis` CASH branch put a $12,000 asset on the books twice.** The fix for a silent *omission* created a silent *duplication*: the trial balance ties, the balance sheet balances, net book value looks plausible, and R11 then depreciates the duplicate for seven years. Root cause: rule 5 banned only AR/AP from the opening JE, which was sufficient **only** because the old ACCRUAL composition offset to OBE and cancelled the plug by construction. Now: the opening JE excludes every account a historical document's composition will post, and a balance-sheet-composed historical document offsets OBE.
- **W2 — R11's prepaid clause stated the accrual answer inside the cash ruleset.** And deleting it alone would make cash-basis insurance $0 forever, so **R12** ships with the deletion.
- **W8 — the layer-5 gate rewording failed a *correct* Golden Company by $7,000** on the R6 retainer and the R5 bad-debt write-off, both CPA-endorsed and both cited two lines below the wording that was changed. Both prior wordings were wrong; the gate is now a **line-by-line attribution** to an enumerated set with an unattributed cent failing.
- **W16/W17 — two fixes landed in the wiki and not in the plan**, and they were the irreversible ones.

### New rules and hardening

- **R12** — prepayments recognize at payment under the 12-month rule (Reg. §1.263(a)-4(f)); the later amortization recognizes nothing. Exactly one branch fires.
- **R11** — the test is now **line-level on the line's own `detail_type`**, never "its contra": `gl_lines` has no line pairing, so a bundled year-end JE recognized $1,700 instead of $500 and a three-line abandonment was undefined. Form-independent, so a direct write-down cannot silently return line 13 to $0.
- **R5a** — gated on `line_reason = OFFSET_SETTLEMENT`, never on a Reversal; **mutuality deliberately NOT required** (*Old Colony Trust* — a payment to my vendor by my customer at my direction is constructive receipt with different counterparties); allocation **pro-rata**, ordering rules forbidden.
- **R1(a)** — money accounts are `detail_type ∈ MONEY_ACCOUNT`, **never a literal list**; processor balances are money accounts held by an agent, so a Shopify seller's year-end receipts stop landing in the wrong year against the 1099-K.
- **R1(c) / R3 / R10** — owner-paid purchases compose the account actually bought; a principal haircut riding a payment recognizes nothing (Reg. §1.166-1(e)); money-in requires **presently payable and unrestricted** (*Kahler*) and is asked **asymmetrically**, because no deposit row carries a marker a shape test could narrow.
- **Composition preamble** — R1–R12 is a priority-ordered predicate evaluated **once per line**, not a union; every line recognizes at most once. Asset disposals are Form 4797, out of Schedule C scope.
- `DetailType` is declared **the recognition key**, enumerated in full; `LineReason` gains `COST_RECOVERY` and `OFFSET_SETTLEMENT`; seed COA gains Merchant Clearing, Prepaid Expenses, Amortization accounts, Machinery & Equipment, Sales Returns, **Inventory and COGS**.
- Attacker claims **refuted** and recorded so they are not resurrected: R5a must *not* require same-counterparty mutuality; deleting R11's prepaid clause alone is harmful; `normal_balance` for Accumulated Depreciation is not mis-derived; §195/§197/§168(k) already match R11's test.

## [2026-07-30] ingest | Tri-persona review (CFO / Shopify solopreneur / CPA 2nd pass) → ruleset closed at R1–R11

- Source: `raw/2026-07-30-tri-persona-review.md`. 43 findings, adversarially verified → **0 blocking, 6 serious**.
- **Method defect recorded:** the first verification pass keyed verdicts by finding id while two personas had both numbered findings `F1…`; their verdicts collided. Re-run with namespaced ids; only the re-run is authoritative. Persona verdicts and realignment assessments were never affected.
- Verdicts: seller *would not adopt* (one entry path missing, not a scope complaint); CFO *bones are right, not my product*; CPA *conditionally yes — better than any QBSE/Wave file I inherit*.
- **The realignment scorecard, from the reviewers themselves:** `provenance`, `policy-set`, `ExceptionKind`, `preview_hash` all earned their keep; `process-instance` earned it for the v2 thesis; **`context-assembly` did not — all three independently rated the lens surface irrelevant to their decision.** Net: a good pass aimed at the wrong axis — it fixed the file the CPA inherits and moved none of the numbers he signs.

### Ruleset changes (drafted, then adversarially attacked from four angles; two attackers died on API errors and their sweeps were completed by hand)

- **R5a** — mutual offsets ARE constructive receipt *and* payment. Offset amount is `min(Σ AP debits w/ ref, Σ AR credits w/ ref)`; every other leg of the posting recognizes nothing. **Attack that changed the draft:** keying on posting *shape* rather than amount let a "walk away from the rest" JE fabricate $1,600 of receipts and deductions, and made the filed number depend on whether the agent wrote one JE or two.
- **R10** — cutoff: recognition date ≠ clearing date. **Attack that changed the draft:** as first written R10 was *inert* — a December cheque discovered on the January statement is refused by `locked_through` and redirected into the new year, the precise error it exists to prevent. Now carries the year-end close precondition and the AMENDMENT path, and asks only on cheque-marked rows.
- **R11 (new)** — cost recovery is basis-independent. **A pre-existing defect the ruleset's allowlist shape hid:** no depreciation/§179/amortization JE matches R1–R10, so `v_pnl_cash` reported Schedule C line 13 as **$0 forever**, while `v1-scope` mandates depreciation as a manual JE. `testing-strategy` layer 5 was *licensing* the bug ("differ by unpaid/non-cash items") and is reworded.
- **`prior_return_basis`** (renamed from `prior_books_basis`) — **three drafting errors caught:** the deciding fact is the *filed return*, not the bookkeeping; `NONE` routed to ACCRUAL and omitted income for the modal shoebox customer (removed — absent an accrual return the answer is CASH); and hardcoding `CR Sales` / `DR Expense` defeated R4's balance-sheet carve-out, deducting a $12,000 machine at settlement *and* again via §179/MACRS. Also **removed from PolicySet** — the composition of the posted documents already carries it, and a second copy on an effective-dated object could contradict the ledger undetectably.
- **`REC_RUN`** — statement balances + a four-term residual. **Attacks that changed the draft:** the residual was written in bank polarity and **inverts on credit cards** (money accounts too), failing every clean card rec and inviting a monthly plug — now stated in signed terms; `rec_clears` keyed by `txn_id` alone cannot say *which account* cleared, so a transfer produced a phantom residual equal to the transfer — now keyed `(txn_id, account_number, side)`, a schema decision that freezes on an append-only sheet at Task 3.2; the residual is computed only after unmatched statement rows are dispositioned (an unbooked bank fee is a missing entry, not a discrepancy); and the first run on an account asserts against the opening JE — the only verification the opening balance ever gets.
- Pages updated: cash-basis-recognition, onboarding-opening-balances, policy-set, bank-reconciliation, sheets-layer, duckdb-layer, safety-nets, scenario-catalog, testing-strategy; plan Tasks 1.1, 1.9, 2.8, 4.3, 5.4.
- **Still open, deliberately:** the two remaining serious findings — seed `Merchant Clearing` + `Sales Returns & Allowances` with a skill rule, and the `NET_SETTLEMENT` cascade rule for processor-net deposits. Both are entry-path work, not ruleset work.

## [2026-07-30] maintenance | Coherence + lint sweep after the parallel object-model update

- Trigger: six new pages and 24 edited pages were written by five agents that could not see each other's work. Links and orphans were clean; duplication and two contradictions were not.
- **Single-owner assignments made explicit** (one concept, one page): `books_version` → duckdb-layer · capture rule → the-skill · null-renders-as-"not recorded" → context-assembly · `provenance` → decision-record · `preview_hash`/`PREVIEW_DRIFT` → approval-flow · policy header + retained renderings + statutory/operational thresholds → policy-set · `ExceptionKind` → safety-nets · column-admission rule → general-ledger-sheet · `ref` vs `origin` → pairing-and-matching · tenant rule for caller-supplied refs → mcp-tool-surface · audit `subject_ref` edge → safety-nets · ledger-vs-context read boundary → duckdb-layer · "approval is not a workflow" → process-instance · packet-section diagnosis → reports-and-analytics · decided-out register → v1-scope. Every other mention reduced to a one-line consequence plus a link.
- **Contradictions fixed:** `ledger_version` survived on posting-pipeline, sheets-layer, reports-and-analytics and index → all now `books_version`; three-store-architecture placed the `Reconciliations` sheet in the month folder while sheets-layer placed it at the company root (company root wins — it carries a `statement_period` column); duckdb-layer called its table `reconciliations` and hedged it as conditional while sheets-layer named it `rec_clears` and committed to it (`rec_clears`, committed); index still described rec as "cleared flags".
- posting-pipeline had been missed entirely by the parallel pass despite three pages pointing at it for COMMIT-time `provenance` and `PREVIEW_DRIFT` — source, `modified`, marker and the two hooks added.
- Frontmatter added to index and log (lint rule requires it on every page; they were exempt only from the orphan rule).
- **One duplication left undecided and escalated:** pairing-and-matching's 6-rule ordered list vs matching-engine's 7-rule cascade — pre-existing (both 2026-07-17), CPA-validated content, not agent-introduced. Resolved separately below on founder instruction.

## [2026-07-30] decision | Matching rules: one cascade, one page (founder-approved)

- **Contradiction, not granularity.** The two lists had already drifted three ways, all provable from file text: (1) `matching-engine` rule 1 **"Invoice cited"** — the user naming INV-0042 — was **absent** from pairing-and-matching, and since both lists were explicitly ordered ("In order" / "first hit wins"), the missing rule was the highest-precedence one, so implementing from that page would override the user's own explicit instruction; (2) the subset **tie-break disagreed** — `oldest-first` vs `prefer fewest, then oldest`: on open invoices of $100/$400/$500 a $500 payment settles `{$100,$400}` under one and `{$500}` under the other, producing different refs, different aging and a different cash-basis composition (R4 recognizes pro-rata *per settled document*); (3) **confidence and ambiguity-as-an-outcome** — the "return ALL candidates and ask the user" safety rule — existed only on matching-engine, so the other page read as "always propose", i.e. always guess.
- Why it mattered beyond tidiness: the plan states "where this plan and the wiki disagree, **the wiki wins**", which assumes the wiki gives one answer. Both pages were `status: verified` and gave two. (Plan Task 5.1 does cite matching-engine, so live risk was low; the exposure was the next edit to either page going uncaught.)
- **Resolution:** pairing-and-matching's ordered list → an **unordered outcome table** ("treatments, not a cascade"), keeping every journal entry verbatim — retainer `DR Bank / CR Unearned Revenue (customer, project)` and `DR Unearned Revenue / CR AR ref` with "income never recognized early" (R6), the overpayment→unapplied-credit treatment, partial-remainder-stays-open, no-context→listed credit. **[[matching-engine]] is now the sole owner of precedence, tie-breaks, confidence and ambiguity.** The cited-invoice rule is correctly absent from the outcome table: it is a *selection* rule, not a distinct ledger outcome — which is exactly why the outcome/precedence split is the right seam.
- **No accounting changed.** Zero CPA-validated treatments were altered, reworded or dropped; only the ordering framing was removed. Verified: both retainer JEs, the R6 claim, the overpayment treatment and the universal ref rule all still present; no numbered rule list remains on pairing-and-matching; matching-engine still carries all 7; all links resolve.
