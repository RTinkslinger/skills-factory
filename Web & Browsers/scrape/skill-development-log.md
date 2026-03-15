# Scrape Specialist — Development Log

## Overview
- **Purpose:** Extract structured or unstructured content from web pages — text, data, schema-driven fields
- **Scope:** Extraction only. Navigation is delegated to browse. Auth is delegated to auth.
- **Methodology:** SKILL-CRAFT
- **Started:** 2026-03-14

## Topic 1: Understanding ✓

### Problem
Claude has multiple extraction tools but no framework for choosing between them:
- Firecrawl scrape (clean markdown) vs Firecrawl extract (schema JSON) vs Firecrawl agent (async research)
- Playwright DOM parsing (full control) vs Chrome DevTools (network data)
- Each has failure modes discovered in Phase 0 (Firecrawl hallucination, image-heavy pages)

### Trigger
- "extract data from", "scrape", "get the content of", "pull [fields] from [URL]"
- "crawl [site]", "extract all [items] from [pages]"
- Invoked by web-router when task = extraction

### Success Criteria
- Right extraction tool selected based on content type and output format
- Schema-driven extraction returns typed fields, not free text
- Firecrawl guardrails enforced (metadata validation)
- Pagination and bulk crawl handled gracefully

### Out of Scope
- Navigation to the page (browse handles that)
- Authentication (auth handles that)
- Web search (search handles that)

## Topic 2: Exploring ✓

### Where Claude Fails Without This Skill
1. Uses Firecrawl on image-heavy pages → gets garbage output
2. Uses markdown scrape when schema extraction would give cleaner results
3. Trusts Firecrawl JSON without checking metadata → accepts hallucinated data
4. Doesn't handle pagination — extracts page 1 and stops
5. Picks Playwright for static text when Firecrawl is faster and cheaper

## Topic 3: Research + Synthesis ✓

### Phase 0 Findings Applied
- Firecrawl blog scrape: excellent (clean markdown)
- Firecrawl extract: excellent (schema-enforced JSON, 38 credits)
- Firecrawl agent: excellent (autonomous multi-source)
- Firecrawl on images: poor (95% image URLs)
- Firecrawl hallucination: critical (fabricates data on blocked pages)
- Playwright DOM: reliable but token-heavy

### Extracted Principles
1. **Content type determines tool** — text → Firecrawl, interactive → Playwright, visual → screenshot
2. **Schema extraction > free-form** — when you know what fields you want, use schema mode
3. **Validate before trust** — Firecrawl metadata check is mandatory, not optional
4. **Boundary discipline** — scrape extracts, browse navigates. Don't mix.

## Decisions Summary

| Decision | Choice | Rationale |
|---|---|---|
| Text extraction default | Firecrawl scrape (markdown) | Fastest, cheapest, cleanest for text |
| Structured extraction | Firecrawl extract (JSON schema) | Schema enforcement, typed output |
| Image-heavy pages | Playwright snapshot | Firecrawl returns garbage on image-heavy sites |
| Multi-page research | Firecrawl agent (async) | Autonomous, handles navigation internally |
| Pagination | Firecrawl crawl (limited depth) | Built-in pagination, depth controls |
| Fallback | Playwright DOM parsing | When Firecrawl fails or is blocked |

## Files Created
- `scrape/skill-development-log.md` (this file)
- `scrape/scrape.md` (reference doc)
