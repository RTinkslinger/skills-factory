# Milestone 2: Phase 0 Completion + Phase 1 Foundation
**Iterations:** 4-6 | **Dates:** 2026-03-14

## Summary
Completed Phase 0 tool evaluation for all 7 Layer 1 tools. Decided the toolset: Playwright (core), Firecrawl (core with guardrails), Chrome DevTools (supplementary), Browserbase (fallback), browser_cookie3 (core). Excluded browser-use and Stagehand v3 as redundant LLM layers. Critical finding: Firecrawl hallucinates JSON on blocked pages. Started Phase 1 — built tool-selection framework, auth specialist (6-layer model + cookie sync), browse specialist (Navigate→Snapshot→Act→Verify), and web-router skill (classification + routing).

## Key Decisions
- Firecrawl Conditional Include: needs metadata.url + statusCode validation before trusting JSON extraction (hallucination on age-gated pages)
- browser-use Skip: Claude Code IS the LLM — adding another LLM layer is redundant and doubles token cost
- Stagehand v3 Defer: same redundancy as browser-use, but selector caching worth revisiting for Phase 4 watch skill
- Auth uses 6-layer escalation (No Auth → API → Cookie → Remote Cookie → Browserbase → Human)
- Browse uses Snapshot→Act→Verify pattern with max 2 snapshots per interaction
- Router loads max 3 reference docs per task to control token budget

## Iteration Details

### Iteration 4 - 2026-03-14
**Phase:** Phase 0: Tool Evaluation
**Focus:** Firecrawl MCP + Chrome DevTools MCP evaluation

**Changes:** `Web & Browsers/phase-0-tool-evaluation.md` (Chrome DevTools + Firecrawl results), `LEARNINGS.md` (hallucination + image-heavy patterns)
**Decisions:** Firecrawl Include-Conditional (needs redirect/hallucination guardrails) -> JSON extraction hallucinates on blocked pages. Chrome DevTools Include (unique Lighthouse value) -> complement to Playwright, not replacement.
**Critical finding:** Firecrawl fabricates structured data when page is behind age gate/redirect — must validate metadata.url + statusCode before trusting results.

---

### Iteration 5 - 2026-03-14
**Phase:** Phase 0: Tool Evaluation
**Focus:** browser-use, Browserbase, Stagehand v3 eval + Layer 1 decision record

**Changes:** `Web & Browsers/phase-0-tool-evaluation.md` (all 7 tools evaluated), `Web & Browsers/layer-1-toolset.md` (decision record), `LEARNINGS.md` (updated)
**Decisions:** browser-use SKIP (redundant LLM layer) -> Claude Code IS the LLM. Stagehand v3 DEFER (same redundancy, revisit Phase 4). Browserbase INCLUDE as fallback (anti-detection). Layer 1 toolset: Playwright (core) + Firecrawl (core w/ guardrails) + Chrome DevTools (supplementary) + Browserbase (fallback) + browser_cookie3 (core).

---

### Iteration 6 - 2026-03-14
**Phase:** Phase 0 close + Phase 1 Foundation
**Focus:** Phase 0 baseline + Phase 1 skills (tool-selection, auth, browse, web-router)

**Changes:** `Web & Browsers/phase-0-baseline.md` (Phase 0 summary), `Web & Browsers/tool-selection.md` (6-dimension framework), `Web & Browsers/auth/` (auth specialist + service registry + cookie-sync.sh), `Web & Browsers/browse/` (browse specialist), `Web & Browsers/web-router/` (SKILL.md router), `ROADMAP.md` (Phase 0 → Verifying, Phase 1 → In Progress)
**Decisions:** tool-selection framework adapted from design doc (removed excluded tools). Auth uses 6-layer escalation model. Browse uses Navigate→Snapshot→Act→Verify pattern. Router loads max 3 reference docs per task.
