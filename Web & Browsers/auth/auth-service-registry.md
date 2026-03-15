# Auth Service Registry

Per-service auth strategies. Update this when you discover what works for a new service.

| Service | Best Layer | Method | Cookie Domain | Notes | Last Verified |
|---|---|---|---|---|---|
| GitHub | L1: API key | `GITHUB_TOKEN` env var or `gh` CLI | — | Personal access tokens, fine-grained scopes | 2026-03-14 |
| Notion | L1: API key | MCP server (already connected) | — | Integration token via Notion MCP | 2026-03-14 |
| Gmail | L1: OAuth | MCP server (already connected) | — | OAuth via Gmail MCP | 2026-03-14 |
| Google Calendar | L1: OAuth | MCP server (already connected) | — | OAuth via Google Calendar MCP | 2026-03-14 |
| YouTube | L2: Cookies | browser_cookie3 → `.youtube.com` | `.youtube.com` | Safari cookies, 1-2 week expiry | 2026-03-14 |
| Vercel | L1: API key | MCP server (already connected) | — | Via Vercel MCP | 2026-03-14 |
| Supabase | L1: API key | MCP server (already connected) | — | Via Supabase MCP | 2026-03-14 |
| Granola | L1: API key | MCP server (already connected) | — | Via Granola MCP | 2026-03-14 |
| X (Twitter) | L2: Cookies | browser_cookie3 → `.x.com` | `.x.com`, `.twitter.com` | No public API for reading feed. Bot-hostile. Cookie sync for read-only. | 2026-03-14 |
| LinkedIn | L4: Isolated | Browserbase + stealth proxy | `.linkedin.com` | Extremely bot-hostile. Never use real session — will get banned. | 2026-03-14 |
| Reddit | L2: Cookies | browser_cookie3 → `.reddit.com` | `.reddit.com` | API exists but rate-limited. Cookies for feed reading. | 2026-03-14 |
| Substack | L0/L2: None or Cookies | Jina Reader (public) / cookies (paywalled) | `.substack.com` | Public posts: no auth needed (Jina works). Paid posts: cookie sync. | 2026-03-14 |
| Steam | L4: Isolated | Browserbase session | `.steampowered.com` | Age gates block headless, use isolated session | 2026-03-14 |
| Amazon | L4: Isolated | Browserbase + stealth proxy | `.amazon.com` | Aggressive bot detection, Firecrawl blocked | 2026-03-14 |

## Adding New Services

When you encounter a service not listed here:

1. Check if an MCP server already provides access (Layer 1)
2. Check if an API key/token exists (Layer 1)
3. Try cookie injection in a Playwright context (Layer 2)
4. If blocked, try Browserbase isolated session (Layer 4)
5. Add the result to this registry with the date

## Cookie Domain Reference

Common domain patterns for browser_cookie3 extraction:

| Service | Domain Filter |
|---|---|
| Google (all) | `.google.com` |
| YouTube | `.youtube.com` |
| GitHub | `.github.com` |
| Twitter/X | `.x.com`, `.twitter.com` |
| Reddit | `.reddit.com` |
| LinkedIn | `.linkedin.com` |
| Amazon | `.amazon.com` |
