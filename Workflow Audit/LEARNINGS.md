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

### 2026-03-14 - Audit-Derived (39 sessions, 180 Bash failures)

- Tried: Using paths without verifying they exist (e.g. `ls preprocessed/history/by-project/`, `head /path/to/assumed-file.jsonl`)
  Works: Always verify first: `[ -d "$dir" ] && ls "$dir"` or `[ -f "$file" ] && head "$file"`
  Context: Most common Bash failure. Claude assumes directory structures exist from prior operations or reading code. Especially bad with relative paths.
  Confirmed: 12x+

- Tried: `python script.py` on macOS
  Works: `python3 script.py` — macOS does not have `python` in PATH by default, only `python3`
  Context: Happens across multiple projects. Always use `python3` explicitly.
  Confirmed: 4x+

- Tried: `timeout 30 some-command` on macOS
  Works: `gtimeout 30 some-command` (from coreutils) — or use Bash tool's built-in `timeout` parameter instead
  Context: macOS doesn't ship GNU coreutils. The `timeout` command is `gtimeout`. Better yet, use the Bash tool's `timeout` parameter.
  Confirmed: 2x+

- Tried: Processing large JSONL files in one pass (exit code 137 = OOM/SIGKILL)
  Works: Stream with `head -n 1000` or `jq --slurp` with limits. Use `--incremental` for preprocessing.
  Context: Large conversation logs (50MB+) exhaust memory when loaded fully. Exit code 137 = kernel killed the process.
  Confirmed: 2x+

- Tried: Running multi-step scripts where intermediate files were assumed to exist
  Works: Add prerequisite checks: `for f in "$dep1" "$dep2"; do [ -f "$f" ] || { echo "Missing: $f"; exit 1; }; done`
  Context: Publish scripts, index pipelines, preprocessing chains fail when upstream files are missing. Verify inputs first.
  Confirmed: 4x+

- Tried: Destructive commands (`rm -rf`) without verifying target first
  Works: `ls "$target"` before `rm -rf "$target"`. For home directories, NEVER rm -rf without explicit user confirmation.
  Context: User had to escalate to sudo because a command wasn't working. Destructive commands need extra care per Operating Principles.
  Confirmed: 2x+
