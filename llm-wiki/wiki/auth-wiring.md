---
type: entity
created: 2026-07-17
modified: 2026-07-17
status: verified
sources: [raw/2026-07-17-auth-wiring-design.md]
tags: [auth, oauth, better-auth, implementation]
---

# Auth Wiring

> Better Auth (Next.js) is the OAuth 2.1 authorization server via its **OAuth Provider plugin** (the MCP plugin is deprecated — Better Auth 1.5, Feb 2026); FastAPI+FastMCP is a stateless resource server verifying JWTs offline via JWKS.

Flow: MCP client → 401 + RFC 9728 protected-resource metadata → DCR + PKCE against Better Auth `/oauth2/*` → user login (Google social or email/password) + consent (kept ON) → signed JWT → FastAPI verifies via cached JWKS (signature/issuer/audience) → `token.user_id → Mongo → company` → tools scoped.

- **One login everywhere** — web session and MCP connection are the same Better Auth user; Mongo adapter keeps users/sessions in the one DB ([[three-store-architecture]]).
- **Tenant rule:** company always from token→user→company, never tool args ([[mcp-tool-surface]]).
- Web UI REST calls use the Better Auth session cookie — no second scheme ([[platform]]).
- Better Auth owns the OAuth machinery — deletes the hardest FinBoard mcp-server code (OAuthProxy).
- **Risk & fallback:** OAuth Provider plugin is new (GA Feb 2026); fallback = manual API-key connect flow, one page, no architecture change.


