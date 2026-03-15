# Build Traces

## Project Summary

Web & Frontend Skills Portfolio project. Design doc + impl plan shipped (user verified). 9-tool Layer 1 toolset with tiered extraction cascade (Jina Reader → Firecrawl → Playwright → browser-use). Phases 0-2 shipped: tool evaluation, foundation (auth/browse/web-router/tool-selection), extraction (scrape/search v3). Phase 3 (qa + perf-audit) built and deployed. Jina Reader is default extractor (FREE, fastest, best CF penetration). Firecrawl hallucination guardrail mandatory. Notion Build Roadmap active with 8 items (5 shipped, 1 verifying, 2 backlog).

## Milestone Index

| # | Iterations | Focus | Key Decisions |
|---|------------|-------|---------------|
| 1 | 1-3 | Design finalization + Phase 0 start | 24 review fixes applied, browser_cookie3 for cookies, Firecrawl@3.11.0 + Chrome DevTools@0.20.0 pinned |
| 2 | 4-6 | Phase 0 completion + Phase 1 Foundation | Firecrawl hallucination guardrails, browser-use/Stagehand skipped (redundant), Layer 1 toolset decided, auth/browse/web-router skills built |
| 3 | 7-11 | Phase 1-2 deployment + verification + Phase 0 extended eval | Jina Reader surprise winner (FREE, 6/6 URLs), extraction cascade reshaped, browser-use re-added as fallback, Phases 0/1/2 shipped |

*Full details: `traces/archive/milestone-N.md`*

<!-- end-header -->

---

## Current Work (Milestone 4 in progress)

### Iteration 12 - 2026-03-14
**Phase:** Phase 3: Quality
**Focus:** Build qa + perf-audit specialists, deploy to web-router

**Changes:** `Web & Browsers/qa/qa.md` (qa specialist — 4 modes, 8-category health scoring, framework patterns, baseline regression), `Web & Browsers/perf-audit/perf-audit.md` (perf-audit specialist — 3-pass Measure/Diagnose/Prescribe, CSS 2026 wins, Core Web Vitals), `Web & Browsers/qa/skill-development-log.md`, `Web & Browsers/perf-audit/skill-development-log.md`, deployed to `~/.claude/skills/web-router/references/` (qa.md + perf-audit.md)
**Decisions:** QA uses auto-mode-selection (diff-aware on branches, full on main). Health score = weighted average of 8 categories (Functional 20%, Console/UX/A11y 15% each). Perf-audit uses INP not FID (deprecated March 2024). CSS 2026 wins table differentiates from generic perf tools. Both gracefully degrade without Chrome DevTools MCP.
**Next:** Phase 4 (watch) or Phase 5 (frontend refresh). Phase 3 in Verifying.

---

### Iteration 13 - 2026-03-14
**Phase:** Phase 4: Intelligence
**Focus:** Build watch specialist, deploy to web-router

**Changes:** `Web & Browsers/watch/watch.md` (watch specialist — 5 monitoring types, baseline/check/diff/alert cycle, environment-aware state storage), `Web & Browsers/watch/skill-development-log.md`, deployed to `~/.claude/skills/web-router/references/watch.md`
**Decisions:** 5 monitoring types (content/price/availability/visual/performance). Watch delegates extraction to scrape/perf-audit specialists — it's the loop orchestrator, not the extractor. CC = manual re-checks (not a daemon), Agent SDK = cron jobs, CAI = configure+query via MCP. State: JSON files in CC, SQLite on droplet.
**Next:** Phase 5 (frontend refresh). Phase 4 in Verifying.

---

### Iteration 14 - 2026-03-14
**Phase:** Phase 5: Frontend Refresh
**Focus:** Update design-system-enforcer, a11y-audit, and CLAUDE.md with CSS 2026 + Vite 8 + WCAG 2.2

**Changes:** `~/.claude/skills/design-system-enforcer/SKILL.md` (CSS 2026 baseline table, Vite 8 section with Context7 grounding, anti-drift failsafes, 2 new traps), `~/.claude/skills/a11y-audit/SKILL.md` (Lighthouse a11y pass 2.5, touch targets upgraded to WCAG 2.2, prefers-reduced-motion enforcement, keyboard testing patterns section), `~/.claude/CLAUDE.md` (CSS 2026 Baseline section, Build Tool Default section, 4 new anti-patterns), source backups in `Frontend Skills/design-system-enforcer-v2/` and `Frontend Skills/a11y-audit-v2/`
**Decisions:** CSS 2026 patterns are mandatory for new projects (container queries, :has(), native nesting, oklch, scroll-driven animations, anchor positioning, view transitions). Vite is default scaffolding tool. Anti-drift via Context7 queries at trigger time. Touch targets: 44px min (WCAG 2.2 AA), 48px recommended mobile. prefers-reduced-motion is mandatory for all animations.
**Next:** All phases (0-5) built. Verify Phase 3, 4, 5 with user.

---
