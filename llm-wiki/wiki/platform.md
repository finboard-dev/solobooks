---
type: entity
created: 2026-07-17
modified: 2026-07-30
status: verified
sources: [raw/2026-07-17-design-doc.md, raw/2026-07-30-process-aware-objects.md]
tags: [auth, nextjs, fastapi, reuse]
---

# Platform

> Better Auth for identity, service account for Sheets, minimal Next.js UI, no billing in v1. Heavy reuse of proven FinBoard mcp-server machinery.

- **Auth:** Better Auth in Next.js (Mongo adapter — same DB as everything). Google social login for convenience but **zero Google scopes needed from users** (sheets use our service account); email/password fine. Better Auth **OAuth Provider plugin** ([[auth-wiring]]) = OAuth 2.1 server for MCP clients; JWKS = stateless FastAPI verification. Fallback: API-key flow.
- **Sheets access:** Google Workspace tenant + **Shared Drives** (post-2025 service accounts have zero My-Drive quota — see [[sheets-layer]] storage architecture); SA writes as drive member; per-company folder shared view-only with the user's email ([[three-store-architecture]]).
- **Exportability mechanism ("your books are yours"):** view-only shared files are copyable by the user (File → Make a copy); the folder stays shared after cancellation (retention: indefinite in v1); `export_accountant_packet` is the structured export.
- **Next.js UI (all of it):** login, "connect Claude" page (MCP URL + auth), folder view linking into the view-only Drive folder, and the **batch review grid** — the ONE sanctioned exception to "never renders a ledger": a read-only import-draft queue (date, description, proposed account, amount, dup-flag; approve/reject per row) wired to the [[approval-flow]] tools. It renders a draft queue, not the ledger ([[product-vision]]). The queue is no longer anonymous: one grid = one `IMPORT_RUN` [[process-instance]], which is what gives the batch an id, a reject list and dedupe counts. **(proposed 2026-07-30)**
- **Billing:** none in v1; nothing gated ([[v1-scope]]).
- **Reused from FinBoard mcp-server:** FastMCP skeleton, core/tools separation (core is domain-blind), `@audit` decorator (→ Mongo), token-budget table renderer, sqlglot SQL guard, rate-limit middleware.
- **Repo:** single new repo — FastAPI+MCP server, Next.js frontend, [[the-skill]].
