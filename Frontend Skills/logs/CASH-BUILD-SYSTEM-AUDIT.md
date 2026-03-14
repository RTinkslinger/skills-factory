# CASH Build System — Error & Failure Audit

**Session analyzed:** 2026-03-06, 12:06–12:47 UTC (41 minutes)
**Log source:** `logs/error-monitor.log` (3,628 lines) + raw session JSONL (913 entries)
**Config source:** `.claude/settings.local.json`, `CLAUDE.md`

---

## Methodology

The previous analysis (conducted in-session) made several claims without verifying them against the raw JSONL data. This corrected audit re-examined every claim, traced each logged event to its JSONL source, and classified true errors vs. false positives with evidence.

**Key corrections from re-analysis:**
- Previous analysis stated "340 TOOL errors" — actually **2 real errors, 336+ false positives**
- Previous analysis stated "all 11 NOTION entries are false positives" — correct conclusion, but the *mechanism* was misidentified
- Previous analysis missed the **biggest operational failure entirely**: the PreToolUse Edit|Write hook blocked 7 out of 26 file operations (27% failure rate)
- Previous claim of "destructive action without confirmation" was wrong — users approve bash commands in Claude Code

---

## Monitor Design Flaw (Root Issue)

**Before analyzing individual errors, the monitor itself must be understood, because it is the primary source of misleading data.**

The error monitor uses `grep -qiE` on raw JSONL lines:

```bash
# TOOL filter:
grep -qiE '(mcp__|ToolUse|tool_use)' && grep -qiE '(error|fail|exception|timeout)'

# NOTION filter:
grep -qiE '(notion|roadmap|data.source|create.page|query.database)' && grep -qiE '(error|fail|exception|denied)'
```

**The fatal flaw:** Every JSONL tool result line contains `"is_error":false` — the substring `error` inside the field name `is_error` matches the keyword filter even when the value is `false`. This means:

| Actual JSONL | Monitor matches on | Result |
|---|---|---|
| `"is_error":false` | `error` in `is_error` | FALSE POSITIVE |
| `"is_error":true` | `error` in `is_error` | True positive |
| Tool output containing "error" in docs text | `error` in content | FALSE POSITIVE |
| Stop hook prompt containing "failed" | `fail` in prompt text | FALSE POSITIVE |

**Verified impact on each category:**

| Category | Logged entries | True errors | False positive rate |
|---|---|---|---|
| `[TOOL]` | 338 | 2 | **99.4%** |
| `[NOTION]` | 9 | 0 | **100%** |
| `[HOOK]` | 7 | 5 | **29%** |
| `[SUBAGENT]` | 3 | 0 | **100%** |

**Evidence:**
- Raw JSONL contains 10 lines with `"is_error":true`. Of those, only 2 are actual tool execution failures (InputValidation + Permission denied). The other 8 are **PreToolUse hook denials** (a completely different error class the monitor doesn't distinguish).
- All 9 `[NOTION]` entries are either: (a) Stop hook prompt text containing "Roadmap" + "failed" matched by both HOOK and NOTION filters (8 entries), or (b) a bash command listing MCP servers whose output included "Notion" + `is_error:false` (1 entry).
- All 3 `[SUBAGENT]` entries are from the monitor's initial startup catching up on JSONL, matching on the word "Agent" in non-error contexts.

---

## True Errors Found

### Error 1: PreToolUse Edit|Write Hook — 27% Denial Rate (CRITICAL)

**This was completely missed by the original analysis and is the most impactful failure.**

The PreToolUse hook on `Edit|Write` fires a prompt asking Claude to check if the target file is in the "Known critical (Sequential) files" list in CLAUDE.md. When the prompt hook cannot verify this, it returns `"Prompt hook condition was not met"`, which Claude Code treats as `is_error: true` — **blocking the edit entirely**.

**7 denials out of 26 Edit/Write operations (27% blocked):**

| Time (UTC) | Tool | Target file | Denial reason |
|---|---|---|---|
| 12:09:01 | Edit | `~/.claude/projects/.../memory/MEMORY.md` | "memory/documentation file, not a code file" |
| 12:23:39 | Edit | `~/.mcp.json` (inferred) | "Unable to locate CLAUDE.md" |
| 12:25:14 | Edit | `~/.claude/CLAUDE.md` | "I need to read that file to check" (circular) |
| 12:27:14 | Write | skill file (inferred) | "Unable to locate CLAUDE.md" |
| 12:37:25 | Write | skill file (inferred) | "Unable to locate CLAUDE.md" |
| 12:40:19 | Edit | `TRACES.md` | "CLAUDE.md file not found" |
| 12:40:24 | Edit | `TRACES.md` | "Cannot verify...need to read CLAUDE.md first" |

**Failure modes:**

1. **Circular dependency (line 274):** The hook blocks editing `~/.claude/CLAUDE.md` because it needs to *read* CLAUDE.md to check the Sequential files list — but the hook runs *before* the edit tool, and the hook itself cannot read files. It's asking Claude to verify something the hook prompt cannot verify.

2. **CLAUDE.md not findable (lines 216, 317, 775, 852):** When editing files outside the project directory (global config files like `~/.mcp.json`, `~/.claude/skills/*`), the hook cannot find the project's CLAUDE.md to check the Sequential files list. The hook prompt assumes project-local context.

3. **Retry storm (lines 852-859):** Editing TRACES.md was denied twice in a row before succeeding on the 3rd attempt. The same hook that is supposed to *protect* TRACES.md (as a Sequential file) is instead *blocking* the TRACES.md update that the Stop hook is *requiring*. The two hooks work against each other.

4. **False blocking of non-code files (line 99):** MEMORY.md was blocked even though it's a documentation/memory file, not a code file in the project. The hook doesn't distinguish between code files and metadata files.

**Impact:** Every denial costs a full tool call round-trip. With 7 denials, that's 7 wasted API turns. The TRACES.md retry storm (2 denials before success) directly conflicts with the Stop hook's mandate to update TRACES.md.

### Error 2: Stop Hook Fires 8 Times Per Session

**8 distinct Stop hook invocations** were detected via the `hookErrors` field in the error monitor log:

| # | Time | Duration | hookErrors | Outcome |
|---|---|---|---|---|
| 1 | 17:43:29 | 11,494ms | `["JSON validation failed"]` | Prompt delivered (hasOutput:true) |
| 2 | 17:53:02 | 4,833ms | `[]` | Prompt delivered |
| 3 | 17:54:36 | 2,693ms | `[]` | Prompt delivered |
| 4 | 17:55:46 | 8,153ms | `["JSON validation failed"]` | Prompt delivered (hasOutput:true) |
| 5 | 17:57:49 | 2,725ms | `[]` | Prompt delivered |
| 6 | 18:03:37 | — | `["Prompt hook condition was not met: Session incomplete..."]` | Blocked |
| 7 | 18:08:59 | — | `["Prompt hook condition was not met: Stop hook detected..."]` | Blocked |
| 8 | 18:11:02 | 4,556ms | `["Error executing prompt hook: No assistant message found"]` | Failed |

**Sub-errors within Stop hook:**

- **"JSON validation failed" (2x):** The hook's prompt text is delivered to Claude (`hasOutput: true`, `preventedContinuation: false`), but the response structure fails JSON validation. The hook still functions — this is a platform-level issue where prompt hooks return text that doesn't match the expected JSON schema. Not actionable at the CLAUDE.md level.

- **"Prompt hook condition was not met" (2x):** Claude's response to the Stop hook check was itself treated as "not meeting the condition." In case #6, Claude was blocked by disk space and couldn't complete the TRACES/LEARNINGS/Roadmap checklist. In case #7, Claude acknowledged the hook but its response was rejected. This creates a feedback loop: the hook demands work → Claude can't do the work → the hook fires again.

- **"No assistant message found" (1x):** At 18:11:02, the Stop hook fired but there was no assistant message in the conversation to inject the prompt after. This is a timing edge case at actual session end.

**Overhead:** 6 measured durations total 34.5 seconds of hook processing (avg 5.7s per invocation). In a 41-minute session, this is ~1.4% of wall time — modest, but the context pollution (8x the same 120-word prompt injected) is the larger cost.

### Error 3: Tool InputValidation Error (1 occurrence)

At 12:15:12 UTC, an `AskUserQuestion` tool call failed:
```
InputValidationError: questions[0].options — Too small: expected array to have >=2 items
```

Claude provided a question with only 1 option. The API requires >=2. Claude recovered by not retrying the question.

**Not logged to LEARNINGS.md** — the protocol says to "immediately log the broken > working pair to LEARNINGS.md before continuing." This was not done.

### Error 4: ENOSPC Disk Space Failure (1 occurrence, cascading)

At ~12:31 UTC, `npm install` for a test project failed with `ENOSPC: no space left on device`. This cascaded:

1. npm install failed → test project incomplete
2. Claude attempted `rm -rf ~/.npm/_cacache` to free space → failed with `Permission denied` (files owned by root)
3. Stop hook fired (#6) but was blocked because Claude couldn't complete the session checklist
4. Phase 4 validation testing was abandoned

Claude DID log this to LEARNINGS.md eventually — but only after the Stop hook reminded it, not "immediately" as the protocol specifies.

**Previous analysis correction:** The `rm -rf` command was NOT executed without user confirmation. Claude Code requires user approval for bash commands. The user approved the cleanup attempt. The "destructive action without confirmation" claim in the original analysis was wrong.

---

## Protocol Compliance Assessment

### Branch Lifecycle: VIOLATED (but nuance required)

**Rule:** "Every code change follows: CREATE > WORK > REVIEW > SHIP"

**Fact:** No `git checkout -b` command was executed during the session. All work happened on `master`. The only git commands run were `git clone` (for test project), `git log`, and `git remote`.

**Nuance the original analysis missed:** The files edited were:
- `~/.claude/CLAUDE.md` (global config, outside any git repo)
- `~/.mcp.json` (global config)
- `~/.claude/skills/*/SKILL.md` (new files in global config)
- `CLAUDE.md`, `TRACES.md`, `LEARNINGS.md` (project infrastructure)
- `.claude/settings.local.json` (project config)
- `test-project/src/app/pricing/page.tsx` (throwaway validation page)

None of these are "project code" in the traditional sense. The deliverables of this project are config files installed into `~/.claude/`. The branch lifecycle rule is arguably not applicable to global config file creation. However, the CLAUDE.md protocol doesn't carve out this exception — it says "every code change."

**Verdict:** Technically violated. Practically, the rule needs a scope clarification for projects whose deliverables are config files outside the repo.

### Roadmap Timing: PARTIALLY COMPLIANT

**Rule:** "Every code change must have a Roadmap item. If none exists, create one before starting."

**Timeline:**
- 12:07:16 — First Write (CLAUDE.md infrastructure setup)
- 12:08:50 — settings.local.json created (hooks configured)
- 12:10:06 — Notion `create-pages` called (Roadmap item created)
- 12:23:38 — First implementation edit (.mcp.json)

The Roadmap item was created ~3 minutes after infrastructure setup started, but ~13 minutes before implementation edits. Infrastructure setup (creating TRACES.md, LEARNINGS.md, hooks config) is arguably "setting up the build system" rather than "code changes" — but the rule doesn't distinguish.

**Verdict:** Partially compliant. Roadmap item existed before implementation work, but not before infrastructure setup.

### TRACES.md Granularity: VIOLATED

**Rule:** Iterations should be ~15 lines, representing focused work.

**Actual:** Iteration 1 covers all four project phases in a single entry. It lists 6 file changes and 4 decisions — reasonable in volume, but the scope (entire project from start to finish) violates the "one coding session's focused work" intent.

### LEARNINGS.md Immediacy: VIOLATED

**Rule:** "Immediately log the broken > working pair to LEARNINGS.md before continuing."

**Actual:** The InputValidation error (12:15:12) was never logged. The ENOSPC error (12:31) was logged only after the Stop hook reminder (~12:33), not immediately.

---

## Hook Interaction Conflicts

The most significant systemic issue is that the three hook types **work against each other:**

```
Stop Hook says: "Update TRACES.md before ending!"
    ↓
Claude attempts: Edit TRACES.md
    ↓
PreToolUse Hook says: "Can't verify if TRACES.md is Sequential — BLOCKED"
    ↓
Claude retries Edit → BLOCKED again
    ↓
Claude retries Edit → finally succeeds (3rd attempt)
    ↓
Stop Hook fires AGAIN (because Claude produced another response)
```

This creates a **hook conflict loop** where:
1. Stop hook demands file edits
2. PreToolUse hook blocks those same edits
3. Recovery from the block triggers the Stop hook again
4. Context fills with duplicate prompts and retry attempts

---

## Recommendations

### Priority 1: Fix PreToolUse Edit|Write Hook (Critical)

The hook blocks 27% of file operations. Root causes and fixes:

1. **Can't find CLAUDE.md for global files:** The hook should default to PASS (not DENY) when it cannot locate the CLAUDE.md reference file. Currently it denies-by-default.

2. **Circular dependency on CLAUDE.md edits:** Editing CLAUDE.md itself should be exempt, or the hook should have the Sequential files list hardcoded rather than requiring a file read.

3. **Non-code files should be exempt:** Memory files, documentation files, and config files outside the project should not trigger the Sequential file check.

### Priority 2: Reduce Stop Hook Frequency

Either:
- Add state tracking so the hook only fires once per session (e.g., check for a sentinel file)
- Shorten the prompt to 1–2 lines instead of 120 words
- Change from `prompt` type to `command` type that checks a condition before injecting

### Priority 3: Rewrite Error Monitor

The grep-based approach produces 99%+ false positive rates. Replace with:
- JSON-aware parsing (use `jq` or `python3 -c` to check `is_error` field values, not field names)
- Negative match on the Stop hook prompt text to prevent cross-contamination between categories
- Separate "hook denial" from "tool execution error" as distinct categories

### Priority 4: Resolve Hook Conflicts

- Exempt TRACES.md and LEARNINGS.md from the PreToolUse Sequential check (these files are always edited by the Stop hook flow — blocking them creates a deadlock)
- Or: have the Stop hook check if the PreToolUse hook will block before demanding the edit

### Priority 5: Clarify Protocol Scope

- Define whether the branch lifecycle applies to config-file-only projects
- Define whether infrastructure setup (creating TRACES.md, LEARNINGS.md, hooks) counts as "code changes" requiring a Roadmap item first

---

## Raw Data Summary

| Metric | Value |
|---|---|
| Session duration | 41 minutes |
| Total JSONL entries | 913 |
| Edit/Write operations attempted | 26 |
| Edit/Write operations denied by PreToolUse hook | 7 (27%) |
| Stop hook invocations | 8 |
| Stop hook errors | 5 of 8 |
| Stop hook overhead | 34.5 seconds |
| Actual tool execution errors | 2 (InputValidation + Permission denied) |
| Notion API calls made | 8 (1 create, 7 updates) |
| Error monitor false positive rate | 97% overall |
| LEARNINGS entries created | 1 (ENOSPC pattern) |
| Git branches created | 0 |
