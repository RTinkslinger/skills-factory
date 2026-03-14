# CASH Build System — Version History

## Versioning Scheme

`MAJOR.MINOR-STAGE` where:
- **MAJOR** — Breaking changes to file formats, hook contracts, or setup flow
- **MINOR** — New features, non-breaking improvements
- **STAGE** — `alpha` (first working draft) → `beta` (validated against real API) → `rc` (production-tested) → `stable`

---

## 1.2 (2026-03-13)

**Hook architecture fix: eliminated prompt-type Stop hooks.** Prompt hooks run on Haiku (separate model, no file access) — they are evaluation gates (`{"ok": true/false}`), not action executors. Using them to instruct Claude to edit files caused "JSON validation failed" errors on every session close across all synced projects.

### Breaking Changes

| Change | Was | Now | Why |
|--------|-----|-----|-----|
| Cross-Sync Stop hook removed | Prompt-type Stop hook instructing Claude to edit state.json | No Stop hook — sync instructions in CLAUDE.md | Prompt hooks run on Haiku (no file access). Haiku can't edit files, responds with natural language, CC fails to parse as JSON |
| Hook count with sync | 9 (6 CBS + 3 sync) | 8 (6 CBS + 2 sync) | Removed 1 prompt hook |
| Prompt hook count with sync | 3 | 2 | Only PreToolUse (Agent) and PostToolUseFailure remain as prompt hooks — both are correct evaluation gates |

### New Features

| Feature | Description |
|---------|-------------|
| Cross-Sync Session Protocol in CLAUDE.md | When sync enabled, Step 6 appends sync instructions to CLAUDE.md. Main Claude sees these directly (not via Haiku) |
| pending_inbox pattern | Claude adds items to `state.pending_inbox[]` via Edit. sync-push.sh drains them into full inbox messages via jq. Eliminates Claude constructing JSON in Bash |
| sync-push.sh pending_inbox drain | New logic reads pending items, generates full inbox messages with id/timestamp/source/priority via jq, appends to inbox.jsonl, clears array |
| sync-pull.sh/push.sh --ff-only | Changed from --rebase (fails on dirty trees) to --ff-only (degrades gracefully) |
| Hooks Mastery skill | Deep research + actionable skill for all CC hook types, events, patterns. Deployed as global `/hooks-reference` command |
| **Broadened TRACES enforcement** | stop-check.sh no longer blanket-exempts `.md`, `.txt`, `CLAUDE.md`, `.claude/`. Now only exempts TRACES/LEARNINGS/ROADMAP (enforced targets), `.claude/sync/` (auto-modified), and entries in `.claude/traces-exempt.txt` |
| `.claude/traces-exempt.txt` | New configurable exempt list. Default: TRACES.md, LEARNINGS.md, ROADMAP.md. Projects can add per-project exemptions (e.g., README.md) without editing stop-check.sh |
| `<!-- end-header -->` sentinel | TRACES.md template uses `<!-- end-header -->` sentinel instead of `---` for compact hook. Immune to user-added `---` separators |

### Behavioral Changes

| Change | Was | Now | Why |
|--------|-----|-----|-----|
| CLAUDE.md edits tracked | Exempt (blanket `.md` + explicit `CLAUDE\.md` filter) | **Tracked** — triggers TRACES requirement | CLAUDE.md edits often contain architectural decisions (adding protocols, system config). This session itself proved it. |
| .claude/hooks/ edits tracked | Exempt (blanket `.claude/` filter) | **Tracked** — triggers TRACES requirement | Hook scripts are implementation code. Rewriting stop-check.sh is work worth tracking. |
| .md skill files tracked | Exempt (blanket `.md` filter) | **Tracked** — triggers TRACES requirement | In Skills Factory, .md skill files ARE the product. 13 commits with 0 TRACES entries was the gap. |
| SessionStart type enforcement | ai-cos-cc-adk used prompt-type (invalid) | All projects use command-type | SessionStart only supports `type: "command"` hooks per CC docs. Prompt type sent to Haiku which can't read files. |

### Deployments

- CBS v1.2 skill deployed globally (`~/.claude/commands/setup-cash-build-system.md`)
- sync-init command updated (removed prompt hook, --ff-only, pending_inbox reference)
- stop-check.sh deployed to all 4 projects (broadened enforcement + configurable exemptions)
- sync-push.sh with pending_inbox drain deployed to all 4 projects
- All prompt-type Stop hooks removed from all 4 project settings
- `<!-- end-header -->` sentinel added to all 4 TRACES.md files
- Compact hooks updated to use sentinel in all 4 projects
- `.claude/traces-exempt.txt` created in all 4 projects
- ai-cos-cc-adk: SessionStart fixed, ROADMAP.md + sequential-files.txt + check-sequential-files.sh + PostToolUseFailure hook deployed
- Cross-Sync Session Protocol added to 3 projects' CLAUDE.md (was only in cc-cai-sync)

### Key Learning

**Prompt hooks are evaluation gates, not action executors.** From official CC docs: "Prompt-based hooks send the hook input and your prompt to a Claude model (Haiku by default). The LLM responds with structured JSON containing a decision." Haiku has no file access, no Edit tool, no Bash. For injecting instructions to main Claude, use CLAUDE.md (always loaded) or command hooks with exit 2 (stderr fed to Claude as feedback).

---

## 1.2-beta (2026-03-12)

**4 bug fixes + cross-sync alignment** from deferred v1.2 iteration plan items and cross-sync v0.2 audit integration.

### Bug Fixes

| Fix | Was | Now | Why |
|-----|-----|-----|-----|
| Stop hook 1-hour blind spot | `$NOW - TRACES_MOD < 3600` (fixed window) | Compare TRACES.md mtime vs newest code file mtime | Code modified 30min after TRACES.md update was missed — the 1-hour window said "recently updated" even though new code changes weren't covered |
| Compact hook `sed` fragility | `sed '/^---$/q'` (matches any `---`) | `sed '/<!-- end-header -->/q'` with sentinel comment in TRACES.md template | A user-added `---` inside Project Summary would truncate the compact hook output, losing the Milestone Index |
| PostToolUseFailure prompt timing | Past tense: "If you tried...and then succeeded" | Future tense: "When you find a working approach after this failure" | Hook fires at moment of failure, not after success — past tense was nonsensical at the point of evaluation |
| `| head -1` in stop-check.sh | `CODE_CHANGES` truncated to 1 line | Full list preserved for mtime iteration | The mtime comparison needs to stat multiple files; `head -1` prevented this |

### Cross-Sync Integration Alignment

Aligned the CBS skill with cross-sync v0.2 audit fixes (deployed to all 4 projects in a prior session):

- **Step 7e:** Added `sync-write.sh` creation (references `/sync-init` Step 4d alongside existing 4b/4c)
- **Step 9:** Added `sync-write.sh` executable check to validation block
- **Step 13:** Added `sync-write.sh` to completion report and hook scripts summary
- **Source/deployed convergence:** Source file in Cash Build System repo now matches deployed `~/.claude/commands/setup-cash-build-system.md` (previously diverged — deployed had sync integration, source didn't)

### Other Changes

- **Prerequisites section** added before Step 1: documents git+remote and jq as requirements
- **TRACES.md template:** `---` separator replaced with `<!-- end-header -->` sentinel comment
- **Stop hook Why section:** Documents the mtime comparison approach

### Accuracy Note

v1.1 plan incorrectly stated `agent_type` doesn't exist in hook input — it does per official docs. `agent_id` was chosen as the more reliable subagent indicator because it's only present inside subagents, whereas `agent_type` requires the `--agent` flag or subagent context.

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
