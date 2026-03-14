# Design Review Pass 3 — Consolidated Findings

**Date:** 2026-03-14
**Reviewers:** Systems Architect + QA Engineer + DevOps Engineer (all Claude Opus 4.6)
**Document:** `docs/superpowers/specs/2026-03-14-web-frontend-skills-portfolio-design.md`
**Prior reviews:** Pass 1 (subagent), Pass 2 (architect) — all fixes applied before this pass

---

## Review Summary

| Lens | BLOCKING | MAJOR | MINOR | Total |
|---|---|---|---|---|
| Systems Architect | 2 | 4 | 4 | 10 |
| QA Engineer | 2 | 4 | 4 | 10 |
| DevOps Engineer | 2 | 5 | 3 | 10 |
| **Unique (deduplicated)** | **5** | **11** | **8** | **24** |

Three findings overlap across reviewers (marked below). After deduplication: **24 unique findings**.

---

## BLOCKING Findings (5) — Must fix before any build starts

### B1. Composite task classification unspecified (Architect)
**What:** Router doesn't specify which reference docs to load for tasks spanning multiple specialists (e.g., "monitor competitor pricing with login" = watch + auth + browse + scrape).
**Fix:** Add composite task classification matrix. Max 3 docs per task. Define canonical combinations.

### B2. 5-dimension conflict resolution missing (Architect + QA overlap)
**What:** When dimensions contradict (hostile site + sub-second speed), no tiebreaker exists. Both architect and QA flagged this independently.
**Fix:** Add dimension priority order: Auth Safety > Site Hostility > Task Complexity > Speed > Cost. Hard constraints win over soft preferences. Add conflict resolution section to `tool-selection.md`.

### B3. No negative-path test scenarios (QA)
**What:** Every testing gate tests happy paths only. Zero tests for: tool unavailable, site 429, auth fails, MCP timeout, empty extraction, fallback chain activation.
**Fix:** Add one failure-path scenario per phase. Phase 1: "URL returns 403 — verify graceful error" + "expired cookie — verify escalation." Phase 2: "rate-limited — verify retry." Phase 3: "localhost down — verify diagnostic." Phase 4: "URL 404s on 2nd check — verify alert."

### B4. Regression comparison method undefined for LLM output (QA)
**What:** "Compare output quality against baseline" is meaningless for non-deterministic LLM output. Same skill + same scenario = different wording each run.
**Fix:** Define structural pass/fail: specific fields in output must match (e.g., `tool_selected: firecrawl`). Minimum signal checklist per scenario (3-5 required signals). Codify in `phase-N-baseline.md`.

### B5. Droplet RAM upgrade is a Phase 1 prerequisite (DevOps)
**What:** 1GB RAM + existing services (~500MB) + Chrome (~300-600MB) = OOM. Installing Playwright on current droplet will kill ai-cos-mcp.
**Fix:** Upgrade to $24/mo (4GB) BEFORE Chrome installation. Add to Phase 1 Step 1.1 as first item. This is a blocker for the AI CoS project, not Skills Factory — communicate via cross-sync.

---

## MAJOR Findings (11)

### M1. Router scaling ceiling undefined (Architect)
**Fix:** Document: "If specialist count exceeds 10, decompose into sub-routers."

### M2. Deliverables table `Lives In` contradicts architecture (Architect)
**Fix:** Deliverables 2-8 should say `~/.claude/skills/web-router/references/` not `~/.claude/skills/`.

### M3. Missing Dimension 6: output format / consumer type (Architect)
**Fix:** Add dimension: Structured JSON, Clean markdown, Raw HTML, Visual/screenshot, Streaming.

### M4. Failure-state log schema absent (Architect)
**Fix:** Add `failure` block to log schema: `primary_error`, `fallback_chain`, `first_success_at`, `graceful_degradation`.

### M5. CAI/Agent SDK test pass criteria weaker than CC (QA)
**Fix:** Same three-part structure for all surfaces: what triggers, what is verified, what constitutes pass.

### M6. Observability system itself untested (QA)
**Fix:** Phase 1 gate adds: verify log file exists, valid YAML, all required fields present.

### M7. QA health scoring untested against known defects (QA)
**Fix:** Calibration scenario: run QA on page with planted defects, verify score decreases and defects appear.

### M8. No MCP server process supervision on droplet (DevOps)
**Fix:** Every MCP server gets a systemd unit. Post-deploy verification. Liveness health check.

### M9. Cookie staging in /tmp/ is world-readable (DevOps)
**Fix:** Extract to `chmod 600` in `~/.ai-cos/cookies/`, never `/tmp/`.

### M10. ai-cos-mcp + browser ops = fault isolation failure (DevOps)
**Fix:** DECIDE NOW: separate web-tools MCP process. Chrome must not share process with ai-cos-mcp.

### M11. deploy.sh unspecified + secret rotation undocumented (DevOps)
**Fix:** Specify deploy.sh fully (rsync flags, checksum verification, DEPLOYED_VERSION). Create secrets-manifest.md with rotation procedure.

---

## MINOR Findings (8)

### m1. Auth registry staleness undetected (Architect)
**Fix:** Skill checks `Last Verified` date before using strategy.

### m2. Phase 5 CLAUDE.md merge timing unsafe (Architect)
**Fix:** Commit CLAUDE.md changes atomically between phases.

### m3. Layer 1→2 transition gate missing (Architect)
**Fix:** Add `layer-1-toolset.md` decision record between Phase 0 and Phase 1.

### m4. Observability has no degradation mode (Architect)
**Fix:** "Logging is best-effort. Never block primary task for observability."

### m5. Rollback procedure untested (QA)
**Fix:** Phase 1 rollback drill after first deployment.

### m6. Stagehand caching criterion qualitative (QA)
**Fix:** Specify: "2nd+ run at least 30% faster, cached selector verified in debug log."

### m7. SQLite state excluded from disaster recovery (DevOps)
**Fix:** Document what's lost if droplet dies. Backup via DO snapshots.

### m8. Unpinned MCP versions break without warning (DevOps)
**Fix:** Pin versions in ~/.mcp.json. Update intentionally.

---

## Cross-Reviewer Overlaps

| Finding | Flagged By | Convergence |
|---|---|---|
| **Dimension conflict resolution** | Architect (F2) + QA (F4) | Both independently identified the same gap. Architect proposed priority order; QA proposed hard/soft constraint distinction. These are the same fix. |
| **Cookie sync reliability** | DevOps (F2) + Architect (implicit in auth registry F7) | DevOps flagged infrastructure failure modes. Architect flagged the downstream effect (stale strategies). Both point to the same root cause: no staleness detection. |
| **Observability gaps** | Architect (F6 failure schema) + QA (F5 log verification) + DevOps (implicit in m9 silent specialist) | Three lenses converging: architect wants richer schema, QA wants the schema tested, DevOps wants failures to be observable. All three are saying: "the observability system is under-designed." |

---

## Recommended Fix Priority

**Before Phase 0 starts (design doc fixes):**
1. B1 — Composite task classification matrix
2. B2 — Dimension conflict resolution + priority order
3. B3 — Negative-path test scenarios added to all gates
4. B4 — Regression comparison method defined
5. M2 — Deliverables table corrected
6. M3 — Dimension 6 added
7. M4 — Failure-state log schema
8. M10 — Decide: separate web-tools MCP (resolve architecture question)
9. m8 — Pin MCP versions in configs

**During Phase 0 (can be resolved alongside tool evaluation):**
10. M1 — Document router scaling ceiling
11. M5 — Strengthen CAI/Agent SDK test criteria
12. M6 — Add log verification to Phase 1 gate
13. M7 — Design QA calibration scenario
14. m3 — Create layer-1-toolset.md template
15. m4 — Add observability degradation note
16. m6 — Quantify Stagehand caching pass criteria

**During Phase 1 (operational setup):**
17. B5 — Droplet RAM upgrade (cross-sync to AI CoS)
18. M8 — Systemd units for all MCP servers
19. M9 — Cookie staging security fix
20. M11 — deploy.sh spec + secrets-manifest.md
21. m1 — Auth registry staleness check
22. m2 — Phase 5 merge timing note
23. m5 — Rollback drill
24. m7 — SQLite backup plan

---

## Verdict

The design is architecturally sound and comprehensively scoped. The three-tier model, 5-dimension framework, and layered auth are genuinely strong foundations. The issues found in Pass 3 are about **operational hardening** (DevOps), **testability depth** (QA), and **edge-case reasoning** (Architect) — not about the core architecture being wrong.

The 5 BLOCKING items must be resolved in the design doc before Phase 0 starts. The 11 MAJOR items should be resolved before Phase 1 starts, with M10 (fault isolation decision) being the most consequential.

After these fixes, this design is ready to build from.
