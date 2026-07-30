---
type: concept
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
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
- **Attention lives in the client, never in the server (proposed 2026-07-30):** headless means the server never sees the question — where attention does live is defined in [[context-assembly]].

**Inherited non-negotiables** (from FinBoard principles): core infra domain-blind; pure composable steps; accounting-first reasoning; extension without modification; everything auditable; no magic strings; **one concept, one implementation** — every derived number traces to a single ledger-grain definition ([[pairing-and-matching]], [[reports-and-analytics]]); and the sharpened architecture statement — **SoloBooks does not retrieve records, it reconstructs financial context** ([[financial-object-model]]) **(proposed 2026-07-30)**.

Scope decisions: [[v1-scope]].
