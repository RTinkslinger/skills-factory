---
description: >
  Read external sources (git repos, arxiv papers, blog posts) and produce
  two-layer analysis: understand the source on its own terms, then map
  patterns to our systems (CC, CAI, CASH Build System, custom agents).
  Interactive flow with deep reasoning and user steering at each step.
---

# /learn-from

**Usage:** `/learn-from <url-or-path> [--focus "area of interest"] [--deep-extract]`

**Learnings directory:** /Users/Aakash/Claude Projects/Learn From/learnings/

## Flow Overview

```
Parse → READ + DEEP REASON → AskUserQuestion → MAP + DEEP REASON → AskUserQuestion → Save → Propose Memories (AskUQ) → End
```

## Global Behaviors

### Early Exit
At any point, if the user says "save what we have", "skip to save", "stop here",
or "not worth it" — jump directly to Save with whatever analysis has accumulated.
Note in the learning document which steps completed. If bailing before deep
reasoning (no analysis yet), ask: "Save just the reading, or discard entirely?"

### Subagent Failure Handling
After each subagent returns, check output against SUCCESS CRITERIA. If insufficient:
1. Tell the user what's missing: "The reading was incomplete — [gap]. Options:
   a) Retry with narrower scope  b) Proceed with what we have  c) Skip this source"
2. Max 2 retries with adjusted prompts, then proceed with best available.

### Data Flow
There are no persistent variables. Subagent outputs appear in the conversation
context as Agent tool results. Do NOT store values in files or variables — the
conversation context IS the state.

### Output Formatting (MANDATORY)

All output to the user MUST follow these rules:

1. **Brevity over completeness.** Each analysis section gets 2-4 bullet points
   MAX, not paragraphs. One sentence per point.
2. **Visual breathing room.** Use `---` between major sections. Never output
   two dense sections back-to-back without a separator.
3. **Bullets over prose.** Prefer `- point` over paragraphs. Scan-friendly > readable.
4. **Blockquotes for your takes.** Use `> ` for analytical opinions to distinguish
   them from factual summaries.
5. **Bold key terms, not whole sentences.** `**term**` on the important word only.
6. **Reading summary as a compact table.** Use a markdown table for Key Concepts
   (concept | description) instead of a long bullet list.
7. **~40-60 lines max per response.** Over 80 lines = too much. The learning
   document is where detail lives, not the interactive output.

---

## Step 1: Parse Input

The user invoked `/learn-from`. Their arguments are: `$ARGUMENTS`

1. Extract the URL or path from `$ARGUMENTS`
2. Extract `--focus "..."` if present (optional)
3. Extract `--deep-extract` if present (use Docling for PDF extraction)
4. Detect source type:

| URL pattern | Source type | Strategy |
|-------------|-----------|----------|
| `github.com/*` or `gitlab.com/*` | **repo** | Shallow clone, read key files |
| `arxiv.org/*` | **paper** | Download PDF, read with Read tool (or Docling) |
| Everything else | **web** | WebFetch |

5. If no URL provided, ask for one.

---

## Step 2: READ + DEEP REASON

This step has two parts: a subagent reads the source, then you present the
reading with your deep analysis in a single response.

### 2a. Dispatch reading subagent

Tell the user: "Reading [URL]..."

#### Repo source

Use Agent with `subagent_type: "Explore"`:

**CONSTRAINTS:** Read-only. No git writes. No MCP tools. Clean up temp dir when done.
**FILE ALLOWLIST:** `/tmp/learn-from-read/` (shallow clone destination)

**TASK:**
1. `gh repo clone [URL] /tmp/learn-from-read/ -- --depth 1`
2. Read README, map file structure, read 10-20 key files
3. [If FOCUS: "Pay special attention to: [FOCUS]"]
4. Clean up: `rm -rf /tmp/learn-from-read/`

Return: Source Summary (what, who, key files, tech stack), Key Concepts (5-10),
Architecture/Design Decisions (3+), Constraints (2+), Notable Patterns (2+).

#### Paper source

Use Agent with `subagent_type: "Explore"`:

**CONSTRAINTS:** Read-only. No MCP tools, no git. May write to /tmp/ only.
**FILE ALLOWLIST:** `/tmp/learn-from-paper.pdf`, `/tmp/learn-from-extract/`

**TASK:**
1. Transform URL: `/abs/` → `/pdf/` + `.pdf`
2. `curl -sL "[PDF_URL]" -o /tmp/learn-from-paper.pdf`
3. If `--deep-extract`: use Docling if installed, else Read tool. Default: Read tool.
4. [If FOCUS: "Pay special attention to: [FOCUS]"]
5. Clean up temp files.

Return: Source Summary (title, authors, date, thesis), Key Concepts (5-10),
Methodology (approach + evaluation), Results and Limitations, Notable Patterns (2+).

#### Web source

Use Agent with `subagent_type: "Explore"`:

**CONSTRAINTS:** Read-only. No MCP tools, no git. Max 3 linked pages.
**FILE ALLOWLIST:** None (web content via WebFetch only)

**TASK:**
1. WebFetch the URL (+ up to 3 linked pages)
2. [If FOCUS: "Pay special attention to: [FOCUS]"]

Return: Source Summary (type, author, thesis), Key Concepts (5-10),
Arguments and Evidence, Constraints/Caveats, Notable Patterns (2+).

### 2b. Check subagent output

Verify against success criteria. If insufficient → inform user, offer
retry/proceed/skip. Max 2 retries.

### 2c. Query past learnings

```
qmd query "patterns related to [key topic]" --collection learnings --limit 5
```

If results found, note connections. If empty, note: "First session — no prior patterns."

### 2d. Present reading + deep analysis

In a single response, show:

1. **The reading** — preface with "Here's what I found:" then show the structured
   output using a compact table for concepts.

2. Then `---` separator, then your deep analysis (4 sections, KEEP EACH SHORT):

   **"Most significant"** — 2-3 bullets. Core non-obvious insight. Use blockquote.

   **"Connects to your systems"** — 3-4 bullets. One per connection. Be precise.

   **"Questions to ask"** — 3-5 bullets. Provocative, one line each.

   **"Recommended mapping focus"** — 1-2 sentences.

### 2e. MANDATORY AskUserQuestion

After presenting the reading + analysis, you MUST call AskUserQuestion.
This mechanically blocks until the user responds.

Include: your recommended focus, 3 options based on the most interesting
patterns, and make clear they can type anything.

After the user responds:
- If they steer or agree → proceed to Step 3
- If they want to discuss → engage, then AskUserQuestion again
- Multiple rounds fine — keep asking until they signal readiness

---

## Step 3: MAP + DEEP REASON

This step has two parts: a subagent maps patterns, then you analyze applicability.

### 3a. Prepare system context

Read these files to build a ~2-3K token summary:
1. `~/.claude/CLAUDE.md` — global CC behaviors
2. Current project's CLAUDE.md — Build System Protocol
3. Relevant memory files from `~/.claude/projects/*/memory/`
4. The user's steering from Step 2

### 3b. Dispatch MAP subagent

Use Agent with `subagent_type: "general-purpose"`:

**CONSTRAINTS:** Read-only. No git. No MCP tools.
**FILE ALLOWLIST:**
- `~/.claude/CLAUDE.md`
- `/Users/Aakash/Claude Projects/Learn From/CLAUDE.md`
- Memory files in `~/.claude/projects/*/memory/`
- Past learnings in `/Users/Aakash/Claude Projects/Learn From/learnings/`

**TASK:** Map patterns from the source to user's systems. Include in prompt:
the full reading output, your deep analysis, user's steering, system context.

**Output format (instruct subagent to be concise — bullets not paragraphs):**
```
## Pattern Mappings
### Pattern: [name]
**In the source:** 1-2 sentences
**In your system:** 1-2 sentences
**Gap/opportunity:** 2-3 bullets
**Effort:** XS/S/M/L/XL
**Risk:** 1-2 sentences
[3-7 patterns]

## Contradictions Found
- One sentence each

## Experiment Ideas
- Each: scope, metric, time-box in 2-3 lines
```

**SUCCESS CRITERIA:** 3+ patterns (all fields), 1+ contradiction, 2+ experiments.

### 3c. Check subagent output

Verify against success criteria. If insufficient → retry/proceed/skip.

### 3d. Present mapping + applicability analysis

In a single response, show the mapping output, then your analysis
(5 sections, KEEP EACH SHORT):

**"Strongest pattern"** — 2-3 bullets. What to adopt, which file changes, effort.

**"Contradicts your setup"** — 2-3 bullets. Conflicts with existing principles.

**"Experiments"** — 2-3 bullets. Each: scope, metric, time-box in one line.

**"Would NOT adopt"** — 2-3 bullets. Interesting but wrong for your context.

**"Pressure-test"** — 2-3 bullets. One-line questions challenging the mappings.

### 3e. MANDATORY AskUserQuestion

After presenting the mapping + analysis, you MUST call AskUserQuestion.

Include: summary of strongest experiment, options for save/go-deeper/discuss.

After the user responds:
- If they say save/done → proceed to Step 4
- If they want to go deeper → engage, then AskUserQuestion again
- Multiple rounds fine

---

## Step 4: Save

### 4a. Write the learning document

**Filename:** `/Users/Aakash/Claude Projects/Learn From/learnings/YYYY-MM-DD-<source-slug>.md`

Slug: repo name, first-author + topic, or domain + slug.

```markdown
---
source_url: [URL]
source_type: repo | paper | web
date: YYYY-MM-DD
focus: [focus area or "broad"]
tags: [3-7 tags]
steps_completed: [read, reason, map, save]
---

# Learnings: [Source Name]

## Layer 1: Understanding the Source
[What it is, key concepts, architecture, patterns. Draw from reading output.]

## Layer 2: Applicable Patterns
[Mapped patterns, contradictions, experiments, what NOT to adopt.
Draw from mapping + analysis. Skip if mapping didn't run.]

## Key Takeaways
[3-5 actionable bullet points]

## Experiments Proposed
[Bounded experiments with scope, metric, time-box. Skip if not reached.]

## Decided Not to Adopt
[Rejected patterns with reasoning. Prevents re-evaluating in future sessions.]
```

### 4b. Propose CC memories via AskUserQuestion

For the most actionable patterns (typically 1-3), propose memory files.
Use a single AskUserQuestion with one question per proposed memory.

If approved, write to:
`~/.claude/projects/-Users-Aakash-Claude-Projects-Learn-From/memory/<name>.md`

Format:
```markdown
---
name: pattern-name
description: One-line description for relevance matching
type: reference
---

Learned from: [SOURCE_URL]

[Core insight in 1-2 sentences]

**How to apply:** [Concrete guidance]
```

### 4c. Update MEMORY.md

Add pointers to any new memory files in the project's MEMORY.md.

### 4d. Report completion

> "Learning saved to `learnings/YYYY-MM-DD-<slug>.md`.
> [N] CC memories created: [list names].
>
> This learning is now part of your knowledge library. Future `/learn-from`
> sessions will query it for compounding insights via qmd."
