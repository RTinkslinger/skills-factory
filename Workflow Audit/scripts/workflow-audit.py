#!/usr/bin/env python3
"""
CC Workflow Audit Engine v2 — Signal-based 7+3 dimension analysis.

v2 changes:
- Reads behavioral signals from preprocessed files (not regex)
- Clusters corrections by theme across sessions
- Cross-references with memory system
- Detects anti-patterns: repeated failures, trial-and-error, assumptions
- Severity thresholds: pattern in 3+ sessions = high

Usage:
  python3 workflow-audit.py                # Full audit + interactive
  python3 workflow-audit.py --report-only  # Generate report only
  python3 workflow-audit.py --reindex      # Re-index first
  python3 workflow-audit.py --deep         # Re-preprocess with LLM then audit
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
STATE_DIR = PROJECT_ROOT / "state"
PREPROCESSED_DIR = PROJECT_ROOT / "preprocessed"
CLAUDE_DIR = Path.home() / ".claude"


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------


def parse_frontmatter(content: str) -> Dict[str, str]:
    """Parse YAML-like frontmatter from markdown."""
    fm = {}
    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            for line in content[3:end].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip()
    return fm


def load_all_sessions() -> List[Dict[str, Any]]:
    """Load all preprocessed conversation sessions with their signals."""
    conv_dir = PREPROCESSED_DIR / "conversations"
    if not conv_dir.exists():
        return []

    sessions = []
    for md_file in conv_dir.rglob("*.md"):
        content = md_file.read_text()
        fm = parse_frontmatter(content)

        session = {
            "file": str(md_file),
            "session_id": fm.get("session_id", md_file.stem),
            "project": fm.get("project", "unknown"),
            "date": fm.get("date", "unknown"),
            "user_messages": int(fm.get("user_messages", 0)),
            "tool_uses": int(fm.get("tool_uses", 0)),
            "errors": int(fm.get("errors", 0)),
            "corrections": int(fm.get("corrections", 0)),
            "frustrations": int(fm.get("frustrations", 0)),
            "trial_and_error": int(fm.get("trial_and_error_sequences", 0)),
            "assumptions": int(fm.get("assumptions_without_read", 0)),
            "duration": fm.get("duration_estimate", "unknown"),
            "classification_mode": fm.get("classification_mode", "signal"),
            "content": content,
        }

        # Extract specific signal details from markdown sections
        session["correction_texts"] = extract_section_quotes(
            content, "### Corrections"
        )
        session["frustration_texts"] = extract_section_quotes(
            content, "### Frustration"
        )
        session["trial_error_details"] = extract_section_items(
            content, "### Trial-and-Error Sequences"
        )
        session["assumption_details"] = extract_section_items(
            content, "### Assumptions"
        )
        session["error_details"] = extract_section_items(
            content, "## Errors Encountered"
        )

        sessions.append(session)

    return sessions


def extract_section_quotes(content: str, header: str) -> List[str]:
    """Extract quoted lines (> ...) from a markdown section."""
    quotes = []
    in_section = False
    for line in content.split("\n"):
        if line.startswith(header):
            in_section = True
            continue
        if in_section and line.startswith("##"):
            break
        if in_section and line.startswith("> "):
            quotes.append(line[2:].strip())
    return quotes


def extract_section_items(content: str, header: str) -> List[str]:
    """Extract list items (- ...) from a markdown section."""
    items = []
    in_section = False
    for line in content.split("\n"):
        if line.startswith(header):
            in_section = True
            continue
        if in_section and line.startswith("##"):
            break
        if in_section and line.startswith("- "):
            items.append(line[2:].strip())
        if in_section and re.match(r"^\d+\.", line):
            items.append(re.sub(r"^\d+\.\s*", "", line).strip())
    return items


def load_memories() -> Dict[str, Any]:
    """Load and analyze all memory files."""
    memories_dir = CLAUDE_DIR / "projects"
    if not memories_dir.exists():
        return {"total": 0, "by_type": Counter(), "projects_with": set(),
                "projects_without": set(), "feedback_memories": [], "all": []}

    stats = {"total": 0, "by_type": Counter(), "projects_with": set(),
             "projects_without": set(), "feedback_memories": [], "all": []}

    for project_dir in memories_dir.iterdir():
        if not project_dir.is_dir():
            continue
        memory_dir = project_dir / "memory"
        if memory_dir.exists():
            md_files = [f for f in memory_dir.glob("*.md") if f.name != "MEMORY.md"]
            if md_files:
                stats["projects_with"].add(project_dir.name)
                for mf in md_files:
                    stats["total"] += 1
                    content = mf.read_text()
                    mem_type = "unknown"
                    for line in content.split("\n"):
                        if line.strip().startswith("type:"):
                            mem_type = line.split(":", 1)[1].strip()
                            break
                    stats["by_type"][mem_type] += 1
                    mem_entry = {
                        "file": mf.name, "project": project_dir.name,
                        "type": mem_type, "content": content[:500],
                        "age_days": (datetime.now().timestamp() - mf.stat().st_mtime) / 86400,
                    }
                    stats["all"].append(mem_entry)
                    if mem_type == "feedback":
                        stats["feedback_memories"].append(mem_entry)
            else:
                stats["projects_without"].add(project_dir.name)
        else:
            stats["projects_without"].add(project_dir.name)

    return stats


# ---------------------------------------------------------------------------
# Anti-Pattern Detection (the 3 user-requested patterns)
# ---------------------------------------------------------------------------


def detect_repeated_failures(sessions: List[Dict]) -> List[Dict]:
    """Detect error patterns that repeat across sessions.

    Signal: Same tool + similar error content in 3+ sessions.
    """
    # Group errors by tool
    error_by_tool: Dict[str, List[Dict]] = defaultdict(list)
    for sess in sessions:
        for err in sess.get("error_details", []):
            # Extract tool name from error format "[Tool] message"
            match = re.match(r"\[(\w+)\]\s*(.*)", err)
            if match:
                tool, msg = match.group(1), match.group(2)
                error_by_tool[tool].append({
                    "message": msg[:100],
                    "session": sess["session_id"][:8],
                    "project": sess["project"],
                    "date": sess["date"],
                })

    findings = []
    for tool, errors in error_by_tool.items():
        if len(errors) >= 3:
            # Group similar error messages
            unique_sessions = len(set(e["session"] for e in errors))
            if unique_sessions >= 2:
                findings.append({
                    "type": "repeated_failure_pattern",
                    "tool": tool,
                    "occurrences": len(errors),
                    "sessions": unique_sessions,
                    "examples": [e["message"] for e in errors[:3]],
                    "projects": list(set(e["project"] for e in errors)),
                })

    findings.sort(key=lambda f: f["sessions"], reverse=True)
    return findings


def detect_trial_and_error(sessions: List[Dict]) -> List[Dict]:
    """Detect sessions where Claude forgets how tools work.

    Signal: tool_failure_sequences in preprocessed data.
    """
    findings = []
    tool_struggles: Dict[str, List[Dict]] = defaultdict(list)

    for sess in sessions:
        for detail in sess.get("trial_error_details", []):
            # Parse: "**Tool** failed Nx → outcome: `error`"
            match = re.match(r"\*\*(\w+)\*\*\s+failed\s+(\d+)x", detail)
            if match:
                tool, fails = match.group(1), int(match.group(2))
                tool_struggles[tool].append({
                    "failures": fails,
                    "session": sess["session_id"][:8],
                    "project": sess["project"],
                    "date": sess["date"],
                    "detail": detail[:150],
                })

    for tool, struggles in tool_struggles.items():
        total_fails = sum(s["failures"] for s in struggles)
        if len(struggles) >= 2 or total_fails >= 5:
            findings.append({
                "type": "tool_trial_and_error",
                "tool": tool,
                "total_failures": total_fails,
                "sessions": len(struggles),
                "examples": [s["detail"] for s in struggles[:3]],
                "projects": list(set(s["project"] for s in struggles)),
            })

    findings.sort(key=lambda f: f["total_failures"], reverse=True)
    return findings


def detect_assumptions(sessions: List[Dict]) -> List[Dict]:
    """Detect sessions where Claude edits without reading first.

    Signal: assumptions_without_read in preprocessed data.
    """
    all_assumptions: Dict[str, List[Dict]] = defaultdict(list)

    for sess in sessions:
        for fp in sess.get("assumption_details", []):
            # Clean up the file path
            clean_fp = fp.strip("`")
            all_assumptions[clean_fp].append({
                "session": sess["session_id"][:8],
                "project": sess["project"],
                "date": sess["date"],
            })

    findings = []
    for fp, occurrences in all_assumptions.items():
        findings.append({
            "type": "assumption_without_verification",
            "file": fp,
            "occurrences": len(occurrences),
            "sessions": list(set(o["session"] for o in occurrences)),
            "projects": list(set(o["project"] for o in occurrences)),
        })

    findings.sort(key=lambda f: f["occurrences"], reverse=True)
    return findings


# ---------------------------------------------------------------------------
# Cross-Reference: Corrections vs Memories
# ---------------------------------------------------------------------------


def find_unmemorized_corrections(
    sessions: List[Dict], memories: Dict
) -> List[Dict]:
    """Find correction patterns that DON'T have corresponding feedback memories.

    This is the highest-value finding: repeated corrections without a memory
    means the same mistake will keep happening.
    """
    # Collect all correction texts
    all_corrections = []
    for sess in sessions:
        for corr in sess.get("correction_texts", []):
            all_corrections.append({
                "text": corr,
                "session": sess["session_id"][:8],
                "project": sess["project"],
                "date": sess["date"],
            })

    if not all_corrections:
        return []

    # Get all feedback memory content for comparison
    feedback_texts = [
        m["content"].lower()
        for m in memories.get("feedback_memories", [])
    ]

    # Check each correction against memories (simple keyword overlap)
    unmemorized = []
    for corr in all_corrections:
        corr_lower = corr["text"].lower()
        # Check if any feedback memory covers this correction
        has_memory = False
        for mem_text in feedback_texts:
            # Simple overlap: if 3+ significant words match
            corr_words = set(w for w in corr_lower.split() if len(w) > 3)
            mem_words = set(w for w in mem_text.split() if len(w) > 3)
            overlap = corr_words & mem_words
            if len(overlap) >= 3:
                has_memory = True
                break

        if not has_memory:
            unmemorized.append(corr)

    return unmemorized


# ---------------------------------------------------------------------------
# 7+3 Dimension Audit
# ---------------------------------------------------------------------------


def run_audit(
    sessions: List[Dict], memories: Dict
) -> List[Dict[str, Any]]:
    """Run the full 7+3 dimension audit."""
    dimensions = []

    # Aggregate stats
    total_sessions = len(sessions)
    total_errors = sum(s["errors"] for s in sessions)
    total_corrections = sum(s["corrections"] for s in sessions)
    total_frustrations = sum(s["frustrations"] for s in sessions)
    total_trial_error = sum(s["trial_and_error"] for s in sessions)
    total_assumptions = sum(s["assumptions"] for s in sessions)
    sessions_with_errors = sum(1 for s in sessions if s["errors"] > 0)
    sessions_with_corrections = sum(1 for s in sessions if s["corrections"] > 0)

    # --- D1: Friction Points ---
    unmemorized = find_unmemorized_corrections(sessions, memories)
    d1_findings = []

    if unmemorized:
        # Group by similar corrections
        d1_findings.append({
            "type": "corrections_without_memory",
            "severity": "critical" if len(unmemorized) >= 5 else "high",
            "count": len(unmemorized),
            "evidence": [u["text"][:150] for u in unmemorized[:5]],
            "suggestion": "Create feedback memories for these recurring corrections",
        })

    if sessions_with_corrections > 0:
        corr_sessions = [s for s in sessions if s["corrections"] > 0]
        d1_findings.append({
            "type": "sessions_with_corrections",
            "severity": "high" if sessions_with_corrections >= 5 else "medium",
            "count": sessions_with_corrections,
            "evidence": [
                f"{s['project']} ({s['date']}): {s['correction_texts'][0][:100]}"
                for s in corr_sessions[:5]
            ],
            "suggestion": "Review correction patterns and create feedback memories",
        })

    if total_frustrations > 0:
        frust_sessions = [s for s in sessions if s["frustrations"] > 0]
        d1_findings.append({
            "type": "frustration_signals",
            "severity": "high" if total_frustrations >= 3 else "medium",
            "count": total_frustrations,
            "evidence": [
                f"{s['project']} ({s['date']}): {s['frustration_texts'][0][:100]}"
                for s in frust_sessions[:5]
            ],
            "suggestion": "Investigate root causes of frustration",
        })

    dimensions.append({
        "dimension": "Friction Points",
        "summary": f"{sessions_with_corrections} sessions with corrections, "
                   f"{total_frustrations} frustration signals, "
                   f"{len(unmemorized)} corrections without feedback memories",
        "findings": d1_findings,
        "metrics": {
            "sessions_with_corrections": sessions_with_corrections,
            "total_corrections": total_corrections,
            "total_frustrations": total_frustrations,
            "unmemorized_corrections": len(unmemorized),
        },
    })

    # --- D2: Tool Usage Patterns ---
    tool_counts = Counter()
    tool_errors = Counter()
    for s in sessions:
        # Parse from content if available
        content = s.get("content", "")
        if "## Tool Usage Summary" in content:
            in_table = False
            for line in content.split("\n"):
                if line.startswith("| Tool "):
                    in_table = True
                    continue
                if line.startswith("|---"):
                    continue
                if in_table and line.startswith("| "):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 4:
                        try:
                            tool_counts[parts[1]] += int(parts[2])
                            tool_errors[parts[1]] += int(parts[3])
                        except ValueError:
                            pass
                elif in_table:
                    in_table = False

    d2_findings = []
    known_tools = {"Edit", "Read", "Write", "Bash", "Grep", "Glob", "Agent", "LSP"}
    unused = known_tools - set(tool_counts.keys())
    if unused:
        d2_findings.append({
            "type": "unused_tools",
            "severity": "info",
            "count": len(unused),
            "evidence": [f"Never used: {', '.join(sorted(unused))}"],
            "suggestion": None,
        })

    # High failure rate tools
    for tool in tool_counts:
        total = tool_counts[tool]
        fails = tool_errors.get(tool, 0)
        if total > 5 and fails / total > 0.15:
            d2_findings.append({
                "type": "high_failure_rate_tool",
                "severity": "medium",
                "count": fails,
                "evidence": [f"{tool}: {fails}/{total} failures ({fails/total:.0%})"],
                "suggestion": f"Investigate why {tool} fails frequently",
            })

    dimensions.append({
        "dimension": "Tool Usage Patterns",
        "summary": f"{sum(tool_counts.values())} tool uses, "
                   f"{sum(tool_errors.values())} failures across {total_sessions} sessions",
        "findings": d2_findings,
        "metrics": {
            "top_tools": dict(tool_counts.most_common(10)),
            "total_failures": sum(tool_errors.values()),
            "unused_tools": sorted(unused),
        },
    })

    # --- D3: Skill Gaps (lighter — uses qmd if available) ---
    dimensions.append({
        "dimension": "Skill Gaps",
        "summary": "Requires qmd semantic queries — run with --reindex for full analysis",
        "findings": [],
        "metrics": {},
    })

    # --- D4: Cross-Project Patterns ---
    project_errors = Counter()
    project_corrections = Counter()
    for s in sessions:
        if s["errors"] > 0:
            project_errors[s["project"]] += s["errors"]
        if s["corrections"] > 0:
            project_corrections[s["project"]] += s["corrections"]

    d4_findings = []
    # Projects with disproportionate errors
    for proj, count in project_errors.most_common(3):
        if count >= 10:
            d4_findings.append({
                "type": "high_error_project",
                "severity": "medium",
                "count": count,
                "evidence": [f"{proj}: {count} errors"],
                "suggestion": f"Investigate error patterns in {proj}",
            })

    dimensions.append({
        "dimension": "Cross-Project Patterns",
        "summary": f"Errors across {len(project_errors)} projects, "
                   f"corrections in {len(project_corrections)} projects",
        "findings": d4_findings,
        "metrics": {
            "errors_by_project": dict(project_errors.most_common(5)),
            "corrections_by_project": dict(project_corrections.most_common(5)),
        },
    })

    # --- D5: Memory Health ---
    d5_findings = []
    with_mem = len(memories.get("projects_with", set()))
    without_mem = len(memories.get("projects_without", set()))
    feedback_count = memories["by_type"].get("feedback", 0)

    if without_mem > with_mem:
        d5_findings.append({
            "type": "low_memory_coverage",
            "severity": "medium",
            "count": without_mem,
            "evidence": [f"{without_mem} projects have no memories vs {with_mem} that do"],
            "suggestion": "Add memories for active projects",
        })

    if feedback_count < 3:
        d5_findings.append({
            "type": "low_feedback_memories",
            "severity": "high" if feedback_count == 0 else "medium",
            "count": feedback_count,
            "evidence": [f"Only {feedback_count} feedback memories"],
            "suggestion": "Save feedback memories when correcting Claude's behavior",
        })

    stale = [m for m in memories.get("all", []) if m["age_days"] > 14]
    if stale:
        d5_findings.append({
            "type": "stale_memories",
            "severity": "low",
            "count": len(stale),
            "evidence": [f"{len(stale)} memories older than 14 days"],
            "suggestion": "Review and update or remove stale memories",
        })

    dimensions.append({
        "dimension": "Memory Health",
        "summary": f"{memories['total']} memories across {with_mem} projects, "
                   f"{feedback_count} feedback memories",
        "findings": d5_findings,
        "metrics": {
            "total": memories["total"],
            "by_type": dict(memories["by_type"]),
            "projects_with": with_mem,
            "projects_without": without_mem,
        },
    })

    # --- D6: Configuration Drift (placeholder) ---
    dimensions.append({
        "dimension": "Configuration Drift",
        "summary": "Requires cross-project CLAUDE.md comparison",
        "findings": [],
        "metrics": {},
    })

    # --- D7: Automation Opportunities (placeholder) ---
    dimensions.append({
        "dimension": "Automation Opportunities",
        "summary": "Requires qmd semantic queries for pattern detection",
        "findings": [],
        "metrics": {},
    })

    # --- D8: Repeated Failure Patterns (NEW) ---
    repeated = detect_repeated_failures(sessions)
    d8_findings = []
    for r in repeated[:5]:
        d8_findings.append({
            "type": "repeated_failure_pattern",
            "severity": "high" if r["sessions"] >= 3 else "medium",
            "count": r["occurrences"],
            "evidence": [
                f"{r['tool']} errors in {r['sessions']} sessions: {', '.join(r['examples'][:2])}"
            ],
            "suggestion": f"Add LEARNINGS.md entry for {r['tool']} failure pattern",
        })

    dimensions.append({
        "dimension": "Repeated Failure Patterns",
        "summary": f"{len(repeated)} tools with cross-session error patterns",
        "findings": d8_findings,
        "metrics": {
            "patterns": [
                {"tool": r["tool"], "sessions": r["sessions"], "occurrences": r["occurrences"]}
                for r in repeated
            ],
        },
    })

    # --- D9: Trial-and-Error (Tool Amnesia) (NEW) ---
    trial_error = detect_trial_and_error(sessions)
    d9_findings = []
    for te in trial_error[:5]:
        d9_findings.append({
            "type": "tool_trial_and_error",
            "severity": "high" if te["total_failures"] >= 10 else "medium",
            "count": te["total_failures"],
            "evidence": [
                f"{te['tool']}: {te['total_failures']} failures across {te['sessions']} sessions",
                *te["examples"][:2],
            ],
            "suggestion": f"Document {te['tool']} usage patterns in CLAUDE.md or LEARNINGS.md",
        })

    dimensions.append({
        "dimension": "Trial-and-Error (Tool Amnesia)",
        "summary": f"{sum(te['total_failures'] for te in trial_error)} tool failures "
                   f"from {len(trial_error)} tools struggling across sessions",
        "findings": d9_findings,
        "metrics": {
            "tools": [
                {"tool": te["tool"], "failures": te["total_failures"],
                 "sessions": te["sessions"]}
                for te in trial_error
            ],
        },
    })

    # --- D10: Assumptions Without Verification (NEW) ---
    assumptions = detect_assumptions(sessions)
    d10_findings = []
    for a in assumptions[:5]:
        d10_findings.append({
            "type": "edit_without_read",
            "severity": "high" if a["occurrences"] >= 3 else "medium" if a["occurrences"] >= 2 else "low",
            "count": a["occurrences"],
            "evidence": [
                f"`{a['file']}` edited without reading in {a['occurrences']} session(s)"
            ],
            "suggestion": "Add 'always Read before Edit' reminder to CLAUDE.md",
        })

    dimensions.append({
        "dimension": "Assumptions Without Verification",
        "summary": f"{total_assumptions} Edit-without-Read instances across "
                   f"{sum(1 for s in sessions if s['assumptions'] > 0)} sessions",
        "findings": d10_findings,
        "metrics": {
            "total_instances": total_assumptions,
            "unique_files": len(assumptions),
            "top_files": [
                {"file": a["file"], "count": a["occurrences"]}
                for a in assumptions[:5]
            ],
        },
    })

    return dimensions


# ---------------------------------------------------------------------------
# Report Generator
# ---------------------------------------------------------------------------


def severity_rank(s: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}.get(s, 5)


def generate_report(
    dimensions: List[Dict], sessions: List[Dict], memories: Dict
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total_sessions = len(sessions)
    projects = len(set(s["project"] for s in sessions))

    all_findings = []
    for dim in dimensions:
        for f in dim.get("findings", []):
            f["dimension"] = dim["dimension"]
            all_findings.append(f)

    all_findings.sort(key=lambda f: severity_rank(f.get("severity", "low")))

    by_sev = Counter(f.get("severity", "low") for f in all_findings)

    lines = [
        "# CC Workflow Audit Report",
        f"**Generated:** {now}",
        f"**Sessions analyzed:** {total_sessions}",
        f"**Projects covered:** {projects}",
        f"**Total findings:** {len(all_findings)} "
        f"({by_sev.get('critical', 0)} critical, {by_sev.get('high', 0)} high, "
        f"{by_sev.get('medium', 0)} medium, {by_sev.get('low', 0)} low)",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
    ]

    # Top findings
    for sev in ["critical", "high", "medium"]:
        items = [f for f in all_findings if f.get("severity") == sev]
        if items:
            icon = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(sev, "")
            lines.append(f"**{icon} {sev.title()} ({len(items)}):**")
            for f in items[:3]:
                ev = f["evidence"][0] if f.get("evidence") else ""
                lines.append(f"- [{f['dimension']}] {f.get('type', '')}: {ev[:120]}")
            lines.append("")

    lines.extend(["---", ""])

    # Per-dimension sections
    for i, dim in enumerate(dimensions, 1):
        findings = dim.get("findings", [])
        if not findings and not dim.get("metrics"):
            continue

        lines.extend([f"## {i}. {dim['dimension']}", "", f"*{dim['summary']}*", ""])

        metrics = dim.get("metrics", {})
        if metrics:
            lines.extend(["| Metric | Value |", "|--------|-------|"])
            for k, v in metrics.items():
                if isinstance(v, (dict, Counter)):
                    v = ", ".join(f"{k2}: {v2}" for k2, v2 in list(v.items())[:5])
                elif isinstance(v, (set, list)):
                    if v and isinstance(v[0], dict):
                        v = "; ".join(str(x) for x in v[:3])
                    else:
                        v = ", ".join(str(x) for x in list(v)[:5])
                lines.append(f"| {k} | {v} |")
            lines.append("")

        for j, f in enumerate(findings, 1):
            sev = f.get("severity", "low")
            ftype = f.get("type", "finding")
            icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "ℹ️"}.get(sev, "")
            lines.extend([
                f"### {dim['dimension'][:3].upper()}-{j}: {ftype} [{sev}] {icon}",
                "",
                "**Evidence:**",
            ])
            for ev in f.get("evidence", []):
                lines.append(f"- {ev[:200]}")
            lines.append("")
            if f.get("suggestion"):
                lines.append(f"**Suggested action:** {f['suggestion']}")
                lines.append("")

        lines.extend(["---", ""])

    # Improvement backlog
    lines.extend(["## Improvement Backlog", "", "| # | Finding | Dimension | Severity | Action |", "|---|---------|-----------|----------|--------|"])
    for i, f in enumerate(all_findings, 1):
        lines.append(
            f"| {i} | {f.get('type', '')[:30]} | {f.get('dimension', '')[:25]} "
            f"| {f.get('severity', 'low')} | {(f.get('suggestion') or '-')[:40]} |"
        )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Interactive Follow-up
# ---------------------------------------------------------------------------


def interactive_followup(dimensions: List[Dict]) -> Dict[str, Any]:
    all_findings = []
    for dim in dimensions:
        for f in dim.get("findings", []):
            f["dimension"] = dim["dimension"]
            all_findings.append(f)

    all_findings.sort(key=lambda f: severity_rank(f.get("severity", "low")))

    if not all_findings:
        print("\nNo findings to review!")
        return {"saved": [], "dismissed": []}

    print(f"\n{'='*60}")
    print(f"Audit found {len(all_findings)} improvements.")
    print(f"Review each: [s]ave / [d]ismiss / [q]uit")
    print(f"{'='*60}\n")

    results = {"saved": [], "dismissed": []}

    for i, f in enumerate(all_findings, 1):
        sev = f.get("severity", "low")
        print(f"[{i}/{len(all_findings)}] {sev.upper()}: {f.get('dimension', '')} — {f.get('type', '')}")
        for ev in f.get("evidence", [])[:2]:
            print(f"  {ev[:150]}")
        if f.get("suggestion"):
            print(f"  → {f['suggestion']}")
        print()

        try:
            choice = input("  [s]ave / [d]ismiss / [q]uit > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice == "q":
            break
        elif choice == "d":
            results["dismissed"].append(f)
        else:
            results["saved"].append(f)

    return results


# ---------------------------------------------------------------------------
# State Persistence & Differential Auditing
# ---------------------------------------------------------------------------

HISTORY_FILE = STATE_DIR / "audit-history.json"


def load_audit_history() -> Dict[str, Any]:
    """Load audit run history."""
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return {"last_run": None, "run_count": 0, "runs": []}


def save_audit_history(
    history: Dict, dimensions: List[Dict], sessions: List[Dict]
) -> None:
    """Save current audit run to history."""
    today = datetime.now().strftime("%Y-%m-%d")

    by_sev = Counter()
    finding_types = []
    for dim in dimensions:
        for f in dim.get("findings", []):
            by_sev[f.get("severity", "low")] += 1
            finding_types.append(f.get("type", "unknown"))

    run_entry = {
        "date": today,
        "sessions_analyzed": len(sessions),
        "findings_total": sum(len(d.get("findings", [])) for d in dimensions),
        "findings_by_severity": dict(by_sev),
        "finding_types": finding_types,
        "report_path": f"reports/audit-{today}.md",
    }

    history["last_run"] = today
    history["run_count"] = history.get("run_count", 0) + 1
    history["runs"].append(run_entry)

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def differential_analysis(
    current_dimensions: List[Dict], history: Dict
) -> Optional[Dict[str, Any]]:
    """Compare current findings with previous run.

    Returns dict with new, recurring, and resolved findings.
    """
    if not history.get("runs"):
        return None

    last_run = history["runs"][-1]
    prev_types = set(last_run.get("finding_types", []))

    current_types = set()
    for dim in current_dimensions:
        for f in dim.get("findings", []):
            current_types.add(f.get("type", "unknown"))

    new_findings = current_types - prev_types
    recurring = current_types & prev_types
    resolved = prev_types - current_types

    return {
        "previous_date": last_run.get("date", "unknown"),
        "previous_total": last_run.get("findings_total", 0),
        "new": sorted(new_findings),
        "recurring": sorted(recurring),
        "resolved": sorted(resolved),
        "new_count": len(new_findings),
        "recurring_count": len(recurring),
        "resolved_count": len(resolved),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="CC Workflow Audit v2")
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--reindex", action="store_true")
    parser.add_argument("--no-llm", action="store_true",
                        help="Skip LLM re-preprocessing (use existing data)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    # Re-preprocess with LLM classification (default)
    if not args.no_llm:
        print("Re-preprocessing with LLM classification...")
        subprocess.run(
            ["python3", str(SCRIPT_DIR / "preprocess-jsonl.py"),
             "--only", "conversations"],
            check=False,
        )
        print()

    # Optional reindex
    if args.reindex:
        print("Re-indexing...")
        subprocess.run(
            [str(SCRIPT_DIR / "reindex.sh"), "--incremental"],
            check=False,
        )
        print()

    print("=" * 60)
    print("CC Workflow Audit v2")
    print("=" * 60)
    print()

    print("[1/3] Loading preprocessed sessions...")
    sessions = load_all_sessions()
    print(f"  {len(sessions)} sessions loaded")

    print("[2/3] Loading memories...")
    memories = load_memories()
    print(f"  {memories['total']} memories, {len(memories.get('feedback_memories', []))} feedback")

    print("[3/3] Running 10-dimension audit...")
    dimensions = run_audit(sessions, memories)

    total_findings = sum(len(d.get("findings", [])) for d in dimensions)
    print(f"  {total_findings} findings across {len(dimensions)} dimensions")
    print()

    if args.json:
        output = {"dimensions": dimensions}
        print(json.dumps(output, indent=2, default=str))
        return

    # Load audit history for differential analysis
    history = load_audit_history()
    diff = differential_analysis(dimensions, history)

    report = generate_report(dimensions, sessions, memories)
    today = datetime.now().strftime("%Y-%m-%d")

    # Append differential section to report if previous run exists
    if diff:
        diff_section = [
            "", "---", "",
            "## Differential Analysis",
            f"*Compared with previous audit from {diff['previous_date']} "
            f"({diff['previous_total']} findings)*",
            "",
            f"- **{diff['new_count']} new findings:** {', '.join(diff['new'][:5]) or 'none'}",
            f"- **{diff['recurring_count']} recurring findings:** {', '.join(diff['recurring'][:5]) or 'none'}",
            f"- **{diff['resolved_count']} resolved findings:** {', '.join(diff['resolved'][:5]) or 'none'}",
            "",
        ]
        report += "\n".join(diff_section)

    report_path = REPORTS_DIR / f"audit-{today}.md"
    report_path.write_text(report)
    print(f"Report saved: {report_path}")

    by_sev = Counter()
    for dim in dimensions:
        for f in dim.get("findings", []):
            by_sev[f.get("severity", "low")] += 1
    print(f"Findings: {total_findings} "
          f"({by_sev.get('critical', 0)} critical, {by_sev.get('high', 0)} high, "
          f"{by_sev.get('medium', 0)} medium, {by_sev.get('low', 0)} low)")

    # Show differential summary
    if diff:
        print(f"\nSince last audit ({diff['previous_date']}):")
        print(f"  {diff['new_count']} new | {diff['recurring_count']} recurring | {diff['resolved_count']} resolved")

    # Save run to history
    save_audit_history(history, dimensions, sessions)
    print(f"Run #{history['run_count']} saved to state/audit-history.json")

    # Suggest next audit
    print(f"\nNext audit: suggest in ~2 weeks (bi-weekly cadence)")

    if not args.report_only:
        results = interactive_followup(dimensions)
        actions_path = STATE_DIR / "runs" / f"{today}-actions.json"
        actions_path.parent.mkdir(parents=True, exist_ok=True)
        actions_path.write_text(json.dumps({
            "date": today,
            "saved": [f.get("type") for f in results.get("saved", [])],
            "dismissed": [f.get("type") for f in results.get("dismissed", [])],
        }, indent=2))
        print(f"\nActions saved: {actions_path}")


if __name__ == "__main__":
    main()
