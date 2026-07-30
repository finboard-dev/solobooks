---
type: synthesis
created: 2026-07-17
modified: 2026-07-31
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-tri-persona-review.md]
tags: [scenarios, edge-cases, accounting]
---

# Scenario Catalog

> The CPA's parade of horribles — every one is just ref-carrying journal lines ([[pairing-and-matching]]), no new machinery. All documents from [[document-model]]. Every row here is an executable cent-exact fixture per [[testing-strategy]].

## Money-in (AR)

| Scenario | Treatment |
|---|---|
| Overpayment | remainder = customer credit (negative AR by ref), apply later |
| Retainer before work exists | `DR Bank / CR Unearned Revenue`; applied on invoicing |
| Processor fees (Stripe nets 970 of 1,000) | `DR Bank 970 / DR Processing Fees 30 / CR AR 1,000 ref` — invoice fully paid, fee expensed |
| Bounced payment (NSF) | reversal of payment lines (invoice reopens via ref sum) + optional NSF fee |
| Refund | `DR AR ref / CR Bank` |
| Chargeback | refund + fee line |
| Early-payment discount | `CR AR ref` full, `DR Sales Discounts` for the discount |
| Cash sale, no invoice | SalesReceipt: `DR Bank / CR Sales` |
| Bad-debt write-off | `DR Bad Debt Expense / CR AR ref` |

## Money-out (AP)

Vendor credits, partial bill payments, vendor refunds — identical with signs flipped.

## Solopreneur-specific (first-class tools in [[mcp-tool-surface]])

| Scenario | Treatment |
|---|---|
| Owner pays business expense personally | `DR Expense / CR Owner's Contributions` — the #1 solopreneur transaction |
| Owner draws money out | `DR Owner's Draw / CR Bank` |
| Transfer between accounts / credit-card payoff | Transfer doc — never touches P&L |
| Customer is also a vendor — offset | JE: `DR AP ref:BILL / CR AR ref:INV` — both balances close. **On cash basis this is a recognition event (constructive receipt and payment); the amount, the intent predicate, the allocation across refs, and the treatment of every other leg are defined once in [[cash-basis-recognition]] R5a — this row deliberately states no amount. (proposed 2026-07-31)** |

Deferred: multi-currency, chargeback-dispute workflow, batch deposits (matters only with bank feeds) — see [[v1-scope]].
