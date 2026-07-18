# SoloBooks LLM Wiki — Schema

Karpathy LLM Wiki pattern. `raw/` holds immutable sources; `wiki/` holds LLM-maintained pages. The wiki is the compounding artifact — keep it consistent.

## Page Types

- **entity** — a concrete product component with fixed identity (company object, GL sheet, tool surface)
- **concept** — a rule, mechanism, or design principle (append-only ledger, pairing, approval flow)
- **synthesis** — cross-cutting analysis (scenario catalog, v1 scope)
- **summary** — single-source distillation (rebuilt when its source changes)

## Naming

- Files: `kebab-case.md`, singular, in `wiki/`
- Cross-references: `[[page-name]]` (no .md extension)
- Dates: YYYY-MM-DD, metadata only

## Frontmatter (required on every page)

```yaml
---
type: entity | concept | synthesis | summary
created: YYYY-MM-DD
modified: YYYY-MM-DD
status: verified | unverified | draft
sources: [raw/<file>.md]
tags: []
---
```

`verified` = decision confirmed by the founder in design discussion and present in a raw source. `draft` = open question / not yet decided. Unverified pages must not be cited as grounds for other pages.

## Ingest checklist (new source lands in raw/)

- [ ] Write/update summary page
- [ ] Update affected entity/concept pages (touch cross-references both ways)
- [ ] Update `index.md`
- [ ] Append `log.md` entry (`## [YYYY-MM-DD] ingest | <title>`)
- [ ] Flag contradictions with existing pages in the log — do not silently overwrite

## Query workflow

1. Read `index.md` → follow `[[links]]`
2. Answer with citations to wiki pages / raw sources
3. File durable answers back as synthesis pages — don't lose insights to chat history

## Lint rules

- No orphan pages (zero inbound links, except index/log)
- All `[[links]]` resolve
- Contradiction scan: newer sources supersede — mark stale claims, log the supersession
- One concept, one page — no duplicate definitions (mirrors product principle #7/#9)

## Domain conventions

- Accounting claims must state the journal impact (DR/CR) explicitly
- Every derived value (open balance, aging, retained earnings) must trace to its single ledger-grain definition page
