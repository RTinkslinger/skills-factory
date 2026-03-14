---
description: Use when creating, debugging, or modifying Claude Code hooks. Provides authoritative reference for all hook types, events, input/output schemas, and common anti-patterns. Invoke before writing any hook configuration or script.
---

# Hooks Mastery

Authoritative guide for Claude Code hooks. Read before creating or debugging any hook.

## The 4 Hook Types

| Type | What it does | Has file access? | Response format |
|------|-------------|-------------------|----------------|
| `command` | Runs a shell script | Yes (full filesystem) | Exit code + stdout/stderr |
| `http` | POSTs to a URL | No (remote endpoint) | HTTP response body (JSON) |
| `prompt` | Single-turn LLM call (Haiku default) | **No** | `{"ok": true/false, "reason": "..."}` |
| `agent` | Multi-turn subagent with tools | Yes (Read, Grep, Glob) | `{"ok": true/false, "reason": "..."}` |

### CRITICAL: Prompt hooks run on a SEPARATE model

Prompt hooks do NOT inject a prompt into the main Claude conversation. They send the prompt to a fast model (Haiku by default) for **single-turn evaluation**. Haiku returns `{"ok": true}` or `{"ok": false, "reason": "..."}`. Haiku cannot read files, run tools, or execute actions.

**Correct use:** Evaluation gates — "Is this safe?", "Are all tasks complete?", "Should this proceed?"
**Incorrect use:** Action instructions — "Edit this file", "Run this command", "Update this JSON"

If Haiku can't answer the question from the context alone, use an `agent` hook instead (has tool access).

## Exit Code Behavior (Command Hooks)

| Exit | Meaning | stdout | stderr |
|------|---------|--------|--------|
| 0 | Success | Parsed for JSON. Most events: verbose only. SessionStart/UserPromptSubmit: visible to Claude | Ignored |
| 2 | Block | **Ignored** (including any JSON) | Fed to Claude as feedback |
| Other | Non-blocking error | Ignored | Verbose mode only |

**Choose one approach per hook:** exit codes alone, OR exit 0 + JSON. Never both. JSON is ignored on exit 2.

## Decision Control Patterns

### Stop / SubagentStop / PostToolUse / PostToolUseFailure / UserPromptSubmit / ConfigChange:
```json
{"decision": "block", "reason": "Explanation for Claude"}
```
Omit `decision` to allow the action.

### PreToolUse:
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "Why",
    "updatedInput": {"field": "modified_value"}
  }
}
```

### PermissionRequest:
```json
{
  "hookSpecificOutput": {
    "decision": {"behavior": "allow|deny"}
  }
}
```

## Stop Hook Input

```json
{
  "session_id": "abc123",
  "transcript_path": "...",
  "cwd": "/Users/.../project",
  "permission_mode": "default",
  "hook_event_name": "Stop",
  "stop_hook_active": true,
  "last_assistant_message": "I've completed the refactoring..."
}
```

`stop_hook_active` is `true` when a previous Stop hook blocked and Claude is retrying. **You must check this to prevent infinite loops.**

## Stop Hook Patterns

### Pattern 1: Filesystem gate (command, recommended)
Check if required pre-stop work was done. Block if not.
```bash
#!/bin/bash
INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
cd "$CWD" 2>/dev/null || exit 0

# Filesystem check first (primary gate)
NOW=$(date +%s)
MOD=$(stat -f %m "target-file" 2>/dev/null || echo 0)
if [ $((NOW - MOD)) -lt 300 ]; then
  exit 0  # Recently updated, allow stop
fi

# Escape hatch: don't block on retry
STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_ACTIVE" = "true" ]; then
  exit 0
fi

# First attempt, work not done — block with instructions
echo "Do X, Y, Z before stopping" >&2
exit 2
```

### Pattern 2: Evaluation gate (prompt)
Ask Haiku if work looks complete based on conversation context.
```json
{
  "type": "prompt",
  "prompt": "Based on the conversation in $ARGUMENTS, check if Claude has completed all user-requested tasks. Respond with {\"ok\": true} if complete, or {\"ok\": false, \"reason\": \"what remains\"} if not.",
  "timeout": 30
}
```

### Pattern 3: Codebase verification gate (agent)
Spawn a subagent to verify conditions against actual files.
```json
{
  "type": "agent",
  "prompt": "Verify all unit tests pass. Run the test suite. $ARGUMENTS",
  "timeout": 120
}
```

## Anti-Pattern: Prompt Hook as Action Executor

```json
{
  "type": "prompt",
  "prompt": "Update state.json, write to inbox, run these bash commands..."
}
```

**This WILL produce "JSON validation failed" every time.** Haiku receives action instructions it cannot execute, responds with natural language, CC fails to parse as JSON.

**Fix options:**
1. Move instructions to **CLAUDE.md** (main Claude always sees them)
2. Use **command hook + exit 2** to inject instructions via stderr
3. Use **agent hook** if file verification is needed

## Multi-Hook Coordination (Stop Event)

**Problem:** `stop_hook_active` is per-stop-attempt, not per-hook. If Hook A (Group 1) blocks, ALL hooks see `stop_hook_active: true` on retry — Hook B (Group 2) may never run its check.

**Solutions:**
1. **Merge related checks** into a single hook that provides all instructions in one exit-2 message
2. **Use CLAUDE.md as primary instruction source** + hooks as enforcement backup. If Hook A blocks but Hook B is skipped on retry, CLAUDE.md still told Claude what to do
3. **Filesystem checks first, escape hatch second.** If the work was done (regardless of which hook requested it), the filesystem check passes

## Universal JSON Output Fields

Available on exit 0 for all events:

| Field | Description |
|-------|-------------|
| `continue` | If `false`, Claude stops entirely (takes precedence over all other fields) |
| `stopReason` | Shown to user when `continue: false` |
| `suppressOutput` | Hides stdout from verbose mode |
| `systemMessage` | Warning shown to the **user** (not injected to Claude's context) |

## Async Hooks

Set `"async": true` to run in background. Claude continues immediately. On completion, `systemMessage` or `additionalContext` from JSON output is delivered on Claude's next conversation turn.

```json
{
  "type": "command",
  "command": "run-tests.sh",
  "async": true,
  "timeout": 120
}
```

## Checklist: Before Writing a Hook

1. [ ] **Right event?** Pre vs Post vs Stop — match the lifecycle point
2. [ ] **Right type?** Command for actions/filesystem checks. Prompt for judgment calls. Agent for file-based verification
3. [ ] **Prompt hook?** Verify it's an evaluation question (yes/no), NOT action instructions
4. [ ] **Exit codes correct?** 0=allow, 2=block+feedback, other=non-blocking
5. [ ] **stdout clean?** No shell profile echo leaking. JSON only on exit 0
6. [ ] **Stop hook?** Check `stop_hook_active` to prevent infinite loops
7. [ ] **Matcher needed?** Only tool events support matchers. Stop, UserPromptSubmit don't
8. [ ] **Timeout set?** Defaults: 600s command, 30s prompt, 60s agent

## Quick Reference: Event Support Matrix

| Event | command | http | prompt | agent | Can block? |
|-------|---------|------|--------|-------|------------|
| PreToolUse | Y | Y | Y | Y | Yes |
| PostToolUse | Y | Y | Y | Y | No |
| PostToolUseFailure | Y | Y | Y | Y | No |
| PermissionRequest | Y | Y | Y | Y | Yes |
| UserPromptSubmit | Y | Y | Y | Y | Yes |
| Stop | Y | Y | Y | Y | Yes |
| SubagentStop | Y | Y | Y | Y | Yes |
| TaskCompleted | Y | Y | Y | Y | Yes |
| SessionStart | Y | - | - | - | No |
| SessionEnd | Y | - | - | - | No |
| ConfigChange | Y | - | - | - | Yes |
| Notification | Y | - | - | - | No |
| PreCompact | Y | - | - | - | No |
| SubagentStart | Y | - | - | - | No |
| TeammateIdle | Y | - | - | - | Yes |
| WorktreeCreate | Y | - | - | - | Yes |
| WorktreeRemove | Y | - | - | - | No |
| InstructionsLoaded | Y | - | - | - | No |
