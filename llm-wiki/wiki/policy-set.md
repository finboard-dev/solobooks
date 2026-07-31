---
type: entity
created: 2026-07-30
modified: 2026-07-30
status: draft
sources: [raw/2026-07-30-process-aware-objects.md, raw/2026-07-30-tri-persona-review.md]
tags: [policy, versioning, reporting, canonical-definition]
---

# Policy Set (versioned, referencable, stamped)

> The founder source wants accounting treatment to trace to a **policy decision**, so the system can answer *which rule was in force when this posted*. Today policy is a column of mutable scalars on a settings blob plus constants scattered across five modules. One versioned policy set fixes a class of silent restatement.

## The failure this prevents

Every policy input is currently a mutable scalar with no effective date. Mutating one silently restates history that has already left the building:

| Mutation | Silent consequence today |
|---|---|
| `accounting_basis` flipped | every prior P&L restates; only the sales-tax report states its basis on its face ([[compliance]] R9) |
| COA `tax_line` remapped | re-running last year's packet regroups a **filed Schedule C** under today's map |
| `fiscal_year_start` changed | Retained Earnings is computed at query time, so **locked** balance sheets restate |
| `sales_tax.flat_rate` changed | a revised invoice PDF disagrees with the original the customer holds ([[invoice-artifact]]) |
| `match_tolerance` changed | the packet's promised tolerance write-off list is not derivable at all |
| R1–R12 revised (**already happened twice** — `log.md` 2026-07-18 and 2026-07-30) | locked-period cash P&Ls change with no trace |

None of these touch a single GL row. The ledger stays perfectly append-only and the *reports* still change — which is precisely the founder's point that meaning is not stored in the record.

## Shape

```
PolicySet {
  policy_version    # monotonic; a new version on every change, never an in-place edit
  effective_from    # PLAIN calendar date ([[dates-and-timezones]])
  changed_by / changed_at / reason
  accounting_basis, approval_mode, fiscal_year_start, timezone
  sales_tax {enabled, flat_rate}
  coa_tax_line_map  # account -> Schedule C line, versioned WITH the set
  ruleset_versions {cash_basis: "R1-R12@2026-07-31", matching: "…"}
  thresholds {…}
}
```

Policy sets are **append-only**; [[company-object]] holds a pointer to the current one, not the values. Resolution is always *as-of a date*, never *as-of now*.

## What is deliberately NOT a policy field (proposed 2026-07-30)

**`prior_return_basis`** — the fact that decides whether collecting a pre-conversion invoice is taxable in the migration year. It is asked once at onboarding, recorded as a `HUMAN` [[decision-record]], and its effect is thereafter carried by the **composition of the posted historical documents** ([[onboarding-opening-balances]]). R4 keys off that composition, so nothing resolves a policy value for it after onboarding day. A field on an append-only, effective-dated object invites a later version that contradicts the ledger with no report able to detect it — the exact divergence this page exists to prevent, and the design's own "nothing stored that can be derived" rule ([[point-in-time-balances]]).

## Thresholds — two classes, deliberately different

Seven thresholds live as hardcoded constants across five modules today (`$600` 1099, `$0.99` tolerance, `±3d` duplicate window, silence nudge written as both ">2 weeks" and ">14 days" for one threshold, the 50-row tail-check).

- **Statutory** (`form_1099_nec_threshold`) — set by law, effective-dated **by tax year**, resolved as-of the report's period. A January packet reports the year just ended; applying today's number to last year's 1099s is a filing error with the same shape as the `tax_line` bug.
- **Operational** (`match_tolerance`, `duplicate_window_days`, `silence_nudge_days`, **`cutoff_ask_days`** — it drives an agent question that decides which tax year a deduction falls in, so it resolves as-of the report's period and is stamped on the header **(proposed 2026-07-31)**) — behavioral knobs. They belong on the versioned policy set, **not in deployment config**: `match_tolerance` drives a real GL line ([[matching-engine]]) and a process-wide env var means one company's write-off is unexplainable from another's books.

The tail-check's 50-row window is neither — it is an implementation detail of [[sheets-layer]] and stays there.

## Stamping

- **Every posting** carries `policy_version` in its `provenance` ([[decision-record]]).
- **Every report** carries a policy header on its face — basis, policy version, ruleset versions, period, and the `books_state` banner. [[compliance]] R9 already requires this of the sales-tax report; it generalizes. A report without a header is a number with no meaning.
- **Every exported rendering is retained.** The design already promises "every rendering a banker or accountant may have seen survives" ([[period-locking-month-close]]) but implements it only for the GL sheet. The renderings outsiders actually see are P&Ls, agings and packets. `export_accountant_packet` and any explicitly exported report write an **immutable, timestamped copy into the Drive folder** with its policy header — reusing the bundle machinery that already exists, and making the permanence promise true as stated.

## What is NOT a policy object

The cash-basis algorithm itself stays in [[cash-basis-recognition]] as prose plus one SQL view — it is a *ruleset*, and only its **version identifier** lives here. Splitting the rules across two pages would violate the wiki's one-concept-one-page rule and principle #9. Same for the matching cascade in [[matching-engine]].
