# LEARNINGS.md

Trial-and-error patterns discovered during Claude Code sessions.
Patterns confirmed 2+ times graduate to CLAUDE.md during milestone compaction.

## Active Patterns

### 2026-03-15 - Sprint 1
- Tried: `pip3 install browser-use` (system pip3, /usr/bin/pip3) — failed: pip version 21.2.4 too old, can't find package
  Then tried: `/opt/homebrew/bin/pip3 install` — failed: PEP 668 externally-managed-environment error (Python 3.14 via Homebrew)
  Works: `brew install uv` then `uv venv /tmp/phase0-eval && source /tmp/phase0-eval/bin/activate && uv pip install browser-use browser_cookie3`
  Context: Homebrew Python 3.14 is externally managed. Always use uv + venv for pip installs, never system pip.
  Confirmed: 1x
