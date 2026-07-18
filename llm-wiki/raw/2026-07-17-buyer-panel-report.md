# Buyer-Lens Review: SoloBooks v1

**Concept shown:** Chat-driven bookkeeping via Claude (MCP): books in view-only Google Sheets (portable GL + COA), double-entry with approval previews, append-only audit trail, month locking, intelligent payment matching (partial/multi/retainers→unearned revenue), PDF invoice artifact, reports incl. P&L cash/accrual, aging, project profitability, 1099s, ad-hoc queries. v1 excludes: bank feeds/CSV import, invoice emailing, online payment links, receipt scanning, recurring transactions, time tracking, mileage, quarterly tax estimates, payroll. Requires Claude.
**Price shown:** none — noted as concept attribute (all 15 respondents reacted to its absence).
**Panel:** solo consultants × 5, creators/digital sellers × 5, CPA/bookkeeper advisors × 5. Method: SSR (free-text first, model-judged anchor mapping).

## Headline

| Segment | n | Mean PI | Distribution (1..5) | Top objection theme |
|---|---|---|---|---|
| CPA/bookkeeper advisor | 5 | 2.91 | 8% / 26% / 39% / 22% / 5% | client narration = garbage-in; can't recommend without a price |
| solo consultant | 5 | 2.68 | 16% / 31% / 28% / 19% / 6% | no bank feed = more work than incumbent |
| creator/digital seller | 5 | 2.65 | 19% / 32% / 23% / 19% / 8% | manual entry friction kills the habit; missing payment links |

The concept converts the **spreadsheet-DIY, AI-native buyer** (consultant-3 EV 3.73, creator-4 EV 3.82 — both already pay for Claude Max, both currently on fragile self-built sheets) and genuinely intrigues the **advisor channel** (highest segment mean; the portable, tied-out Google Sheets ledger is the first thing that made the EA "stop and think in years"). Intent decays hardest wherever an incumbent already automates data capture (FreshBooks/QBO/bookkeeper users: EVs 1.91–2.73) — the single highest-leverage fix is killing the "I am the data pipe" objection (bank/CSV import), named by 11 of 15 respondents.

## Workflow coverage map

| Persona workflow (cadence) | Coverage | Note |
|---|---|---|
| Send invoice + get paid online (weekly) | **Named-only** | PDF artifact exists; no email send, no payment link — B5 hard stop, incumbents all have it |
| Expense capture from bank/card (weekly-monthly) | **Missing** | v1's biggest gap; every incumbent has feeds; narration = "more work dressed up nicer" (B2) |
| Recurring/retainer auto-billing (monthly) | **Missing** | A4's sacred workflow; FreshBooks earns its $35 here |
| Who-owes-me / AR chasing (weekly) | **Covered** | AR aging + matching resonated hardest with A5, B4 (lost $1,500 to unchased sponsor) |
| Per-client/launch/project profitability (monthly) | **Covered** | The #1 resonator across A1, A4, B1; incumbents weak here |
| Deposits/retainers booked correctly (monthly) | **Covered** | B5's CPA-sigh problem solved; unique vs FreshBooks/QBSE |
| Clean books for tax prep (annual) | **Covered** | C3: "I'd just prepare the return" — the portable ledger is the advisor hook |
| Quarterly estimated taxes | **Missing** | B1 relies on QBSE's; single mention, not a chorus |
| Receipts/audit support | Missing | Barely raised (folder convention suffices for v1) |
| Completeness assurance (monthly) | **Named-only** | Bank tie-out at close exists and C4 called it the one control that matters — surface it louder |

## Competitive read

- **Status quo per segment:** consultants — FreshBooks $19–35 or DIY sheets; creators — QBSE $15–25, Wave free, or a $300/mo bookkeeper; advisors — QBO ProAdvisor stack ($30+/client) with a quiet spreadsheet underclass they tolerate.
- **Incumbent overlap:** invoicing + reports duplicate FreshBooks/Wave/QBSE; the redundancy objection fires exactly where feeds exist. Zero overlap on: portable ledger, real double-entry with controls, chat interface, ad-hoc queries.
- **Named alternatives (verified):** QuickBooks Solopreneur $15–25/mo (feeds, quarterly taxes, mileage), Wave free (+2%+50¢ processing), FreshBooks $19–35 (feeds, payment links, recurring, time tracking).
- **Unclaimed pains (cheapest wins):** per-project/launch profitability; deposits-as-unearned-revenue; the January handoff (advisor-readable books); "who's at day 47" AR visibility for non-software users.

## Per-respondent detail

### consultant-1 — 38yo brand consultant, $180k, FreshBooks $19 | {1:.08 2:.32 3:.42 4:.15 5:.03} | EV 2.73
> "Intrigued but not sold. The client profitability thing — that's my actual pain point with FreshBooks, so you're poking at a real bruise. But… no bank feed means I'm narrating every transaction to a chatbot instead of just reviewing what it pulled. That's a step backward for my 60-transaction categorization routine. Pricing unknown is annoying… Come back when there's a number."
resonated: per-client profitability | objection: narration vs feed | incumbent: FreshBooks | price: wants a number to anchor vs $19

### consultant-2 — 51yo IT consultant, CPA-run QBO, satisfied | {1:.35 2:.45 3:.15 4:.04 5:.01} | EV 1.91
> "Not likely… What you're describing sounds like I'd be doing the bookkeeping myself, just by chatting instead of clicking. That's more work for me, not less… Call me when you can hand it to my CPA."
resonated: sheets angle mildly | objection: does MORE work, CPA must bless | incumbent: CPA+QBO | price: can't run the math

### consultant-3 — 29yo designer, DIY spreadsheet, Claude Max, squeezed | {1:.02 2:.08 3:.25 4:.45 5:.20} | EV 3.73
> "Pretty likely, which surprises me… The March tax weekend is the thing that kills me every year… It would replace my Sheets setup entirely… My objection is the 'you tell it about money in/out yourself' part. That's the discipline I don't have… I'm already paying $100 for Claude. If this is another $40 on top, I need to think hard."
resonated: year-round current ledger, Doc invoices match current workflow | objection: own discipline / no import | incumbent: DIY sheets | price: stacking anxiety

### consultant-4 — 44yo fractional CMO, FreshBooks Premium retainers | {1:.30 2:.45 3:.18 4:.06 5:.01} | EV 2.03
> "The margin-per-client thing catches my attention… But the 1st of every month my retainer invoices go out automatically without me touching anything. That's sacred… No bank feed in v1 is a dealbreaker for my use case."
resonated: margin per client | objection: no recurring auto-billing, no feed | incumbent: FreshBooks Premium | price: "missing features bother me first"

### consultant-5 — 35yo grant writer, Wave free, squeezed | {1:.06 2:.24 3:.40 4:.24 5:.06} | EV 3.00
> "The AR aging piece alone makes me sit up — I spend stupid amounts of time cross-referencing Wave's transaction list against my invoice tracker just to know who's at day 47… My big objection is the no-bank-feed thing… 'Not announced yet' from a bootstrapped tool usually means 'we're deciding how much we can charge.'"
resonated: AR aging, partial payments | objection: no feed | incumbent: Wave free | price: yellow flag, tight ceiling

### creator-1 — 31yo course creator, QBSE $20 | {1:.04 2:.18 3:.34 4:.34 5:.10} | EV 3.28
> "My first reaction is 'finally'… The per-launch P&L alone would've saved me hours… And the Stripe fee thing? Yes… My top objection is the no-bank-feed part. I'm not going to manually narrate every Gumroad payout summary biweekly — that friction will kill my habit within a month."
resonated: per-launch P&L, fee split, real books for CPA | objection: payout narration friction | incumbent: QBSE | price: >$50 needs full replacement

### creator-2 — 27yo Etsy seller, Wave free, squeezed | {1:.25 2:.45 3:.22 4:.07 5:.01} | EV 2.14
> "The Google Sheets part caught me… But I already tell Wave what stuff is, manually, and it works. The 'you tell the assistant' part — that's just more work dressed up nicer? Wave does that too, free. Then $20/mo Claude PLUS whatever SoloBooks costs… I cancelled Canva for less."
resonated: data portability, product-line profitability | objection: no advantage over free Wave; stacked cost | incumbent: Wave free | price: already gone

### creator-3 — 39yo YouTuber, $300/mo bookkeeper, AI skeptic | {1:.35 2:.45 3:.15 4:.04 5:.01} | EV 1.91
> "Not likely… my bookkeeper situation already works… The idea of manually telling an AI about every transaction sounds like more work than what I do now, which is nothing. And AI touching my financial records — I've seen these things hallucinate confidently… Maybe revisit when bank feeds exist."
resonated: — | objection: displaces nothing, AI trust | incumbent: human bookkeeper + QBO | price: not the issue

### creator-4 — 33yo newsletter writer, erratic spreadsheet, Claude Max | {1:.02 2:.08 3:.22 4:.42 5:.26} | EV 3.82
> "The AR aging piece alone has me. That $1,500 I wrote off last year because I couldn't be bothered to chase a sponsor… Chatting an invoice into existence and having something actually track whether it got paid is exactly the workflow I've been too lazy to build… If it's 'works inside Claude Max you already pay' plus $25ish, I'm in day one. If it's $79/mo on top, I'm back to my spreadsheet and regret."
resonated: invoice+tracking in chat, AR | objection: he's still the data pipe | incumbent: Doc template + vibes | price: $25 in / $79 out

### creator-5 — 45yo photographer, FreshBooks, payment links sacred | {1:.28 2:.44 3:.20 4:.07 5:.01} | EV 2.09
> "The deposit handling alone would make me look twice — that's my actual headache every January… But here's my hard stop: no online payment link on the invoice… My clients pay through FreshBooks' link at 11pm on a Sunday. If I have to chase a PDF and then separately collect payment, I'm staying on FreshBooks."
resonated: unearned-revenue deposits | objection: no payment link (dealbreaker) | incumbent: FreshBooks | price: absence = "assume not cheap"

### advisor-1 — 47yo solo CPA, 80 clients, ProAdvisor | {1:.12 2:.36 3:.38 4:.12 5:.02} | EV 2.56
> "The double-entry preview with client approval — that part I actually like… If the ledger is real double-entry and exports to something I can pull into UltraTax without rebuilding it, that's interesting. But 'client narrates transactions to the AI' — have you met my clients? They'll narrate wrong. Who eats that error?… I can't recommend what I can't quote."
resonated: approval controls, clean export | objection: narration errors, liability | incumbent: QBO wholesale | price: can't recommend unpriced

### advisor-2 — 36yo cloud bookkeeper CAS, tech-forward | {1:.05 2:.20 3:.40 4:.28 5:.07} | EV 3.12
> "The double-entry with owner approval and the Google Sheets export are the two things that would make me even consider this. That's the gap — I turn away maybe a dozen solopreneurs a year because QBO plus my minimum doesn't pencil for a $60k freelancer. My top objection is no-bank-feeds… manual narration is where errors live… If pricing creeps toward QBO territory the value proposition collapses."
resonated: referral-safe cheap clean system | objection: narration error surface | incumbent: QBO+Dext | price: must stay well under QBO

### advisor-3 — 58yo EA, 150 Schedule C clients | {1:.08 2:.25 3:.40 4:.22 5:.05} | EV 2.91
> "The Google Sheets thing is the first thing in years that made me stop and think. I spend half of February reconstructing what happened in somebody's business from Chase PDFs and a QBSE export where forty percent is 'Uncategorized'… If a client showed up with a locked, tied-out ledger I could open myself, I'd just prepare the return. My objection is the narration piece… they'll get lazy. And if it's subscription SaaS, they'll cancel in March."
resonated: portable locked ledger, cash-basis P&L | objection: client laziness | incumbent: shoeboxes/QBSE | price: cancel-in-March worry

### advisor-4 — 41yo fractional CFO for creators, MCP-comfortable | {1:.04 2:.16 3:.38 4:.32 5:.10} | EV 3.28
> "The bank-balance tie-out at close is what makes me even consider this — that's the one control I'd need… My actual nightmare isn't wrong categories, it's missing transactions entirely… could replace QBO for my $800-1500/year Substack-and-merch folks where QBO feels like renting a forklift to move a couch. Top objection: completeness… I need a number before I'd bring it up in a client call."
resonated: tie-out control, queryable ledger | objection: completeness of narrated books | incumbent: QBO (overkill tier) | price: needs a number to pitch

### advisor-5 — 50yo firm partner, QBO-standardized | {1:.10 2:.32 3:.40 4:.15 5:.03} | EV 2.69
> "More interesting than I expected. For the truly tiny ones… it would replace the shoebox and the spreadsheet, not QBO, so my standardization wall stays intact. My top objection is the 'narrate your transactions' part… That's a cleanup nightmare at tax time. And no pricing tells me it's not ready."
resonated: fits below the QBO wall | objection: narration → cleanup | incumbent: QBO standard + tolerated spreadsheets | price: absence = "not ready"

## Synthesis

- **What resonated:** per-client/launch profitability (5 mentions); AR aging / who-owes-me (4); portable tied-out Google Sheets ledger (6 — strongest with advisors); correct deposit/retainer accounting (2, intense); approval preview + audit controls (3 advisors); bank tie-out at close (C4, "the one control").
- **Objection themes ranked:** (1) **no bank/CSV import — "I am the data pipe"**: 11/15; (2) **pricing absent**: 15/15 reacted, 6 as active red flag; (3) **completeness/accuracy of narrated books** (advisor flavor of #1): 5/5 advisors; (4) **missing payment links/recurring billing** (incumbent-parity features): 3, two as dealbreakers; (5) **AI trust/liability**: 2.
- **Price sensitivity:** anchors are brutal — $19 (FreshBooks), $15–25 (QBSE), free (Wave), plus the ~$20 Claude prerequisite. Stated bands: $25/mo converts the enthusiasts; $50+ requires full incumbent replacement; unpriced reads as "expensive" or "not ready."
- **Moves 3s→4s (stated conditions only):** CSV/bank import (A1, A5, B1, C2, C4, B3), a price under ~$30 (A3, B4, C2), accountant-ready export packet (C1, C3), payment links (B5), recurring billing (A4).

## Suggestions (prioritized)

1. **Add bank-statement CSV import (agent-assisted categorization, approval-gated) to v1** — addresses the 11/15 "data pipe" objection; converts A1, A5, B1, C2, C4; the coverage map's only Missing-at-weekly-cadence row. Full Plaid feeds can wait; CSV cannot.
2. **Announce pricing early, anchored ≤$29/mo** — 15/15 reacted to absence; converts B4 ("$25 I'm in day one"), A3, C2; unpriced actively reads "not ready" to advisors quoting clients.
3. **Ship the "accountant packet" export** (TB + GL + 1099 CSV bundle, one tool) — converts the advisor channel (C1's UltraTax condition, C3's February); cheapest win since books are already sheets.
4. **Market the completeness controls, don't just build them** — the tie-out at close + missing-weeks nudges answer the advisor garbage-in objection (C4 explicitly bought the tie-out); add an agent nudge when a money account is silent >2 weeks.
5. **v1.5: Stripe payment link on the invoice artifact** — B5's dealbreaker, table stakes vs all three incumbents.
6. **v1.5: recurring/retainer auto-billing** — A4's sacred workflow; opens the fractional-executive segment.
7. **Do not prioritize**: time tracking, mileage, receipt OCR (≤1 mention each) — the panel confirms the v1 cut there.

## Caveats

- Synthetic panel — directional, not a substitute for talking to real buyers.
- Reliable signals: relative ranking between segments/concepts, objection themes, budget-pressure effects. The advisor > consultant ≈ creator ordering and the bank-import objection dominance are the trustworthy outputs.
- Weak signals: absolute PI levels (hidden pricing depresses stated intent; human consumer panels skew ~4.0/5) — do not read 2.9 as a conversion forecast.
- Method note: anchor mapping is model-judged semantic similarity, not the paper's embedding cosine similarity.
