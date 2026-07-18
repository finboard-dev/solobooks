# Sheets Layer — approved design (2026-07-17)

## Provisioning
- Company folder + COA sheet at onboarding; monthly GL spreadsheets created LAZILY (first posting dated in a month creates the file from a template: header row, formats, frozen top rows).
- Every file shared view-only with the user's email; registered in Mongo (spreadsheet_id, sheet_id per month — never resolved by name at runtime).

## Appending (posting pipeline PROJECT step)
- One values.append call per transaction — all lines of a txn in one API call; a txn never splits across a failure boundary.
- Tail-check dedupe before any retry (read last ~50 rows, look for txn_id).
- RAW value input; we pre-format dates/amounts — Sheets never interprets ledger data.

## TOTALS row = formulas, not values
- =SUM() for debits/credits + difference cell. Sheet self-verifies: a writer bug shows as non-zero difference visible without our system. Self-sufficiency applied to integrity.

## Quotas
- ~60 writes/min/user API quota vs a handful of txns/day — orders of magnitude under. Drainer serializes appends, exponential backoff on 429/5xx. Quota pressure = "seconds later", never "lost".

## COA sheet
- Fully rewritten on every COA change (small).

## Re-render path (unlock-month case only)
- Write fresh tab → verify row count + totals → swap → delete old. Never edit in place; crashed re-render cannot leave a half-written ledger.
