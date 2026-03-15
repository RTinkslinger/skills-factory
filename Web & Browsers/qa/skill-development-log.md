# QA Specialist - Development Log

## Overview
- **Purpose:** Systematic web app testing with structured reports and health scoring
- **Scope:** 4 testing modes (Quick, Diff-Aware, Full, Regression), 8-category health scoring, framework-specific patterns
- **Methodology:** SKILL-CRAFT (expertise transfer, not instructions)

## Topic 1: Testing Modes
- Quick (30s smoke), Diff-Aware (git diff scoped), Full (systematic crawl), Regression (baseline comparison)
- Default behavior: Diff-Aware on feature branches, Full on main
- Decision: Don't ask the user which mode — read context and pick

## Topic 2: Health Scoring
- 8 categories with weights from design doc Section 5.5
- Heaviest weights: Functional (20%), Console (15%), UX (15%), Accessibility (15%)
- Score clamped 0-100, interpretation bands: 90+ solid, 70-89 needs work, <50 critical
- Decision: Per-category scoring with weighted average — simple enough to be useful, detailed enough to track improvement

## Topic 3: Framework Detection
- Next.js (hydration, _next/data), Rails (CSRF, Turbo), WordPress (plugin conflicts), SPAs (state, deep linking)
- Decision: Include top 4 frameworks. Others can be added as encountered.

## Topic 4: Tool Palette
- Primary: Playwright MCP (snapshot, screenshot, interact, console, network)
- Secondary: Chrome DevTools MCP (deeper console, network timing)
- Decision: Playwright is sufficient alone — Chrome DevTools adds depth but isn't required

## Topic 5: Boundaries
- Performance profiling → perf-audit
- Deep accessibility → a11y-audit
- Security testing → out of scope
- Code review → out of scope (except git diff for diff-aware mode)

## Decisions Summary

| Decision | Rationale |
|---|---|
| 4 modes, auto-selected | Users shouldn't have to choose — context determines mode |
| 8 weighted categories | Covers all quality dimensions, weights reflect impact on user experience |
| Framework-specific section | Generic QA misses framework-specific bugs (hydration, CSRF, etc.) |
| YAML baseline format | Simple, human-readable, supports regression comparison |
| Severity levels (4) | Critical/Major/Minor/Cosmetic — standard QA language |

## Files Created
- `qa.md` — QA specialist reference doc
- `skill-development-log.md` — this file
