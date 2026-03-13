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
