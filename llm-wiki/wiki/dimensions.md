---
type: entity
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
tags: [dimensions, gl]
---

# Dimensions

> Every GL line can carry: customer, project (nested under customer), vendor, class, location (column from day one, nullable), memo. Mongo collections referenced by id; rendered **by name** in the sheet.

| Dimension | Why |
|---|---|
| `customer` | income by client, AR |
| `project` | **child of customer** (QuickBooks-jobs style); engagement profitability |
| `vendor` | spend by vendor, AP, 1099 prep (`track_1099` flag — [[compliance]]) |
| `class` | line of business — P&L by segment |
| `location` | rare for target user, but column exists from day one (adding later is painful) |
| `memo` | free text, always |

Used by rollup reports in [[reports-and-analytics]] (income_by_customer, spend_by_vendor, project_profitability) and by the retainer path in [[pairing-and-matching]] (deposits tagged customer+project).
