# Skills Factory

This is the skill development workspace. All skill-making projects live here.

## Skill Development Methodology

When creating, reviewing, or iterating on skills in this project, follow the **SKILL-CRAFT** methodology in `SKILL-CRAFT.md`.

Key principles to always apply:

1. **Expertise transfer, not instructions** - Make Claude think like an expert, not follow steps
2. **Flow, not friction** - Produce output, not intermediate documents
3. **Voice matches domain** - Sound like a practitioner, not documentation
4. **Focused beats comprehensive** - Every section earns its place

## The Process

For any skill development work, follow this sequence:

1. **Understanding** - What problem? What triggers? What's out of scope?
2. **Exploring** - Test where Claude fails without guidance
3. **Research** - Study how practitioners actually work
4. **Synthesis** - Extract principles from research
5. **Drafting** - Write initial skill with domain voice
6. **Self-Critique** - Review against quality criteria
7. **Iterating** - Cut ruthlessly, strengthen mental models
8. **Testing** - Use skill on real scenario
9. **Finalizing** - Lock in optimal structure

## Development Logging

**For every skill project, maintain a development log.**

At the start of any skill development:
1. Create `skill-development-log.md` in the skill's project folder
2. Log all interview discussions, decisions, and rationale
3. Update the log as work progresses
4. Include: topics covered, decisions made, files created, open questions

The log serves as:
- Decision record (why we chose X over Y)
- Context preservation (resume work after breaks)
- Pattern library (reference for future skills)
- Onboarding doc (others can understand the skill's design)

**Log structure:**
```markdown
# [Skill Name] - Development Log

## Overview
- Purpose, scope, methodology

## Topic N: [Topic Name] ✓/In Progress/Pending
- Discussion summary
- Decisions made
- Rationale

## Decisions Summary
- Table of key decisions

## Files Created
- List of artifacts
```

## Quality Check

Before finalizing any skill, verify:

- [ ] Does it transfer expertise or just give instructions?
- [ ] Does reading it make you think differently about the domain?
- [ ] Could you remove 30% and still have the essence?
- [ ] Does it sound like an expert, not documentation?
- [ ] Would a domain practitioner recognize themselves in it?
- [ ] Is the development log complete and up to date?

## File Reference

- `SKILL-CRAFT.md` - Full methodology with examples and anti-patterns
- `[skill-folder]/skill-development-log.md` - Per-skill development log

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

- **Notion DB Data Source ID:** 2ccf9222-eb39-4093-9e76-ec408afedcba
- **Default View URL:** https://www.notion.so/249a8b27c5014138909263a5f1ecf137

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
1. Query Notion: notion-query-database-view with view_url: "https://www.notion.so/249a8b27c5014138909263a5f1ecf137"
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
notion-create-pages with parent: { data_source_id: "2ccf9222-eb39-4093-9e76-ec408afedcba" }
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
