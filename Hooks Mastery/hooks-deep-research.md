# Claude Code Hooks — Deep Research

**Date:** 2026-03-13
**Sources:** code.claude.com/docs/en/hooks, code.claude.com/docs/en/hooks-guide, Context7 /anthropics/claude-code, /websites/code_claude
**Purpose:** Authoritative reference for hook behavior, compiled from official documentation

---

## 1. Hook Types (4 types)

### 1.1 Command hooks (`type: "command"`)
- Run a shell command as a child process
- Receive event JSON on **stdin**
- Communicate results through **exit codes**, **stdout**, and **stderr**
- Shell profile is sourced (~/.zshrc or ~/.bashrc) — can interfere with JSON parsing
- Default timeout: 600 seconds (10 minutes)

### 1.2 HTTP hooks (`type: "http"`)
- POST event JSON to a URL endpoint
- Response body uses same JSON output format as command hooks
- Non-2xx responses = non-blocking error (execution continues)
- Cannot signal blocking error through status codes alone — must use JSON body
- Support `headers` with env var interpolation via `allowedEnvVars`

### 1.3 Prompt hooks (`type: "prompt"`)
- **CRITICAL: Sends prompt to a SEPARATE Claude model (Haiku by default), NOT to the main Claude**
- Single-turn evaluation only — no tool access, no file access, no multi-turn
- The LLM's only job is to return a yes/no decision as JSON
- Expected response: `{"ok": true}` or `{"ok": false, "reason": "explanation"}`
- If `ok: false`, the reason is fed back to main Claude so it can adjust
- Use `$ARGUMENTS` placeholder to inject hook input JSON into prompt
- Default timeout: 30 seconds
- Optional `model` field to use a different model

### 1.4 Agent hooks (`type: "agent"`)
- Spawn a subagent with tool access (Read, Grep, Glob)
- Can verify conditions against actual codebase state
- Same `{"ok": true/false}` response format as prompt hooks
- Default timeout: 60 seconds, up to 50 tool-use turns
- Optional `model`, `description`, `subagent_type` fields

---

## 2. Hook Events (20 events)

### Events supporting all 4 hook types (command, http, prompt, agent):
| Event | When it fires | Can block? | Matcher |
|-------|--------------|------------|---------|
| `PreToolUse` | Before a tool call executes | Yes — blocks tool call | tool_name |
| `PostToolUse` | After a tool call succeeds | No — tool already ran | tool_name |
| `PostToolUseFailure` | After a tool call fails | No — tool already failed | tool_name |
| `PermissionRequest` | When a permission dialog appears | Yes — denies permission | tool_name |
| `UserPromptSubmit` | When user submits a prompt | Yes — blocks/erases prompt | No matcher |
| `Stop` | When Claude finishes responding | Yes — continues conversation | No matcher |
| `SubagentStop` | When a subagent finishes | Yes — prevents subagent stopping | No matcher |
| `TaskCompleted` | When a task is marked completed | Yes — prevents completion | No matcher |

### Events supporting ONLY `type: "command"` hooks:
| Event | When it fires | Can block? | Matcher |
|-------|--------------|------------|---------|
| `SessionStart` | Session begins or resumes | No | source (startup/resume/clear/compact) |
| `SessionEnd` | Session ends | No | reason |
| `SubagentStart` | Subagent is spawned | No | No matcher |
| `InstructionsLoaded` | CLAUDE.md or rules file loaded | No | No matcher |
| `ConfigChange` | Config file changes during session | Yes | config type |
| `Notification` | CC sends a notification | No | notification type |
| `PreCompact` | Before context compaction | No | No matcher |
| `TeammateIdle` | Agent teammate about to go idle | Yes | No matcher |
| `WorktreeCreate` | Worktree created | Yes (non-zero fails creation) | No matcher |
| `WorktreeRemove` | Worktree removed | No | No matcher |

---

## 3. Input Schema

### Common fields (all events):
```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/.../my-project",
  "permission_mode": "default",
  "hook_event_name": "Stop"
}
```

### Event-specific fields:

**PreToolUse / PostToolUse / PostToolUseFailure / PermissionRequest:**
- `tool_name` (string) — name of the tool
- `tool_input` (object) — arguments Claude passed to the tool

**PostToolUse additionally:**
- `tool_result` (varies) — the tool's return value

**UserPromptSubmit:**
- `prompt` (string) — the user's submitted text

**Stop / SubagentStop:**
- `stop_hook_active` (boolean) — `true` when CC is already continuing from a prior Stop hook block
- `last_assistant_message` (string) — text of Claude's final response

**SubagentStop additionally:**
- `agent_id`, `agent_type`, `agent_transcript_path`

**SessionStart:**
- `source` (string) — "startup", "resume", "clear", "compact"
- `model` (string) — model identifier
- `agent_type` (string, optional) — if started with `claude --agent <name>`

---

## 4. Exit Code Behavior

### Exit 0: Success
- stdout parsed for JSON output fields
- For most events, stdout only shown in verbose mode (Ctrl+O)
- **Exceptions:** `UserPromptSubmit` and `SessionStart` — stdout added as context Claude can see

### Exit 2: Blocking Error
- stdout and JSON within it are **IGNORED**
- stderr is fed back to Claude as error message
- Effect depends on event (see table below)

### Other exit codes: Non-blocking Error
- stderr shown in verbose mode (Ctrl+O) only
- Execution continues

### Exit 2 behavior per event:
| Event | What happens |
|-------|-------------|
| PreToolUse | Blocks the tool call |
| PermissionRequest | Denies the permission |
| UserPromptSubmit | Blocks prompt, erases it |
| **Stop** | **Prevents Claude from stopping, continues conversation** |
| SubagentStop | Prevents subagent from stopping |
| TeammateIdle | Teammate continues working |
| TaskCompleted | Prevents task completion |
| ConfigChange | Blocks config change (except policy_settings) |
| PostToolUse | Shows stderr to Claude (tool already ran) |
| PostToolUseFailure | Shows stderr to Claude |
| Notification, SubagentStart, SessionStart, SessionEnd, PreCompact | Shows stderr to user only |
| WorktreeCreate | Non-zero exit fails creation |
| WorktreeRemove | Logged in debug mode only |

---

## 5. JSON Output (Command Hooks, exit 0 only)

**Must choose one approach:** exit codes alone, OR exit 0 + JSON. Not both. JSON ignored on exit 2.

**stdout must contain ONLY the JSON object.** Shell profile echo statements can interfere.

### Universal fields (all events):
| Field | Default | Description |
|-------|---------|-------------|
| `continue` | `true` | If `false`, Claude stops entirely |
| `stopReason` | none | Message shown to user when `continue: false` |
| `suppressOutput` | `false` | Hides stdout from verbose mode |
| `systemMessage` | none | Warning shown to the **user** (NOT injected to Claude) |

### Decision control patterns per event:
| Events | Pattern | Key fields |
|--------|---------|------------|
| Stop, SubagentStop, UserPromptSubmit, PostToolUse, PostToolUseFailure, ConfigChange | Top-level `decision` | `decision: "block"`, `reason` |
| PreToolUse | `hookSpecificOutput` | `permissionDecision` (allow/deny/ask), `permissionDecisionReason`, `updatedInput` |
| PermissionRequest | `hookSpecificOutput` | `decision.behavior` (allow/deny) |
| TeammateIdle, TaskCompleted | Exit code or `continue: false` | Exit 2 continues, JSON `continue: false` stops entirely |
| WorktreeCreate | stdout path | Hook prints absolute path to created worktree |
| Others | None | No decision control, side effects only |

### Stop hook decision (command type):
```json
{"decision": "block", "reason": "Tests must pass before stopping"}
```
Omit `decision` (or exit 0 with no JSON) to allow stopping.

---

## 6. Prompt Hook Response Schema

The LLM MUST respond with:
```json
{
  "ok": true | false,
  "reason": "Required when ok is false"
}
```

- `ok: true` → action proceeds (for Stop: Claude stops)
- `ok: false` → action blocked, `reason` fed to main Claude as next instruction
- If LLM response is not valid JSON → **"JSON validation failed" error**

---

## 7. Critical Anti-Pattern: Prompt Hook as Action Executor

### The mistake we made:
```json
{
  "type": "prompt",
  "prompt": "Update state.json, write to inbox, consider cross-project messaging..."
}
```

### Why it fails:
1. Prompt is sent to **Haiku** (separate model), not main Claude
2. Haiku has **no file access**, no Edit tool, no Bash
3. Haiku can't execute the instructions — it's supposed to return `{"ok": true/false}`
4. Haiku responds with natural language attempting to follow action instructions
5. CC parses response as JSON → **"JSON validation failed"**

### The correct pattern:
Prompt hooks are **evaluation gates**, not action executors.

**Correct use:** "Based on $ARGUMENTS, are all tasks complete? Respond with JSON."
**Incorrect use:** "Edit state.json, run these Bash commands, write to inbox."

For injecting instructions to make Claude DO work before stopping:
- Use **command hooks with exit 2** — stderr is fed to Claude as instructions
- Or put instructions in **CLAUDE.md** (always loaded, followed by main Claude)

---

## 8. Stop Hook Infinite Loop Prevention

When a Stop hook exits 2 (blocking), `stop_hook_active` becomes `true` on the retry. Check it:
```bash
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0  # Allow Claude to stop on retry
fi
```

**Implication for multiple Stop hooks:** `stop_hook_active` is per-stop-attempt, not per-hook. If Hook A blocks (exit 2), ALL hooks see `stop_hook_active: true` on retry — including Hook B which never got to run. This means Hook B's check may be skipped.

**Mitigation:** Use filesystem checks as primary gate, `stop_hook_active` as escape hatch only. Or merge multiple checks into a single hook.

---

## 9. Hook Handler Configuration Fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | yes | `"command"`, `"http"`, `"prompt"`, or `"agent"` |
| `timeout` | no | Seconds. Defaults: 600 (command), 30 (prompt), 60 (agent) |
| `statusMessage` | no | Custom spinner message while hook runs |
| `once` | no | If `true`, runs once per session then removed (skills only) |
| `async` | no | If `true`, runs in background, delivers systemMessage on completion |

### Command-specific:
| `command` | yes | Shell command to execute |

### HTTP-specific:
| `url` | yes | Endpoint URL |
| `headers` | no | HTTP headers (supports env var interpolation) |
| `allowedEnvVars` | no | Env vars allowed in header interpolation |

### Prompt-specific:
| `prompt` | yes | Prompt text (use `$ARGUMENTS` for input injection) |
| `model` | no | Model override (default: fast/Haiku) |

### Agent-specific:
| `prompt` | yes | Task description (use `$ARGUMENTS` for input) |
| `description` | no | Short task description |
| `subagent_type` | no | Specialized agent type (e.g., "Explore") |
| `model` | no | Model override |

---

## 10. Matcher Patterns

- Regex patterns matched against event-specific fields
- `Edit|Write` matches either tool
- `Notebook.*` matches any tool starting with Notebook
- Case-sensitive
- Events without matcher support: `UserPromptSubmit`, `Stop`, `TeammateIdle`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove`, `InstructionsLoaded`
- Adding `matcher` to unsupported events: silently ignored
- MCP tools can be matched with full tool name format

---

## 11. Async Hooks

- Set `async: true` in hook config
- Hook starts and Claude continues immediately
- On completion, `systemMessage` or `additionalContext` delivered on next conversation turn
- Useful for background tasks (test suites, linting)

---

## 12. Hook Locations (precedence)

| Location | Scope | Shareable |
|----------|-------|-----------|
| `~/.claude/settings.json` | All projects | No |
| `.claude/settings.json` | Single project | Yes (committable) |
| `.claude/settings.local.json` | Single project | No (gitignored) |
| Managed policy settings | Organization-wide | Admin-controlled |
| Plugin `hooks/hooks.json` | When plugin enabled | Bundled with plugin |
| Skill/agent frontmatter | While skill/agent active | Defined in component |

---

## 13. Troubleshooting

### "JSON validation failed"
**Cause:** Shell profile (~/.zshrc) contains unconditional `echo` statements that output text before the hook's JSON.
**Fix:** Wrap echos in interactive-only guard:
```bash
if [[ $- == *i* ]]; then
  echo "Shell ready"
fi
```

**Also caused by:** Prompt hooks where the LLM returns natural language instead of `{"ok": true/false}` JSON. This happens when the prompt asks the LLM to take actions instead of making a yes/no evaluation.

### "Stop hook runs forever"
**Cause:** Stop hook doesn't check `stop_hook_active`.
**Fix:** Check `stop_hook_active` and exit 0 if true.

### "Hook not firing"
- Check `/hooks` menu for correct event
- Verify matcher pattern (case-sensitive)
- Confirm correct event type (Pre vs Post)

### Debug
- `claude --debug` for execution details
- `Ctrl+O` for verbose mode in transcript
