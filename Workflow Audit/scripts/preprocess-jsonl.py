#!/usr/bin/env python3
"""
Preprocess CC JSONL data into searchable markdown for qmd indexing.

v2: Signal-based detection replaces regex. Proper JSONL schema handling.
    --deep mode uses Claude API for LLM-as-judge classification.

Processors:
  1. history.jsonl → per-project prompt files
  2. Conversation JSONLs → per-session summary files (with behavioral signals)
  3. Subagent JSONLs → per-subagent summary files
  4. Sync inbox JSONLs → single cross-project messages file

Usage:
  python3 preprocess-jsonl.py                    # Full run
  python3 preprocess-jsonl.py --incremental      # Only new/changed files
  python3 preprocess-jsonl.py --deep             # Use LLM for message classification
  python3 preprocess-jsonl.py --only conversations
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Paths
CLAUDE_DIR = Path.home() / ".claude"
HISTORY_FILE = CLAUDE_DIR / "history.jsonl"
PROJECTS_DIR = CLAUDE_DIR / "projects"
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "preprocessed"
STATE_FILE = PROJECT_ROOT / "state" / "preprocess-state.json"


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def slugify(path: str) -> str:
    """Convert a project path to a filesystem-safe slug."""
    home = str(Path.home())
    if path.startswith(home):
        path = path[len(home):]
    path = path.strip("/")
    slug = re.sub(r"[/\\]", "--", path)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-zA-Z0-9_\-.]", "", slug)
    return slug.lower() or "home"


def ts_to_date(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def ts_to_time(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%H:%M")


def parse_timestamp(ts: Any) -> Optional[float]:
    """Normalize timestamp (ms int or ISO string) to epoch seconds."""
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return ts / 1000.0 if ts > 1e12 else float(ts)
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.timestamp()
        except ValueError:
            return None
    return None


def epoch_to_date(epoch_sec: float) -> str:
    return datetime.fromtimestamp(epoch_sec, tz=timezone.utc).strftime("%Y-%m-%d")


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"processed_files": {}, "last_run": None}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2))


def file_changed(filepath: Path, state: dict) -> bool:
    key = str(filepath)
    current_mtime = filepath.stat().st_mtime
    current_size = filepath.stat().st_size
    prev = state["processed_files"].get(key, {})
    return prev.get("mtime") != current_mtime or prev.get("size") != current_size


def mark_processed(filepath: Path, state: dict) -> None:
    key = str(filepath)
    state["processed_files"][key] = {
        "mtime": filepath.stat().st_mtime,
        "size": filepath.stat().st_size,
    }


# ---------------------------------------------------------------------------
# Tight Correction Detection (replaces broken regex)
# ---------------------------------------------------------------------------

# Only match when the FULL pattern indicates a correction, not just a word
CORRECTION_STARTERS = re.compile(
    r"^(?:"
    r"no[,!.\s]+(?:that'?s|don'?t|not|i\s|we\s|stop|wrong|instead)"  # "no, don't..." not just "no"
    r"|don'?t\s+(?:do|change|modify|touch|delete|assume|add|remove|mock|skip)"  # "don't assume"
    r"|stop[!.\s]"  # "stop!" not "stop and think"
    r"|pause[!.\s]"  # "pause!" not "pause the video"
    r"|that'?s\s+(?:not|wrong|incorrect)"  # "that's not what I meant"
    r"|i\s+(?:said|meant|asked|wanted)\s"  # "I said X not Y"
    r"|wrong[!.,\s]"  # "wrong!" or "wrong, it should be"
    r"|not\s+that[!.,\s]"  # "not that!"
    r"|instead[,\s]+(?:do|use|try)"  # "instead, do X"
    r"|undo\s"  # "undo that"
    r"|revert\s"  # "revert that"
    r")",
    re.IGNORECASE,
)

# Frustration: only match genuine frustration, not technical acronyms
FRUSTRATION_SIGNALS = re.compile(
    r"(?:"
    r"!{3,}"  # 3+ exclamation marks (not just 1-2)
    r"|(?:fuck|shit|damn|wtf|ffs|omfg|jfc)"  # profanity
    r"|(?:^|\s)(?:UGH|ARGH|SIGH|FFS|WTF)(?:\s|$|!)"  # frustration words in caps (whole word)
    r")",
    re.IGNORECASE,
)


def is_correction(text: str) -> bool:
    """Check if a user message is a correction/override. Much tighter than v1."""
    return bool(CORRECTION_STARTERS.match(text.strip()))


def is_frustration(text: str) -> bool:
    """Check if a message shows genuine frustration (not just technical caps)."""
    return bool(FRUSTRATION_SIGNALS.search(text))


# ---------------------------------------------------------------------------
# LLM-as-Judge (--deep mode)
# ---------------------------------------------------------------------------


def classify_messages_with_llm(
    user_messages: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """Use Claude Haiku to classify each user message.

    Returns list of dicts with 'text', 'classification', 'confidence'.
    Classifications: instruction, correction, frustration, acknowledgment, clarification
    """
    # Auto-load API key from ~/.anthropic/api_key if not in env
    key_file = Path.home() / ".anthropic" / "api_key"
    if not os.environ.get("ANTHROPIC_API_KEY") and key_file.exists():
        os.environ["ANTHROPIC_API_KEY"] = key_file.read_text().strip()

    try:
        import anthropic
    except ImportError:
        print("  WARN: anthropic SDK not installed, skipping LLM classification")
        return []

    if not user_messages:
        return []

    # Batch messages (max 30 per API call to stay within limits)
    batch_size = 30
    all_results = []

    client = anthropic.Anthropic()

    for i in range(0, len(user_messages), batch_size):
        batch = user_messages[i : i + batch_size]

        # Build the prompt
        msg_list = "\n".join(
            f"[{j+1}] {m['text'][:300]}" for j, m in enumerate(batch)
        )

        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Classify each user message in an AI coding assistant conversation.

Classifications:
- instruction: Normal task request or instruction
- correction: User is correcting the AI's behavior, pointing out errors, or overriding a decision
- frustration: User expresses frustration, anger, or strong dissatisfaction with the AI
- acknowledgment: User acknowledges, approves, or accepts (e.g., "looks good", "ship it")
- clarification: User provides additional context or answers the AI's question

Return JSON array with format: [{{"idx": 1, "class": "instruction"}}, ...]
Only return the JSON array, nothing else.

Messages:
{msg_list}""",
                    }
                ],
            )

            # Parse response
            text = response.content[0].text.strip()
            # Find JSON array in response
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                classifications = json.loads(text[start:end])
                for cls in classifications:
                    idx = cls.get("idx", 0) - 1
                    if 0 <= idx < len(batch):
                        batch[idx]["classification"] = cls.get("class", "instruction")

        except Exception as e:
            print(f"  WARN: LLM classification failed: {e}")

        all_results.extend(batch)

    return all_results


# ---------------------------------------------------------------------------
# Processor 1: history.jsonl (unchanged from v1)
# ---------------------------------------------------------------------------


def process_history(incremental: bool = False, state: Optional[dict] = None) -> int:
    if not HISTORY_FILE.exists():
        print("  SKIP: history.jsonl not found")
        return 0
    if incremental and state and not file_changed(HISTORY_FILE, state):
        print("  SKIP: history.jsonl unchanged")
        return 0

    out_dir = OUTPUT_DIR / "history" / "by-project"
    out_dir.mkdir(parents=True, exist_ok=True)

    by_project: Dict[str, List[dict]] = defaultdict(list)
    with open(HISTORY_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            project = entry.get("project", "unknown")
            by_project[project].append(entry)

    count = 0
    for project_path, entries in by_project.items():
        slug = slugify(project_path)
        entries.sort(key=lambda e: e.get("timestamp", 0))
        first_ts = entries[0].get("timestamp", 0)
        last_ts = entries[-1].get("timestamp", 0)
        date_range = f"{ts_to_date(first_ts)} to {ts_to_date(last_ts)}"
        display_name = project_path.replace(str(Path.home()), "~")

        lines = [
            "---", "source: history.jsonl",
            f"project: {display_name}",
            f"generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
            f"prompt_count: {len(entries)}",
            f"date_range: {date_range}",
            "---", "",
            f"# User Prompts: {display_name}", "",
        ]

        current_date = None
        for entry in entries:
            ts = entry.get("timestamp", 0)
            date_str = ts_to_date(ts)
            time_str = ts_to_time(ts)
            session_id = entry.get("sessionId", "unknown")[:8]
            display = entry.get("display", "").strip()
            if not display:
                continue
            if date_str != current_date:
                current_date = date_str
                lines.extend([f"## {date_str}", ""])
            lines.append(f"### Session {session_id} ({time_str})")
            for prompt_line in display.split("\n"):
                lines.append(f"> {prompt_line}")
            lines.append("")

        outfile = out_dir / f"{slug}.md"
        outfile.write_text("\n".join(lines))
        count += 1

    if state:
        mark_processed(HISTORY_FILE, state)
    print(f"  history.jsonl → {count} project files")
    return count


# ---------------------------------------------------------------------------
# Processor 2: Conversation JSONLs (v2 — signal-based)
# ---------------------------------------------------------------------------


def parse_conversation_jsonl(filepath: Path) -> Dict[str, Any]:
    """Parse a conversation JSONL into structured data with behavioral signals.

    Properly handles the CC JSONL schema:
    - user entries with str content = user text messages
    - user entries with list content = tool results (may have is_error)
    - assistant entries with list content = tool uses (tool_use blocks)
    """
    data = {
        "user_messages": [],        # text messages from user
        "tool_uses": [],            # {name, input, timestamp}
        "tool_results": [],         # {name, is_error, content_snippet, timestamp}
        "files_read": set(),        # files Read during session
        "files_written": set(),     # files Written/Edited during session
        "timestamps": [],
        "entry_count": 0,
        "project": "",
    }

    pending_tool_name = None  # Track tool_use → tool_result pairing

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            data["entry_count"] += 1
            ts = parse_timestamp(entry.get("timestamp"))
            if ts:
                data["timestamps"].append(ts)

            entry_type = entry.get("type", "")

            # Extract project from any entry
            if not data["project"]:
                cwd = entry.get("cwd", "")
                if cwd:
                    data["project"] = cwd

            if entry_type == "user":
                msg = entry.get("message", {})
                if not isinstance(msg, dict):
                    continue
                content = msg.get("content", "")

                if isinstance(content, str) and content.strip():
                    # User text message
                    user_type = entry.get("userType", "")
                    if user_type != "tool_result":
                        data["user_messages"].append({
                            "text": content.strip(),
                            "timestamp": ts,
                        })

                elif isinstance(content, list):
                    # Tool results
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") == "tool_result":
                            is_error = block.get("is_error", False)
                            result_content = ""
                            bc = block.get("content", "")
                            if isinstance(bc, str):
                                result_content = bc[:300]
                            elif isinstance(bc, list):
                                for sub in bc:
                                    if isinstance(sub, dict) and sub.get("type") == "text":
                                        result_content = sub.get("text", "")[:300]
                                        break

                            data["tool_results"].append({
                                "name": pending_tool_name or "unknown",
                                "is_error": is_error,
                                "content": result_content,
                                "timestamp": ts,
                            })
                            pending_tool_name = None

            elif entry_type == "assistant":
                msg = entry.get("message", {})
                if not isinstance(msg, dict):
                    continue
                content = msg.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") == "tool_use":
                            tool_name = block.get("name", "")
                            tool_input = block.get("input", {})
                            pending_tool_name = tool_name

                            data["tool_uses"].append({
                                "name": tool_name,
                                "input": tool_input if isinstance(tool_input, dict) else {},
                                "timestamp": ts,
                            })

                            # Track file reads/writes
                            if isinstance(tool_input, dict):
                                fp = (tool_input.get("file_path")
                                      or tool_input.get("filePath", ""))
                                if fp:
                                    if tool_name == "Read":
                                        data["files_read"].add(fp)
                                    elif tool_name in ("Write", "Edit"):
                                        data["files_written"].add(fp)

    return data


def detect_signals(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Detect behavioral signals from parsed conversation data.

    Signals detected:
    1. Corrections (tight pattern matching)
    2. Frustration (genuine, not acronyms)
    3. Tool failure sequences (trial-and-error)
    4. Assumptions (Write/Edit without prior Read)
    5. Error density
    """
    signals = {
        "corrections": [],
        "frustrations": [],
        "tool_failure_sequences": [],
        "assumptions_without_read": [],
        "error_count": 0,
        "error_details": [],
        "tool_counts": Counter(),
        "tool_failures": Counter(),
        "files_modified": Counter(),
    }

    # 1. Corrections and frustrations from user messages
    for msg in parsed["user_messages"]:
        text = msg["text"]
        if is_correction(text):
            signals["corrections"].append(text[:200])
        if is_frustration(text):
            signals["frustrations"].append(text[:200])

    # 2. Tool usage stats and error tracking
    for tr in parsed["tool_results"]:
        signals["tool_counts"][tr["name"]] += 1
        if tr["is_error"]:
            signals["error_count"] += 1
            signals["tool_failures"][tr["name"]] += 1
            signals["error_details"].append({
                "tool": tr["name"],
                "content": tr["content"][:150],
            })

    # 3. Tool failure sequences (trial-and-error detection)
    # Look for: same tool fails 2+ times then succeeds
    results = parsed["tool_results"]
    i = 0
    while i < len(results):
        if results[i]["is_error"]:
            tool = results[i]["name"]
            fail_count = 0
            j = i
            while j < len(results) and results[j]["name"] == tool and results[j]["is_error"]:
                fail_count += 1
                j += 1
            # Check if next use of same tool succeeded
            succeeded = (j < len(results)
                         and results[j]["name"] == tool
                         and not results[j]["is_error"])
            if fail_count >= 2:
                signals["tool_failure_sequences"].append({
                    "tool": tool,
                    "failures": fail_count,
                    "eventually_succeeded": succeeded,
                    "first_error": results[i]["content"][:100],
                })
            i = j if j > i else i + 1
        else:
            i += 1

    # 4. Assumptions without verification
    # Files that were Written/Edited without a preceding Read
    files_read = parsed["files_read"]
    files_written = parsed["files_written"]
    for fp in files_written:
        if fp not in files_read:
            # Check it's not a new file creation (Write is OK for new files)
            # Heuristic: if the file was Edited (not just Written), it should have been Read
            was_edited = any(
                tu["name"] == "Edit" and tu["input"].get("file_path") == fp
                for tu in parsed["tool_uses"]
            )
            if was_edited:
                short = fp.replace(str(Path.home()), "~")
                signals["assumptions_without_read"].append(short)

    # 5. File modification counts
    for tu in parsed["tool_uses"]:
        if tu["name"] in ("Edit", "Write"):
            fp = tu["input"].get("file_path", "")
            if fp:
                short = fp.replace(str(Path.home()), "~")
                signals["files_modified"][short] += 1

    return signals


def process_conversation(
    filepath: Path, out_dir: Path, deep: bool = False
) -> bool:
    """Process a single conversation JSONL into a markdown file with signals."""
    session_id = filepath.stem
    outfile = out_dir / f"{session_id}.md"

    parsed = parse_conversation_jsonl(filepath)
    if parsed["entry_count"] == 0:
        return False

    signals = detect_signals(parsed)

    # LLM classification in deep mode
    llm_corrections = []
    llm_frustrations = []
    if deep and parsed["user_messages"]:
        classified = classify_messages_with_llm(parsed["user_messages"])
        for msg in classified:
            cls = msg.get("classification", "instruction")
            if cls == "correction":
                llm_corrections.append(msg["text"][:200])
            elif cls == "frustration":
                llm_frustrations.append(msg["text"][:200])

    # Compute duration
    timestamps = parsed["timestamps"]
    duration_str = "unknown"
    if len(timestamps) >= 2:
        duration_min = (max(timestamps) - min(timestamps)) / 60
        if duration_min < 60:
            duration_str = f"~{int(duration_min)}min"
        else:
            duration_str = f"~{duration_min / 60:.1f}hr"

    session_date = epoch_to_date(min(timestamps)) if timestamps else "unknown"
    project = parsed["project"] or "unknown"
    display_project = project.replace(str(Path.home()), "~")
    total_tool_uses = sum(signals["tool_counts"].values())

    # Use LLM results if available, otherwise use signal-based
    final_corrections = llm_corrections if llm_corrections else signals["corrections"]
    final_frustrations = llm_frustrations if llm_frustrations else signals["frustrations"]

    # Build markdown
    lines = [
        "---",
        "source: conversation",
        f"session_id: {session_id}",
        f"project: {display_project}",
        f"date: {session_date}",
        f"entry_count: {parsed['entry_count']}",
        f"user_messages: {len(parsed['user_messages'])}",
        f"tool_uses: {total_tool_uses}",
        f"errors: {signals['error_count']}",
        f"corrections: {len(final_corrections)}",
        f"frustrations: {len(final_frustrations)}",
        f"trial_and_error_sequences: {len(signals['tool_failure_sequences'])}",
        f"assumptions_without_read: {len(signals['assumptions_without_read'])}",
        f"duration_estimate: {duration_str}",
        f"classification_mode: {'llm' if deep and llm_corrections else 'signal'}",
        "---",
        "",
        f"# Session: {display_project} — {session_date}",
        "",
    ]

    # User messages
    if parsed["user_messages"]:
        lines.append("## User Messages (chronological)")
        lines.append("")
        for msg in parsed["user_messages"]:
            text = msg["text"].strip()
            if len(text) > 500:
                text = text[:500] + "..."
            for msg_line in text.split("\n"):
                lines.append(f"> {msg_line}")
            lines.append("")

    # Tool usage summary
    if signals["tool_counts"]:
        lines.append("## Tool Usage Summary")
        lines.append("")
        lines.append("| Tool | Count | Failures | Notes |")
        lines.append("|------|-------|----------|-------|")
        for tool, count in signals["tool_counts"].most_common(15):
            fails = signals["tool_failures"].get(tool, 0)
            notes = ""
            relevant = {f: c for f, c in signals["files_modified"].items() if c > 1}
            if tool in ("Edit", "Write") and relevant:
                top_file = max(relevant, key=relevant.get)
                notes = f"Most edited: {top_file}"
            lines.append(f"| {tool} | {count} | {fails} | {notes} |")
        lines.append("")

    # Files modified
    if signals["files_modified"]:
        lines.append("## Files Modified")
        lines.append("")
        for fp, count in signals["files_modified"].most_common(15):
            lines.append(f"- `{fp}` ({count} edits)")
        lines.append("")

    # Errors
    if signals["error_details"]:
        lines.append("## Errors Encountered")
        lines.append("")
        for i, err in enumerate(signals["error_details"][:20], 1):
            lines.append(f"{i}. [{err['tool']}] {err['content'][:150]}")
        if len(signals["error_details"]) > 20:
            lines.append(f"... and {len(signals['error_details']) - 20} more")
        lines.append("")

    # Behavioral Signals section
    has_signals = (final_corrections or final_frustrations
                   or signals["tool_failure_sequences"]
                   or signals["assumptions_without_read"])

    if has_signals:
        lines.append("## Behavioral Signals")
        lines.append("")

        if final_corrections:
            mode_label = "(LLM-classified)" if deep and llm_corrections else "(pattern-detected)"
            lines.append(f"### Corrections {mode_label}")
            lines.append("")
            for corr in final_corrections[:10]:
                lines.append(f"> {corr}")
                lines.append("")

        if final_frustrations:
            lines.append("### Frustration")
            lines.append("")
            for frust in final_frustrations[:5]:
                lines.append(f"> {frust}")
                lines.append("")

        if signals["tool_failure_sequences"]:
            lines.append("### Trial-and-Error Sequences")
            lines.append("")
            for seq in signals["tool_failure_sequences"]:
                outcome = "→ succeeded" if seq["eventually_succeeded"] else "→ gave up"
                lines.append(
                    f"- **{seq['tool']}** failed {seq['failures']}x {outcome}: "
                    f"`{seq['first_error'][:80]}`"
                )
            lines.append("")

        if signals["assumptions_without_read"]:
            lines.append("### Assumptions (Edit without prior Read)")
            lines.append("")
            for fp in signals["assumptions_without_read"]:
                lines.append(f"- `{fp}`")
            lines.append("")

    outfile.write_text("\n".join(lines))
    return True


def process_conversations(
    incremental: bool = False, state: Optional[dict] = None, deep: bool = False
) -> int:
    if not PROJECTS_DIR.exists():
        print("  SKIP: projects directory not found")
        return 0

    count = 0
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue
        jsonl_files = list(project_dir.glob("*.jsonl"))
        if not jsonl_files:
            continue

        project_slug = slugify(project_dir.name)
        out_dir = OUTPUT_DIR / "conversations" / project_slug
        out_dir.mkdir(parents=True, exist_ok=True)

        for jf in sorted(jsonl_files):
            if incremental and state and not file_changed(jf, state):
                continue
            try:
                if process_conversation(jf, out_dir, deep=deep):
                    count += 1
                    if state:
                        mark_processed(jf, state)
            except Exception as e:
                print(f"  ERROR processing {jf.name}: {e}", file=sys.stderr)

    print(f"  conversations → {count} session files")
    return count


# ---------------------------------------------------------------------------
# Processor 3: Subagent JSONLs
# ---------------------------------------------------------------------------


def process_subagent(filepath: Path, out_dir: Path) -> bool:
    agent_id = filepath.stem
    outfile = out_dir / f"{agent_id}.md"

    task_prompt = ""
    tool_counts: Counter = Counter()
    entry_count = 0
    timestamps: List[float] = []
    errors: List[str] = []

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_count += 1
            ts = parse_timestamp(entry.get("timestamp"))
            if ts:
                timestamps.append(ts)
            entry_type = entry.get("type", "")

            if entry_type in ("user", "system") and not task_prompt:
                msg = entry.get("message", {})
                content = msg.get("content") if isinstance(msg, dict) else ""
                if isinstance(content, list):
                    parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            parts.append(block.get("text", ""))
                        elif isinstance(block, str):
                            parts.append(block)
                    content = "\n".join(parts)
                if isinstance(content, str) and content.strip():
                    task_prompt = content[:1000]

            elif entry_type == "user":
                msg = entry.get("message", {})
                content = msg.get("content", []) if isinstance(msg, dict) else []
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_result":
                            if block.get("is_error"):
                                bc = block.get("content", "")
                                err_text = bc[:100] if isinstance(bc, str) else str(bc)[:100]
                                errors.append(err_text)

            elif entry_type == "assistant":
                msg = entry.get("message", {})
                content = msg.get("content", []) if isinstance(msg, dict) else []
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_use":
                            tool_counts[block.get("name", "")] += 1

    if entry_count == 0:
        return False

    duration_str = "unknown"
    if len(timestamps) >= 2:
        duration_sec = max(timestamps) - min(timestamps)
        if duration_sec < 60:
            duration_str = f"{int(duration_sec)}s"
        elif duration_sec < 3600:
            duration_str = f"{int(duration_sec / 60)}min"
        else:
            duration_str = f"{duration_sec / 3600:.1f}hr"

    session_date = epoch_to_date(min(timestamps)) if timestamps else "unknown"

    lines = [
        "---", "source: subagent", f"agent_id: {agent_id}",
        f"date: {session_date}", f"entry_count: {entry_count}",
        f"tool_uses: {sum(tool_counts.values())}",
        f"errors: {len(errors)}", f"duration: {duration_str}",
        f"outcome: {'success' if not errors else 'had_errors'}",
        "---", "",
        f"# Subagent: {agent_id[:12]}... — {session_date}", "",
    ]

    if task_prompt:
        lines.append("## Task Assignment")
        lines.append("")
        for tl in task_prompt.split("\n"):
            lines.append(f"> {tl}")
        lines.append("")

    if tool_counts:
        lines.append("## Tools Used")
        lines.append("")
        for tool, count in tool_counts.most_common():
            lines.append(f"- {tool}: {count}")
        lines.append("")

    if errors:
        lines.append("## Errors")
        lines.append("")
        for err in errors[:10]:
            lines.append(f"- {err}")
        lines.append("")

    outfile.write_text("\n".join(lines))
    return True


def process_subagents(
    incremental: bool = False, state: Optional[dict] = None
) -> int:
    if not PROJECTS_DIR.exists():
        print("  SKIP: projects directory not found")
        return 0

    count = 0
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue
        jsonl_files = list(project_dir.glob("*/subagents/agent-*.jsonl"))
        if not jsonl_files:
            continue

        project_slug = slugify(project_dir.name)
        out_dir = OUTPUT_DIR / "subagents" / project_slug
        out_dir.mkdir(parents=True, exist_ok=True)

        for jf in sorted(jsonl_files):
            if incremental and state and not file_changed(jf, state):
                continue
            try:
                if process_subagent(jf, out_dir):
                    count += 1
                    if state:
                        mark_processed(jf, state)
            except Exception as e:
                print(f"  ERROR processing {jf.name}: {e}", file=sys.stderr)

    print(f"  subagents → {count} agent files")
    return count


# ---------------------------------------------------------------------------
# Processor 4: Sync Inbox
# ---------------------------------------------------------------------------


def process_sync(
    incremental: bool = False, state: Optional[dict] = None
) -> int:
    out_dir = OUTPUT_DIR / "sync"
    out_dir.mkdir(parents=True, exist_ok=True)
    outfile = out_dir / "cross-project-messages.md"

    all_messages: List[dict] = []
    claude_projects = Path.home() / "Claude Projects"
    if claude_projects.exists():
        for project_dir in sorted(claude_projects.iterdir()):
            inbox = project_dir / ".claude" / "sync" / "inbox.jsonl"
            if not inbox.exists():
                continue
            project_name = project_dir.name
            with open(inbox) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        msg["_project"] = project_name
                        all_messages.append(msg)
                    except json.JSONDecodeError:
                        continue

    if not all_messages:
        print("  SKIP: no sync inbox messages found")
        return 0

    all_messages.sort(key=lambda m: m.get("timestamp", ""))

    lines = [
        "---", "source: sync-inbox",
        f"generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"message_count: {len(all_messages)}",
        f"projects: {len({m['_project'] for m in all_messages})}",
        "---", "",
        "# Cross-Project Sync Messages", "",
    ]

    for msg in all_messages:
        ts = msg.get("timestamp", "unknown")
        source = msg.get("source", "unknown")
        msg_type = msg.get("type", "unknown")
        priority = msg.get("priority", "normal")
        content = msg.get("content", "")
        project = msg.get("_project", "unknown")
        lines.extend([
            f"### [{priority}] {msg_type} — {ts}",
            f"**Source:** {source} | **Project inbox:** {project}",
            "", f"> {content}", "",
        ])

    outfile.write_text("\n".join(lines))
    print(
        f"  sync → {len(all_messages)} messages from "
        f"{len({m['_project'] for m in all_messages})} projects"
    )
    return 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess CC JSONL data for qmd")
    parser.add_argument(
        "--incremental", action="store_true", help="Only process new/changed files"
    )
    parser.add_argument(
        "--no-llm", action="store_true",
        help="Skip LLM classification, use signal-based detection only"
    )
    parser.add_argument(
        "--only",
        choices=["history", "conversations", "subagents", "sync"],
        help="Run only a specific processor",
    )
    args = parser.parse_args()

    state = load_state() if args.incremental else None

    print(f"Preprocessing CC data → {OUTPUT_DIR}/")
    use_llm = not args.no_llm
    print(f"Mode: {'incremental' if args.incremental else 'full'}"
          f"{' + LLM classification' if use_llm else ' (signal-only)'}")
    print()

    processors = {
        "history": lambda: process_history(args.incremental, state),
        "conversations": lambda: process_conversations(
            args.incremental, state, deep=use_llm
        ),
        "subagents": lambda: process_subagents(args.incremental, state),
        "sync": lambda: process_sync(args.incremental, state),
    }

    if args.only:
        processors = {args.only: processors[args.only]}

    total = 0
    for name, proc in processors.items():
        print(f"[{name}]")
        total += proc()

    if state:
        save_state(state)

    print(f"\nDone. {total} files generated.")


if __name__ == "__main__":
    main()
