# Professional review — Priya Raman (persona: CAS/advisory firm founder, 14-person Austin firm)

Operator's review: (a) referral bar for too-small leads, (b) could pods operate it as a low-tier
offering. Read 20+ wiki pages. Status: findings NOT yet ingested/fixed — raw input.

## Findings (condensed)

1. **Bank rec is a vibe, not a rec.** Single-number honor-system tie-out passes offsetting errors.
   No statement-based rec object, no per-line cleared flag, no outstanding-items report, no rec
   history. THE control in bookkeeping; caps everything else. Panel's 5/5 advisor objection.
2. **Chat is a terrible batch interface and month-end IS a batch job.** 60 CSV rows = 60 chat
   previews or YOLO approve_all_drafts (control becomes theater). "UI never renders a ledger" is
   ideological purity beating operator reality — needs ONE batch review grid for import drafts.
3. **Firm operation architecturally absent:** one company per user, no accountant role/seat, no
   multi-client console, no cross-client close board / exceptions rollup, shared-credential audit
   attribution. Running 20 = 20 chat sessions + a self-built tracking sheet. Economics die on labor.
4. **Single-drainer serialization** sized for one solopreneur; multi-client close-day bulk import
   makes 60 writes/min a queue on the day that matters. Stated ceiling, flag not bug.
5. **Google in BOTH write and read paths:** reports load from Sheets (projection is analytics source
   of record) → Sheets incident takes down posting AND reporting; projection bug silently corrupts
   reports while Mongo sits correct. TOTALS formula catches balance bugs, not dimension/categorization
   projection bugs.
6. **Graduation export 80% there:** packet lacks open AR/AP item detail with refs, customer/vendor/
   project masters, document-level invoice line detail (Mongo+PDF only). Self-sufficiency rule
   delivers "read the ledger," not "migrate the business." Packet should be one artifact.
7. **Reporting package is not a client deliverable and there is NO budget object anywhere** → no BvA
   (the #1 thing $500+/mo clients pay for). No KPIs, runway, trends, PDF/scheduled package; cash_flow
   v1 is a category summary. Irony: owns the Sheets layer, doesn't render a package tab.
8. **Mid-year onboarding hole:** point-in-time TB + open items but no YTD P&L detail / historical
   transaction backfill path → transition-year return stitches two systems. Nothing prompts OBE
   reclassification ("accountant reclassifies later" assumes an accountant shows up).
9. **Recurring billing in v1.5 contradicts the retainer story** — retainer clients bill monthly,
   identically; manual chat per client per month. Difference between "used in month 3" and
   "abandoned in month 3."
10. **Graduation verdict: books arrive materially cleaner than QBSE** (tied TB, locked GL with refs,
    deposits in Unearned, owner spend classified). 6-week cleanup → ~2 weeks: reclass OBE, drain
    Uncategorized/unapplied, REDO cash rec from statements (finding 1). Rec is the gap between
    "cleaner" and "trustable."
11. **Data access genuinely open, one asterisk:** copyable sheets, post-cancel retention, canonical
    views, guarded SQL = opposite of trapped, better than QBO API posture. Asterisk: MCP-only machine
    access — no plain REST read layer, no webhooks, no white-label; firm tooling doesn't speak MCP.
    "Does it sync or import?" It imports — CSV, hand-fed.
12. **On record as good:** $0.99 tolerance auto-line shown in preview; ambiguity-first-class +
    LLM-never-touches-debits; cent-exact Golden Company gate; corrections-visible-forever.

## Missing requirements (verbatim structure)

**To recommend to too-small leads (referral bar):**
- Statement-based bank rec (per-line cleared, monthly rec report) — non-negotiable trust floor
- Recurring invoices/retainer auto-billing pulled INTO v1(.0/.1) + Stripe payment link
- Batch review grid for CSV-import drafts (bend the no-ledger-UI rule once)
- Mid-year onboarding: historical transaction backfill
- OBE cleanup nudge + "send to accountant" packet trigger in close ritual
- Published pricing at launch

**To operate as a firm low-tier offering (different product):**
- Accountant role: multi-company under one identity, per-user audit attribution
- Cross-client console: close status + exceptions rollup (uncategorized/unapplied/drafts/silent
  accounts across all clients)
- Persistent close checklist per period (tracked, assignable), not ephemeral chat ritual
- Bank feeds (Plaid) — firms don't chase 20 clients for CSVs
- Bulk posting throughput re-examined (single drainer)
- REST read API / webhooks for firm tooling
- Open-item detail + contact masters in export_accountant_packet

## Bottom line (verbatim condensed)

Accounting engine is the real thing; a SoloBooks graduate hands the firm the cleanest DIY books
she's ever received — legitimate referral for too-small leads ONCE it has real bank rec, recurring
billing, and a batch review surface. As a pod-operated offering: no — operating model is one human
chatting with one company's books. Build the accountant-facing wedge (multi-company role, exceptions
rollup, statement rec) and it flips to "I'd pilot five clients next quarter." The buyer panel already
said who scored highest — it wasn't the solopreneurs, it was people like her.
