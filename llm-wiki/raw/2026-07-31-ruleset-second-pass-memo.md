# Ruleset Second-Pass Adjudication (2026-07-31)

> Immutable source. Four adversarial angles against the revised R1-R11, adjudicated. Verdict: FREEZE WITH EDITS.

# VERDICT MEMO — R1–R11 ruleset, second-pass adjudication

## 1. Verdict

**FREEZE WITH EDITS.** The architecture survived hard attack — the allowlist shape, `min()`, the composition-carries-basis decision, the signed residual, the `(txn_id, account_number, side)` triple all held. But eight defects put a wrong number on a filed Schedule C and two `verified` pages contradict each other. Every fix below is bounded text; none requires a design change. Apply §2–§4, bump to **R1–R12**, then freeze.

---

## 2. Demonstrably WRONG — verified against the files

Ranked by tax impact. I re-derived each ledger myself; the tally at the end of each item is what I computed, not what the attacker asserted.

---

### W1. R11's mechanical test is not computable over `gl_lines` — and gives two different answers where it is

**Verified.** `general-ledger-sheet.md:16` lists every GL column: there is no line number, no pair id, no ordering column. "The contra of a P&L line" is undefined for any posting with more than one debit or one credit, and `post_journal_entry` accepts N lines (plan Task 1.4: "JE lines ≥ 2").

Bundled year-end JE (the normal accountant habit): `DR Depreciation 500 / DR Bad Debt 1,200 / CR Accum Dep 500 / CR AR 1,200`. Transaction-scoped (the only thing SQL can express) → **$1,700** of cash deductions. Correct is **$500** (R5: bad debt recognizes nothing). Line-pairing → undefined. Abandonment `DR Loss 800 / DR Accum Dep 1,600 / CR Computer Equipment 2,400` → **$0 or −$800** depending on which reading the view author picks, and nothing in R1–R11 picks.

Separately: the test misses the direct write-down `DR Depreciation Expense / CR Machinery & Equipment` entirely → line 13 = $0, the exact bug R11 exists to end.

**Replace R11's "Mechanically:" sentence with:**

> Mechanically, and **line-level**: a P&L line recognizes on both bases at its own date **iff its own account's `detail_type` ∈ `CostRecovery` (`DEPRECIATION`, `AMORTIZATION`, `DEPLETION`)**. The test is on the line's own account, never on "its contra": `gl_lines` carries no line pairing ([[general-ledger-sheet]]), so "the contra of a line" is undefined for any posting with more than one debit or one credit — a bundled year-end JE (`DR Depreciation 500 / DR Bad Debt 1,200 / CR Accum Dep 500 / CR AR 1,200`) would otherwise recognize the bad-debt leg too, $1,700 instead of $500, and a three-line abandonment would recognize $0 or −$800 depending on the reader. The line-level test is also **form-independent**: it fires on `CR Accumulated Depreciation` and on a direct `CR Machinery & Equipment` write-down alike, so no booking style silently returns Schedule C line 13 to $0. **§179 is a tax election, not a second entry** — it is depreciation for the full basis in the year elected, distinguished only by `tax_line`. **Prepaid amortization is NOT cost recovery and is excluded — see R12.** **(proposed)**

---

### W2. R11's prepaid clause states the accrual answer inside the cash ruleset — and deleting it alone makes the deduction $0 forever

**Verified.** $1,200 twelve-month policy paid 12/01/2026, coverage to 11/30/2027. Payment `DR Prepaid Insurance 1,200 / CR Bank 1,200` — R1(a) fires, R3 finds no P&L leg, R4's carve-out keeps it balance-sheet → **$0**. Amortization `DR Insurance Expense 100 / CR Prepaid Insurance 100` — R11 fires → **$100** in FY2026. Correct is **$1,200**: Reg. §1.263(a)-4(f), benefit ends 11/30/2027, before the close of the year following payment, so no capitalization is required and a cash-method filer deducts when paid. $1,100 of deduction shifted a year.

R11 contradicts its own stated rationale — §§167/168/179 do not touch a prepayment; §1.263(a)-4(f) does, and it keys on the benefit period, which no account type can express.

**Attacker angle 2 is wrong that deletion alone fixes this.** Delete "or prepaid-asset" with nothing else and the payment recognizes $0 (R4 carve-out) and the amortization recognizes $0 (no rule fires) — cash-basis insurance becomes **$0 forever**, worse than today. The deletion must ship with R12.

**Insert after R11:**

> - **R12 — Prepayments recognize at payment, not on the amortization schedule. (proposed)** A **prepaid-asset leg reached by a recognition event** — directly, or pro-rata through an R4 settlement of a bill that composed to a prepaid — recognizes its full amount on the **cash** basis at that date whenever the 12-month rule is satisfied (Reg. §1.263(a)-4(f): the benefit does not extend beyond the earlier of 12 months after first realization or the end of the tax year following payment). That is the modal case: a 12-month insurance premium, an annual software subscription. The later amortization entries then recognize **nothing** on cash. Where the benefit runs past that window the prepayment stays capitalized on both bases, its amortization lines are emitted with `LineReason.COST_RECOVERY`, and they recognize under R11 instead. **Exactly one of the two branches recognizes, never both.** This is the one exception to R4's balance-sheet carve-out on the cash side, because the cash method *does* govern the timing of a payment; it does not govern §§167/168/179/197 cost recovery (R11). The accrual view amortizes in every case, so a prepaid is a legitimate cash/accrual delta and an enumerated term of the layer-5 gate.

Requires: `PREPAID_ASSET` DetailType, `Prepaid Expenses` in the seed COA, `COST_RECOVERY` in `LineReason`.

---

### W3. Onboarding's new CASH branch puts a $12,000 asset on the books twice, with a balanced trial balance

**Verified, and it is the page's own worked example.** Prior TB 12/31/2025: Checking 5,000 DR; Machinery 12,000 DR; Accum Dep 2,000 CR; AP 12,000 CR; Owner's Equity 3,000 CR (ties at 17,000).

Opening JE with AP stripped by rule 5 → DR 17,000 / CR 5,000 → rule 3 plugs **CR OBE 12,000**.
- `ACCRUAL`: historical bill `DR OBE 12,000 / CR AP 12,000` → OBE nets to 0, Machinery 12,000. Correct — and correct *by construction*, because the OBE debit exists to cancel the plug.
- `CASH` (per `onboarding-opening-balances.md:28`): `DR Machinery & Equipment 12,000 / CR AP 12,000` → nothing cancels the plug. **Machinery = 24,000.** TB ties (29,000/29,000). NBV 22,000 looks plausible. R11 then depreciates the duplicate every year.

I traced the AR and expense cases too: they do **not** double, because income and expense accounts were closed to equity in the prior TB. The defect is specific to historical documents whose composition is a **balance-sheet** account — which is exactly the case rule 6 illustrates. `onboarding-opening-balances.md:29` ("nothing appears twice on either basis") is false; self-balancing is not non-duplicative.

**Rule 5 → replace with:**

> 5. **Double-count rule:** the opening JE **never includes AR/AP lines** — compose rejects them; AR/AP at books start is built exclusively from the historical open documents. **It must equally never include a balance-sheet account that a historical open document's own composition will post. (proposed)** Under `ACCRUAL` the historical document's offsetting leg is OBE, which cancels the opening JE's plug by construction, so nothing can double. Under `CASH` the offsetting leg is a real account — and a prior trial balance already carries every balance-sheet account, because only P&L accounts were closed to equity. A $12,000 machine on a pre-conversion unpaid bill otherwise lands **twice**, the trial balance still ties, net book value still looks plausible, and R11 depreciates the duplicate for seven years.

**Add as a bullet under rule 6:**

> - **Under `CASH`, a historical open document carries its real composition only where that composition is a P&L account.** Where it is a **balance-sheet** account the prior trial balance already carries it, so the document offsets **OBE** instead (`DR OBE 12,000 / CR AP 12,000` for the machine). The recognized result is identical either way — R4's balance-sheet carve-out and R2's OBE exclusion both recognize nothing — so this changes only the balance sheet, and it is the difference between one machine and two. **(proposed)**

**Replace the `:29` bullet with:**

> - Under `CASH` the pre-`books_start_date` date keeps the line out of every reported period, and each historical document is self-balancing on its own. **Self-balancing is not the same as non-duplicative:** a P&L-composed document adds an account the prior trial balance never carried, so it cannot double; a balance-sheet-composed one would, which is why it offsets OBE instead. **(proposed)**

**Add:**

> - Under `CASH`, OBE does **not** net to zero after migration — the plug offsets pre-period P&L that flows to computed Retained Earnings, so equity is correct in total but split across two lines. `NONZERO_OBE` ([[safety-nets]]) fires on this branch and not on `ACCRUAL`; that is expected, not a missed check. **(proposed)**

---

### W4. R5a's trigger is an account+ref pattern with no intent predicate — it fabricates receipts out of routine cleanup and error back-outs

**Verified.** The trigger is "a posting that debits AP carrying a ref and credits AR carrying a ref." Two postings that satisfy it and must not:

- Month-end cleanup, one JE: `DR Bad Debt 1,500 / CR AR 1,500 ref:INV-0061 (Northwind)` + `DR AP 400 ref:BILL-0022 (Staples) / CR Office Supplies 400`. Fires. min(400, 1,500) = 400 → **$400 of gross receipts and $400 of deductions** on unrelated parties, no money, nothing extinguished. Correct: **$0.00**. Written as two JEs it fires in neither — R5a's own closing sentence ("Determinism is the point") is still false.
- Duplicate back-out: `DR AP 1,000 ref:B-77 / DR Sales 1,000 / CR Expense 1,000 / CR AR 1,000 ref:INV-104`. Fires → **$1,000/$1,000 fabricated** out of a pure error correction, with R5a's third bullet suppressing the two reversal legs.

This also breaks `bad-debt-nothing`, which the same page still lists as a CPA endorsement.

**Attacker angle 2's proposed same-counterparty fix is wrong** — angle 4 is right that a payment made to my vendor by my customer at my direction is constructive receipt and payment with *different* counterparties (Old Colony Trust, 279 U.S. 716). Mutuality would break R5a's clearest case. The correct predicate is **declared intent**, which `LineReason` (an already-admitted GL column, machine-set enum) can carry and DuckDB can read.

**Replace R5a's first sentence with:**

> - **R5a — Mutual offsets ARE a recognition event. (proposed)** A posting that **debits AP carrying a ref and credits AR carrying a ref, where both legs carry `line_reason = OFFSET_SETTLEMENT`** ([[general-ledger-sheet]] `LineReason` gains this member) extinguishes both obligations, which on cash basis is **constructive receipt and constructive payment** on that date. R5a **never fires on a posting of `type = Reversal`, nor on any leg whose `line_reason` is a reversal or correction** — an error back-out that touches AP and AR is not a settlement, and an account+ref pattern alone fabricates receipts and deductions out of a duplicate back-out or a month-end JE that batched an unrelated bad debt with an unrelated vendor credit. **Mutuality is deliberately NOT required**: a payment made to my vendor by my customer at my direction is constructive receipt and payment even though the counterparties differ (Old Colony Trust, 279 U.S. 716) — which is why the predicate is declared intent, not same party. Nothing about the taxpayer's position differs from receiving a cheque and posting one back the same day; R5 previously swept this in with credit notes and was wrong.

---

### W5. R5a fixes the offset amount but never says how it is allocated across multiple refs

**Verified.** "its share of that amount" is undefined whenever one side's ref-carrying legs exceed the offset. `DR AP 1,000 ref:BILL-1 (contract labor) / DR AP 600 ref:BILL-2 (a used compressor, capitalized) / CR AR 1,200 ref:INV-9 / CR Other Income 400` → offset 1,200 against 1,600 of AP.

- Pro-rata: Schedule C line 11 = **$750**, $450 to basis.
- Oldest-first (the tie-break the matching cascade uses elsewhere, so an implementer will reach for it): line 11 = **$1,000**, $200 to basis.

$250 of current deduction plus a different fixed-asset basis carried into every future R11 year, on an unwritten choice. Angle 3's three-AR-document variant spreads gross receipts $1,350 / $1,543 / $1,800.

**Append to R5a bullet 2:**

>   - **Allocation is pro-rata by leg amount, on both sides.** Where one side's ref-carrying legs exceed the offset, each settled document's share is `offset × (its ref-carrying leg ÷ that side's ref-carrying total)`, rounded to the cent with the largest remainder to the largest leg. Ordering rules (oldest-first, largest-first) are forbidden **here**: R4 recognizes pro-rata *per settled document*, so allocation order changes the recognized composition — on AP legs of $1,000 (contract labor) and $600 (a capitalized compressor) against a $1,200 offset, pro-rata deducts $750 and capitalizes $450 while oldest-first deducts $1,000 and capitalizes $200. Pro-rata is the only order-free answer and matches R4's own doctrine. The un-offset remainder stays open and settles later on its own terms.

---

### W6. R1(a)'s three-name money-account list moves the modal buyer's year-end receipts into the wrong year, every year

**Verified.** R1(a) enumerates "Bank/Cash/Credit Card". A Stripe/PayPal/Shopify Payments balance is none of the three, so no recognition event exists until the bank credit. Orders 12/28–12/31/2026 settling into the Stripe balance, payout landing 01/02/2027: **$4,150 of gross receipts and $157.56 of fees fall into 2027**, while Stripe's 2026 Form 1099-K reports the $4,150 by transaction date. A CP2000 gross-receipts mismatch on the design's own stated persona.

The log parks this as "entry-path work, not ruleset work." That is wrong: R1(a)'s account list is what fixes the recognition *date*, and a closed literal list cannot be extended later without revising the ruleset after books exist — the precise thing `cash-basis-recognition.md:14` forbids. Funds credited to a processor balance the taxpayer may draw on are constructively received (Reg. §1.451-2(a); the processor holds as agent).

**Replace R1(a) with:**

> A document recognizes on cash basis when it (a) moves a **money account** — any account whose funds the taxpayer may draw on demand: Bank, Cash, Credit Card, **and processor / merchant-clearing balances (Stripe, PayPal, Shopify Payments), which the processor holds as the taxpayer's agent and which therefore recognize on credit to the balance, not on payout** (Reg. §1.451-2(a)); amounts under a mandatory rolling reserve are a substantial limitation and recognize on release, and the payout itself is a Transfer (R8). The set is `detail_type ∈ MONEY_ACCOUNT` ([[chart-of-accounts]]), **never a literal list** — a closed three-name list moves a Shopify seller's year-end receipts into the following year while the 1099-K reports them by transaction date. **(proposed)**

Requires: `MERCHANT_CLEARING` DetailType and a `Merchant Clearing` seed account.

---

### W7. R10's money-in half has no "presently payable" qualifier, and no trigger at all

**Verified, two distinct defects in one bullet.**

*Doctrine.* "Money in recognizes when the **instrument is received**" is stated as an absolute while the money-out half carries its qualifier. A $5,000 cheque handed over 12/31/2026 dated 01/05/2027 recognizes in 2026 — **$5,000 of income a year early**, on money the taxpayer cannot touch (Reg. §1.451-2(a): substantial limitation).

*Trigger.* "Ask narrowly… only for rows the file itself marks cheque-shaped" is shape-based. An $8,000 customer cheque received 12/29/2026 and deposited 01/03/2027 appears as `01/03 DEPOSIT 8,000.00` — no cheque marker exists on an incoming deposit row in any bank CSV. No question is asked, and **$8,000 of 2026 gross receipts lands in 2027**. R10's money-in half is inert.

*Card carve-out.* "For a credit-card import the recognition date *is* the file's transaction date and is never asked" — plan Task 5.3a defines `parse_statement -> (date, description, amount, direction)`, **one date field**. Where the export carries only a posting date (bank-issued card CSVs; OFX `DTPOSTED` required, `DTUSER` optional), R1(b)'s date is not in the file, and the one control that would catch it has been explicitly switched off for that file type. $2,400 of 12/29–12/31 ad spend posting 01/02 moves a year.

**Replace the money-in clause and the "Ask narrowly" sub-bullet with:**

> …money in recognizes when an instrument that is **presently payable and unrestricted** is received — a cheque handed over on 12/31 is that year's income even if the bank is shut (*Kahler*, 18 T.C. 31) — not when it is deposited or when the deposit settles. A **post-dated** cheque, or funds under a substantial limitation (escrow, a processor's mandatory reserve), recognizes when it first becomes payable or available (Reg. §1.451-2(a)).
>
>   - **Ask narrowly, and asymmetrically. (proposed)** **Money out:** only for rows the file itself marks cheque-shaped, within `cutoff_ask_days` of the fiscal year start. **Money in:** every receipt row in that window is asked when the payment reached the taxpayer — a deposit row carries no marker that could narrow it and the instrument-received date is never in the file, so a shape test leaves R10's money-in half with no trigger at all; that is two or three taps in January, not the twenty-row interrogation the narrowing was written to avoid. For a **credit-card** import the recognition date *is* the file's **transaction (charge)** date under R1(b) and is never asked — **but only where the column mapping identifies a transaction date distinct from the posting date**; a card file supplying one settlement date does not contain R1(b)'s date and those rows are asked on the same terms as cheque rows. `StatementRow` therefore carries `txn_date` and `post_date` separately and the `IMPORT_RUN` records which column was used. `cutoff_ask_days` is an operational threshold on the versioned [[policy-set]], not a phrase.

---

### W8. The canonical page contradicts its own derived page on the layer-5 gate — and **both** wordings are wrong

**Verified.** `cash-basis-recognition.md:35` still reads "differ *exactly* by unpaid/**non-cash** items"; `testing-strategy.md:18` reads "differ exactly by **unpaid documents — never by non-cash P&L entries**". A test author reading the canonical page (which its own line 12 declares is THE definition) writes the assertion R11 exists to defeat, it fails on the depreciation fixture, and the cheapest way to make it pass is to drop depreciation from `v_pnl_cash`.

**But the corrected wording is also wrong.** It fails a *correct* Golden Company by $7,000: a $5,000 retainer received 11/15/2026 and earned in 2027 is a delta on a **paid** document (R6, CPA-endorsed); a $2,000 bad-debt write-off is a delta that is exactly a **non-cash P&L entry** (R5, CPA-endorsed). Both are scenario-catalog rows, so the Golden Company contains both. Angle 3's regression check — "layer 5's rewording is now consistent" — is wrong.

**Replace the last sentence of `cash-basis-recognition.md:35` AND `testing-strategy.md:18`'s clause with the same text:**

> On any fixture ledger the accrual-vs-cash delta must reconcile **line by line to an enumerated set — unpaid documents (R4), retainers recognized at receipt (R6), non-cash settlements such as a bad-debt write-off (R5), prepaid timing (R12) — with an unattributed cent failing the gate, and cost-recovery entries (R11) contributing exactly 0.00.** Both prior wordings were wrong: "unpaid/non-cash items" licensed the R11 cost-recovery bug; "unpaid documents only" fails a correct ledger by the retainer and the write-off. **(proposed)**

---

### W9. R3 recognizes a bad-debt haircut that rode in with a payment — overstating gross receipts and taking a deduction §166 disallows

**Verified.** INV-100 $1,000; customer pays $900 and disputes $100, one Payment document: `DR Bank 900 / DR Bad Debt 100 / CR AR 1,000 ref:INV-100`. R4 pro-rata (applied ÷ total = 100%) → **$1,000** of gross receipts against a **$900** deposit. R3 (direct P&L leg) → a **$100 bad-debt deduction** a cash-method filer may not take (Reg. §1.166-1(e); a cash-basis receivable has zero basis). Net profit is right, line 1 and the deduction are not.

Post the identical economics as a no-money offset and R5a gives $900/$0. Same event, two answers, decided by whether cash rode in the posting. R3's own rationale ("cash income ties to bank deposits") is false here.

**Append to R3, and define `applied` in R4:**

> …they accompany real cash, so cash income ties to bank deposits. **Except a leg that writes off part of the settled document's own principal above `match_tolerance` — bad debt, forgiveness, a negotiated haircut: it recognizes nothing (R5) on either side of the posting, and R4's `applied` for that document is reduced by it. (proposed)** Otherwise a $900 payment on a $1,000 invoice with a $100 write-off reports $1,000 of gross receipts against a $900 deposit plus a deduction Reg. §1.166-1(e) disallows. The $0.99-tolerance leg is the stated exception — immaterial by construction, and it posts to Sales Discounts / Bank Fees rather than writing off principal.

R4: "`applied` = the settling AR-credit (or AP-debit) amount **less any write-off leg of that document in the same posting**."

---

### W10. Rules are described as an allowlist with no uniqueness clause — the natural union implementation double-recognizes

**Verified.** Asset sold: `DR Cash 900 / DR Accum Dep 2,400 / CR Computer Equipment 2,400 / CR Gain on Disposal 900`. R1(a)+R3 recognize the gain; transaction-scoped R11 recognizes the same line again → **+$1,800 on a $900 sale**. The line-level R11 fix in W1 removes this specific collision, but nothing states the general invariant, and "recognizes on **both** bases" invites adding depreciation to the accrual view a second time.

**Insert above R1:**

> **How the rules compose. (proposed)** R1–R12 are a priority-ordered predicate evaluated **once per `gl_line`**, not a union of recognition events: **every line recognizes at most once, on exactly one date.** They add lines to `v_pnl_cash` only — `v_pnl` (accrual) contains every P&L line by construction and is never modified by a recognition rule. **Disposals of depreciated assets are out of scope:** gain or loss is §1245/§1231 Form 4797 income, not Schedule C and not subject to SE tax, so no `tax_line` may map a disposal account to a Schedule C line.

---

### W11. R1(c) hardcodes `DR Expense` — the same defect the last pass fixed in `prior_return_basis`, unfixed on the canonical page

**Verified.** R1(c) and `scenario-catalog.md:36` both give one template: `DR Expense / CR Owner's Contributions`. A $4,200 camera on the owner's personal card must be capitalized — the de minimis safe harbor for a taxpayer with no AFS is $2,500 per item (Reg. §1.263(a)-1(f)). The template expenses it in full; with R11 in force a §179 election then deducts it again. **$8,400 on a $4,200 asset.** R4 on the same page says the opposite for the identical purchase made on a bill.

**Replace R1(c):**

> …or (c) records an **owner-paid business purchase** — sole prop: the owner's personal payment IS the taxpayer paying (`DR <the account the purchase actually was> / CR Owner's Contributions`, recognizes at transaction date, [[scenario-catalog]]). **The debit is whatever was bought, including a balance-sheet account** — a $4,200 camera composes `DR Camera Equipment`, not `DR Equipment Expense`; hardcoding an expense defeats R4's carve-out and, with R11 in force, deducts the asset at purchase and again through §179/MACRS. Only P&L legs recognize (R3). **(proposed)**

Mirror verbatim in `scenario-catalog.md:36`.

---

### W12. The residual has no period predicate — a completed rec stops being reproducible

**Verified.** `bank-reconciliation.md:30` defines uncleared as "*no `rec_clears` row for that triple*", unqualified. December rec on 01/05: statement 8,000, book 5,550, one outstanding cheque 2,450 → residual **0.00**, month locked. February 3, the January rec appends the clearing row. Any re-run of December — the packet reprint, `verify_books`, an accountant re-performing the month, the Golden Company on a later commit — now computes **+2,450**. The page's own headline claim is that the rec is re-performable.

**Replace the last sentence of `:30`:**

> "Uncleared **as at a period end**" means: no `rec_clears` row for that triple whose `statement_period` ends on or before that period end. The qualification is not optional — unqualified, a December residual of 0.00 silently becomes the outstanding-cheque amount the moment the January run appends its rows, and a completed rec stops being reproducible. Every residual is a function of a period, never of the sheet's current state. **(proposed)**

---

### W13. The CLEARING lock rule is inoperable — two `verified` pages contradict each other

**Verified.** `bank-reconciliation.md:38`: "a `CLEARING` dated at or before `locked_through` is refused." `dates-and-timezones.md:25,28`: `cleared_at` is a Decision instant and "never faces `locked_through`". `cleared_at` is the clearing's only date. Compare it and the rule never fires for any clearing ever; compare the paired GL line's date and the rule is correct. Nothing says which.

Compounding: the `Reconciliations` row shape has no state column, and "superseded by a later row" can only restate `statement_period`/`rec_id` — never *not cleared*. A mis-pairing permanently removes a line from every future outstanding-items term.

**Replace the bullet:**

> - **Clearings never reach a locked period.** A `CLEARING` is tested against the **accounting date of the GL line it pairs** — never against `cleared_at`, which is a decision instant and by [[dates-and-timezones]] never faces `locked_through`. A clearing on a line dated at or before `locked_through` is refused; correcting a closed month's reconciled state is an `AMENDMENT` [[process-instance]] like any other post-lock change. The `Reconciliations` sheet carries a `state` (CLEARED|UNCLEARED) column and the effective state of a triple for a period is its latest row — without it an erroneous pairing is permanent, because the sheet is append-only and a superseding row can only restate *which* statement cleared it. **(proposed)**

---

### W14. R10 and R11 both delegate to `period-locking-month-close`, which still says "Year-end close: nothing to do"

**Verified by reading the file.** Four close steps, none fiscal-year-conditional; section heading `## Year-end close: nothing to do`; `sources:` omits the tri-persona review; plan Task 7.3 carries no precondition. R10 is therefore still inert for anyone building from the page that owns the close: cheque #1043 for $3,800 written 12/28/2026, December locked 01/03/2027, January statement imported 02/03 → the true date is refused, [[general-ledger-sheet]] rule 4 redirects it into 2027. **FY2026 Schedule C line 11 short $3,800.** Identical to the pre-fix outcome.

R11 needs the same precondition and did not get one: `date > locked_through` refuses a 12/31 posting once `locked_through = 12-31`, and depreciation/§179 is computed at tax prep in February–April. (Angle 1's "R11 is inert end-to-end" overstates it — `AMENDMENT` exists — but the precondition is the right primary path.)

**Replace the `## Year-end close: nothing to do` section with:**

> ## Year-end close: no closing ENTRIES, but two preconditions (proposed)
>
> No closing entries ever — **Retained Earnings is computed** in balance-sheet SQL (cumulative prior-year net income; current-year net income shown as its own equity line). `fiscal_year_start` just tells reports where years cut ([[reports-and-analytics]], [[dates-and-timezones]]).
>
> A `CLOSE_RUN` whose period ends the **fiscal** year has two step-0 preconditions the monthly close does not:
>
> 1. **Cutoff dispositioned.** The following month's statement is imported for every money account and every pre-year-end item on it is dated at its true recognition date ([[cash-basis-recognition]] R10). A cheque written 12/28 clears in January and the lock would otherwise refuse its true date, moving a deduction a whole year invisibly to the rec. **The cutoff pass is separately gated ahead of the lock:** it must be dispositioned before `1099_payments` or the accountant packet renders for that tax year, because information returns are due 01/31 and cannot wait for a card statement that closes 02/15 (a $400 December cheque to a contractor otherwise leaves a $850 payee reading $450, and no 1099 is filed — §§6721/6722). The pass also asks in words for **R5a events, which leave no statement footprint at all**: offsets, barters, and payments made on the taxpayer's behalf agreed before year end.
> 2. **Cost recovery posted.** Depreciation / §179 / amortization entries for the year are posted at 12/31, or a `HUMAN` [[decision-record]] declares there are none ([[cash-basis-recognition]] R11) — these are computed at tax prep, after the close, and `date > locked_through` refuses a 12/31 posting once the year is locked.
>
> Either found afterwards is an `AMENDMENT` ([[process-instance]]) that unlocks, posts at the true date and re-locks. A precondition is not an `ExceptionKind` — exceptions never block ([[safety-nets]]) — but a close may legitimately refuse to run.

---

### W15. `safety-nets`' `CUTOFF_DATE_UNCONFIRMED` row is the broad pre-narrowing form — 22 exceptions on a 22-row card CSV

**Verified.** `safety-nets.md:22` declares "this page owns the vocabulary" — it is the row an implementer codes to — and `:40` carries no cheque-shape test, no threshold, no card exclusion. A 22-row Amex CSV imported 01/20 raises **22** `CUTOFF_DATE_UNCONFIRMED` exceptions, each needing a disposition; R10 says **0**. That is verbatim the interrogation the narrowing was written to remove.

**Replace the row:**

> | `CUTOFF_DATE_UNCONFIRMED` | a money-**out** row the file marks **cheque-shaped**, or any money-**in** row, dated within `cutoff_ask_days` of the fiscal year start — the statement date is a *clearing* date, not the recognition date ([[cash-basis-recognition]] R10). **Never raised on a credit-card import whose mapping supplies a transaction date distinct from the posting date** (R1(b)). | `IMPORT_RUN` + the fiscal-year-end close |

---

### W16. Plan Task 3.2 freezes the wrong `Reconciliations` schema, on an append-only sheet

**Verified.** Plan line 262: "(txn_id, statement_period, rec_id, cleared_at)". Wiki `sheets-layer.md:27` and `duckdb-layer.md:16` both specify the `(txn_id, account_number, side)` triple. `log.md:136` says the schema "freezes on an append-only sheet at Task 3.2" — and Task 3.2 was not in the list of tasks the commit updated. A Checking→Savings transfer of $5,000 clearing on the January Checking statement reads cleared on the Savings leg too → **residual −5,000.00** on a clean month, posted to Reconciliation Discrepancies, unfixable after the first company is provisioned.

**Replace the parenthetical in Task 3.2:**

> **Plus `ensure_reconciliations_sheet(company)`** — a third per-company sheet at the company folder root, columns `txn_id`, **`account_number`**, **`side`** (DEBIT|CREDIT), `statement_period`, `rec_id`, **`state`** (CLEARED|UNCLEARED), `cleared_at`, **keyed by the `(txn_id, account_number, side)` triple** (wiki `sheets-layer`; a `txn_id`-only key marks a transfer cleared on both accounts at once and drives the second account's residual off by the whole transfer). Written by APPEND only; `cleared` is not a GL column and never a cell edit. **This schema freezes here** — the sheet is append-only, so a missing key column is unfixable after the first company is provisioned. Test: a Transfer cleared on account A leaves its account-B leg uncleared.

---

### W17. Plan Task 5.4 restates the residual in the bank-presentation vocabulary the wiki explicitly removed

**Verified.** Plan line 327: `(statement_ending + deposits_in_transit − outstanding_payments) − book_balance`. `bank-reconciliation.md:28` says in terms why that is fatal on a credit card. Amex, signed statement −2,400, uncleared payment DR 500, uncleared charge CR 180, signed book balance −2,080. Wiki formula: −2,400 + 500 − 180 = −2,080 → **0.00**. Plan formula as an implementer maps the nouns (no deposits; the $500 is a payment; the $180 charge has no bucket): −2,400 + 0 − 500 − (−2,080) = **−820.00** on a clean month.

**Replace the formula in Task 5.4 with the wiki's, verbatim:**

> `discrepancy_amount` is **redefined as the residual**, stated in **signed terms** (never "deposits in transit" / "outstanding cheques" — both invert on a credit card, which is a money account too):
> ```
>   signed_statement_ending_balance          (+ asset; − credit-card/liability)
> + Σ uncleared book DEBITS  to the account  (date ≤ period end)
> − Σ uncleared book CREDITS to the account  (date ≤ period end)
> − signed book balance (Σ DR − Σ CR) at period end
> = 0.00
> ```
> "Uncleared" is qualified by period: no `rec_clears` row for the triple whose `statement_period` ends on or before this period end. Cent-exact fixtures assert 0.00 on a clean month for **both a checking account and a credit card**, the exact residual on a seeded omission, and reproducibility (run December → run January → re-run December, still 0.00).

---

## 3. Regressions — correct before the last revision, damaged by it

1. **`testing-strategy` layer 5.** Was loose ("unpaid/non-cash items"), now too tight ("unpaid documents — never non-cash P&L entries"), and now **fails a correct Golden Company by $7,000** on the R6 retainer and the R5 bad-debt write-off, both CPA-endorsed and both cited two lines further down. Fixed by W8.

2. **Onboarding rule 5 vs the new `prior_return_basis = CASH` branch.** The `ACCRUAL` composition cancelled the OBE plug by construction; the `CASH` composition cancels nothing, so a QuickBooks migrator's $12,000 machine is on the books twice with a balanced TB, a plausible NBV, and OBE carrying the only evidence — which the standard "reclassify OBE" cleanup destroys. Rule 5 still bans AR/AP only, which was sufficient only under the old branch. Fixed by W3.

3. **R5 lost an unconditional guarantee.** R5 previously read "non-cash settlements recognize nothing, **ever**" — safe. R5a's carve-out is scoped by *posting*, so a bad-debt write-off now recognizes whenever it shares a JE with any ref-carrying AP debit. The page still lists `bad-debt-nothing` as a CPA endorsement it now breaks. Fixed by W4.

4. **R5a's third bullet states correct doctrine that untouched R3/R4 now contradict.** Before the revision the write-off-riding-a-payment case was handled consistently (if wrongly) by R3+R4. Now the same haircut recognizes $900 as an offset and $1,000-plus-a-disallowed-deduction as a payment. Fixed by W9.

5. **Plan Task 4.3 got worse.** It previously read "`v_pnl_cash` (settlement-proportional recognition via refs)" — vague but correct. It now instructs the implementer to build "the `prior_return_basis` branch in R4", a value Task 2.8 deliberately made unreachable from PolicySet and `duckdb-layer.md:17` makes structurally unreachable from the view. The only correct exits are to break the read boundary or to re-add the field. **Replace with:** "and R4's **OBE-composition test** (an AR/AP settlement whose settled document's offsetting composition is Opening Balance Equity recognizes nothing; every other composition recognizes pro-rata). **There is deliberately NO `prior_return_basis` branch in the view** — the answer was baked into the posted documents' composition at onboarding. Grep-test: `views.py` references no field outside `gl_lines`/`accounts`/`rec_clears`."

6. **`scenario-catalog` was the cleanest page in the wiki and is now internally inconsistent.** It carries a `(proposed 2026-07-30)` claim under `modified: 2026-07-17`, `sources: [raw/2026-07-17-design-doc.md]`, `status: verified`. The "newer sources supersede" scan will resolve its drift against R5a **backwards**. Its restatement has already drifted twice: it drops "carrying a ref" from the `min()` and drops R5a's money-leg carve-out, so on `DR AP 1,200 ref / DR Checking 800 / CR AR 2,000 ref` it recognizes $1,200 against a real $800 bank deposit — gross receipts short $800.

**Replace `scenario-catalog.md:39`:**

> | Customer is also a vendor — offset | JE: `DR AP ref:BILL / CR AR ref:INV` — both balances close. **On cash basis this is a recognition event (constructive receipt and payment); the amount, the intent predicate, the allocation and the treatment of every other leg are defined once in [[cash-basis-recognition]] R5a — this row states no amount. (proposed)** |

Set `modified: 2026-07-31`, add the tri-persona source.

---

## 4. Consistency checklist — file + change

| File | Change |
|---|---|
| `wiki/cash-basis-recognition.md` | Title → **R1–R12**. Apply W1, W2, W4, W5, W6, W7, W9, W10, W11. Add uniqueness preamble. R9 → "tax portion of amounts **recognized as received under R1 and R5a — including constructive receipt through a mutual offset** — not merely of cash deposited" (an offset otherwise recognizes the income and collects none of the embedded sales tax). Line 35 → W8. |
| `wiki/onboarding-opening-balances.md` | W3 (rule 5, rule 6 bullet, `:29`, OBE note). Reword the question to "Pull last year's Schedule C. Line F — is **Cash** or **Accrual** checked? If you did not file a business return, answer Cash." Add to the ACCRUAL row: filing cash after an accrual return is a §446(e) overall method change — record Σ open AR and Σ open AP at `books_start_date` as the implied §481(a) (= AP − AR; the ledger treatment is arithmetically equivalent) and raise `METHOD_CHANGE_3115_REQUIRED`, carried on the packet's face (Rev. Proc. 2022-14, DCN 233). Add: if `books_start_date` is not a fiscal-year start, the pre-books portion of the current tax year exists only inside the OBE plug — every report covering that year raises `PARTIAL_PERIOD`, carries `books_start_date` in its header, and the packet refuses a Schedule C mapping for it. |
| `wiki/period-locking-month-close.md` | W14. Add `raw/2026-07-30-tri-persona-review.md` to `sources`. |
| `wiki/bank-reconciliation.md` | W12, W13. |
| `wiki/safety-nets.md` | W15. Add `PARTIAL_PERIOD`, `METHOD_CHANGE_3115_REQUIRED`. Add tri-persona source. |
| `wiki/policy-set.md` | Add `cutoff_ask_days` to the **operational** threshold list ("drives an agent question that decides which tax year a deduction falls in, so it must resolve as-of the report's period and be stamped on the header"); correct the threshold count. `ruleset_versions {cash_basis: "R1-R12@<date>"}`. Add `books_start_date` to the report header field list. |
| `wiki/chart-of-accounts.md` | `detail_type` is **the recognition key, not report grouping** — a named `DetailType` enum; `MONEY_ACCOUNT` = {BANK, CASH, CREDIT_CARD, MERCHANT_CLEARING}; `CostRecovery` = {DEPRECIATION, AMORTIZATION, DEPLETION}; plus PREPAID_ASSET, ACCUMULATED_DEPRECIATION, ACCUMULATED_AMORTIZATION, UNEARNED_REVENUE, SALES_TAX_PAYABLE, EQUITY_OBE. **v_pnl_cash must never match on account name or number.** Seed COA gains **Merchant Clearing, Prepaid Expenses, Depreciation Expense, Amortization Expense, Accumulated Amortization, Machinery & Equipment, Sales Returns & Allowances**. |
| `wiki/general-ledger-sheet.md` | `LineReason` gains `COST_RECOVERY`, `OFFSET_SETTLEMENT` — note that the set freezes at the first posting. |
| `wiki/decision-record.md` | `DecisionKind` gains `PRIOR_RETURN_BASIS`, `MIGRATION_COMPLETE`, `CUTOFF_DATE_CONFIRMATION`, `STATEMENT_ROW_DISPOSITION`. Without the first two, the fix that moved `prior_return_basis` off PolicySet has nowhere to write. |
| `wiki/testing-strategy.md` | Layer 5 → W8, with a `(proposed)` marker. Add `given.{books_start_date, prior_return_basis, opening_balances, historical_open_docs[], statement{...}}` and `expect.{recognized{basis:{account:amount},period}, rec{residual, cleared[], outstanding[]}}` to the block table. Add tri-persona source. |
| `wiki/scenario-catalog.md` | Regression 6 + frontmatter. Fix the owner-paid row (W11). |
| `wiki/reports-and-analytics.md` | Bridge terms → **Δ(AR from P&L-composed lines) / Δ(AP from P&L-composed lines) / Δunearned, and nothing else.** Cost recovery is not a bridge term (R11: identical on both bases; the old "non-cash" term double-counts depreciation out of cash net profit — $58,400 reported against a `v_pnl_cash` of $56,000). AR/AP from balance-sheet-composed documents are not bridge terms (R4 carve-out). The bridge ties to `v_pnl_cash` to the cent: a presentation of the one definition, never a second one. |
| `wiki/sheets-layer.md`, `wiki/duckdb-layer.md` | Add `state` to the `Reconciliations` columns; add tri-persona source. |
| `wiki/index.md` | Update the cash-basis entry (R1–R12, cutoff, cost recovery, offsets) and the bank-rec entry (statement balances, signed residual, triple key). Add tri-persona source. |
| `plans/…-v1-plan.md` Task 1.1 | Enumerate `DetailType` in full (no ellipsis) and declare it the recognition key. Add the four `DecisionKind` members, `LineReason` values, `Side` (DEBIT/CREDIT). Rename `OriginType` → `OriginKind` with `document-model`'s five values. |
| Task 1.8 | Land the `given`/`expect` extensions above **before** the 25 YAMLs. Define `report_deltas` keys as `{report: {line_or_account: amount}}` with `schedule_c_<n>`. `expect.recognized` is evaluated by the Phase-1 helper, **not deferred to Phase 4** — otherwise every R1–R12 fixture asserts bookkeeping and nothing about recognition. |
| Task 1.9 | Split `ar_ap_offset` into `ar_ap_offset_equal`, `ar_ap_offset_walkaway` (multi-ref, one expense bill + one capitalized bill, asserts pro-rata), `ar_ap_offset_cross_party` (unrelated bad debt + vendor credit in one JE → 0.00, identical to two JEs), `ar_ap_offset_with_cash_leg` (R1(a)/R4 govern, full composition). **Delete `ar_ap_offset` from the line-195 list** — one filename is currently specified twice with different contents. Add `prepaid_12_month`, `prepaid_multi_year`, `bundled_yearend_je`, `prior_return_cash_capitalized_bill_no_double_count`, `merchant_clearing_year_end`, `rec_reproducibility`. Retarget `depreciation_and_179` to mandate the contra form and assert the direct-write-down form also recognizes. |
| Task 3.2, 5.4 | W16, W17. |
| Task 4.3 | Regression 5 + line-level R11 + R12; drop "prepaid" from the R11 clause. |
| Task 5.3a | `parse_statement -> StatementRow(txn_date, post_date, description, amount, direction)`. |
| Task 5.3b | Add the R10 cutoff ask (asymmetric; card exclusion conditional on a distinct transaction-date column). Test: a 22-row January card CSV raises zero; one cheque row on a January bank CSV raises one. |
| Task 7.2, 7.3 | Bridge rewrite; year-end preconditions; cutoff pass gates `1099_payments` and the packet. |
| Frontmatter sweep | Add `raw/2026-07-30-tri-persona-review.md` to `sources` on testing-strategy, duckdb-layer, safety-nets, sheets-layer, scenario-catalog, period-locking-month-close, index. `scenario-catalog` → `modified: 2026-07-31`. Add `(proposed)` markers to every changed claim, including `testing-strategy:18`, which currently has none. |

Lower-priority, non-blocking: `context-assembly`'s "reads Mongo, never DuckDB" vs the SETTLEMENT lens needing open balance by ref — resolve by stating that ledger facts inside a dossier are read through the same `v_*` views (the boundary is about where context is *stored*), not from Mongo's derived-status cache.

---

## 5. Attacker errors

Named plainly; do not action these.

- **Angle 2: "R5a needs a same-counterparty test."** Wrong. Angle 4 is right that a payment made to my vendor by my customer at my direction is genuine constructive receipt and payment with *different* counterparties (Old Colony Trust). Requiring mutuality would break R5a's clearest case. The predicate is declared intent (W4).
- **Angle 2: "delete prepaid from R11 and defer prepaids to out-of-scope."** Wrong and harmful. Deletion alone makes cash-basis insurance $0 forever — worse than the $100/month bug it replaces. R12 must ship with the deletion.
- **Angle 3's regression check: "layer 5's rewording is now consistent with R11 and correctly retires the phrasing."** Wrong. Angle 1 proved it fails a correct Golden Company by $7,000 on R5 and R6. Both wordings are defective (W8).
- **Angle 1: "`normal_balance` is mis-derived for Accumulated Depreciation, so `v_lines` signs it wrong."** Arithmetically false. Accum Dep as a debit-normal Asset with a credit balance signs to −2,400, producing the correct net book value. It is a presentation-label nit, not a numeric defect — and R11 must not key on `normal_balance` in any case.
- **Angle 1: "R11 is inert end-to-end without a hard close precondition."** Overstated. The `AMENDMENT` path already exists and is the general answer for any post-lock correction. The precondition is the right *primary* path and I have landed it (W14), but the rule is not inert.
- **Angle 4: "R10's year-end precondition causes the missed 1099."** Causation is backwards. The precondition delays the *lock*, not the arrival of data; the cheque is absent on 01/28 with or without R10. The valid finding underneath — the cutoff pass must gate the information returns independently of the lock — is landed in W14.
- **Angle 4's own retraction, worth recording:** R11 does **not** miss §195 start-up amortization, §197 intangibles, or §168(k) bonus. All three credit Accumulated Depreciation or Accumulated Amortization and match the test as written. The real gaps were the direct write-down and the missing seed accounts.
- **Angle 3: `PriorReturnBasis` "has nowhere to live."** It is already in plan Task 1.1's enum list. Only the `DecisionKind` that carries it is missing.

---

## 6. Residual risk

**The processor / merchant-clearing path (W6) is the one edit in this memo that is brand-new ruleset text nobody has attacked, and it touches the modal buyer's every transaction.** Making a Stripe balance a money account rewires four rules at once: gross receipts now recognize on credit to the clearing balance rather than on payout (R1a), processor fees now recognize inside the clearing account rather than at deposit (R3), refunds and chargebacks now take negative recognition at the clearing date rather than the bank date (R7), and the payout becomes a Transfer between two money accounts (R8). Any one of those four being off by a date moves December receipts across a year boundary in the exact direction the 1099-K will contradict.

**How I would find it:** author one fixture — the Shopify persona's 12/20–01/05 at the real grain (gross orders, per-transaction fees, a refund, a chargeback, a rolling reserve, a 01/02 payout) — and assert three things simultaneously: (a) FY2026 Schedule C line 1 equals the 2026 1099-K gross to the cent; (b) the four-term signed residual on the Merchant Clearing account ties to 0.00 against a December Stripe balance statement; (c) the reserve balance recognizes on release and not before. If any of those three disagree, the money-account generalization is wrong somewhere and it will be wrong for every seller.

The general control that catches this class rather than this instance is the **attribution gate** in W8: build the accrual-to-cash bridge as a computed line-by-line reconciliation over the Golden Company's ~200 transactions and require every cent to carry an attribution tag from the enumerated set. An unattributed cent is the alarm — it is the only test in the suite that can surface a recognition rule nobody wrote down.
