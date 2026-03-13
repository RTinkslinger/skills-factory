# Best-in-Class: AskUserQuestion Interview Skills in Claude Code

## Executive Summary

The `AskUserQuestion` tool is a built-in Claude Code tool that inverts the traditional prompt engineering dynamic — instead of you crafting the perfect prompt, Claude prompts *you*. When baked into Skills as multi-round interviews, it becomes the foundation of **spec-based development**: interview → spec → implement. This guide covers the tool's exact specification, the best open-source implementations, and how to build your own.

---

## 1. AskUserQuestion Tool Specification

### Schema (from CC system prompts)

```typescript
interface AskUserQuestionTool {
  questions: Question[];     // 1-4 questions per call (required)
  answers?: Record<string, string>;  // User answers collected (returned)
}

interface Question {
  question: string;     // Complete question text (required)
  header: string;       // Very short label, max 12 chars (required)
  multiSelect: boolean; // Allow multiple selections (required)
  options: Option[];    // 2-4 options per question (required)
}

interface Option {
  label: string;        // Display text, 1-5 words concise (required)
  description: string;  // Explanation of choice (required)
}
```

### Hard Constraints

| Constraint | Value |
|---|---|
| Questions per call | 1–4 |
| Options per question | 2–4 |
| Header max length | 12 characters |
| Label length | 1–5 words |
| Timeout | 60 seconds (SDK), varies in CLI |
| Free text | Users can always select "Other" / "Type something else" |
| Subagents | NOT available in subagents (Task tool) |

### System Prompt Guidance (from CC internals)

```
Use this tool when you need to ask the user questions during execution. 
This allows you to:
1. Gather user preferences or requirements
2. Clarify ambiguous instructions
3. Get decisions on implementation choices as you work
4. Offer choices to the user about what direction to take

If you recommend a specific option, make that the first option in the 
list and add "(Recommended)" at the end of the label.

Plan mode note: In plan mode, use this tool to clarify requirements or 
choose between approaches BEFORE finalizing your plan. Do NOT use this 
tool to ask "Is my plan ready?" or "Should I proceed?" — use 
ExitPlanMode for plan approval.
```

### Answer Flow

1. Claude calls `AskUserQuestion` with `questions` array
2. CLI renders questions with numbered options
3. User selects option number OR types free text
4. Response comes back as `answers` map: `{ "question text": "selected label" }`
5. Claude receives both original `questions` and `answers` to continue

---

## 2. The Spec-Based Development Pattern

The canonical workflow (per Anthropic's own docs and Thariq's original pattern):

### Step 1: Enter Plan Mode
`Shift+Tab` → cycle to `⏸ plan mode on`

### Step 2: Give a Minimal Prompt
```
I want to build [brief description]. Interview me in detail using the 
AskUserQuestion tool. Ask about technical implementation, UI/UX, edge 
cases, concerns, and tradeoffs. Don't ask obvious questions, dig into 
the hard parts I might not have considered. Keep interviewing until 
we've covered everything, then write a complete spec to SPEC.md.
```

### Step 3: Interview (5-10 rounds)
Claude asks AskUserQuestion repeatedly, building understanding.

### Step 4: Spec Output
Claude writes a structured spec file (SPEC.md, PRD.md, or `.claude/plans/<name>.md`).

### Step 5: New Session
Start fresh with: `"Read SPEC.md and implement it."`

**Why new session:** Clean context window, no interview noise. The spec is the compressed, decision-complete artifact.

---

## 3. Best Open-Source Implementations

### 3.1 Neonwatty's `feature-interview` (Best Reference)

**Source:** `neonwatty/claude-skills` on GitHub / playbooks.com

This is the most complete and battle-tested implementation. Key design decisions:

**Skill Frontmatter:**
```yaml
---
name: feature-interview
description: Deeply interviews the user about a feature idea before 
  implementation. Use this when the user says "interview me about 
  [feature]", "I want to create a new feature", "let's create a new 
  feature", "new feature", "plan a feature", or describes a feature 
  they want to build. Asks probing, non-obvious questions about 
  technical implementation, UI/UX decisions, edge cases, concerns, 
  tradeoffs, and constraints. Continues interviewing until the feature 
  is fully understood, then writes a detailed implementation plan.
---
```

**4-Phase Architecture:**

1. **Initial Understanding** — Read context, acknowledge what's understood
2. **Deep Interview** — Multi-round AskUserQuestion across 5 categories:
   - Technical Architecture (state/data flows, failure modes, race conditions, perf)
   - User Experience (mental model, slow connections, undo/recovery, a11y, mobile)
   - Edge Cases (empty state, too much data, mid-action navigation, concurrent edits)
   - Scope & Tradeoffs (explicit out-of-scope, 50% cut test, simplest valuable version)
   - Integration & Dependencies (existing features, API changes, testing, rollback)
3. **Synthesis** — Summarize 5 things: core reqs, key decisions, edge cases, out-of-scope, open questions. **Get user confirmation.**
4. **Write the Plan** — Structured markdown to `.claude/plans/<feature-name>.md`

**Critical Instructions (what makes it good):**
```
Do not ask obvious questions. Instead, ask questions that:
- Reveal hidden assumptions
- Expose edge cases the user hasn't considered
- Uncover tradeoffs they'll need to make
- Challenge the proposed approach constructively
- Identify dependencies and constraints
```

**Interview Style Guidelines:**
- 1-3 focused questions at a time, not a barrage
- Reference previous answers (show you're listening)
- Push back gently: "What if..." / "Have you considered..."
- Be concrete: "If a user has 50 tables and drags one..." not "What about scale?"
- Offer options when user is uncertain: "We could A, B, or C—what resonates?"

**When to Stop:**
- Enough detail to write the implementation plan
- Further questions would be speculative/premature optimization
- User signals they want to move to planning
- DON'T stop just because a few questions were answered — thorough = 5-10 rounds

### 3.2 Neonwatty's `think-through` (Idea Validation Variant)

Not purely for implementation — designed for Socratic exploration of ideas *before* deciding to build. The real-world example on a party video sharing app produced 10 rounds covering:

1. Usage scenario (physical vs remote vs async?)
2. Actual pain point (what's broken today?)
3. Target audience (college vs millennials vs families?)
4. Beachhead market
5. Competitive landscape
6. Technical complexity
7. Scope constraints
8. Queue mechanics
9. Core value proposition
10. Business model

Result: User decided to **shelve** the idea. The interview saved weeks of building the wrong thing.

### 3.3 Neonwatty's `bug-interview` (Debug Variant)

Pre-investigates before touching code:
```
Ask probing questions about:
- Exact reproduction steps
- Environment details (browser, OS, network conditions)
- When it started happening
- What changed recently
- Patterns (does it happen every time? Only for certain users?)
```

**Why this matters:** Prevents Claude from seeing an error, making an assumption about the cause, and "fixing" something unrelated to the actual bug.

### 3.4 Thariq's Original Pattern (The Simplest Version)

From the Anthropic engineer who popularized this:
```
Read this plan file $1 and interview me in detail using the 
AskUserQuestionTool about literally anything: technical implementation, 
UI & UX, concerns, tradeoffs, etc. but make sure the questions are not 
obvious. Be very in-depth and continue interviewing me continually 
until it's complete, then write the spec to the file.
```

This is a **slash command** (`/interview $1`), not a full skill. Simpler, but no phased structure or question categories.

### 3.5 Workflow Generator Pattern (Approval Gates)

Neonwatty's iOS/browser workflow generators add a critical pattern: **mandatory approval gates**.

```
### Phase 6: Review with User (REQUIRED)
**This step is mandatory. Do not write the final file without user approval.**

Use AskUserQuestion to ask:
- "Do these workflows cover all the key user journeys?"
- Options: Approve / Add more workflows / Modify existing / Start over

**Only after explicit approval**, write to `/workflows/ios-workflows.md`
```

---

## 4. The Complete Implementation Pattern

Based on analyzing all the best implementations, here's the synthesized best-in-class pattern:

### Skill Structure

```
.claude/skills/
  interview/
    SKILL.md          # Main skill file
```

### Optimal SKILL.md Template

```markdown
---
name: interview
description: Interviews the user about any idea, feature, or problem 
  before implementation. Triggers on "interview me", "let's plan", 
  "I want to build", "spec this out", "think through", or any request 
  that benefits from discovery before action. Asks probing, non-obvious 
  questions using AskUserQuestion, then outputs a structured spec.
---

# Interview Skill

You are a senior engineer and product thinker conducting a thorough 
discovery session. Your job is to ask probing, insightful questions the 
user might not have considered — questions that reveal hidden complexity, 
edge cases, and design decisions that will affect implementation.

## Invocation

When triggered, determine the **interview type** from context:

| Signal | Type | Focus |
|--------|------|-------|
| Feature/product description | Feature Interview | Architecture, UX, scope |
| Bug report or error | Bug Interview | Reproduction, environment, patterns |
| Vague idea or exploration | Think-Through | Viability, audience, tradeoffs |
| Existing spec/plan file | Spec Refinement | Gaps, edge cases, assumptions |

## Process

### Phase 1: Acknowledge & Orient (1 turn)

Read any context provided. State what you understand so far in 2-3 
sentences. Identify the interview type. Then begin Phase 2 immediately.

### Phase 2: Deep Interview (5-10 rounds)

Use AskUserQuestion repeatedly. Follow these rules:

**Question Quality Rules:**
- NEVER ask obvious questions ("What should the button color be?")
- ALWAYS ask questions that reveal hidden assumptions
- ALWAYS push gently on stated requirements ("What if...")
- Reference previous answers to show continuity
- Ask 1-2 focused questions per round, not a barrage
- Be concrete, not abstract ("If they have 50 items and drag one..." 
  not "What about scale?")
- When the user seems uncertain, offer options with tradeoffs

**Question Categories (explore all relevant ones):**

For **Feature Interviews:**
- Architecture: state/data flow, failure modes, race conditions, perf
- UX: mental model match, offline/slow behavior, undo, accessibility
- Edge Cases: empty state, overflow, mid-action abandonment, concurrency
- Scope: explicit v1 cuts, "cut 50%" test, simplest valuable version
- Integration: existing system impact, API changes, testing, rollback

For **Bug Interviews:**
- Reproduction: exact steps, frequency, user-specific?
- Environment: OS, browser, network, recent changes
- Timeline: when started, what changed, any pattern to timing
- Impact: who's affected, workarounds, severity
- Prior investigation: what's been tried, logs available?

For **Think-Through:**
- Usage scenario: who, when, where, physical context
- Pain point: what's broken today? how do they work around it?
- Audience: who specifically? what's the beachhead?
- Competition: what exists? why isn't it enough?
- Viability: technical complexity vs value delivered
- Business: monetization, distribution, retention
- Scope: what's the minimum that proves the thesis?

For **Spec Refinement:**
- Gaps: what's missing from the spec?
- Assumptions: what's stated but not validated?
- Edge cases: what happens when X goes wrong?
- Dependencies: what external factors could block this?

### Phase 3: Synthesis (1 turn)

Summarize:
1. Core requirements / problem definition
2. Key decisions made during interview
3. Edge cases to handle
4. Explicitly out of scope
5. Open questions that need research or external input

Ask user to confirm synthesis is accurate using AskUserQuestion:
- Options: Looks good / Needs changes / Interview more

### Phase 4: Output

**For Feature/Spec interviews:** Write to `.claude/plans/<name>.md`:

```
# [Name]

> [One-line description]

## Summary
[2-3 paragraphs: what we're building and why]

## Requirements

### Must Have
- [ ] Requirement

### Should Have  
- [ ] Requirement

### Out of Scope
- Item

## Technical Design

### Architecture
[System fit, data flow, state changes]

### Key Components
[Create/modify, with responsibilities]

### Data Model
[Schema, types, state shape]

## Implementation Plan

### Phase 1: [Foundation]
1. Step

### Phase 2: [Core]
1. Step

### Phase 3: [Polish]
1. Step

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Case | Approach |

## Testing Strategy
- Unit: [what]
- E2E: [critical flows]
- Manual: [exploratory areas]

## Open Questions
- [ ] Question

## Decision Log

| Decision | Rationale | Alternatives |
|----------|-----------|-------------|
| Choice | Why | What else |
```

**For Think-Through:** Write to `.claude/plans/<name>-assessment.md`:

```
# Assessment: [Idea Name]

## Verdict: [Build / Shelve / Needs More Research]

## Key Findings
[3-5 bullet synthesis]

## Strengths
[What's compelling]

## Risks
[What could kill it]

## Open Questions
[What needs answering before building]

## If Proceeding
[Recommended next steps]
```

**For Bug Interviews:** Write to `.claude/plans/debug-<name>.md`:

```
# Debug: [Bug Description]

## Symptoms
[What's happening]

## Environment
[Where/when it happens]

## Hypothesis
[Most likely cause based on interview]

## Investigation Plan
1. Check X
2. Verify Y
3. Test Z

## Information Gaps
[What we still don't know]
```

## When to Stop Interviewing

Stop when:
- You have enough detail to write the output document
- Further questions would be speculative or premature optimization
- User signals they want to move forward
- You're going in circles on the same topic

Do NOT stop just because 2-3 questions were answered. A thorough 
interview typically takes 5-10 rounds. A think-through can go 10+.
```

---

## 5. Advanced Patterns

### 5.1 Conditional Branching

Within AskUserQuestion, you can't do programmatic branching — but you 
can instruct Claude to branch its questioning path based on answers:

```
If the user selects "Mobile-first" in the platform question, 
focus subsequent questions on:
- Offline/sync strategy
- Touch interaction patterns
- Push notification design
```

This is done through natural language instruction in the skill, not code.

### 5.2 Integration with CLAUDE.md

After an interview produces a spec, you can instruct the skill to append 
key decisions to CLAUDE.md for persistence:

```
After writing the plan, append a section to CLAUDE.md:

## Recent Interview Decisions
- [Date]: [Feature] — [Key architectural choice]
```

### 5.3 Chaining Interview → Implementation

Two-skill pattern:
1. `/interview <feature>` → produces spec at `.claude/plans/feature.md`
2. User starts new session: "Implement `.claude/plans/feature.md`"

Or within the same session:
```
After writing the plan, ask:
"Ready to implement this plan?"
- Options: Yes, start implementing / Let me review first / Save for later
```

### 5.4 The "Recommended" Pattern

From the CC system prompt: put your recommended option first and add "(Recommended)" to the label. This guides without forcing:

```
options: [
  { label: "SQLite (Recommended)", description: "Simple, embedded, good for single-user" },
  { label: "PostgreSQL", description: "Scalable, but adds deployment complexity" },
  { label: "Redis", description: "Fast, but ephemeral by default" }
]
```

### 5.5 Plan Mode + Custom Skill Combo

Best approach for AI CoS-type features:
1. **Custom skill** for the structured interview (repeatable, category-aware)
2. **Plan Mode** as fallback for ad-hoc interviews when no skill applies
3. **Never overlap** — if you have a relevant skill, use it over Plan Mode

---

## 6. Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|---|---|---|
| Asking obvious questions | Wastes user's time, erodes trust | "Do not ask obvious questions" instruction |
| Too many questions per round | Overwhelms, feels like a form | Max 1-2 per AskUserQuestion call |
| No synthesis before output | Misunderstandings compound | Always confirm synthesis |
| Skipping approval gate | Output doesn't match intent | Mandatory "confirm?" step |
| Interviewing forever | Diminishing returns after ~10 rounds | Define clear stopping criteria |
| Not referencing previous answers | Feels like a survey, not a conversation | "Reference their previous answers" |
| Generic categories only | Miss domain-specific concerns | Add project-aware categories |
| Writing spec without interview | Defeats the purpose | Enforce Phase 2 minimum (5 rounds) |
| No progressive summarization | User loses track of what's decided | Summarize decisions-so-far every 3-4 rounds |
| Missing the "50% cut" question | Scope stays bloated, v1 is huge | Always ask "If you had to cut 50%, what stays?" |

---

## 7. Key Insight

From the Atcyrus analysis:

> "For years, we've obsessed over prompt engineering — crafting the 
> perfect instructions to get AI to do what we want. The AskUserQuestion 
> tool quietly inverts this relationship. Now the model prompts *you*."

The power isn't just in getting better specs. It's that **each question 
is a fork in the road** — each answer narrows the solution space. By the 
time Claude starts coding, you've navigated the decision tree together 
and have a clear record of every choice.

---

## Sources

- Neonwatty/claude-skills: github.com/neonwatty/claude-skills
- Thariq's gist: gist.github.com/robzolkos/40b70ed2dd045603149c6b3eed4649ad
- Claude Code system prompts: github.com/Piebald-AI/claude-code-system-prompts
- Anthropic Agent SDK docs: platform.claude.com/docs/en/agent-sdk/user-input
- Claude Code best practices: code.claude.com/docs/en/best-practices
- Claude Code skills docs: code.claude.com/docs/en/skills
- Atcyrus AskUserQuestion guide: atcyrus.com/stories/claude-code-ask-user-question-tool-guide
- Stormy AI blog: stormy.ai/blog/claude-code-planning-ask-user-question-tool-prds
- CC internal tools gist: gist.github.com/bgauryy/0cdb9aa337d01ae5bd0c803943aa36bd

---

## AI CoS Relevance

### Thesis Connections
- **Agentic AI Infra**: AskUserQuestion is a primitive for human-in-the-loop agentic workflows. The pattern of Claude prompting the human (inverting prompt engineering) is a design pattern that will show up in every serious agent framework. Composio/Smithery should be tracking this.
- **SaaS Death / Agentic Replacement**: Spec-based development is the agentic replacement for Jira/Linear ticket writing. The Cyrus example (AskUserQuestion piped into Linear issues) shows exactly this — the agent asks clarifying questions asynchronously inside the project management tool itself.

### Concrete AI CoS Build Actions
1. **Create a `deal-interview` skill** for Claude Code that IDS-interviews you after founder meetings. Categories: product thesis, team quality, market dynamics, technical moat, key concerns, conviction signals. Output: structured `.claude/plans/deal-<company>.md` that maps to your IDS notation (+, ++, ?, ??). This is PostMeetingAgent territory.
2. **Create a `thesis-interview` skill** that interviews you when creating new thesis threads — forces you to articulate key questions, investment implications, and conviction level before writing to the Thesis Tracker.
3. **The AskUserQuestion → Actions Queue pattern**: Interview outputs could auto-generate scored actions for the Actions Queue. A deal interview that surfaces "need to check Apple policy implications" → P1 Research action.

### Build Roadmap Impact
The interview skill pattern maps directly to the PostMeetingAgent design. Instead of Granola transcription → auto-extract, you'd have: Granola transcription → AskUserQuestion interview about what was notable → structured deal assessment → Actions Queue entries. The human-in-the-loop via AskUserQuestion is the right trust level for early PostMeetingAgent (Suggest tier, not Auto-act).
