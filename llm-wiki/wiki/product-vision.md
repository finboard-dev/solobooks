---
type: concept
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-design-doc.md]
tags: [vision, positioning]
---

# Product Vision

> Headless accounting for solopreneurs: books live in the user's viewable Google Sheets, the brain is an MCP server, the UI is only login/connect/folder-view.

**The pitch:** "Your books are yours — plain spreadsheets you can open, share with your accountant, and keep forever. We add the discipline (double-entry, numbering, audit trail, approvals) and the intelligence (chat-driven bookkeeping and analytics)."

- All bookkeeping happens conversationally via MCP tools ([[mcp-tool-surface]]) from Claude or any MCP client. The MCP tools ARE the API.
- Target user: one-person US businesses — freelancers, consultants, creators (1099s, flat sales tax, cash-basis filing → see [[compliance]]).
- The web UI never renders a ledger — with exactly one sanctioned exception, the import-draft review grid ([[platform]]).
- Architecture rests on three stores with one truth chain: [[three-store-architecture]].
- Ships with an agent skill teaching correct accounting behavior: [[the-skill]].

**Inherited non-negotiables** (from FinBoard principles): core infra domain-blind; pure composable steps; accounting-first reasoning; extension without modification; everything auditable; no magic strings; **one concept, one implementation** — every derived number traces to a single ledger-grain definition ([[pairing-and-matching]], [[reports-and-analytics]]).

Scope decisions: [[v1-scope]].
