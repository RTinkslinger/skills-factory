# Design Review Pass 3 — Systems Architect

**Date:** 2026-03-14
**Reviewer:** Claude Opus 4.6 (Systems Architect lens)
**Document:** `docs/superpowers/specs/2026-03-14-web-frontend-skills-portfolio-design.md`

---

## Strengths

- Reference-doc-inside-router pattern cleanly solves CC skill-activation collision
- Three-tier model is sound. Phase 0 tool evaluation before any skill writing is exactly right.
- Auth layering is production-grade thinking.

---

## Findings

### FINDING 1 — BLOCKING: Composite task classification unspecified

**Issue:** A task like "monitor competitor pricing (requires login)" spans watch, auth, browse, and scrape. Router doesn't specify which reference docs to load for composite tasks, or the maximum doc-load.
**Fix:** Add composite task classification matrix. Define: single-specialist tasks (1 doc), multi-specialist (2-3 docs), max load = 3. Canonical combos: "watch + auth + scrape" for authenticated monitoring.

### FINDING 2 — BLOCKING: 5-dimension conflict resolution missing

**Issue:** Speed=sub-second + hostility=adversarial produce opposing tool recommendations. No tiebreaker.
**Fix:** Add dimension priority: Auth Safety > Site Hostility > Task Complexity > Speed > Cost. Hard constraints win over soft preferences.

### FINDING 3 — MAJOR: Router scaling ceiling undefined

**Issue:** At 13+ specialists, router's classification logic grows O(n). SKILL.md becomes too long.
**Fix:** Document ceiling: "If specialist count exceeds 10, decompose into sub-routers." Current 8 is under ceiling.

### FINDING 4 — MAJOR: Section 14 deliverables `Lives In` contradicts architecture

**Issue:** Deliverables 2-8 say `~/.claude/skills/` but architecture says specialists are reference docs inside web-router.
**Fix:** Change `Lives In` to `~/.claude/skills/web-router/references/`.

### FINDING 5 — MAJOR: Missing Dimension 6: output format / consumer type

**Issue:** Two identical tasks with different consumers (human JSON inspection vs database pipeline) need different tools.
**Fix:** Add Dimension 6: Output Format — structured JSON, clean markdown, raw HTML, visual/screenshot, streaming.

### FINDING 6 — MAJOR: Failure-state log schema absent

**Issue:** Log schema has no structure for cascading failures through fallback chains.
**Fix:** Add `failure` block: primary_error, fallback_chain, first_success_at, graceful_degradation.

### FINDING 7 — MINOR: Auth registry has no staleness detection

**Fix:** Auth skill checks `Last Verified` date before using strategy. Flag if stale.

### FINDING 8 — MINOR: Phase 5 CLAUDE.md not safe to merge mid-phase

**Fix:** Phase 5 CLAUDE.md changes committed atomically between phases, not mid-phase.

### FINDING 9 — MINOR: No explicit gate between Layer 1 verification and Layer 2 build

**Fix:** Add `layer-1-toolset.md` decision record between Phase 0 and Phase 1.

### FINDING 10 — MINOR: Observability has no degradation mode

**Fix:** "Logging is best-effort. Never block primary task for observability."

---

## Summary

| # | Severity | Issue |
|---|---|---|
| 1 | BLOCKING | Composite task classification — which docs to load unspecified |
| 2 | BLOCKING | 5-dimension conflict resolution — no priority order |
| 3 | MAJOR | Router scaling ceiling undefined |
| 4 | MAJOR | Deliverables table contradicts sole-entry-point architecture |
| 5 | MAJOR | Missing Dimension 6: output format |
| 6 | MAJOR | Failure-state log schema absent |
| 7 | MINOR | Auth registry staleness undetected |
| 8 | MINOR | Phase 5 CLAUDE.md merge timing unsafe |
| 9 | MINOR | Layer 1→2 transition gate missing |
| 10 | MINOR | Observability no degradation mode |
