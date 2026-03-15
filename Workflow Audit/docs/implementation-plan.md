# Implementation Plan: QMD + CC Workflow Enrichment

**Date:** 2026-03-14
**Project:** QMD and CC Workflow Enrichment
**Prerequisite:** [Feasibility Assessment](./feasibility-assessment.md) — all checks passed

---

## Overview

Four phases, each delivering standalone value:

```
Phase 1: QMD Foundation        → Searchable knowledge base across all CC data
Phase 2: Workflow Audit        → Report + interactive improvement session
Phase 3: Audit as Skill        → Periodic `/workflow-audit` with run history
Phase 4: Visualize Tool        → Interactive architecture/workflow visualizer for repos
```

Each phase builds on the previous. No phase requires all prior phases to be 100% complete — Phase 2 can start once Phase 1 has basic collections working, etc.

---

## Phase 1: QMD Foundation

**Goal:** Install qmd, build the JSONL preprocessing pipeline, create collections, generate embeddings. End state: you can run `qmd query "what frustrations have I expressed?"` and get meaningful results across all your CC data.

### Step 1.1: Install QMD

```
npm install -g @tobilu/qmd
```

Verify: `qmd --version` and `qmd status`

First run will auto-download three GGUF models (~2.5GB total) to `~/.cache/qmd/models/`.

### Step 1.2: Build the JSONL Preprocessing Pipeline

This is the core engineering work of Phase 1. Create a Python script (`scripts/preprocess-jsonl.py`) that converts CC conversation data into searchable markdown.

#### 1.2.1: history.jsonl Processor

**Input:** `~/.claude/history.jsonl` (1,707 entries)
**Output:** One markdown file per project: `preprocessed/history/by-project/<project-slug>.md`

Each file contains all user prompts for that project, chronologically:

```markdown
---
source: history.jsonl
project: Skills Factory/Cash Build System
generated: 2026-03-14T12:00:00Z
prompt_count: 65
date_range: 2026-02-10 to 2026-03-14
---

# User Prompts: Skills Factory / Cash Build System

## 2026-02-10

### Session abc123 (14:32)
> let's set up the build system traces

### Session abc123 (14:45)
> no not that, do it as a stop hook instead

## 2026-02-11
...
```

**Why per-project files:** qmd's context system works at the file/collection level. One file per project means search results come back with project context attached. Also keeps individual files under the ~900-token chunk size sweet spot.

#### 1.2.2: Conversation JSONL Processor

**Input:** `~/.claude/projects/*/*.jsonl` (113 sessions, 163MB)
**Output:** One markdown file per session: `preprocessed/conversations/<project-slug>/<session-id>.md`

Extraction logic (structured, no LLM — Phase 1 option c):

```markdown
---
source: conversation
session_id: c1c5e4e3-2569-4eee-9cc2-e7baa61d4b8b
project: Skills Factory/Cash Build System
date: 2026-03-12
entry_count: 376
user_messages: 84
tool_uses: 131
errors: 3
duration_estimate: ~45min
---

# Session: Cash Build System — 2026-03-12

## User Messages (chronological)

> let's deploy the hooks to all four projects

> pause! do not reframe any approaches. the ai cos is for context!

> propose

> looks good, ship it

## Tool Usage Summary

| Tool | Count | Notes |
|------|-------|-------|
| Edit | 42 | Most edited: .claude/hooks/stop-check.sh |
| Read | 35 | |
| Bash | 28 | |
| Agent | 15 | 8 subagents spawned |
| Write | 11 | |

## Files Modified

- `.claude/hooks/stop-check.sh` (12 edits)
- `CLAUDE.md` (5 edits)
- `.claude/hooks/sync-push.sh` (4 edits)

## Errors Encountered

1. [Line 234] `Exit code 1: pre-commit hook failed — ruff formatting`
2. [Line 456] `JSON validation failed in sync-push.sh`
3. [Line 612] `Permission denied: /Users/Aakash/.claude/hooks/stop-check.sh`

## User Corrections / Feedback

> "pause! do not reframe any approaches"
> "don't fucking assume things!"
> "no not that, instead do..."

(Extracted by pattern matching: messages starting with "no", "don't", "stop", "pause", "not that", or containing corrections)
```

**Extraction rules for each field:**

| Field | Source | Logic |
|-------|--------|-------|
| User messages | Entries with `type: "user"` | Extract `message.content` text blocks |
| Tool usage | Entries with `type: "progress"` | Count by tool name from `data.toolName` or similar |
| Files modified | Tool use entries for Edit/Write | Extract `file_path` parameter |
| Errors | Tool results containing exit codes > 0, or error patterns | Regex for `exit code`, `error`, `failed`, `denied` |
| Corrections | User messages matching frustration/correction patterns | Regex: `^(no|don't|stop|pause|not that|instead)`, exclamation marks, ALL CAPS |
| Duration | First and last timestamp in session | Difference in minutes |

#### 1.2.3: Subagent JSONL Processor

**Input:** `~/.claude/projects/*/subagents/agent-*.jsonl` (227 sessions, 53MB)
**Output:** One markdown file per subagent session: `preprocessed/subagents/<project-slug>/<agent-id>.md`

Lighter extraction — focus on:
- What task was the subagent given (first user/system message)
- What tools did it use
- Did it succeed or fail
- How long did it run

#### 1.2.4: Sync Inbox Processor

**Input:** `.claude/sync/inbox.jsonl` files across 4 projects
**Output:** Single file: `preprocessed/sync/cross-project-messages.md`

Simple chronological list of all cross-project messages with source/target project context.

### Step 1.3: Create QMD Collections

After preprocessing, set up collections that map to our data topology:

```bash
# Direct markdown sources
qmd collection add ~/.claude/projects/ --name cc-memories --mask "**/memory/*.md"
qmd collection add "/Users/Aakash/Claude Projects" --name project-claude-mds --mask "**/CLAUDE.md"
qmd collection add ~/.claude --name global-config --mask "CLAUDE.md"

# Preprocessed conversation data
qmd collection add preprocessed/history --name prompt-history --mask "**/*.md"
qmd collection add preprocessed/conversations --name conversations --mask "**/*.md"
qmd collection add preprocessed/subagents --name subagent-logs --mask "**/*.md"
qmd collection add preprocessed/sync --name cross-project-sync --mask "**/*.md"

# CASH Build System artifacts
qmd collection add "/Users/Aakash/Claude Projects/Skills Factory" --name skills-factory --mask "**/*.md"
qmd collection add "/Users/Aakash/Claude Projects" --name traces-learnings --mask "**/TRACES.md"
```

**Note:** Exact paths and masks will be refined during implementation. The `preprocessed/` directory should live within this project: `/Users/Aakash/Claude Projects/Skills Factory/Workflow Audit/preprocessed/`.

### Step 1.4: Add Context Annotations

qmd's context system is hierarchical — context propagates to search results. This is critical for making audit queries meaningful.

```bash
# Collection-level context
qmd context add qmd://cc-memories "Claude Code memory files — user preferences, feedback corrections, project context, reference pointers"
qmd context add qmd://prompt-history "Raw user prompts from Claude Code history — shows what the user asks for, how they phrase requests, frustration patterns"
qmd context add qmd://conversations "Preprocessed conversation sessions — tool usage, errors, files modified, user corrections"
qmd context add qmd://subagent-logs "Subagent execution logs — parallel work patterns, success/failure rates"
qmd context add qmd://project-claude-mds "Project-level CLAUDE.md files — per-project protocols, constraints, conventions"
qmd context add qmd://global-config "Global Claude Code configuration — operating principles, code quality rules"
qmd context add qmd://skills-factory "Skills Factory project — skill definitions, CASH Build System, methodology"
qmd context add qmd://traces-learnings "TRACES.md and LEARNINGS.md — iteration logs and accumulated lessons from development"
qmd context add qmd://cross-project-sync "Cross-project sync messages — coordination patterns between projects"

# Sub-path context for richer results
qmd context add qmd://cc-memories/feedback "Feedback memories — corrections the user has given Claude about behavior"
qmd context add qmd://cc-memories/user "User memories — role, preferences, knowledge profile"
qmd context add qmd://cc-memories/project "Project memories — ongoing work context, goals, deadlines"
```

### Step 1.5: Index and Embed

```bash
qmd update          # Scan all collections, index documents
qmd embed           # Generate vector embeddings for semantic search
```

### Step 1.6: Validation

Run test queries to verify the index is working:

```bash
# Should find frustration patterns in conversation logs
qmd query "what mistakes does Claude keep making?"

# Should find tool usage patterns
qmd query "which tools are used most often?"

# Should find specific feedback
qmd search "don't mock the database" -c cc-memories

# Should find cross-project patterns
qmd query "what learnings apply across multiple projects?"
```

### Step 1.7: Re-indexing Strategy

New conversation data arrives every session. The preprocessing pipeline needs to run before qmd can see new data.

**Option A (recommended for Phase 1): Manual re-index script**

Create `scripts/reindex.sh`:
```bash
#!/bin/bash
# Run preprocessor for any new/changed JSONLs
python3 scripts/preprocess-jsonl.py --incremental
# Update qmd index
qmd update
qmd embed
```

Run before each audit. Simple, predictable.

**Option B (Phase 3): Hook-triggered**

Add a SessionEnd hook that queues re-indexing. More automated but adds complexity.

**Option C (Phase 3): Cron**

`crontab` entry to run `reindex.sh` daily/weekly. Low-effort automation.

### Phase 1 Deliverables

- [ ] qmd installed and models downloaded
- [ ] `scripts/preprocess-jsonl.py` — converts all JSONL sources to markdown
- [ ] `scripts/reindex.sh` — one-command re-index pipeline
- [ ] 9 qmd collections configured with context annotations
- [ ] All documents indexed and embedded
- [ ] Validation queries returning meaningful results

### Phase 1 Estimated Effort

| Task | Effort |
|------|--------|
| Install qmd + model download | 10 min |
| Build JSONL preprocessor | 2-3 hours (main engineering work) |
| Create collections + contexts | 30 min |
| Index + embed | 20-30 min (mostly waiting) |
| Validation + tuning | 30 min |
| **Total** | **~4 hours** |

---

## Phase 2: Workflow Audit

**Goal:** Build an analysis engine that queries qmd, synthesizes findings into a structured report, then runs an interactive session to implement selected improvements.

### Step 2.1: Define Audit Dimensions

The audit examines your CC workflow across seven dimensions:

#### Dimension 1: Friction Points
**Query strategy:** Search for frustration patterns in conversations and history.
- User corrections ("no", "don't", "stop", "not that", "instead")
- Repeated requests (same question asked multiple times)
- Sessions with high error counts
- Long sessions (possibly stuck on something)

**Sample queries:**
```bash
qmd query "user frustration or correction" -c conversations --json
qmd query "repeated errors or failures" -c conversations --json
qmd search "don't" -c prompt-history --json --all --min-score 0.3
```

#### Dimension 2: Tool Usage Patterns
**Query strategy:** Analyze tool usage summaries across conversations.
- Most/least used tools
- Tool failure rates
- Subagent usage patterns
- Tools that could replace manual work

**Sample queries:**
```bash
qmd query "tool usage summary" -c conversations --json --all
qmd query "subagent spawned failed" -c subagent-logs --json
```

#### Dimension 3: Skill Gaps
**Query strategy:** Find tasks where available skills weren't used, or where manual work could be automated.
- Tasks done manually that a skill could handle
- Skills that exist but are never invoked
- Patterns that suggest a missing skill

**Cross-reference:** Compare tool usage in conversations against available skills list.

#### Dimension 4: Cross-Project Patterns
**Query strategy:** Find themes, tools, or problems that appear across multiple projects.
- Same errors in different projects
- Similar CLAUDE.md rules duplicated
- Sync friction between projects

**Sample queries:**
```bash
qmd query "recurring pattern across projects" --json
qmd query "same error different project" -c conversations --json
```

#### Dimension 5: Memory Health
**Query strategy:** Audit the memory system itself.
- Stale memories (saved long ago, never referenced)
- Missing memories (repeated corrections that should have been saved)
- Feedback memories that are being ignored (same correction given multiple times)
- Memory coverage gaps (projects with no memories)

**Sample queries:**
```bash
qmd query "feedback correction preference" -c cc-memories --json
# Cross-reference with corrections found in conversations
```

#### Dimension 6: Configuration Drift
**Query strategy:** Compare CLAUDE.md files across projects for inconsistencies.
- Rules in global CLAUDE.md that are contradicted at project level
- Project CLAUDE.md rules that should be promoted to global
- Hook configurations that differ between projects unnecessarily

#### Dimension 7: Automation Opportunities
**Query strategy:** Find manual patterns ripe for hooks or skills.
- Commands run frequently in Bash that could be hooks
- Multi-step workflows repeated across sessions
- Tasks that always follow the same pattern

### Step 2.2: Build the Audit Engine

Create `scripts/workflow-audit.py` — a Python script that:

1. **Runs a battery of qmd queries** across all seven dimensions
2. **Parses and correlates results** (e.g., a friction point in conversations matches a feedback memory)
3. **Scores and ranks findings** by impact (frequency x severity)
4. **Generates a structured report**

#### Report Structure

```markdown
# CC Workflow Audit Report
**Generated:** 2026-03-14
**Data range:** 2026-02-01 to 2026-03-14
**Sessions analyzed:** 113
**Projects covered:** 15

## Executive Summary
- Top 3 friction points (with evidence)
- Top 3 automation opportunities
- Memory system health score

## 1. Friction Points (ranked by frequency)

### FP-1: [Pattern name] (occurred N times)
**Evidence:**
- Session X (2026-03-10): "don't mock the database"
- Session Y (2026-03-12): "stop assuming things"
**Impact:** High — causes repeated corrections
**Suggested fix:** [specific action]

### FP-2: ...

## 2. Tool Usage Analysis

### Most Used Tools
| Tool | Total Uses | Failure Rate | Avg per Session |
|------|-----------|-------------|-----------------|
| Edit | 1,234 | 2% | 11 |
| ...  | ... | ... | ... |

### Underutilized Capabilities
- Agent tool used in only 15% of sessions despite available subagent types
- LSP tool never used (is it configured?)

## 3. Skill Gaps
- [Gap description + evidence]

## 4. Cross-Project Patterns
- [Pattern + which projects]

## 5. Memory Health
| Metric | Value | Status |
|--------|-------|--------|
| Total memories | 19 | |
| Projects with memories | 8/20 | Needs attention |
| Feedback memories | 5 | |
| Stale memories (>30d) | 3 | Review needed |

## 6. Configuration Drift
- [Inconsistencies found]

## 7. Automation Opportunities
- [Opportunity + estimated time savings]

## Improvement Backlog (prioritized)
| # | Improvement | Dimension | Impact | Effort |
|---|------------|-----------|--------|--------|
| 1 | ... | Friction | High | Low |
| 2 | ... | Automation | High | Medium |
| ... | ... | ... | ... | ... |
```

### Step 2.3: Interactive Follow-up

After generating the report, the audit enters interactive mode. This is a conversation where:

1. **Present findings one at a time** (highest impact first)
2. **For each finding, offer actions:**
   - "Implement this now" — Claude makes the change (add memory, update CLAUDE.md, create hook, etc.)
   - "Save for later" — Added to a backlog file
   - "Dismiss" — Not relevant, skip
   - "Discuss" — Need more context before deciding
3. **Track what was implemented** in a run log

#### Interactive Session Flow

```
Audit found 12 improvements across 7 dimensions.

[1/12] FRICTION: You've corrected Claude about mocking databases 3 times
       across 2 projects, but there's no feedback memory for this.

       Action: Create a feedback memory in the global project?
       [implement / save / dismiss / discuss]

> implement

Created memory: feedback_no_database_mocking.md
"Integration tests must hit a real database, not mocks."

[2/12] AUTOMATION: You run `ruff format . && ruff check .` manually before
       every commit (found in 8 sessions). This could be a pre-commit hook.

       Action: Add pre-commit hook configuration?
       [implement / save / dismiss / discuss]

> discuss

The .pre-commit-config.yaml pattern is already in your global CLAUDE.md
for new projects. But 3 existing projects don't have it. Want me to add
it to those projects?

> implement
...
```

### Phase 2 Deliverables

- [ ] `scripts/workflow-audit.py` — audit engine with 7-dimension analysis
- [ ] Report template (markdown, saved to `reports/audit-YYYY-MM-DD.md`)
- [ ] Interactive follow-up mode
- [ ] Run log tracking implemented/saved/dismissed items

### Phase 2 Estimated Effort

| Task | Effort |
|------|--------|
| Define query battery per dimension | 1 hour |
| Build audit engine + report generator | 3-4 hours |
| Build interactive follow-up mode | 2 hours |
| Testing and tuning thresholds | 1 hour |
| **Total** | **~7-8 hours** |

---

## Phase 3: Audit as Skill/Command

**Goal:** Codify the workflow audit as a Claude Code skill (`/workflow-audit`) that can be run periodically, with state persistence between runs.

### Step 3.1: Skill Structure

Create as a skill in the superpowers plugin (or a standalone plugin):

```
skills/
  workflow-audit/
    SKILL.md              # Skill definition + trigger description
    references/
      audit-dimensions.md # The 7 dimensions defined in Phase 2
      query-battery.md    # All qmd queries used
```

**Skill trigger:** "audit my workflow", "run workflow audit", "check for improvements", `/workflow-audit`

### Step 3.2: State Persistence

The skill needs to remember past runs. Create a state file:

**Location:** `/Users/Aakash/Claude Projects/Skills Factory/Workflow Audit/state/`

```
state/
  audit-history.yaml       # Index of all past audit runs
  runs/
    2026-03-14.md          # Full report from that date
    2026-03-14-actions.md  # What was implemented/saved/dismissed
    2026-03-28.md          # Next run
    2026-03-28-actions.md
    ...
```

#### audit-history.yaml

```yaml
last_run: 2026-03-28
run_count: 3
runs:
  - date: 2026-03-14
    sessions_analyzed: 113
    findings: 12
    implemented: 5
    saved: 4
    dismissed: 3
    report: runs/2026-03-14.md
  - date: 2026-03-28
    sessions_analyzed: 128
    findings: 8
    implemented: 3
    saved: 3
    dismissed: 2
    new_since_last: 15 sessions
    report: runs/2026-03-28.md
```

### Step 3.3: Differential Auditing

After the first run, subsequent runs should focus on **what's new**:

1. **Read audit-history.yaml** to find last run date
2. **Preprocess only new/changed JSONLs** (incremental mode)
3. **Run qmd update + embed** (incremental — only new docs)
4. **Run audit queries** but filter to new data window
5. **Cross-reference with past findings:**
   - "This was flagged last time and saved for later — still relevant?"
   - "This was implemented last time — did it stick? (Still seeing the pattern?)"
   - "New finding not seen before"
6. **Generate differential report** showing new, recurring, and resolved findings

### Step 3.4: Recommended Cadence

Based on the user's CC usage patterns (~1,700 prompts over ~5 weeks ≈ ~50 prompts/day):

- **Bi-weekly** (every 14 days) as baseline — matches the X poster's suggestion
- **Before major project milestones** — catch issues before they compound
- **After a "bad week"** (lots of corrections/errors) — diagnose what went wrong

The skill should suggest the next run date based on data volume since last run.

### Step 3.5: Upgrade to LLM-Assisted Preprocessing (Phase 1 Option B)

Once the basic pipeline is working, add an optional `--deep` flag that:

1. For each conversation session, sends the raw user messages + tool summaries to Claude API
2. Gets back a richer summary: "This session was about deploying CASH Build System v1.2 hooks. Key decisions: switched from prompt hooks to CLAUDE.md instructions due to Haiku limitation. Main friction: sync-push.sh error handling."
3. These LLM summaries replace the structured extractions in the qmd index
4. Richer summaries = better semantic search = better audit findings

**Cost estimate:** 113 sessions x ~2K tokens each ≈ ~230K tokens. At Claude Haiku rates (~$0.25/M input, $1.25/M output) ≈ $0.35 total. Negligible.

**Implementation:** Add a `--deep` flag to `preprocess-jsonl.py` that calls Claude API for summarization. Cache results so re-runs don't re-summarize unchanged sessions.

### Phase 3 Deliverables

- [ ] `/workflow-audit` skill definition (SKILL.md)
- [ ] State persistence (audit-history.yaml + per-run reports)
- [ ] Differential auditing (new/recurring/resolved findings)
- [ ] `--deep` LLM summarization mode for preprocessing
- [ ] Cadence recommendations in the skill output
- [ ] Re-index automation (cron or hook-triggered)

### Phase 3 Estimated Effort

| Task | Effort |
|------|--------|
| Skill scaffolding + trigger config | 1 hour |
| State persistence layer | 1-2 hours |
| Differential auditing logic | 2-3 hours |
| LLM summarization upgrade | 2 hours |
| Cron/hook re-index automation | 1 hour |
| Testing across 2-3 audit cycles | 2 hours |
| **Total** | **~9-11 hours** |

---

## Phase 4: Visualize Tool

**Goal:** Build an interactive visualization tool that can render architecture diagrams, workflow maps, and data flow visualizations for any repo or system — opened in the browser.

### Step 4.1: What to Visualize

| Visualization | Input | Output |
|--------------|-------|--------|
| **Repo architecture** | Any git repo path | Interactive dependency/module map |
| **Workflow audit results** | Audit report | Visual dashboard of findings |
| **Project topology** | All CC projects | Map of projects, their connections, data flows |
| **Session timeline** | Conversation logs | Timeline of what happened, errors, decisions |
| **Skill/hook dependency graph** | CASH Build System config | Which hooks trigger where, skill relationships |
| **Memory network** | All memory files | Graph of memories, which projects reference what |

### Step 4.2: Architecture

```
/visualize command/skill
        │
        ├── Analyzer module
        │   ├── Repo structure parser (glob + AST for imports)
        │   ├── Audit report parser
        │   ├── CASH Build System parser
        │   └── qmd query interface (for data retrieval)
        │
        ├── Renderer module
        │   ├── HTML generator (React + D3.js or vis.js)
        │   ├── Layout engine (force-directed, hierarchical, timeline)
        │   └── Interactive controls (zoom, filter, click-to-detail)
        │
        └── Server module
            ├── Local HTTP server (serves generated HTML)
            └── Playwright integration (auto-opens in browser)
```

### Step 4.3: Visualization Types

#### 4.3.1: Repo Architecture Map

**Input:** Path to any git repo
**Analysis:**
1. Glob for source files by language
2. Parse imports/requires/includes to build dependency graph
3. Detect modules/packages by directory structure
4. Identify entry points, config files, test files

**Output:** Force-directed graph with:
- Nodes = files/modules (sized by line count or import count)
- Edges = import relationships (colored by type: internal/external)
- Clusters = directories or detected module boundaries
- Click a node to see file summary, recent changes, complexity metrics

#### 4.3.2: Workflow Audit Dashboard

**Input:** Audit report (from Phase 2/3)
**Output:** Visual dashboard with:
- Friction heatmap (which projects, which time periods)
- Tool usage treemap
- Finding severity scatter plot
- Timeline of implemented improvements
- Before/after comparison (if multiple audit runs exist)

#### 4.3.3: CC Project Topology

**Input:** All CC projects, CASH Build System sync config
**Output:** Network graph showing:
- Each project as a node (sized by session count)
- Sync connections between projects
- Shared hooks/skills
- Memory coverage overlay (green = has memories, red = none)

#### 4.3.4: Session Timeline

**Input:** A conversation session (preprocessed markdown)
**Output:** Horizontal timeline showing:
- User messages as events
- Tool usage as colored bars
- Errors as red markers
- File modifications as annotations
- Duration and activity density

### Step 4.4: Technical Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Graph rendering | D3.js (force-directed) | Most flexible, handles all our viz types |
| Layout | dagre (hierarchical), D3-force (network) | Good defaults for code graphs |
| UI framework | Vanilla JS + Tailwind | No build step, fast to generate |
| Interactivity | D3 zoom/drag + click handlers | Native to D3 |
| Server | Python `http.server` or Node `http` | Zero dependency, just serve static HTML |
| Browser | Playwright `browser_navigate` | Auto-open, screenshot capability |

**No React needed** — these are generated single-file HTML documents. Keep it simple.

### Step 4.5: Skill Definition

```
/visualize <target> [--type <type>]
```

| Target | Example | Default type |
|--------|---------|-------------|
| `.` or path | `/visualize .` | repo-architecture |
| `audit` | `/visualize audit` | audit-dashboard |
| `projects` | `/visualize projects` | project-topology |
| `session <id>` | `/visualize session abc123` | session-timeline |

The skill:
1. Analyzes the target (reads files, queries qmd if needed)
2. Generates a self-contained HTML file in `visualizations/`
3. Opens it in the browser via Playwright
4. Returns the file path for future reference

### Step 4.6: Integration with QMD

The visualize tool uses qmd as its data backend for several views:

- **Audit dashboard:** Queries qmd for findings, correlations, evidence
- **Project topology:** Queries qmd for cross-project patterns
- **Session timeline:** Uses preprocessed conversation data from qmd index

This means Phase 4 fully leverages the infrastructure built in Phases 1-3.

### Phase 4 Deliverables

- [ ] `/visualize` skill definition
- [ ] Repo architecture analyzer + renderer
- [ ] Audit dashboard renderer
- [ ] Project topology renderer
- [ ] Session timeline renderer
- [ ] Playwright auto-open integration
- [ ] Generated HTML files saved to `visualizations/`

### Phase 4 Estimated Effort

| Task | Effort |
|------|--------|
| Skill scaffolding + argument parsing | 1 hour |
| Repo structure analyzer | 3-4 hours |
| D3.js graph renderer (reusable) | 3-4 hours |
| Audit dashboard renderer | 2-3 hours |
| Project topology renderer | 2 hours |
| Session timeline renderer | 2 hours |
| Playwright integration | 1 hour |
| Polish + interactivity | 2-3 hours |
| **Total** | **~16-20 hours** |

---

## Cross-Cutting Concerns

### Data Freshness

| Data Source | Update Frequency | Re-index Strategy |
|-------------|-----------------|-------------------|
| Conversation JSONLs | Every CC session | Incremental preprocess + `qmd update` before audit |
| history.jsonl | Every CC prompt | Full reprocess (small file, fast) |
| Memory files | When Claude saves | `qmd update` detects changes automatically |
| CLAUDE.md files | Manual edits | `qmd update` detects changes automatically |
| TRACES/LEARNINGS | Per CASH Build session | `qmd update` detects changes automatically |

### File Organization

```
/Users/Aakash/Claude Projects/Skills Factory/Workflow Audit/
├── docs/
│   ├── feasibility-assessment.md     # This document
│   └── implementation-plan.md        # This document
├── scripts/
│   ├── preprocess-jsonl.py           # Phase 1: JSONL → Markdown converter
│   ├── reindex.sh                    # Phase 1: One-command re-index
│   └── workflow-audit.py             # Phase 2: Audit engine
├── preprocessed/                     # Phase 1: Generated markdown from JSONLs
│   ├── history/
│   │   └── by-project/
│   ├── conversations/
│   │   └── <project-slug>/
│   ├── subagents/
│   │   └── <project-slug>/
│   └── sync/
├── reports/                          # Phase 2: Generated audit reports
│   └── audit-YYYY-MM-DD.md
├── state/                            # Phase 3: Persistent audit state
│   ├── audit-history.yaml
│   └── runs/
├── visualizations/                   # Phase 4: Generated HTML visualizations
│   └── <type>-YYYY-MM-DD.html
├── skills/                           # Phase 3+4: Skill definitions
│   ├── workflow-audit/
│   │   └── SKILL.md
│   └── visualize/
│       └── SKILL.md
└── CLAUDE.md                         # Project-level instructions
```

### Privacy and Security

- All data stays local (qmd runs entirely on-device)
- No conversation data is sent to external services (Phase 1)
- Phase 3 LLM summarization (`--deep`) uses Claude API but only sends user messages + tool summaries — no secrets, credentials, or file contents
- The `preprocessed/` directory should be `.gitignore`d if this project becomes a repo
- Audit reports may contain user corrections/frustrations — treat as personal notes

### Dependencies

| Phase | Dependencies |
|-------|-------------|
| Phase 1 | qmd (npm), Python 3.9+ (already installed) |
| Phase 2 | Phase 1 collections working, Python 3.9+ |
| Phase 3 | Phase 2 audit engine, anthropic Python SDK (for --deep mode) |
| Phase 4 | D3.js (CDN, no install), Playwright (already installed), Phase 1 qmd |

---

## Summary Timeline

| Phase | Effort | Can Start | Depends On |
|-------|--------|-----------|------------|
| Phase 1: QMD Foundation | ~4 hours | Immediately | Nothing |
| Phase 2: Workflow Audit | ~7-8 hours | After Phase 1 Step 1.5 | Phase 1 collections indexed |
| Phase 3: Audit as Skill | ~9-11 hours | After Phase 2 working | Phase 2 audit engine |
| Phase 4: Visualize Tool | ~16-20 hours | After Phase 1 (partially independent) | Phase 1 for data; Phases 2-3 for audit viz |
| **Total** | **~36-43 hours** | | |

Phase 4 is the largest because it involves both analysis (parsing repos, understanding structure) and rendering (D3.js visualizations, interactivity). It can be built incrementally — start with repo architecture (most standalone), add audit dashboard after Phase 3 is stable.

---

## Success Criteria

**Phase 1 is successful when:**
- `qmd query "what mistakes does Claude keep making?" --json` returns relevant, cross-project results
- All 9 collections are indexed with context annotations
- Re-indexing pipeline works incrementally

**Phase 2 is successful when:**
- Audit report surfaces genuine, actionable findings (not noise)
- Interactive mode successfully implements at least one improvement (e.g., creates a memory, adds a hook)
- Report can be regenerated and shows consistent results

**Phase 3 is successful when:**
- `/workflow-audit` runs end-to-end from skill invocation
- Second run shows differential results (new vs. recurring vs. resolved)
- `--deep` mode produces noticeably richer findings than structured extraction alone

**Phase 4 is successful when:**
- `/visualize .` on any repo produces a useful, navigable architecture diagram
- `/visualize audit` turns the audit report into a scannable dashboard
- Visualizations open automatically in the browser and are interactive
