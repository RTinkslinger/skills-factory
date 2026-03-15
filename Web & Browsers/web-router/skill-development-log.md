# Web Router — Development Log

## Overview
- **Purpose:** Classify web tasks and route to the right specialist(s), loading only the reference docs needed
- **Scope:** Task classification, environment detection, specialist invocation, composite task handling
- **Methodology:** SKILL-CRAFT
- **Started:** 2026-03-14

## Topic 1: Understanding ✓

### Problem
Without a router, Claude either:
- Uses the wrong tool (Firecrawl for interactive pages, Playwright for static text)
- Loads all reference docs (token waste)
- Doesn't think about auth requirements until it hits a login wall
- Doesn't log tool selection decisions (no observability)

### Trigger
Any web-related task: "browse to", "scrape", "extract data from", "check the website", "search for", "monitor [site]", "log in to", "audit [page]"

### Success Criteria
- Correct specialist selected for the task type
- Max 3 reference docs loaded per task (token budget)
- Auth needs detected before starting work
- Tool selection logged for observability

## Decisions Summary

| Decision | Choice | Rationale |
|---|---|---|
| Architecture | SKILL.md → references/ | Trigger in SKILL.md, expertise in reference docs |
| Max loaded docs | 3 per task | Token budget — full reference docs are 2-5KB each |
| Routing model | Classification matrix | Fast, deterministic, no LLM call for routing |

## Files Created
- `web-router/skill-development-log.md` (this file)
- `web-router/SKILL.md` (the skill)
