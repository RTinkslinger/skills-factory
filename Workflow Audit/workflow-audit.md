---
description: >
  Run a 10-dimension audit of your Claude Code workflow. Analyzes conversation
  logs for friction points, tool failures, corrections, trial-and-error patterns,
  and assumptions. Generates actionable reports with severity-ranked findings and
  differential analysis between runs. Use when the user says "audit my workflow",
  "run workflow audit", "check for improvements", "analyze my CC usage".
---

# /workflow-audit

**Usage:** `/workflow-audit [--no-llm] [--reindex]`

**Project directory:** /Users/Aakash/Claude Projects/Skills Factory/Workflow Audit
**Scripts:** /Users/Aakash/Claude Projects/Skills Factory/Workflow Audit/scripts/
**Reports:** /Users/Aakash/Claude Projects/Skills Factory/Workflow Audit/reports/
**State:** /Users/Aakash/Claude Projects/Skills Factory/Workflow Audit/state/

## Flags

- `--no-llm` — Skip LLM classification, signal-based detection only (faster, free)
- `--reindex` — Re-index qmd collections before audit (picks up new conversation data)

---

## Step 1: Check Prerequisites

Verify qmd is installed and indexed:

```bash
qmd status 2>/dev/null | head -5
```

If qmd shows 0 documents or isn't installed, tell the user to run setup first:
```bash
cd "/Users/Aakash/Claude Projects/Skills Factory/Workflow Audit"
./scripts/reindex.sh
```

## Step 2: Check Audit State

Read the audit history to determine if this is a first run or differential run:

```bash
cat "/Users/Aakash/Claude Projects/Skills Factory/Workflow Audit/state/audit-history.json" 2>/dev/null
```

If history exists, note the last run date and finding count for comparison.

## Step 3: Re-index (if requested or stale)

If `--reindex` was passed, or if the user hasn't re-indexed in the current session:

```bash
cd "/Users/Aakash/Claude Projects/Skills Factory/Workflow Audit"
./scripts/reindex.sh --incremental
```

This preprocesses any new conversation JSONLs and updates the qmd index.

## Step 4: Run the Audit

```bash
cd "/Users/Aakash/Claude Projects/Skills Factory/Workflow Audit"
python3 scripts/workflow-audit.py --report-only
```

If `--no-llm` was passed by the user, add `--no-llm` to the command.

The audit runs 10 dimensions:
1. Friction Points (corrections, frustration, unmemorized corrections)
2. Tool Usage Patterns (failure rates, unused tools)
3. Skill Gaps
4. Cross-Project Patterns (error distribution)
5. Memory Health (coverage, staleness, feedback gaps)
6. Configuration Drift
7. Automation Opportunities
8. Repeated Failure Patterns (same errors across sessions)
9. Trial-and-Error / Tool Amnesia (Claude forgetting how tools work)
10. Assumptions Without Verification (Edit without prior Read)

## Step 5: Read and Present the Report

Read the generated report:

```bash
cat "/Users/Aakash/Claude Projects/Skills Factory/Workflow Audit/reports/audit-$(date +%Y-%m-%d).md"
```

Present to the user:
1. **Executive Summary** — critical and high severity findings first
2. **Differential Analysis** (if previous run exists) — new vs recurring vs resolved
3. **Top 5 findings** with evidence and suggested actions

## Step 6: Interactive Follow-up

For each finding (highest severity first), ask the user:

- **Implement now** — Execute the suggested action:
  - Create a feedback memory
  - Update CLAUDE.md with a new rule
  - Add a pattern to LEARNINGS.md
  - Create a hook
- **Save for later** — Note it in the backlog
- **Dismiss** — Skip, not relevant
- **Discuss** — Provide more context before deciding

Track decisions. When implementing, actually make the changes (create memory files,
edit CLAUDE.md, etc.) — don't just log them.

## Step 7: Save Run State

The audit engine saves state automatically to `state/audit-history.json`.
Verify it was saved:

```bash
cat "/Users/Aakash/Claude Projects/Skills Factory/Workflow Audit/state/audit-history.json" | python3 -c "import sys,json; h=json.load(sys.stdin); print(f'Run #{h[\"run_count\"]} saved. Last: {h[\"last_run\"]}')"
```

## Step 8: Suggest Next Audit

Based on usage volume:
- Heavy usage (50+ prompts/day): suggest weekly
- Normal usage: suggest bi-weekly
- Light usage: suggest monthly

Tell the user when to run `/workflow-audit` next.
