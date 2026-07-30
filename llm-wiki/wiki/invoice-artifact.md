---
type: entity
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
tags: [invoice, drive, artifact]
---

# Invoice Artifact (the sendable thing)

> Recording an invoice is not enough — the solopreneur must have something to give the client, or they stay on Word + bank app. Biggest gap caught in the solopreneur review.

- On posting, render the invoice as a **Google Doc from a template** in `<Company>/invoices/`, auto-export **PDF**, return the link in chat.
- Contents: company identity + contact info and payment instructions (from [[company-object]]), customer, line items, tax ([[compliance]]), due date.
- **No email sending in v1** — artifact + link only ([[v1-scope]]).

Uses the same service-account Drive as the ledger ([[three-store-architecture]]).

## Generation details (drafted 2026-07-17)

- One Doc template in service-account Drive (`_templates/invoice`): Drive `copy` → Docs `batchUpdate` replacing `{{placeholders}}` → PDF export into `<Company>/invoices/`; both links on the Mongo invoice doc, PDF link returned in chat.
- Editing a posted invoice (reversal+repost, [[general-ledger-sheet]]) regenerates as `INV-xxxx (revised)`; old PDFs kept — **artifacts are append-only too**.
- Line items (description, qty, rate) live on the Mongo invoice doc; the GL carries only account-split totals. The artifact renders from the document — the one render not sourced from the ledger, correct because line-item prose isn't accounting data.
- **Scope-corrected**, not reversed: that claim holds for description/qty/rate and **not** for `service_period {start, end}`, which is accounting context, not prose — it is what answers "when was this earned?" ([[financial-object-model]]). Ships as a nullable seam on invoice lines, **free capture only** ([[the-skill]]); it changes no cash-basis recognition ([[cash-basis-recognition]]). **(proposed 2026-07-30)**
- Per-company templates deferred; v1 ships one clean default.

## Frozen at issue

The artifact renders from **mutable** [[company-object]] settings and a mutable `sales_tax.flat_rate`, so a revised PDF silently disagrees with the original PDF the customer already holds. Freeze onto the artifact at issue, per the retained-renderings rule in [[policy-set]]: **(proposed 2026-07-30)**

| Frozen at issue | Why |
|---|---|
| company identity + contact info | **(proposed 2026-07-30)** a rebrand must not rewrite last year's invoice |
| payment instructions | **(proposed 2026-07-30)** a bank-detail change must not appear on a document already sent |
| tax rate + `policy_version` | **(proposed 2026-07-30)** the rate that computed `CR Sales Tax Payable` is the rate the PDF must state ([[compliance]]) |

`INV-xxxx (revised)` re-renders from **today's** values by design and is a new artifact; old PDFs are kept, so both renderings survive and disagree *visibly*. **(proposed 2026-07-30)**

## Delivery record

`ar_aging` reports an invoice as overdue while nothing records that it was ever sent, and *"I never sent it"* is the most common real answer to "why is this outstanding" ([[context-assembly]]). Add `delivery {delivered_at, channel}` — nullable, **free capture only**, `DeliveryChannel`: `EMAIL_MANUAL | LINK_SHARED | PRINTED | OTHER`. It is a fact the user volunteers, never a prompt, and it gates nothing: an undelivered invoice still posts and still ages. Null renders as **"not recorded"**, never as "not delivered". **(proposed 2026-07-30)**
