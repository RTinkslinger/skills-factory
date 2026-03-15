# Layer 1 Toolset Decision Record

**Date:** 2026-03-14
**Phase:** 0 (Tool Evaluation)
**Sprint:** 2
**Status:** Final

## Decision

The Layer 1 toolset for the Web & Frontend Skills Portfolio is:

| Tool | Role | Version | Status |
|------|------|---------|--------|
| **Playwright MCP** | Primary browser automation (baseline) | plugin built-in | **Core** |
| **Firecrawl MCP** | Text extraction + structured data | @3.11.0 | **Core** (with guardrails) |
| **Chrome DevTools MCP** | Lighthouse audits + network inspection | @0.20.0 | **Supplementary** |
| **Browserbase** | Anti-detection cloud browser | API (live) | **Fallback** |
| **Jina Reader** | Clean markdown extraction (FREE, best CF penetration) | r.jina.ai API | **Core** |
| **WebFetch** | Built-in URL → AI-processed content (FREE) | Built-in | **Core** |
| **browser_cookie3** | Cookie extraction (Safari + Chrome) | pip (venv) | **Core** |
| **browser-use** | Autonomous multi-step browsing (cloud API) | bu_ API key | **Fallback** |

### Excluded

| Tool | Reason |
|------|--------|
| **Stagehand v3** | Redundant — same architecture as browser-use (AI + Playwright). Selector caching claim (30%+ faster) worth revisiting in Phase 4 for watch skill if repeated navigation is a bottleneck. |
| **yt-dlp** (cookies) | browser_cookie3 has native domain filtering; yt-dlp requires post-processing. Both handle Safari + Chrome. |

## Architecture

```
Claude Code (LLM reasoning)
├── Playwright MCP (navigate, interact, snapshot)
│   ├── Browserbase sessions (when bot-detected)
│   └── browser-use cloud (fallback for complex autonomous multi-step tasks)
├── Content Extraction (tiered by cost + capability)
│   ├── Jina Reader (FREE, fastest, best Cloudflare penetration — default for text)
│   ├── WebFetch (FREE, built-in, AI-processed — simple lookups)
│   ├── Firecrawl scrape (1 credit, more detailed markdown)
│   ├── Firecrawl extract (38 credits, schema-driven JSON — structured data only)
│   └── Firecrawl agent (async, autonomous multi-source research)
│   └── GUARDRAIL: validate metadata.url + statusCode before trusting Firecrawl JSON
├── Chrome DevTools MCP (Lighthouse, network panel)
└── browser_cookie3 (cookie extraction for authenticated sessions)
```

### Tool Selection Heuristic (for skills to use)

1. **Text content extraction** (blog, docs, article) → Firecrawl scrape (markdown)
2. **Structured data extraction** (pricing, specs, schema) → Firecrawl extract (JSON)
3. **Multi-source research** → Firecrawl agent (async)
4. **Interactive browsing** (navigate, fill forms, click) → Playwright MCP
5. **Quality audit** (accessibility, SEO, best practices) → Chrome DevTools Lighthouse
6. **Network debugging** → Chrome DevTools network panel
7. **Bot-hostile sites** → Browserbase session → connect Playwright
8. **Authenticated sessions** → browser_cookie3 → inject into Playwright context

## Critical Guardrails

### Firecrawl JSON Extraction Hallucination
- **Risk:** When Firecrawl can't access content (age gates, redirects, bot blocks), its JSON extraction FABRICATES plausible-looking structured data
- **Mitigation:** Before trusting JSON extraction results:
  1. Check `metadata.statusCode` — must be 200
  2. Check `metadata.url` against requested URL — detect redirects
  3. If either fails, discard results and fall back to Playwright

### Firecrawl Image-Heavy Pages
- **Risk:** SaaS landing pages with heavy image carousels produce ~95% image URLs in markdown
- **Mitigation:** For image-heavy pages, use Playwright snapshot instead of Firecrawl

## Evaluation Evidence

Full evaluation data: `Web & Browsers/phase-0-tool-evaluation.md`

### Key Metrics

| Tool | Reliability | Best Quality | Worst Quality | Unique Value |
|------|------------|-------------|--------------|-------------|
| Playwright MCP | 100% (2/2) | Navigation + form fill | Token-heavy snapshots | Always available, deterministic |
| Firecrawl MCP | 75% (3/4 tests) | Blog/docs extraction | Age-gated pages (hallucination) | Structured extraction, async agent |
| Chrome DevTools | 100% (3/3) | Lighthouse scores | Same token cost as Playwright | Lighthouse (unique), network panel |
| Browserbase | 100% (2/2 API) | Fast session (0.24s) | Full anti-detection untested | Cloud browser, anti-detection |
| browser_cookie3 | 100% (2/2) | Domain filtering | No Arc support | Cookie extraction with filtering |

## Next Steps

1. Phase 1 will build skills on this toolset:
   - `auth` skill → browser_cookie3 + Playwright
   - `browse` skill → Playwright MCP (+ Browserbase fallback)
   - `web-router` skill → selects Firecrawl vs Playwright based on task type
2. Firecrawl guardrails will be built into the `scrape` skill (Phase 2)
3. Chrome DevTools Lighthouse integration → `perf-audit` skill (Phase 3)
4. Stagehand v3 caching → revisit for `watch` skill if needed (Phase 4)
