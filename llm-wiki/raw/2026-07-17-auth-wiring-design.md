# Auth Wiring — approved design (2026-07-17)

## Research finding (supersedes earlier assumption)
Better Auth's MCP plugin is being DEPRECATED in favor of the OAuth Provider plugin
(Better Auth 1.5, Feb 2026): OAuth 2.1 + OIDC, /oauth2/* endpoints, built for MCP clients.
Sources: better-auth.com/docs/plugins/mcp, better-auth.com/docs/plugins/oauth-provider,
better-auth.com/blog/1-5.

## Flow
1. MCP client hits our MCP server → 401 + protected-resource metadata (RFC 9728) pointing at the Next.js auth server.
2. Dynamic client registration + PKCE authorize against Better Auth OAuth Provider plugin.
3. User logs in (Google social or email/password), consents. Consent stays ON (no trusted-client bypass).
4. Better Auth issues signed JWT access token; JWKS published.
5. FastAPI+FastMCP (resource server) verifies OFFLINE via JWKS — signature, issuer, audience. No per-request callback.
6. token.user_id → Mongo → user's company → tools scoped. Tenant never from tool args.

## Properties
- One login everywhere: web session and MCP connection are the same Better Auth user (Mongo adapter).
- FastAPI stateless; JWKS cached with rotation handling.
- Web UI REST calls use the normal Better Auth session cookie.
- Better Auth owns the OAuth machinery — deletes the hardest code in FinBoard's mcp-server (OAuthProxy).

## Risk
OAuth Provider plugin is new (GA Feb 2026). Fallback if immature: manual API-key connect flow —
one page of code, no architecture change.
