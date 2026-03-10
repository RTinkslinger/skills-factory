---
description: Set up the CASH Build System (Context-Aware Session Handling) — branch lifecycle, Notion Build Roadmap, learning loop, subagent protocol, and enforcement hooks. Evolves from setup-traces. One command installs everything.
---

# Setup CASH Build System

**Version: 1.1-beta** | [Version History](../documents/cash-build-system-version-history.md)

Set up the CASH Build System for this project. This is a project-agnostic build system that provides: a branch lifecycle protocol, a Notion Build Roadmap for PDLC tracking, a learning loop that captures and graduates error patterns, a subagent delegation protocol, and enforcement hooks.

**This skill is a superset of setup-traces.** It absorbs all existing TRACES.md functionality and extends it with LEARNINGS.md, Build Roadmap, subagent protocol, file classification, and additional hooks.

## Steps to Execute

### Step 1: Check for existing files

Check if these files already exist in the project root:
- `TRACES.md` — if exists, preserve it (likely from a previous setup-traces run)
- `LEARNINGS.md` — if exists, preserve it
- `traces/archive/` — if exists, preserve it
- `.claude/hooks/` — if exists, check for v1 scripts that need replacing

Warn the user about any existing files and ask if they want to overwrite.

### Step 2: Create TRACES.md (if missing)

Create `TRACES.md` in the project root with this content:

```markdown
# Build Traces

## Project Summary

*No iterations yet. This summary will be updated after each milestone to capture cumulative progress, key architectural decisions, and current project state.*

## Milestone Index

| # | Iterations | Focus | Key Decisions |
|---|------------|-------|---------------|
| - | - | - | *No milestones yet* |

*Full details: `traces/archive/milestone-N.md`*

---

## Current Work (Milestone 1 in progress)

*Iteration entries appear here. After iteration 3, these will be archived to `traces/archive/milestone-1.md`.*

---
```

### Step 3: Create traces/archive/ directory (if missing)

Create `traces/archive/.gitkeep`:

```
# This file ensures the archive directory is tracked by git
```

### Step 4: Create LEARNINGS.md (if missing)

Create `LEARNINGS.md` in the project root with this content:

```markdown
# LEARNINGS.md

Trial-and-error patterns discovered during Claude Code sessions.
Patterns confirmed 2+ times graduate to CLAUDE.md during milestone compaction.

## Active Patterns

<!--
Entry format:

### YYYY-MM-DD - Sprint N
- Tried: [what failed and why]
  Works: [what succeeded]
  Context: [brief context about when this applies]
  Confirmed: Nx
-->
```

### Step 5: Connect Notion Build Roadmap

This step is interactive. Use `AskUserQuestion` for the Notion DB connection.

**First, check if CLAUDE.md already contains a Notion Build Roadmap DB ID** (look for "Notion DB Data Source ID" or similar in a Build System Protocol section).

**If an ID is found:**
- Show the found ID and ask: "Found Build Roadmap ID: [ID]. Use this? Or provide a different Notion database ID?"

**If no ID is found:**
- Present the user with options:
  ```
  No Build Roadmap database connected.

  Option A: Connect existing database
    1. Open your Build Roadmap database in Notion
    2. Click the "..." menu at top-right
    3. Click "Copy link"
    4. Paste the link here — I'll extract the Data Source ID

  Option B: I'll guide you through creating one
    I'll create a new Notion database with the Build Roadmap schema.

  Which option? (A/B/skip)
  ```

**If Option A:** Extract the Data Source ID from the pasted link, verify connection by querying the DB, store the ID and view URL.

**If Option B:** Create a new Notion database with this schema:

| Property | Type | Options / Notes |
|----------|------|-----------------|
| Item | Title | Main description of the build item |
| Status | Select | Insight, Backlog, Planned, In Progress, Verifying, Shipped, Won't Do |
| Priority | Select | P0 - Now, P1 - Next, P2 - Later, P3 - Someday |
| Epic | Select | Core Product, Data & Schema, Frontend/UX, API/Integration, Infrastructure, Developer Tooling, Research/Spike |
| T-Shirt Size | Select | XS (<1hr), S (1-3hr), M (3-8hr), L (1-2 days), XL (3+ days) |
| Parallel Safety | Select | Safe, Coordinate, Sequential |
| Source | Select | Builder Request, Build Insight, Bug/Regression, Verification Failure, Dependency, Refactor, Architecture Decision, External Inspiration, User Feedback |
| Sprint# | Number | Integer, no decimal |
| Branch | Text | Git branch name when in progress, cleared on merge |
| Technical Notes | Rich Text | Implementation context, dependencies, rationale |
| Task Breakdown | Rich Text | Implementation steps, auto-populated when item moves to In Progress |

Create a Board view grouped by Status. Save the view URL for CLAUDE.md configuration.

**If "skip":** Skip Roadmap connection gracefully. Inform the user that the Build Roadmap can be connected later by re-running the skill.

**Handle the case where Notion MCP isn't connected:** If Notion tools are unavailable, skip Roadmap gracefully and inform the user.

### Step 5b: Create ROADMAP.md

Create `ROADMAP.md` in the project root. This is the local working copy of the Build Roadmap — it stays in sync with Notion via a checkout/commit model.

**If Notion was connected in Step 5:** Query the database and populate `ROADMAP.md` with current items:

```markdown
# Build Roadmap

Last synced: [ISO timestamp] | Sprint: [N]

## In Progress
- [Item description] [Priority, Branch] <!-- notion:page-id -->

## Up Next
- [Item description] [Priority] <!-- notion:page-id -->

## Verifying
- [Item description] [Sprint N] <!-- notion:page-id -->

## Insights
- [Item description] <!-- notion:page-id -->
```

**If Notion was skipped:** Create an empty template:

```markdown
# Build Roadmap

Last synced: never (Notion not connected) | Sprint: 1

## In Progress

## Up Next

## Verifying

## Insights
```

**Add `ROADMAP.md` to `.gitignore`** — it's ephemeral working state with Notion page IDs. If `.gitignore` doesn't exist, create it. If it exists, append `ROADMAP.md` if not already present.

### Step 6: Append Build System Protocol to CLAUDE.md

Read the existing `CLAUDE.md` file. If a `## Build System Protocol` section already exists, replace it. If a `## Build Traces Protocol (MANDATORY)` section exists (from old setup-traces), replace it with the new section. Otherwise, append this section at the end:

```markdown

---

## Build System Protocol

### Build Traces (MANDATORY)

Track implementation decisions with minimal context overhead using a rolling window + compaction pattern.

**IMPORTANT:** Enforced by a Stop hook — if you modify code files but don't update TRACES.md, the hook will prevent you from stopping and require you to update TRACES.md first.

#### Quick Reference

| File | Purpose | When to Read |
|------|---------|--------------|
| `TRACES.md` | Rolling window (~80 lines) | Start of every coding session + before closing |
| `traces/archive/milestone-N.md` | Full historical detail | Only when debugging or researching past decisions |

#### What Counts as an Iteration

An iteration is a work session where you:
- Write or modify code files (not specs/docs)
- Complete tasks from the phase plan
- Make architectural or implementation decisions

**Scope rule:** One iteration = one focus area. If you worked on 3 different things,
that's 3 iterations, not 1. A good test: can you describe the focus in 5 words?

NOT an iteration: Pure research, Q&A, planning, or documentation-only changes.

#### After Each Coding Session (or before Session Close)

1. **Read `TRACES.md`** - find the last iteration number in "Current Work"
2. **Add iteration entry** to "Current Work" section (template below)
3. **If iteration 3, 6, 9...** -> run compaction process (see below)

#### Iteration Entry Template (Concise ~15 lines)

```
### Iteration N - YYYY-MM-DD
**Phase:** Phase X: Name
**Focus:** Brief description

**Changes:** `file.py` (what), `other.py` (what)
**Decisions:** Key decision -> rationale
**Next:** What's next

---
```

#### Compaction Process (Every 3 Iterations)

When you complete iteration 3, 6, 9, 12..., perform these steps:

1. **Create archive file** `traces/archive/milestone-N.md`:
   ```
   # Milestone N: [Focus Area]
   **Iterations:** X-Y | **Dates:** YYYY-MM-DD to YYYY-MM-DD

   ## Summary
   [2-3 sentences on what was accomplished]

   ## Key Decisions
   - Decision 1: Rationale
   - Decision 2: Rationale

   ## Iteration Details
   [Copy all 3 iteration entries from Current Work]
   ```

2. **Update Project Summary** in TRACES.md - add key decisions from this milestone
3. **Update Milestone Index** - add one row to the table
4. **Clear Current Work** - remove the 3 archived iterations, keep section header

#### When to Read Archive Files

Only read `traces/archive/` if:
- User asks about historical decisions
- Debugging requires understanding why something was built a certain way
- You need context from a specific past milestone

**Do NOT read archive files during normal iteration updates.**

### Branch Lifecycle

**Scope:** Applies to project source code changes — files that implement features, fix bugs,
or modify application behavior. Does NOT apply to:
- Build system infrastructure (TRACES.md, LEARNINGS.md, ROADMAP.md, CLAUDE.md build system section, hooks, settings.json) — this is exempt from both branch lifecycle AND Roadmap item requirements
- Documentation-only changes (README, docs/, .md files not in src/)
- Global config files outside the project (~/.claude/*, ~/.mcp.json)

When in doubt: if the change could break the application, use a branch.

Every code change follows: CREATE > WORK > REVIEW > SHIP

- **CREATE** — `git checkout -b {feat|fix|research|infra}/slug` from main.
  Update Build Roadmap: Status = In Progress, Branch = branch name.
- **WORK** — Edit, commit, iterate. Keep changes scoped (1-2 files ideal, single concern).
- **REVIEW** — `git diff main..branch` — review all changes before merge. This is the quality gate.
- **SHIP** — `git checkout main && git merge branch && git branch -d branch`.
  Update Roadmap: Status = Verifying, Branch = clear.
- **VERIFY** — User tests outside Claude Code. On next session, SessionStart hook asks about
  Verifying items. Pass = Shipped. Fail = spawn fix/ item with Source = Verification Failure.

### Build Roadmap

- **Notion DB Data Source ID:** [configured by /setup-cash-build-system]
- **Default View URL:** [configured by /setup-cash-build-system]

#### Checkout/Commit Model

`ROADMAP.md` is the local working copy. Notion is the remote. Sync is always one-direction-at-a-time.

| Phase | Direction | What happens |
|-------|-----------|-------------|
| **Session start** | Notion → local | Query Notion DB, rebuild `ROADMAP.md` with fresh state |
| **During session** | Local only | Read/update `ROADMAP.md` directly — it's your working state |
| **State transition** | Local + Notion | Update `ROADMAP.md` AND call `notion-update-page` in the same action |
| **Notion offline** | Local only | Update `ROADMAP.md`, add `<!-- sync pending -->` note. Next session with Notion catches up |

**Session start sync (rebuild ROADMAP.md):**
```
1. Query Notion: notion-query-database-view with view_url: "[configured view URL]"
2. Parse results into ROADMAP.md format (grouped by Status)
3. Write ROADMAP.md with "Last synced" timestamp and Sprint number
4. If Notion unavailable: read existing ROADMAP.md as-is (stale but usable)
```

**ROADMAP.md is ephemeral** — do NOT commit it to git. Add to `.gitignore`.
Between sessions, Notion is source of truth (user can reprioritize, add items).
During a session, `ROADMAP.md` is working state (Claude owns it).

#### Real-time updates (not batch-at-end)

- Start working on item → update `ROADMAP.md` to In Progress + call `notion-update-page`
- Ship (merge to main) → update `ROADMAP.md` to Verifying + call `notion-update-page`
- Discover insight → add to `ROADMAP.md` Insights section + call `notion-create-pages`
- Every code change must have a Roadmap item. If none exists, create one before starting.
  - Exception: Build system infrastructure setup (creating TRACES.md, LEARNINGS.md, ROADMAP.md,
    configuring hooks) does not require a Roadmap item — it IS the system that creates Roadmap items.

**Auto-filled fields:** Priority, Technical Notes (medium depth — implementation approach,
key dependencies, why it matters), Parallel Safety (via 3-tier heuristic), Sprint#,
Source, Task Breakdown (populated when item moves to In Progress).

**Creating items (Notion):**
```
notion-create-pages with parent: { data_source_id: "[configured DB ID]" }
properties: {
  "Item": "Description",
  "Status": "Insight",
  "Priority": "[auto-assessed]",
  "Epic": "[from standard set]",
  "Source": "[category]",
  "Sprint#": [current sprint number],
  "Technical Notes": "[auto-filled context]",
  "Parallel Safety": "[auto-classified]"
}
```
Then immediately add the new item to `ROADMAP.md` with its Notion page ID in a comment.

### Sprint System

- Sprint# = current TRACES.md milestone being worked toward
- Sprint N = all work between Milestone N-1 and Milestone N
- Find current sprint: read TRACES.md > last milestone number + 1
- Items discovered during Sprint N get tagged Sprint# = N
- "What shipped in Sprint 3?" = query Roadmap: Sprint# = 3, Status = Shipped

### Subagent Protocol

Every Agent call must include 4 blocks:

1. **CONSTRAINTS** — What the subagent cannot do: no MCP tools, no git operations,
   no network access, no files outside the allowlist below.
2. **FILE ALLOWLIST** — Every file the subagent may Read/Edit/Write, explicitly listed.
   "Do NOT touch any files not on this list."
3. **TASK** — Specific instructions with enough context to work independently.
4. **SUCCESS CRITERIA** — What "done" looks like so the subagent can self-validate.

**Parallel delegation pattern (for breaking big changes into multiple subagents):**
1. DECOMPOSE — Analyze the change, identify independent subtasks
2. MAP FILES — Assign each subtask an explicit file allowlist with ZERO overlap
3. PARALLEL SPAWN — Multiple Agent calls, each with all 4 blocks
4. REVIEW — Main session reviews all outputs for consistency
5. COMMIT — Main session commits the combined changes

### File Classification (Parallel Safety)

Before parallel work (multi-tab or multi-subagent), classify target files:
- **Safe** — New files, isolated files (0-1 importers), docs, research
- **Coordinate** — Shared files with 2-4 importers across the codebase
- **Sequential** — Config files, shared type definitions, files with 5+ importers

**Auto-classification heuristic:**
1. Pattern match on item description ("new file" = Safe, "schema change" = Sequential)
2. If ambiguous: Grep for imports/references to target file, count fan-out
3. Check known critical files list below

**Known critical (Sequential) files for this project:**
Maintained in `.claude/sequential-files.txt` (one filename per line).
Initial: `CLAUDE.md`. Add files when parallel edits cause merge conflicts.
The PreToolUse hook reads this file and warns subagents — it never blocks edits.

Task safety = worst classification of any file it touches. Default = Coordinate if uncertain.

### LEARNINGS.md Protocol

- When you try a method, it fails, and you succeed with a different method:
  immediately log the broken > working pair to LEARNINGS.md before continuing.
- Don't wait for session end. Capture at the moment of discovery.
- During TRACES.md milestone compaction (every 3 iterations):
  1. Review LEARNINGS.md
  2. Patterns confirmed 2+ times > graduate to CLAUDE.md anti-patterns
  3. Universal patterns (not project-specific) > also add to ~/.claude/CLAUDE.md
  4. Clear graduated entries from LEARNINGS.md
```

### Step 7: Create hook helper scripts

Create the `.claude/hooks/` directory and write the command-type hook scripts.

#### 7a: Create `.claude/hooks/check-sequential-files.sh`

```bash
#!/bin/bash
# Check if a file being edited is classified as Sequential.
# Outputs JSON with additionalContext so Claude actually sees the warning.
# Never blocks (always exit 0). Only fires for subagents (uses agent_id field).
# TRACES.md, LEARNINGS.md, ROADMAP.md are always exempt — they must never be blocked
# because the Stop hook requires updating them.

# jq is required for parsing hook input JSON
command -v jq >/dev/null 2>&1 || exit 0

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')
AGENT_ID=$(echo "$INPUT" | jq -r '.agent_id // empty')
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

# Only relevant for subagents — main session can edit anything
# agent_id is only present when hook fires inside a subagent
if [ -z "$AGENT_ID" ]; then
  exit 0
fi

# Build system files are always exempt (Stop hook requires updating these)
BASENAME=$(basename "$FILE_PATH" 2>/dev/null)
case "$BASENAME" in
  TRACES.md|LEARNINGS.md|ROADMAP.md) exit 0 ;;
esac

# Check sequential files list using cwd from JSON
SEQ_FILE="$CWD/.claude/sequential-files.txt"
if [ ! -f "$SEQ_FILE" ]; then
  exit 0  # No list = no restriction
fi

# Match against the list (exact whole-line match on basename to avoid false positives)
if [ -n "$BASENAME" ] && grep -qxF "$BASENAME" "$SEQ_FILE" 2>/dev/null; then
  # Use jq to safely build JSON (prevents injection from filenames with special chars)
  jq -n --arg bn "$BASENAME" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "allow",
      permissionDecisionReason: ("Allowed, but warning: " + $bn + " is a Sequential file. Ensure no other agent is editing it simultaneously."),
      additionalContext: ("Warning: " + $bn + " is listed in .claude/sequential-files.txt as a Sequential file. If other agents are running in parallel, coordinate to avoid merge conflicts.")
    }
  }'
  exit 0
fi

exit 0
```

#### 7b: Create `.claude/hooks/stop-check.sh`

```bash
#!/bin/bash
# Conditional Stop hook — only reminds about TRACES/LEARNINGS/Roadmap
# when code files were modified but traces weren't updated.
# Uses exit 2 + stderr to inject reminder into Claude's context.
# Exit 0 = Claude stops normally. Exit 2 = Claude continues with stderr as context.

# jq is required for parsing hook input JSON
command -v jq >/dev/null 2>&1 || exit 0

INPUT=$(cat)

# Break infinite loop: if Stop hook is already active, let Claude stop
STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_ACTIVE" = "true" ]; then
  exit 0
fi

CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
if [ -z "$CWD" ]; then
  exit 0
fi

cd "$CWD" 2>/dev/null || exit 0

# Check if any tracked code files were modified (staged or unstaged)
# Uses git status --porcelain which works even on repos with no commits
# Exclude TRACES.md, LEARNINGS.md, ROADMAP.md, CLAUDE.md, .claude/, all .md/.txt files, and untracked files
CODE_CHANGES=$(git status --porcelain 2>/dev/null | grep -vE '(TRACES\.md|LEARNINGS\.md|ROADMAP\.md|CLAUDE\.md|\.claude/)' | grep -vE '\.(md|txt)$' | grep -vE '^\?\?' | head -1)

# If no code files changed, no reminder needed
if [ -z "$CODE_CHANGES" ]; then
  exit 0
fi

# Check if TRACES.md was updated in this session (modified time within last hour)
# If recently updated, assume Claude is tracking the session properly
NOW=$(date +%s)

if [ -f "TRACES.md" ]; then
  TRACES_MOD=$(stat -f %m "TRACES.md" 2>/dev/null || stat -c %Y "TRACES.md" 2>/dev/null || echo 0)
  DIFF=$((NOW - ${TRACES_MOD:-0}))
  if [ "$DIFF" -lt 3600 ]; then
    exit 0  # TRACES.md was recently updated, no reminder needed
  fi
fi

# Build reminder listing what needs updating
REMIND=""
if [ -f "TRACES.md" ]; then
  REMIND="${REMIND}(1) Add an iteration entry to TRACES.md. "
else
  REMIND="${REMIND}(1) Create TRACES.md and add an iteration entry (run /setup-cash-build-system if not yet set up). "
fi

if [ -f "ROADMAP.md" ]; then
  ROADMAP_MOD=$(stat -f %m "ROADMAP.md" 2>/dev/null || stat -c %Y "ROADMAP.md" 2>/dev/null || echo 0)
  DIFF=$((NOW - ${ROADMAP_MOD:-0}))
  if [ "$DIFF" -ge 3600 ]; then
    REMIND="${REMIND}(2) Update ROADMAP.md with current status. "
  fi
fi

REMIND="${REMIND}(3) Log any trial-and-error patterns to LEARNINGS.md."

# Code was modified but TRACES.md wasn't updated — exit 2 so Claude continues
# stderr is fed to Claude as context (per hooks reference: Stop exit 2 = continue with stderr)
echo "Session check: Code files were modified but TRACES.md was not updated. Before stopping: ${REMIND}" >&2

exit 2
```

#### 7c: Create `.claude/sequential-files.txt`

```
CLAUDE.md
```

#### 7d: Make scripts executable

```bash
chmod +x .claude/hooks/check-sequential-files.sh
chmod +x .claude/hooks/stop-check.sh
```

### Step 8: Configure Hooks

**Determine the project settings file path.** Check for:
1. `.claude/settings.local.json` in the project root (preferred — local, not committed)
2. `.claude/settings.json` in the project root (committed to repo)

If the file exists, merge the `hooks` key into the existing JSON. If it doesn't exist, create `.claude/settings.local.json` with the hooks.

**IMPORTANT:** When merging into an existing settings file, preserve all existing keys (permissions, other hooks, etc.). Remove any legacy setup-traces Stop hook if present (the new consolidated hook is a superset). Remove any v1 prompt-type Stop or Edit|Write hooks.

Add/merge these hooks:

#### Stop Hook (command type — conditional, loop-safe)

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/stop-check.sh\""
          }
        ]
      }
    ]
  }
}
```

**Why command type:** The Stop hook checks git status and file timestamps — purely deterministic. Uses exit 2 + stderr when a reminder is needed (per hooks reference: Stop exit 2 = Claude continues with stderr fed as context). Exit 0 when no reminder needed (Claude stops normally). The `stop_hook_active` guard breaks infinite loops: on the second firing after Claude updates TRACES.md, `stop_hook_active` is true so it exits 0 immediately. Uses `git status --porcelain` instead of `git diff HEAD` so it works on fresh repos with no commits.

#### SessionStart Hook (startup — command type)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'REQUIRED before responding to the user: (1) Read TRACES.md to find current sprint number and last iteration. (2) Rebuild ROADMAP.md from Notion if connected (query DB, overwrite local file), or read existing ROADMAP.md. Check for items with Status=Verifying — ask user for pass/fail. (3) Scan LEARNINGS.md for the 3 most recent patterns to avoid repeating mistakes.'"
          }
        ]
      }
    ]
  }
}
```

**Why `startup` matcher:** Prevents double-fire on `/resume` (known issue #30825). Uses "REQUIRED" directive language (not a suggestion) because SessionStart stdout is added to context but Claude has no obligation to act on passive text. The directive ensures Claude reads TRACES.md and checks the Roadmap before engaging with the user's first message.

#### SessionStart Hook (compact — re-inject context)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "sed '/^---$/q' \"$CLAUDE_PROJECT_DIR/TRACES.md\" 2>/dev/null || echo 'No TRACES.md found'"
          }
        ]
      }
    ]
  }
}
```

**Why separate compact hook:** After context compaction, sprint context is lost. This re-injects the TRACES.md header (Project Summary + Milestone Index) to preserve continuity. Uses `sed '/^---$/q'` instead of `head -20` because the Milestone Index table grows by 1 row per 3 iterations — after 15 iterations it exceeds 20 lines and `head -20` would truncate the most recent milestones.

#### PreToolUse Hook: Agent (subagent validation — prompt type)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Agent",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if this Agent call includes: (1) CONSTRAINTS section, (2) FILE ALLOWLIST with explicit file paths, (3) TASK section, (4) SUCCESS CRITERIA. If FILE ALLOWLIST is missing, respond {\"ok\": false, \"reason\": \"Add FILE ALLOWLIST before spawning\"}. If other sections are missing, respond {\"ok\": true, \"reason\": \"\"} but note the missing sections — they are recommended but not blocking."
          }
        ]
      }
    ]
  }
}
```

**Why prompt type:** Evaluating whether an Agent prompt contains the required sections requires LLM judgment. Only FILE ALLOWLIST is a hard block (prevents unscoped file access). Other sections are advisory — reduces false denials.

#### PreToolUse Hook: Edit/Write (sequential file warning — command type)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/check-sequential-files.sh\""
          }
        ]
      }
    ]
  }
}
```

**Why command type:** Checking a filename against a text file list is deterministic — no LLM needed. The script reads `.claude/sequential-files.txt` (not CLAUDE.md — no circular dependency). Always exits 0 (never blocks). Uses `jq -n --arg` to safely build JSON output (prevents injection from filenames with special characters). Uses JSON `additionalContext` field so Claude actually sees the warning (plain stderr is verbose-mode-only and invisible to Claude). Uses `agent_id` field to detect subagents (only present when hook fires inside a subagent — main session has no `agent_id`). Exempts TRACES.md, LEARNINGS.md, and ROADMAP.md to prevent conflict with the Stop hook (which requires updating these files). Uses `cwd` from JSON input for the file path (safer than relying on `CLAUDE_PROJECT_DIR` env var propagation). Uses `grep -qxF` for exact whole-line matching (prevents `CLAUDE.md` from matching `MY_CLAUDE.md`). Requires `jq` (validated in Step 9).

#### PostToolUseFailure Hook (LEARNINGS.md nudge — prompt type)

```json
{
  "hooks": {
    "PostToolUseFailure": [
      {
        "matcher": "Bash|Edit|Write",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "A tool just failed. If you tried a method that failed and then succeeded with a different approach, log the broken > working pair to LEARNINGS.md now. If the failure is expected or you haven't found a fix yet, continue normally."
          }
        ]
      }
    ]
  }
}
```

**Why `Bash|Edit|Write` matcher:** Only these tools produce learnable trial-and-error patterns (wrong command, wrong file path, wrong edit syntax). Without a matcher, every Glob/Grep/Read returning no results triggers a Haiku API call (~2-5s each), causing 20-50+ unnecessary evaluations per exploration-heavy session. The Haiku model has no conversation context — it can't distinguish "expected miss" from "learnable failure" — so an empty matcher produces unpredictable decisions.

**Why prompt type:** Deciding whether a specific Bash/Edit/Write failure is a learnable pattern requires judgment that a command hook can't provide.

**Merge all hooks into a single settings file.** Combine all PreToolUse hooks into one array. Combine all SessionStart hooks (startup + compact) into one array. Do not create separate entries for each hook event — merge them properly.

### Step 9: Validate hook configuration

After writing all hooks and scripts, validate the setup:

```bash
# Verify jq is installed (required by hook scripts for parsing JSON input)
command -v jq >/dev/null 2>&1 || echo "ERROR: jq is required for hook scripts but not found (install: brew install jq / apt install jq)"

# Validate JSON syntax
jq . .claude/settings.local.json > /dev/null 2>&1 || echo "ERROR: Invalid JSON in settings"

# Verify hook scripts exist and are executable
[ -x .claude/hooks/stop-check.sh ] || echo "ERROR: stop-check.sh not executable"
[ -x .claude/hooks/check-sequential-files.sh ] || echo "ERROR: check-sequential-files.sh not executable"

# Verify sequential files list exists
[ -f .claude/sequential-files.txt ] || echo "ERROR: sequential-files.txt missing"
```

Report any errors to the user before proceeding. Fix them if possible.

### Step 10: Add MEMORY.md Reminder

Check if the project has a MEMORY.md file in the auto-memory directory (`~/.claude/projects/{encoded-project-path}/memory/MEMORY.md`).

If it exists, append or update this section:

```markdown
## CASH Build System (MANDATORY)
If code files are modified during a session, **update `TRACES.md`** with an iteration entry before closing. Update `ROADMAP.md` with current item status. Log trial-and-error patterns to `LEARNINGS.md` immediately when discovered. At session start, rebuild `ROADMAP.md` from Notion if connected. This is enforced by hooks. Read `TRACES.md` at the start of coding sessions to know the current iteration and sprint number.
```

If MEMORY.md doesn't exist yet, create it with just this section.

### Step 11: Integrate with Session Close Checklist (if one exists)

Search CLAUDE.md for a "Session Close" or "Session Lifecycle" section. If one exists:
- Add Build Traces as **Step 1** if it isn't already there
- Add LEARNINGS.md check as an additional step
- Add Build Roadmap status check as an additional step

If no session close checklist exists, skip this step — the hooks and MEMORY.md reminder are sufficient.

### Step 12: Sprint# Bootstrapping

Determine the current Sprint number:
- **If TRACES.md exists with milestones:** Sprint# = last milestone + 1
- **If TRACES.md exists with no milestones (only current work):** Sprint# = 1
- **If TRACES.md was created fresh:** Sprint# = 1

Report the current Sprint# to the user.

### Step 13: Confirm completion

Tell the user what was created/configured:

- `TRACES.md` — Rolling window trace file [created / already existed]
- `traces/archive/.gitkeep` — Archive directory for milestones [created / already existed]
- `LEARNINGS.md` — Learning loop file [created / already existed]
- `ROADMAP.md` — Local Build Roadmap working copy [created from Notion / created empty template]
- `.gitignore` — Updated to exclude ROADMAP.md
- Updated `CLAUDE.md` with Build System Protocol (lifecycle, roadmap checkout/commit model, sprint, subagent, file classification, learnings)
- **Build Roadmap** — Notion DB [connected / skipped]
- **Hook scripts created:**
  - `.claude/hooks/stop-check.sh` — Conditional Stop reminder (command type, loop-safe)
  - `.claude/hooks/check-sequential-files.sh` — Sequential file warning (command type, advisory)
  - `.claude/sequential-files.txt` — Editable list of Sequential files
- **Hooks configured (6 active):**
  - Stop: Conditional check via `stop-check.sh` — exit 2 + stderr forces TRACES update (command)
  - SessionStart (startup): REQUIRED directive — read TRACES, check Roadmap (command)
  - SessionStart (compact): Re-inject TRACES.md header after compaction (command)
  - PreToolUse (Agent): Subagent 4-block validation, FILE ALLOWLIST required (prompt)
  - PreToolUse (Edit/Write): Sequential file warning via `check-sequential-files.sh` (command)
  - PostToolUseFailure (Bash|Edit|Write): LEARNINGS.md capture nudge (prompt)
- **MEMORY.md** entry — auto-loaded reminder every session

Report:
- Current Sprint: [N]
- Roadmap: [X] items ([Y] in progress, [Z] verifying) — or "not connected"
- Hooks: 6 active (4 command, 2 prompt)
- Hook scripts: `.claude/hooks/` (2 scripts, both executable)
- Validation: [pass/fail details]

Remind them:
- The system uses O(1) context: TRACES.md stays ~80 lines forever
- LEARNINGS.md captures trial-and-error patterns and graduates them to CLAUDE.md
- Build Roadmap uses a checkout/commit model: ROADMAP.md is the local working copy, Notion is the remote. Syncs at session start, updates both during state transitions
- Subagent protocol enforces safe parallel work
- Six hooks enforce the system: 4 command (deterministic, no context cost) + 2 prompt (judgment-based)
- Stop hook is loop-safe (`stop_hook_active` guard) and uses exit 2 to force TRACES.md updates (Claude continues with stderr as context, not exit 0 which is invisible)
- Edit/Write hook never blocks — uses JSON `additionalContext` so Claude sees warnings (not stderr which is verbose-mode-only), no more circular dependency failures
