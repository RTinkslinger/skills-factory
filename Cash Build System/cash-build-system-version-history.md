# CASH Build System — Version History

## Versioning Scheme

`MAJOR.MINOR-STAGE` where:
- **MAJOR** — Breaking changes to file formats, hook contracts, or setup flow
- **MINOR** — New features, non-breaking improvements
- **STAGE** — `alpha` (first working draft) → `beta` (validated against real API) → `rc` (production-tested) → `stable`

---

## 1.1-beta (2026-03-10)

**7 fixes + 1 new feature** addressing all issues found in the 41-minute production audit and recovered session analysis.

### New Feature: ROADMAP.md Checkout/Commit Model

Local `ROADMAP.md` mirrors the Notion Build Roadmap using a checkout/commit pattern:
- Session start → sync down from Notion (overwrite local)
- During session → work from local file
- State transitions → update local + Notion simultaneously
- Notion offline → local file works, marks "sync pending"

New setup step (5b) creates the file and adds it to `.gitignore`. Stop hook now checks `ROADMAP.md` modification time alongside TRACES.md. SessionStart directive includes ROADMAP.md rebuild.

**Why:** TRACES.md works because it's local (visible, enforceable). Build Roadmap failed because it was Notion-only (behind MCP, invisible to hooks, easily forgotten).

### Bug Fixes

| Fix | Was | Now | Why |
|-----|-----|-----|-----|
| `stop-check.sh` file exclusion | `\.md ` / `\.txt ` (trailing space) | `\.(md\|txt)$` (end-of-line anchor) | `git status --porcelain` puts filenames at end of line — trailing space never matched, so .md files falsely counted as "code changes" |
| `check-sequential-files.sh` subagent detection | `agent_type` (unreliable) | `agent_id` (only present inside subagents) | `agent_type` is only present with `--agent` flag or inside subagents; `agent_id` is the reliable indicator |
| Build system file exemptions | None | TRACES.md, LEARNINGS.md, ROADMAP.md exempt from sequential check | Prevented hook conflict loop: Stop hook demands TRACES.md update → PreToolUse blocks it → retry triggers Stop again |
| `stop-check.sh` ROADMAP.md awareness | Only checks TRACES.md | Checks both TRACES.md and ROADMAP.md | Reminder now includes ROADMAP.md status if it hasn't been updated |
| Protocol scope clarification | "Build system setup" in scope exemption | Explicit: "exempt from both branch lifecycle AND Roadmap item requirements" | Audit showed ambiguity about whether infrastructure setup needs a Roadmap item first |
| SessionStart directive | No mention of ROADMAP.md | Includes "Rebuild ROADMAP.md from Notion if connected" | Ensures ROADMAP.md is synced at session start |

### Sources
- Production audit: `Frontend Skills & MCPs/logs/CASH-BUILD-SYSTEM-AUDIT.md` (41-minute session, 27% edit denial rate)
- Recovered analysis: `Documents/recovered-session-artifacts/cash-build-system-notion-roadmap-fix-plan.md`
- Recovered notes: `Documents/recovered-session-artifacts/skills-factory-publish-setup.md`
- Hook input schema: verified against official Claude Code hooks documentation

---

## 1.0-beta (2025-03-06)

**14 targeted fixes** after deep research validated v2-alpha against official Claude Code Hooks API docs, GitHub issues, and community reports.

### Critical Fixes (would have caused silent failures)

| Fix | Was | Now | Why |
|-----|-----|-----|-----|
| Stop hook exit code | exit 0 + stdout | exit 2 + stderr | Exit 0 stdout is invisible to Claude on Stop hooks (only SessionStart/UserPromptSubmit add stdout to context) |
| Sequential file field | `agent_name` | `agent_type` | `agent_name` doesn't exist in the API — made the entire check a no-op |
| Git status command | `git diff --name-only HEAD` | `git status --porcelain` | `git diff HEAD` fails with "fatal: ambiguous argument 'HEAD'" on repos with no commits |

### Behavioral Fixes (noise, drift, edge cases)

| Fix | Was | Now | Why |
|-----|-----|-----|-----|
| PostToolUseFailure matcher | empty (all tools) | `Bash\|Edit\|Write` | Empty matcher fired on every Glob/Grep/Read miss — 20-50 false triggers per session |
| Compact hook | `head -20` | `sed '/^---$/q'` | Milestone Index grows; `head -20` truncates after ~15 iterations |
| PreToolUse context injection | stderr | JSON `additionalContext` | Plain stderr from PreToolUse is verbose-mode only; JSON is the only way to inject visible context |
| SessionStart language | "Read TRACES.md..." (suggestion) | "REQUIRED before responding..." (directive) | Passive text gets deprioritized when user's message is urgent |
| `stat` arithmetic | raw `stat -f %m` | `stat -f %m ... \|\| echo 0` + `${TRACES_MOD:-0}` | Empty stat output breaks bash arithmetic |
| File matching | `grep -qF` | `grep -qxF` | Substring match: `CLAUDE.md` would false-positive on `MY_CLAUDE.md` |

### Structural Changes
- Removed inline v2 changes block from skill header (was getting long; this document replaces it)
- Hook scripts moved to `.claude/hooks/` with documented contracts
- Sequential files list moved to `.claude/sequential-files.txt`

### Validation Sources
- Official docs: `code.claude.com/docs/en/hooks`, `code.claude.com/docs/en/hooks-guide`
- GitHub issue #18215 (stdout visibility contradictions in docs)
- GitHub issue #30825 (SessionStart fires twice on `/resume`)
- Community reports on Stop hook exit code semantics

---

## 0.9-alpha (2025-03-06)

**First major rewrite** incorporating 5 systemic fixes from a 41-minute production audit. Expanded from 11 to 13 steps.

### New Capabilities
- **Hook scripts** (Steps 7a, 7b) — `stop-check.sh` and `check-sequential-files.sh` as external scripts instead of inline commands
- **Validation step** (Step 9) — Verify hooks, file structure, and CLAUDE.md after setup
- **SessionStart hooks** — Startup matcher (context loading directive) and compact matcher (TRACES.md header injection)
- **PreToolUse hook** — Sequential file detection for subagents editing shared files
- **PostToolUseFailure hook** — Prompt-type hook to capture trial-and-error patterns
- **Stop hook** — Conditional reminder when code files modified but TRACES.md not updated
- **`stop_hook_active` guard** — Prevents infinite Stop hook loops (official pattern from docs)

### Fixes from Production Audit
1. **Stop hook was silent** — Claude finished sessions without updating TRACES.md because no enforcement mechanism existed
2. **Sequential file conflicts** — Parallel subagents edited the same files causing merge conflicts; no detection mechanism
3. **Context loss on compaction** — After `/compact`, Claude lost awareness of current sprint/iteration state
4. **Learning capture was optional** — Trial-and-error patterns were lost because nothing prompted their capture
5. **CLAUDE.md circular dependency** — Sequential file list was in CLAUDE.md, which was itself a sequential file

### Source
- Production audit document: `cash-build-system-v2-improvement-plan.md`
- 41-minute audit across multiple real coding sessions

---

## 0.1-alpha (2025-02 era)

**Original skill.** Basic setup of TRACES.md, LEARNINGS.md, Build Roadmap, and CLAUDE.md configuration.

### Capabilities
- TRACES.md with iteration tracking, milestone index, sprint headers
- LEARNINGS.md with trial-and-error pattern capture and graduation protocol
- Notion Build Roadmap integration
- File classification (Parallel vs Sequential)
- Subagent delegation protocol
- Archive system for completed sprints
- 11-step setup procedure

### Known Issues (discovered in production)
- No enforcement hooks — all compliance was honor-system
- No context recovery after compaction
- Sequential file list stored in CLAUDE.md (circular dependency)
- No validation step to verify setup correctness
