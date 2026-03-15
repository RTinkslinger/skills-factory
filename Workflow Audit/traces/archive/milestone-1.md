# Milestone 1: QMD Foundation + Audit Engine v2 + Skill
**Iterations:** 1-3 | **Dates:** 2026-03-14

## Summary
Built the complete QMD-based CC workflow analysis system from scratch: JSONL preprocessing pipeline (4 processors), qmd indexing (9 collections, 469 docs, 1237 vectors), 10-dimension audit engine with LLM-as-judge classification, behavioral signal detection (replacing broken regex), and /workflow-audit skill with state persistence and differential auditing.

## Key Decisions
- Python 3.9 compat (Optional[X] not X | None)
- CLI mode for qmd (not MCP daemon) — 8GB RAM constraint
- Conversation JSONL timestamps are ISO strings, not ms ints — parse_timestamp() normalizer
- Subagent JSONLs nested in session dirs — glob */subagents/agent-*.jsonl
- v1 regex correction detection was catastrophically broken (100/115 sessions) → replaced with signal-based (16/117)
- Tool results are in user entries with is_error field, not progress entries
- 3 new audit dimensions from user feedback: Repeated Failures, Trial-and-Error, Assumptions
- LLM-as-judge (Haiku) is default, ~$0.35/run
- API key at ~/.anthropic/api_key, global memory reference
- Differential auditing via finding_types comparison between runs

## Iteration Details

### Iteration 1 - 2026-03-14
**Phase:** Phase 1: QMD Foundation
**Focus:** Project setup, CBS, preprocessing pipeline, collections, embedding
**Changes:** preprocess-jsonl.py, reindex.sh, CBS hooks, CLAUDE.md, sync

### Iteration 2 - 2026-03-14
**Phase:** Phase 2: Workflow Audit v2
**Focus:** Signal-based audit engine replacing broken regex
**Changes:** preprocess-jsonl.py v2, workflow-audit.py v2, research/audit-system-redesign.md

### Iteration 3 - 2026-03-14
**Phase:** Phase 3: Audit as Skill
**Focus:** /workflow-audit skill, differential auditing, API key setup
**Changes:** skills/workflow-audit/SKILL.md, state persistence, LLM default
