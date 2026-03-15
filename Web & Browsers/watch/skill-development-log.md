# Watch Specialist - Development Log

## Overview
- **Purpose:** Monitor websites for changes over time — content, price, availability, visual, performance
- **Scope:** Baseline capture, periodic re-check, diff, alert. 5 monitoring types.
- **Methodology:** SKILL-CRAFT (expertise transfer, not instructions)

## Topic 1: Core Pattern
- Baseline → Check → Diff → Decide (alert or skip)
- Decision: Same cycle for all 5 monitoring types. Type only affects extraction and diff methods.

## Topic 2: Monitoring Types
- Content (text diff), Price (numeric comparison), Availability (boolean), Visual (screenshot hash), Performance (Lighthouse scores)
- Decision: 5 types cover the practical use cases. Content is the default when user is vague.

## Topic 3: State Storage
- CC: JSON files in `~/.ai-cos/watch/`
- Agent SDK: SQLite on droplet (`/opt/ai-cos-mcp/watch.db`)
- CAI: Via MCP to droplet SQLite
- Decision: Match storage to environment. JSON for simplicity in CC, SQLite for atomicity on droplet.

## Topic 4: Environment Behavior
- CC = interactive (manual re-checks or /loop)
- Agent SDK = autonomous (cron jobs)
- CAI = configure + query via MCP
- Decision: Watch skill is environment-aware but CC can't do true background monitoring.

## Topic 5: Delegation
- Scrape specialist handles extraction
- Perf-audit handles Lighthouse
- Browse handles navigation
- Decision: Watch is the loop orchestrator, not the extractor. Delegates to existing specialists.

## Decisions Summary

| Decision | Rationale |
|---|---|
| 5 monitoring types | Covers real use cases without overcomplicating |
| Content as default type | Most common ask is "tell me if something changes" |
| JSON in CC, SQLite on droplet | Match storage to environment capabilities |
| Delegate extraction to specialists | Don't duplicate scrape/perf-audit logic |
| No true background in CC | CC isn't a daemon — honest about limitations |

## Files Created
- `watch.md` — Watch specialist reference doc
- `skill-development-log.md` — this file
