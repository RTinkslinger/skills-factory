---
description: >
  Read external sources (git repos, arxiv papers, blog posts) and produce
  two-layer analysis: understand the source on its own terms, then map
  patterns to our systems (CC, CAI, CASH Build System, custom agents).
  6-stage interactive flow with deep reasoning checkpoints.
---

# /learn-from

**Usage:** `/learn-from <url-or-path> [--focus "area of interest"] [--deep-extract]`

**Learnings directory:** /Users/Aakash/Claude Projects/Learn From/learnings/

## Global Behaviors

### Stage Tracking
After completing each stage, announce: **"Moving to Stage N: [NAME]."**

### Early Exit
At any point, if the user says "save what we have", "skip to save", "stop here",
or "not worth it" — jump directly to Stage 6 with whatever analysis has accumulated.
Note in the learning document which stages completed. If bailing before Stage 3
(no analysis yet), ask: "Save just the reading, or discard entirely?"

### Subagent Failure Handling
After each subagent returns, check output against SUCCESS CRITERIA. If insufficient:
1. Tell the user what's missing: "The reading was incomplete — [gap]. Options:
   a) Retry with narrower scope  b) Proceed with what we have  c) Skip this source"
2. Max 2 retries with adjusted prompts, then proceed with best available.

### Data Flow
There are no persistent variables. Subagent outputs appear in the conversation
context as Agent tool results. Reference prior outputs by stage name: "the Stage 1
reading output", "the user's steering from Stage 3". Do NOT store values in files
or variables — the conversation context IS the state.

---

## Step 0: Parse Input

The user invoked `/learn-from`. Their arguments are: `$ARGUMENTS`

**Parse the input:**

1. Extract the URL or path from `$ARGUMENTS`
2. Extract `--focus "..."` if present (optional focus area for the reading subagent)
3. Extract `--deep-extract` if present (use Docling for PDF extraction instead of default Read tool)
4. Detect source type from URL:

| URL pattern | Source type | Reading strategy |
|-------------|------------|-----------------|
| `github.com/*` or `gitlab.com/*` | **repo** | Shallow clone to temp dir, read key files |
| `arxiv.org/*` | **paper** | Download PDF, read with Read tool (or Docling if `--deep-extract`) |
| Everything else | **web** | WebFetch to read page content |

5. If no URL provided or URL is invalid, ask the user:
   > "Please provide a URL to learn from. Examples:
   > - `github.com/user/repo` — analyze a git repository
   > - `arxiv.org/abs/2401.xxxxx` — analyze an academic paper
   > - `https://blog.example.com/post` — analyze a blog post or article"

**Announce:** "Moving to Stage 1: READ."

---

## Stage 1: READ (Subagent)

Launch a subagent to deeply read the source material. The subagent does the
token-heavy work and returns a structured summary to the main conversation.

**Announce to the user:**
> "Reading [the source URL]... Sending a subagent to read the source deeply."

### Dispatch: Repo source

Use the Agent tool with `subagent_type: "Explore"`:

**CONSTRAINTS:**
- Read-only — do not modify any files in the repo or elsewhere
- No git write operations (commit, push, force-push, reset)
- No MCP tools
- Cloning for read purposes is allowed (shallow clone only)
- Clean up: remove the temp clone directory when done

**FILE ALLOWLIST:**
- `/tmp/learn-from-read/` — shallow clone destination (read-only after clone)

**TASK:**
Read the repository thoroughly:

1. Shallow clone: `gh repo clone [SOURCE_URL] /tmp/learn-from-read/ -- --depth 1`
2. Read the README first for orientation
3. Use Glob to map `/tmp/learn-from-read/` file structure — identify:
   - Entry points (main files, index files)
   - Configuration files (package.json, pyproject.toml, Cargo.toml, etc.)
   - Design docs, architecture docs, CHANGELOG, program.md-style instruction files
   - Key source files that reveal design patterns (not every file — prioritize by
     architectural significance)
4. Read the most important files (aim for 10-20 key files, not the entire repo)
5. [If FOCUS was specified: "Pay special attention to: [FOCUS]"]
6. Clean up: `rm -rf /tmp/learn-from-read/`

Extract and return this structured analysis:

```
## Source Summary
- What this is (1-2 sentences)
- Who made it and why (author, motivation)
- Key files read (list with brief purpose of each)
- Tech stack and dependencies

## Key Concepts (5-10 items)
- Concept: brief description of what it is and why it matters

## Architecture / Design Decisions
- Decision: what was chosen, why, what alternatives were rejected

## Constraints and Boundaries
- What the system deliberately does NOT do
- What's fixed vs. configurable
- Opinionated choices and their rationale

## Notable Patterns
- Pattern: description of how it works and where it appears
```

**SUCCESS CRITERIA:**
- Source Summary has all 4 sub-items filled
- At least 5 Key Concepts identified
- At least 3 Architecture/Design Decisions with rationale
- At least 2 Constraints identified
- At least 2 Notable Patterns described

### Dispatch: Paper source

Use the Agent tool with `subagent_type: "Explore"`:

**CONSTRAINTS:**
- Read-only — do not create or modify permanent files
- No MCP tools, no git operations
- May write to /tmp/ for PDF download only

**FILE ALLOWLIST:**
- `/tmp/learn-from-paper.pdf` (download target)
- `/tmp/learn-from-extract/` (Docling output directory, if used)

**TASK:**
Read the academic paper:

1. **URL transformation:** If URL contains `/abs/`, construct the PDF URL:
   replace `/abs/` with `/pdf/` and append `.pdf`
   (e.g., `arxiv.org/abs/2401.12345` → `arxiv.org/pdf/2401.12345.pdf`)
   If URL already contains `/pdf/`, use as-is.
2. **Download:** `curl -sL "[PDF_URL]" -o /tmp/learn-from-paper.pdf`
3. **Extract:**
   - If `--deep-extract` was specified: check `pip show docling`. If installed,
     run `docling /tmp/learn-from-paper.pdf --output-dir /tmp/learn-from-extract/`
     and read the resulting markdown. If not installed, fall back to Read tool.
   - Default: Use the Read tool on `/tmp/learn-from-paper.pdf` directly.
     Claude's multimodal vision understands papers semantically.
4. [If FOCUS was specified: "Pay special attention to: [FOCUS]"]
5. Clean up: `rm -f /tmp/learn-from-paper.pdf && rm -rf /tmp/learn-from-extract/`

Extract and return this structured analysis:

```
## Source Summary
- Title, authors, date, venue
- Core thesis (1-2 sentences)
- Key sections read

## Key Concepts (5-10 items)
- Concept: what it is, why it matters to the paper's argument

## Methodology
- Approach taken and why
- Evaluation strategy (metrics, baselines, datasets)

## Results and Limitations
- Key findings (quantitative where possible)
- Acknowledged limitations
- What the authors explicitly leave as future work

## Notable Patterns
- Transferable techniques or ideas beyond the paper's specific domain
```

**SUCCESS CRITERIA:**
- Title and authors identified
- Core thesis stated in 1-2 sentences
- At least 5 Key Concepts
- Methodology section filled with approach + evaluation
- At least 2 Notable Patterns (transferable, not domain-locked)

### Dispatch: Web source

Use the Agent tool with `subagent_type: "Explore"`:

**CONSTRAINTS:**
- Read-only — do not create or modify files
- No MCP tools, no git operations
- Only fetch the provided URL and linked pages (max 3 linked pages)

**FILE ALLOWLIST:**
- None (web content only, accessed via WebFetch)

**TASK:**
Read the web content:

1. Use WebFetch to retrieve the page content
2. If the page references key linked resources (max 3), fetch those too
3. [If FOCUS was specified: "Pay special attention to: [FOCUS]"]

Extract and return this structured analysis:

```
## Source Summary
- What this is (article, tutorial, documentation, opinion piece)
- Author and publication context
- Core thesis or purpose

## Key Concepts (5-10 items)
- Concept: description

## Arguments and Evidence
- Main claims and how they're supported
- Frameworks or mental models presented

## Constraints and Caveats
- Scope limitations the author acknowledges
- Context where the advice applies vs. doesn't

## Notable Patterns
- Transferable ideas, techniques, or frameworks
```

**SUCCESS CRITERIA:**
- Source type and author identified
- Core thesis stated
- At least 5 Key Concepts
- At least 2 Notable Patterns

### After subagent returns

Check output against SUCCESS CRITERIA. If insufficient:
1. Tell the user: "The reading was incomplete — [specific gap]. Options:
   a) Retry with a narrower focus  b) Proceed with what we have  c) Skip this source"
2. If retrying, dispatch another Explore subagent with a more focused prompt.
3. Max 2 retries, then proceed with best available output.

The subagent's output is now in your conversation context as the Stage 1 reading.

**Announce:** "Moving to Stages 2+3: SURFACE + DEEP REASONING."

---

## Stages 2+3: SURFACE + DEEP REASONING (Checkpoint 1)

**This runs in the main conversation. Do NOT use a subagent.**

Present the Stage 1 reading output to the user, then immediately follow with
your deep analysis. The user gets both at once — they can redirect if the
reading is wrong, or engage with the reasoning directly.

### 2a. Present the reading

Show the full structured output from Stage 1. Preface with:
> **Here's what I found in [the source URL]:**

Then show the reading output in full.

> If anything above looks wrong or incomplete, tell me and I'll re-read
> those parts. Otherwise, here's my deeper analysis:

### 3a. Query past learnings

Before your analysis, query the learnings knowledge base for related patterns:

```
qmd query "patterns related to [key topic from the source]" --collection learnings --limit 5
```

If qmd returns results, read the most relevant ones and look for:
- Related patterns already studied
- Connections or contradictions with the current source
- Compounding insights ("We saw X in [previous source], and this source adds Y")

If the learnings collection is empty (this is the first session), skip and note:
"This is the first learning session — no prior patterns to cross-reference."

Mention any connections found: "We've seen a similar pattern before in
[source] — here's how it compares."

### 3b. Deep analysis (present all 4 sections)

**1. "What I think is most significant and why"**
Your analytical take. What's the core insight? What's the non-obvious thing
that makes this source worth studying? Go beyond the surface — what principle
is at work?

**2. "Patterns I see connecting to your systems"**
Specific, concrete connections to:
- Claude Code (commands, hooks, settings, memory system)
- Claude.ai (artifacts, projects, custom instructions)
- CASH Build System (TRACES, LEARNINGS, ROADMAP, subagent protocol)
- Custom agents and workflows

Be precise: "Their `program.md` is structurally similar to your CLAUDE.md,
but they use it as a search boundary constraint, not just behavioral
instructions."

NOT vague: "This could be useful for your workflow." ← Never say this.

**3. "Questions you should be asking"**
Provocative, non-obvious questions that push thinking deeper. These should
challenge assumptions, not just summarize. Aim for 3-5 questions that make
the user stop and think.

Examples of good questions:
- "Their harness reverts bad experiments automatically. Your CASH Build System
  traces iterations but doesn't revert. Should it?"
- "They constrain the agent to one file. You constrain subagents via file
  allowlists. But your allowlists are per-task, not per-system. What would
  a system-level constraint look like?"

**4. "Recommended focus for the mapping stage"**
"I'd suggest we go deeper on X because [reasoning]. Agree, or redirect me."

### 3c. User steers

Present your analysis and let the user respond naturally. You MAY use
AskUserQuestion to offer structured options (top 3 patterns to focus on),
but also accept free-form responses. The user might want to discuss,
challenge, redirect, or go deeper in ways that don't fit predefined options.

The user's steering from this interaction guides the Stage 4 MAP subagent.

**Announce:** "Moving to Stage 4: MAP."

---

## Stage 4: MAP (Subagent)

Launch a subagent to produce detailed pattern mappings. This subagent needs
context about the user's systems to make concrete connections.

### 4a. Prepare system context

Before dispatching, build a focused system context summary (~2-3K tokens)
by reading these files:

1. **CC setup:** Read `~/.claude/CLAUDE.md` for global behaviors
2. **CASH Build System:** Summarize the Build System Protocol section from
   the current project's CLAUDE.md (TRACES, LEARNINGS, ROADMAP, subagent
   protocol, branch lifecycle)
3. **Memory system:** Read a few relevant memory files from
   `~/.claude/projects/*/memory/` that relate to the patterns being mapped
4. **User's steering:** Incorporate the user's direction from Stage 3

Include this summary directly in the subagent prompt. The subagent also has
file access for deeper reading if the summary isn't sufficient.

### 4b. Dispatch MAP subagent

Use the Agent tool with `subagent_type: "general-purpose"`:

**CONSTRAINTS:**
- Read-only — do not modify any files
- No git operations
- No MCP tools

**FILE ALLOWLIST:**
- `~/.claude/CLAUDE.md` (read-only — global CC behaviors)
- `/Users/Aakash/Claude Projects/Learn From/CLAUDE.md` (read-only)
- Memory files in `~/.claude/projects/*/memory/` (read-only)
- Past learnings in `/Users/Aakash/Claude Projects/Learn From/learnings/` (read-only)

**TASK:**
You are mapping patterns from an external source to the user's systems.

Use the provided system context summary as your primary reference for the
user's systems. Only read the allowlisted files directly if you need deeper
detail the summary doesn't cover.

**Source reading (from Stage 1):**
[INSERT the full Stage 1 reading output]

**Claude's analysis (from Stage 3):**
[INSERT the Stage 3 deep reasoning output]

**User's direction:**
[INSERT the user's steering response]

**System context summary:**
[INSERT the prepared system context]

Produce a detailed mapping document:

```
## Pattern Mappings

### Pattern: [name from source]
**In the source:** How it works there (be specific — quote structure, show mechanism)
**In your system:** Which of the user's systems this maps to, and how specifically
**Gap/opportunity:** What's different, what could be adopted, what would change
**Effort to adopt:** XS (<1hr) | S (1-3hr) | M (3-8hr) | L (1-2 days) | XL (3+ days)
**Risk:** What could go wrong if adopted

[Repeat for each mapped pattern — aim for 3-7 patterns]

## Contradictions Found
- "[Source] does X, but your CLAUDE.md says Y. Worth resolving?"
- Be specific about the contradiction and why it matters

## Experiment Ideas
- "What if we applied [concept] to [your system]? Here's what it would look like..."
- Each experiment should be bounded: what to try, how to measure, when to stop
```

**SUCCESS CRITERIA:**
- At least 3 pattern mappings with all 5 fields filled
- Effort estimates use T-shirt sizes consistent with Build Roadmap
- At least 1 contradiction identified (or explicit "no contradictions found")
- At least 2 experiment ideas with bounded scope

### After subagent returns

Check output against SUCCESS CRITERIA. If insufficient, follow the same
failure handling as Stage 1 (inform user, offer retry/proceed/skip).

The subagent's output is now in your conversation context as the Stage 4 mapping.

**Announce:** "Moving to Stage 5: DEEP REASONING (Applicability)."

---

## Stage 5: DEEP REASONING + STEER (Checkpoint 2)

**This runs in the main conversation. Do NOT use a subagent.**

You have the Stage 4 mapping output. Now analyze for *applicability and action*.
Stage 3 asked "what's interesting?" — this stage asks "what should we actually do?"

### 5a. Deep applicability analysis (present all 5 sections)

**1. "Strongest applicable pattern"**
The one thing most worth adopting. Be specific to the user's systems — not
abstract. Describe concretely what would change: which file, which protocol,
which workflow.

**2. "What this contradicts in your current setup"**
Honest analysis. Not everything should be adopted. Where does the source's
approach conflict with existing principles or architecture? Why might the
user's current approach actually be better for their context?

**3. "Experiment proposals"**
Concrete, bounded experiments:
- "Try applying [pattern] to [one specific project] for [one sprint].
  Measure [metric]. If it helps, roll out to others."
- Time-boxed. Measurable. Reversible.
- Reference T-shirt sizes from the Build Roadmap.

**4. "What I'd NOT adopt and why"**
Equally important. Which patterns are interesting but wrong for the user's
context? Why? This shows critical thinking, not enthusiasm for everything.

**5. "Pressure-test questions"**
Questions that challenge the mappings before committing:
- "This pattern works for [source] because [condition]. Your setup has
  [different condition]. Does the pattern still hold?"
- "If we adopt this, what breaks? What needs to change first?"

### 5b. User refines

Present your analysis and let the user respond. You MAY use AskUserQuestion
to offer structured options (which experiments to pursue), but also accept
free-form responses. The user might say "Go deeper on experiment 2" or
"What about applying this to the sync system specifically?" or just
"I've heard enough, let's save."

Multiple iterations are fine. Keep reasoning until the user signals they're
ready to save.

**Announce:** "Moving to Stage 6: SAVE."

---

## Stage 6: SAVE

Persist the learning as two artifacts: a full document and (optionally)
distilled CC memories.

### 6a. Generate the learning document

**Filename:** `/Users/Aakash/Claude Projects/Learn From/learnings/YYYY-MM-DD-<source-slug>.md`

Where `<source-slug>` is derived from the source:
- Repo: repo name (e.g., `autoresearch`)
- Paper: first-author-lastname + key topic (e.g., `karpathy-autoresearch`)
- Web: domain + slug (e.g., `simonwillison-prompt-injection`)

**Stages completed:** If the user used early exit, note which stages ran.

Write the document:

```markdown
---
source_url: [URL]
source_type: repo | paper | web
date: YYYY-MM-DD
focus: [focus area or "broad"]
tags: [3-7 relevant tags extracted from analysis]
stages_completed: [1, 2/3, 4, 5, 6]
---

# Learnings: [Source Name]

## Layer 1: Understanding the Source

[Summary of what the source is and how it works. This is the "blog post"
layer — someone reading this should understand the source without having
seen it. Include: what it is, who made it, key concepts, architecture
decisions, notable patterns. Draw from the Stage 1 reading output.]

## Layer 2: Applicable Patterns

[Mapped patterns with gaps, experiments, and reasoning. This is the
"what does this mean for us" layer. Draw from the Stage 4 mapping and
Stage 5 analysis. Include: pattern mappings, contradictions, experiment
proposals, what NOT to adopt. Skip this section if mapping stage didn't run.]

## Key Takeaways

[3-5 bullet points of the most actionable insights. Each should be
concrete enough to act on without reading the full document.]

## Experiments Proposed

[Bounded experiments from Stage 5, refined by user input. Each with:
scope, metric, time-box, reversibility. Skip if Stage 5 didn't run.]

## Decided Not to Adopt

[Patterns considered but rejected, with reasoning. This is valuable
context for future sessions — prevents re-evaluating the same patterns.]
```

### 6b. Propose CC memories

For the most actionable patterns (typically 1-3), propose memory files.
Present each one to the user and wait for approval before creating.
No automatic memory creation — the user approves each individually.

Use AskUserQuestion for each proposed memory:
> "I'd like to save this as a CC memory so it influences future work:
>
> **Name:** `pattern-name-from-source`
> **Type:** reference
> **Content:** [2-3 sentence distillation + how to apply]
>
> Save this memory?"

If approved, write to the Learn From project's memory directory:
`~/.claude/projects/-Users-Aakash-Claude-Projects-Learn-From/memory/<name>.md`

(This directory is indexed by qmd's `cc-memories` collection, making the
memory searchable from any project.)

Use the standard memory format:
```markdown
---
name: pattern-name
description: One-line description for relevance matching
type: reference
---

Learned from: [SOURCE_URL]

[Core insight in 1-2 sentences]

**How to apply:** [Concrete guidance for when and how to use this pattern]
```

Then update the project's `MEMORY.md` with a pointer to the new file.

### 6c. Report completion

> "Learning saved to `learnings/YYYY-MM-DD-<slug>.md`.
> [N] CC memories created: [list names].
>
> This learning is now part of your knowledge library. Future `/learn-from`
> sessions will query it for compounding insights via qmd."
