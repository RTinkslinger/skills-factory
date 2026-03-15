# Search v3 — Development Log

## Overview
- **Purpose:** Evolve search-router v2 to v3 with Firecrawl search tier, environment awareness, observability, and browse integration
- **Scope:** Web search routing — selecting the right search tool for the query
- **Methodology:** SKILL-CRAFT (delta from v2)
- **Started:** 2026-03-14

## Changes from v2

### Added
1. **Firecrawl search tier** — web search + optional scrape in one call, fills gap between WebSearch (free/shallow) and Parallel (deep/expensive)
2. **Environment awareness** — CAI may lack Exa/Parallel; Agent SDK may lack some tools
3. **Observability logging** — which tool selected, why, outcome
4. **Browse integration** — "search then navigate to result" pattern
5. **Firecrawl map** — URL discovery for site-specific search

### Preserved
- All v2 routing logic (Context7 → WebSearch → Exa → Parallel cascade)
- Cost optimization (free tools first)
- Parallel processor selection logic

## Files Created
- `search/skill-development-log.md` (this file)
- `search/search.md` (reference doc, evolved from v2)
