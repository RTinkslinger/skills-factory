# CBS Roadmap Enforcement Gaps

**Date:** 2026-03-14
**Source:** Audit during QMD project CBS setup
**Status:** Open — needs design decision

---

## Problem Statement

The CASH Build System enforces TRACES.md updates via `stop-check.sh` (exit 2 blocks session end), but ROADMAP.md and Notion updates have no independent enforcement. This creates a reliability gap where Claude can update TRACES.md and stop without updating the Roadmap — either locally or in Notion.

## Findings

### 1. ROADMAP.md Has No Independent Enforcement

**Current behavior:** `stop-check.sh` lines 86-92 check ROADMAP.md staleness (>1 hour), but this check only appends to the reminder string — it rides on the TRACES.md exit 2 trigger.

**Gap:** If TRACES.md IS updated but ROADMAP.md isn't, stop-check.sh exits 0 at line 73. The ROADMAP.md reminder never fires.

**Impact:** ROADMAP.md drifts from actual work state. Between sessions, Notion is supposed to be source of truth, but if neither ROADMAP.md nor Notion was updated, the next session starts with stale data.

### 2. Notion Updates Are Architecturally Unenforceable by Hooks

**Constraint:** CC hooks cannot call MCP tools.
- Command hooks: shell scripts with no MCP access
- Prompt hooks: run on Haiku (separate model, no file access, no MCP tools)

**Current mitigation:** CLAUDE.md protocol instructions ("Real-time updates, not batch-at-end"). The main Claude model sees these and is supposed to follow them.

**Gap:** Instructions are advisory. Claude can skip them, especially under time pressure or when context is compacted. There's no validation gate.

### 3. SessionStart Notion Rebuild Has No Validation

**Current behavior:** SessionStart hook echoes "REQUIRED before responding: rebuild ROADMAP.md from Notion if connected."

**Gap:** Nothing prevents Claude from responding without doing the rebuild. The "REQUIRED" directive is just stdout text injected into context — no hook validates that ROADMAP.md was actually rebuilt.

### 4. LEARNINGS.md Enforcement Is Weak

**Current behavior:** Piggybacks on TRACES.md reminder + PostToolUseFailure prompt nudge.

**Gap:** PostToolUseFailure runs on Haiku without session context, so it can't distinguish "learnable failure" from "expected miss." No independent check that LEARNINGS.md was updated.

## Summary Table

| Target | Enforcement Level | Mechanism | Gap? |
|--------|------------------|-----------|------|
| TRACES.md | **Hard** (exit 2 blocks stop) | stop-check.sh mod-time comparison | No |
| ROADMAP.md | **Soft** (piggybacks on TRACES) | Appended to TRACES reminder | Yes — no independent trigger |
| Notion sync | **None** (instructions only) | CLAUDE.md protocol | Yes — architectural |
| LEARNINGS.md | **Soft** (piggybacks + nudge) | Appended + PostToolUseFailure | Moderate |
| SessionStart sync | **Instructed** | Echo "REQUIRED" in stdout | Yes — no validation |

## Possible Solutions (To Evaluate)

### For ROADMAP.md independent enforcement
- **Option A:** Add a separate mod-time check for ROADMAP.md in stop-check.sh that independently triggers exit 2 (not just when TRACES is also stale)
- **Option B:** Check if any Roadmap items are "In Progress" (read ROADMAP.md, grep for current branch) and warn if status wasn't updated
- **Tradeoff:** More exit 2 triggers = more friction. Need to balance enforcement vs. annoyance.

### For Notion sync
- **Option A (accept limitation):** Keep as CLAUDE.md instructions. Accept that Notion sync is best-effort.
- **Option B (indirect enforcement):** stop-check.sh could check if ROADMAP.md contains `<!-- sync pending -->` markers and remind Claude to sync when Notion is available.
- **Option C (SessionStart validation):** Add a command hook that checks ROADMAP.md "Last synced" timestamp. If stale >24hr and Notion tools are available, inject a stronger directive.

### For SessionStart validation
- **Option A:** Add a PreToolUse prompt hook that checks if ROADMAP.md was read/written before allowing code edits. (Heavy — fires on every edit.)
- **Option B:** Accept that SessionStart is advisory. The real enforcement is at Stop time.

## Recommendation

Focus on **ROADMAP.md independent enforcement** (Option A — straightforward stop-check.sh change). Accept Notion as best-effort with indirect enforcement (sync pending markers). SessionStart validation is probably not worth the overhead.

---

*This document should be reviewed as part of CBS v1.3 planning.*
