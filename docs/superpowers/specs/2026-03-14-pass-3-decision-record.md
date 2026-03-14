# Pass 3 Review — Decision Record

**Date:** 2026-03-14
**Reviewed by:** Aakash Kumar
**Method:** All 24 unique findings reviewed one-by-one via AskUserQuestion

---

## Decisions

All 24 findings ACCEPTED. One finding upgraded (B3).

### BLOCKING (5/5 accepted)

| # | Finding | Decision | Notes |
|---|---|---|---|
| B1 | Composite task classification unspecified | **Accept** | Add classification matrix, max 3 docs per task, define canonical combos |
| B2 | 5-dimension conflict resolution missing | **Accept** | Priority order: Auth Safety > Site Hostility > Task Complexity > Speed > Cost. Hard constraints win. |
| B3 | No negative-path test scenarios | **Accept + UPGRADE** | User directive: **5-6 failure scenarios per phase**, not just one. Covers: 403, expired cookies, rate limits, MCP timeout, empty extraction, fallback chain activation. |
| B4 | Regression comparison undefined for LLM output | **Accept** | Structural field matching + minimum signal checklist (3-5 required signals per scenario) |
| B5 | Droplet RAM upgrade is Phase 1 prerequisite | **Accept** | Upgrade to $24/mo (4GB) BEFORE Chrome install. Cross-sync to AI CoS as blocker. |

### MAJOR (11/11 accepted)

| # | Finding | Decision | Notes |
|---|---|---|---|
| M1 | Router scaling ceiling undefined | **Accept** | Document 10-specialist ceiling, sub-router decomposition plan |
| M2 | Deliverables table contradicts architecture | **Accept** | Change Lives In to ~/.claude/skills/web-router/references/. User also flagged: this was a Pass 2 fix that didn't cascade — must verify all downstream references this time. |
| M3 | Missing Dimension 6: output format | **Accept** | Add 6th dimension: Structured JSON, Clean markdown, Raw HTML, Visual/screenshot, Streaming |
| M4 | Failure-state log schema absent | **Accept** | Add failure block: primary_error, fallback_chain, first_success_at, graceful_degradation |
| M5 | CAI/Agent SDK test criteria weaker than CC | **Accept** | Same three-part structure for all surfaces |
| M6 | Observability system itself untested | **Accept** | Phase 1 gate: verify log file exists, valid YAML, all fields present |
| M7 | QA health scoring untested against known defects | **Accept** | Calibration scenario with planted defects in Phase 3 gate |
| M8 | No MCP server process supervision | **Accept** | Systemd units + liveness checks for all droplet MCP servers |
| M9 | Cookie staging in /tmp/ is world-readable | **Accept** | Extract to chmod 600 in ~/.ai-cos/cookies/, never /tmp/ |
| M10 | ai-cos-mcp + browser ops = fault isolation failure | **Accept — DECIDED** | Separate web-tools MCP process on droplet. Chrome must not share process with ai-cos-mcp. This is now a resolved architecture decision, not an open question. |
| M11 | deploy.sh unspecified + secret rotation undocumented | **Accept both** | Specify deploy.sh fully + create secrets-manifest.md |

### MINOR (8/8 accepted)

| # | Finding | Decision | Notes |
|---|---|---|---|
| m1 | Auth registry staleness undetected | **Accept** | Skill checks Last Verified date, flags if stale (>30d cookies, >90d API keys) |
| m2 | Phase 5 CLAUDE.md merge timing unsafe | **Accept** | CLAUDE.md changes committed atomically between phases |
| m3 | Layer 1→2 transition gate missing | **Accept** | Add layer-1-toolset.md as Phase 0 output / decision record |
| m4 | Observability has no degradation mode | **Accept** | "Logging is best-effort. Never block primary task for observability." |
| m5 | Rollback procedure untested | **Accept** | Phase 1 rollback drill after first deployment |
| m6 | Stagehand caching criterion qualitative | **Accept** | "2nd+ run at least 30% faster, debug log confirms cached selector" |
| m7 | SQLite state excluded from DR plan | **Accept** | Document what's lost + DO snapshots or sqlite3 .dump backup |
| m8 | Unpinned MCP versions | **Accept** | Pin all versions in ~/.mcp.json, update intentionally |

---

## Key Escalations

1. **B3 upgraded:** User wants 5-6 failure scenarios per phase, not the proposed 1 per phase
2. **M2 cascading fix:** User flagged that Pass 2 fixed the architecture description but didn't propagate to the deliverables table — need to verify ALL downstream references are consistent
3. **M10 resolved:** Separate web-tools MCP is now a decided architecture choice, not an open question — remove from unknowns section

---

## Next Steps

1. Apply all 24 fixes to the design doc (new session — context-intensive)
2. Generate final design doc version
3. Push to remote
4. Transition to implementation planning (writing-plans skill)
