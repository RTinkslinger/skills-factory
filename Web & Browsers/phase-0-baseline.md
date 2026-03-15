# Phase 0 Baseline — Web & Frontend Skills Portfolio

**Date:** 2026-03-14
**Sprint:** 2
**Status:** Complete

## What Was Evaluated

7 tools across 4 categories: browser automation, content extraction, cookie management, cloud infrastructure. 15 test scenarios executed, 5 failure scenarios tested.

## Layer 1 Toolset

| Tool | Version | Role | Reliability |
|------|---------|------|-------------|
| Playwright MCP | plugin built-in | Primary browser automation | 100% |
| Firecrawl MCP | @3.11.0 | Text/structured extraction | 75% (hallucination risk) |
| Chrome DevTools MCP | @0.20.0 | Lighthouse + network | 100% |
| Browserbase | API (live) | Anti-detection fallback | 100% (API-level) |
| browser_cookie3 | pip (venv) | Cookie extraction | 100% |

## Key Findings

1. **Firecrawl hallucinates on blocked pages** — JSON extraction fabricates data when content is inaccessible (age gates, redirects). Guardrail: validate `metadata.url` + `statusCode` before trusting results.

2. **browser-use and Stagehand v3 are redundant** — both add an LLM layer on Playwright. Claude Code already IS the LLM. Building browse skill directly on Playwright + Claude's reasoning is simpler and avoids double-LLM token costs.

3. **Firecrawl excels at text, fails at images** — blog/docs extraction is excellent. Image-heavy SaaS pages produce ~95% image URLs. Use Playwright for visual pages.

4. **Chrome DevTools' unique value is Lighthouse** — navigation/form fill matches Playwright (no advantage). Lighthouse audits (A11y/BP/SEO scores) and network inspection are capabilities no other tool provides.

5. **Browserbase session creation is fast (0.24s)** — viable as a fallback for bot-hostile sites. Not needed for general browsing.

## Failure Scenarios

| # | Scenario | Result |
|---|----------|--------|
| 1 | Chrome not running | Deferred to Phase 1 |
| 2 | Firecrawl on blocked content | **FAIL** — hallucinates data |
| 3 | browser-use timeout | Deferred (tool skipped) |
| 4 | Cookie keychain locked | **PASS** — clear error |
| 5 | Browserbase invalid key | **PASS** — 401 Unauthorized |

## Tool Selection Heuristic

```
IF text content (blog, docs, article) → Firecrawl scrape
IF structured data (pricing, specs) → Firecrawl extract
IF multi-source research → Firecrawl agent
IF interactive browsing → Playwright MCP
IF quality audit → Chrome DevTools Lighthouse
IF network debugging → Chrome DevTools network
IF bot-hostile site → Browserbase → Playwright
IF authenticated session → browser_cookie3 → Playwright
```

## Prerequisites for Phase 1

- [x] Layer 1 toolset decided
- [x] Firecrawl guardrails documented
- [x] Tool selection heuristic defined
- [ ] Droplet RAM upgrade (4GB, $24/mo) — blocker for remote execution
- [ ] Chrome install on droplet — needed for Chrome DevTools MCP

## References

- Evaluation report: `Web & Browsers/phase-0-tool-evaluation.md`
- Decision record: `Web & Browsers/layer-1-toolset.md`
- Design doc: `docs/superpowers/specs/2026-03-14-web-frontend-skills-portfolio-design.md`
- Implementation plan: `docs/superpowers/plans/2026-03-14-web-frontend-skills-portfolio.md`
