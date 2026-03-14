# Design Review Pass 3 — QA Engineer

**Date:** 2026-03-14
**Reviewer:** Claude Opus 4.6 (QA Engineer lens)
**Document:** `docs/superpowers/specs/2026-03-14-web-frontend-skills-portfolio-design.md`
**Prior reviews:** Pass 1 (subagent), Pass 2 (architect) — fixes applied

---

## Strengths

- Testing gates are scenario-driven, not checklist-driven — each has surface, task, pass criteria
- Phase 0 correctly placed as a true blocker
- Baseline documentation plan (Section 12) stores actual output alongside expected — makes regression meaningful

---

## Findings

### FINDING 1 — BLOCKING: No negative-path test scenarios

**Location:** Section 9, all phase testing gates
**Issue:** Every test scenario tests the happy path. Zero tests for: tool unavailable, site returns 429, auth fails, MCP timeout, extraction returns empty/malformed data, fallback chain activation.
**Fix:** Add one failure-path scenario per phase:
- Phase 1: "Navigate to URL returning 403 — verify graceful error" + "auth cookie expired — verify escalation"
- Phase 2: "Scrape page that rate-limits on 2nd request — verify delay/retry"
- Phase 3: "QA on localhost when localhost is down — verify diagnostic output"
- Phase 4: "Watch URL that 404s on 2nd check — verify alert behavior"

### FINDING 2 — BLOCKING: Regression test comparison method undefined for LLM output

**Location:** Section 12 (Regression Testing)
**Issue:** "Compare output quality against baseline" is undefined for non-deterministic LLM output. Same skill, same scenario = different wording each run.
**Fix:** Define concrete pass/fail:
- Structural output: test scenarios produce structured data where specific fields can be compared (e.g., `tool_selected` must be `firecrawl`, `fallback_used` must be `false`)
- Minimum signal checklist: 3-5 required signals per scenario (e.g., "must name tool selected", "must include hostility assessment")
- Codify in `phase-N-baseline.md`

### FINDING 3 — MAJOR: CAI/Agent SDK test pass criteria are weaker than CC

**Location:** Section 9, Phases 1-2
**Issue:** CC tests specify what activates, what is logged, what is returned. CAI tests say only "Works in CAI." Agent SDK tests reference schemas never defined.
**Fix:** Same three-part structure for all surfaces: what triggers, what is verified, what constitutes a pass.

### FINDING 4 — MAJOR: No dimension conflict resolution in tool selection framework

**Location:** Section 4
**Issue:** When dimensions contradict (hostile site + sub-second speed), no tiebreaker exists. Framework leaves Claude to improvise.
**Fix:** Add conflict resolution: define hard constraints (auth sensitivity, site hostility) vs soft preferences (speed, cost). Hard constraints win. Skill flags tradeoff to user.

### FINDING 5 — MAJOR: No test verifies the observability system itself

**Location:** Sections 4 + 11
**Issue:** Logs are the learning loop's input. If log format is wrong, patterns don't graduate and learning degrades silently.
**Fix:** Phase 1 testing gate adds: verify `~/.claude/web-logs/browse-YYYY-MM.yml` exists, is valid YAML, has all 10 required fields, numeric types are correct.

### FINDING 6 — MAJOR: QA health scoring not tested against known defects

**Location:** Section 9, Phase 3
**Issue:** Test verifies report exists, not that scoring is correct. A 95/100 on a page with broken links passes the gate.
**Fix:** Calibration scenario: run QA on page with planted defects (broken link, console error, inaccessible button). Verify score decreases and defects appear in report.

### FINDING 7 — MINOR: Rollback procedure is untested

**Fix:** Phase 1 rollback drill: deliberate trivial change → deploy → test → rollback → verify restored.

### FINDING 8 — MINOR: Stagehand caching test criterion is qualitative

**Fix:** Specify threshold: "2nd+ run at least 30% faster, debug log confirms cached selector used."

### FINDING 9 — MINOR: Phase 2 Agent SDK "expected schema" never defined

**Fix:** Define test schema for company profile extraction in Phase 2 step 2.1.

### FINDING 10 — MINOR: No verification that graduated patterns are applied

**Fix:** After graduation during compaction, re-run the triggering test scenario and verify the pattern is visible in skill reasoning.

---

## Summary

| # | Severity | Area |
|---|---|---|
| 1 | BLOCKING | No negative-path test scenarios |
| 2 | BLOCKING | Regression comparison undefined for LLM output |
| 3 | MAJOR | CAI/Agent SDK pass criteria weaker than CC |
| 4 | MAJOR | No dimension conflict resolution |
| 5 | MAJOR | Observability system itself untested |
| 6 | MAJOR | QA health scoring untested against known defects |
| 7 | MINOR | Rollback procedure untested |
| 8 | MINOR | Stagehand caching criterion qualitative |
| 9 | MINOR | Phase 2 schema undefined |
| 10 | MINOR | Graduated pattern verification missing |
