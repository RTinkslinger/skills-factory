# Design Review Pass 2 — Systems Architect

**Date:** 2026-03-14
**Reviewer:** Claude Opus 4.6 (Systems Architect lens)
**Document:** `docs/superpowers/specs/2026-03-14-web-frontend-skills-portfolio-design.md`
**Verdict:** APPROVED with 10 findings requiring fixes before build starts

---

## Findings

### FINDING 1 — BLOCKING: Activation model is architecturally unimplementable

**Section:** 5.1 (web-router activation model)
**Issue:** Doc says web-router is "sole entry point" that "shadows specialist triggers." CC's skill system has NO mechanism for trigger shadowing or skill-invokes-skill patterns. All skills with matching triggers will activate independently.
**Fix:** Specialists must NOT be registered as skills. They are reference docs inside `~/.claude/skills/web-router/references/`. Router is the only SKILL.md with web triggers. Matches existing search-router pattern.
**Status:** MUST FIX

### FINDING 2 — MAJOR: Observability logging has no persistent storage

**Section:** 4 (Observability) + 11 (Learning Loop)
**Issue:** YAML log format defined but no storage mechanism. CC sessions are ephemeral — logs vanish. Learning loop requires cross-session log accumulation that doesn't exist.
**Fix:** Define storage: append-only log files at `~/.claude/web-logs/` (CC), SQLite on droplet (Agent SDK). Logs written after each web operation. LEARNINGS.md captures patterns; logs provide the raw data.
**Status:** MUST FIX

### FINDING 3 — MAJOR: Phase 1 internal build order is wrong

**Section:** 9 (Build Order)
**Issue:** Order is browse → auth → web-router. Browse needs auth for authenticated tasks. Auth should be built first.
**Fix:** Reorder: 1.2 auth → 1.3 browse → 1.4 web-router.
**Status:** MUST FIX

### FINDING 4 — MAJOR: Missing Phase 0 (tool evaluation)

**Section:** 9 (Build Order, Step 1.1)
**Issue:** Tool evaluation lumped with installation. If Browserbase is too expensive or browser-use MCP is unreliable, the 5-dimension framework needs adjustment. Evaluation is blocking.
**Fix:** Add Phase 0: hands-on evaluation of Chrome DevTools MCP, Firecrawl MCP, browser-use MCP, Browserbase, Stagehand, cookie extraction tools. Produce evaluation report.
**Status:** MUST FIX

### FINDING 5 — MAJOR: CAI integration assumes non-existent hosted MCP

**Section:** 8 (CAI Integration)
**Issue:** Recommends "Option C: Firecrawl's hosted MCP" — but Firecrawl MCP runs locally via npx. No hosted endpoint exists. CAI scraping requires running Firecrawl MCP on the droplet + Cloudflare Tunnel exposure (Option B pattern).
**Fix:** Correct the recommendation. CAI scraping = Firecrawl MCP on droplet exposed via Tunnel. Evaluate whether ai-cos-mcp extension (Option A) or separate web-tools MCP (Option B) is better.
**Status:** MUST FIX

### FINDING 6 — MAJOR: No versioning or rollback for skills

**Section:** Missing (no section)
**Issue:** 21 deliverables with no version pinning, A/B testing, or rollback plan. If updated design-system-enforcer generates worse CSS, only manual revert from git.
**Fix:** Add section: Versioning & Rollback. Git-tracked source in Skills Factory = version history. Every skill update runs regression test (same test scenarios from testing gates). Regression = revert. Tag releases in git.
**Status:** MUST FIX

### FINDING 7 — MAJOR: Agent SDK skill delivery is undefined

**Section:** 2 (Architecture, Environment Detection)
**Issue:** "Skill logic embedded in agent code or loaded as prompt context" — hand-waved. Builders don't know how to give an Agent SDK runner browse expertise.
**Fix:** Define: runners read skill reference docs from a defined path at startup, include as system prompt context. Same reference docs used by web-router in CC. Single source of truth.
**Status:** MUST FIX

### FINDING 8 — MAJOR: Cookie extraction needs production-grade tooling

**Section:** 5.6 (auth, cookie sync)
**Issue:** yt-dlp cookie extraction is a YouTube downloader side-feature, not production cookie tooling. Browser cookie databases (SQLite for Chrome/Arc/Brave, keychain for Safari) need dedicated extraction. Full system for cookie handling is imperative.
**Fix:** Cookie extraction tool selection elevated to Phase 0 evaluation. Evaluate: gstack's compiled binary approach, direct SQLite reading, dedicated cookie extraction libraries, browser extension approach (Ghost Agent pattern). Production system = compiled binary or robust script, not yt-dlp hack.
**Status:** MUST FIX

### FINDING 9 — MAJOR: Cross-sync is unidirectional in detail

**Section:** 10 (Cross-Project Workflow)
**Issue:** Detailed message formats from Skills Factory → AI CoS. Reverse direction is vaguely described. Both directions need same specificity for non-linear development to work.
**Fix:** Add reverse message format with same structure. Define trigger scenarios for AI CoS → Skills Factory messages.
**Status:** MUST FIX

### FINDING 10 — MAJOR: Scrape + browse boundary is fuzzy

**Section:** 5.3 (scrape)
**Issue:** When scraping needs navigation (pagination, form filling, scrolling), does scrape invoke browse or handle navigation itself? Doc says "browse skill for authenticated extraction" but unclear for general case.
**Fix:** Clarify: scrape skill ALWAYS delegates navigation to browse. Scrape only handles extraction logic. Clean separation: browse = interaction, scrape = data extraction.
**Status:** MUST FIX

---

## Strengths

1. 5-dimension tool selection framework — durable, evolvable, tool-agnostic
2. "Protect My Account" as non-negotiable named principle
3. Pre-written cross-sync messages at phase boundaries
4. Open questions cleanly categorized (technical, architecture, process)
5. Auth as layered system (6 layers with clear escalation)
6. Phase 5 independence enabling parallel development
