---
type: entity
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
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
- Per-company templates deferred; v1 ships one clean default.
