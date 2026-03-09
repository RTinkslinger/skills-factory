# LEARNINGS.md

Trial-and-error patterns discovered during Claude Code sessions.
Patterns confirmed 2+ times graduate to CLAUDE.md during milestone compaction.

## Active Patterns

### 2026-03-06 - Sprint 1
- Tried: npm install on a large Next.js project with <200MB free disk space — fails with ENOSPC, and once disk is fully exhausted, even Bash tool stops working (can't write its own output file to /private/tmp)
  Works: Check disk space with `df -h /` BEFORE cloning/installing large projects. Need ~2GB free minimum for a Next.js + shadcn project.
  Context: Scaffolding test projects for validation. The Bash tool itself needs writable /private/tmp.
  Confirmed: 1x
