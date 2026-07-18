---
type: concept
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
tags: [tax, 1099, cash-basis, us]
---

# Compliance (US-first): Sales Tax, 1099, Cash/Accrual

> The three US-solopreneur must-haves that survived the CPA review, kept deliberately minimal in v1.

- **Cash vs accrual basis** — most solopreneurs file taxes cash-basis, but the ledger is accrual (AR/AP everywhere). Both bases computed from the same ledger; the precise algorithm (pro-rata on cash settlements, card-charge-date rule, retainers-at-receipt, tax portion to liability) is canonical in [[cash-basis-recognition]]. `accounting_basis` on [[company-object]] sets the default; per-report toggle in [[reports-and-analytics]]. Must be v1 — retrofitting basis logic is painful.
- **Sales tax** — single flat rate on [[company-object]]; optional per invoice → extra `CR Sales Tax Payable` line ([[document-model]]); `sales_tax_liability` report answers "what do I owe the state". No jurisdictions, no filings.
- **1099 tracking** — `track_1099` boolean on vendor ([[dimensions]]) + `1099_payments` report. **Method exclusion (prevents over-reporting and IRS mismatch letters):** payment `method` is accounting-relevant — **card and third-party-processor payments are EXCLUDED from 1099-NEC totals** (the processor's 1099-K territory). Report = cash/check/ACH payments only, $600 threshold applied, per-vendor method breakdown shown. Still open scope: W-9/TIN capture, NEC vs MISC classification, corporate-payee exemption ([[professional-review-findings]]).
- **Sales-tax basis disclosure** — the liability report states its basis on its face; many states require accrual-basis remittance regardless of income-tax basis ([[cash-basis-recognition]] R9).
