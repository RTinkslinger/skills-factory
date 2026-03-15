# Performance Audit Specialist - Development Log

## Overview
- **Purpose:** Measure, diagnose, and prescribe web performance fixes using Core Web Vitals and CSS 2026 knowledge
- **Scope:** 3-pass methodology (Measure/Diagnose/Prescribe), CSS 2026 performance wins, dual use (URL audit + code audit)
- **Methodology:** SKILL-CRAFT (expertise transfer, not instructions)

## Topic 1: Three-Pass Methodology
- Pass 1 Measure: Lighthouse via Chrome DevTools MCP, Core Web Vitals capture, performance traces
- Pass 2 Diagnose: Render-blocking resources, image issues, JS bloat, layout shift causes, server/network
- Pass 3 Prescribe: Ranked fixes with impact estimates, highest-impact/lowest-effort first
- Decision: Always run all three passes in order. Skipping measurement is the #1 mistake in performance work.

## Topic 2: CSS 2026 Performance Wins
- scroll-driven animations > AOS/ScrollReveal (30-50KB savings)
- anchor positioning > Popper.js (10-30KB savings)
- container queries > JS responsive logic
- native nesting > Sass/PostCSS
- :has() > JS querySelector traversal
- Decision: Include as prescriptions but gate on browser support requirements

## Topic 3: Tool Palette
- Primary: Chrome DevTools MCP (Lighthouse, performance traces, snapshots)
- Fallback: Playwright (performance.timing, network requests, screenshots)
- Decision: Chrome DevTools MCP preferred but Playwright fallback ensures the skill works everywhere

## Topic 4: Dual Use
- Web auditing: Lighthouse on live URL, real-world measurement, server + frontend prescriptions
- Code auditing: Pattern analysis without a URL, code-level fixes, CSS 2026 opportunities
- Decision: Both modes in one skill — the three-pass method adapts naturally

## Topic 5: Core Web Vitals Thresholds
- LCP: <2.5s good, >4.0s poor
- INP: <200ms good, >500ms poor
- CLS: <0.1 good, >0.25 poor
- FCP: <1.8s good, >3.0s poor
- TTFB: <800ms good, >1800ms poor
- Decision: Use Google's official thresholds (2024 update with INP replacing FID)

## Decisions Summary

| Decision | Rationale |
|---|---|
| 3-pass method (never skip) | Prevents premature optimization and ensures data-driven fixes |
| CSS 2026 wins table | Differentiator — generic tools don't know about native CSS replacements |
| Impact + effort on prescriptions | Users need to prioritize. "Fix everything" isn't actionable. |
| Chrome DevTools primary, Playwright fallback | Best tool when available, graceful degradation when not |
| INP not FID | FID deprecated March 2024, INP is the current metric |

## Files Created
- `perf-audit.md` — Performance audit specialist reference doc
- `skill-development-log.md` — this file
