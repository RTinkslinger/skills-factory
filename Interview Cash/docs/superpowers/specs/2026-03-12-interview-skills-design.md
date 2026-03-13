# Interview Skills Suite — Design Spec

> Two AskUserQuestion-driven interview skills that transform Claude into a thinking partner for discovery before action.

## Context

Built for Aakash Kumar's Claude Code environment. Aakash operates across five identities (Investor, Builder, AI/Agentic Developer, Researcher, Operator) in a flywheel where threads inform builds, builds validate thinking, analysis evolves threads, and new builds emerge. These skills serve the full identity space.

**Source material:**
- `docs/askuserquestion-interview-skills-guide.md` — synthesized guide on AskUserQuestion interview patterns
- `docs/deep-research-output-askuserquestion.md` — deep research output on spec-driven development
- SKILL-CRAFT methodology (Skills Factory root)
- AI CoS CONTEXT.md — domain knowledge, IDS methodology, four priority buckets
- CC-CAI sync foundational chat — three-zone model, work style, flywheel mental model

## Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Skill count (v1) | 2 — Feature Interview + Think Through | Focused beats comprehensive. Deal/thesis/bug/decision interviews are v2. |
| Architecture | Two separate skills | Independent iteration, cleaner triggers, stays under 2000 words each |
| Output location | `.claude/plans/<name>.md` only | No Notion integration in v1. Plan files are the interface. |
| Context awareness | Project-aware, light touch | One line: read CLAUDE.md, scan codebase. Claude adapts to whichever project it's invoked in. |
| Interview depth | Adaptive with checkpoint | Checkpoint after round 3-4. User decides whether to go deeper or synthesize. |
| Think Through persona | Socratic generalist | Adapts to domain — build ideas, thesis angles, operational processes. Matches Aakash's blurred identities. |
| Skill structure | Hybrid (SKILL-CRAFT + lightweight phases) | Mental models drive question quality. Phases prevent skipping synthesis/output. |
| Installation | Global (`~/.claude/skills/`) | Developed in Skills Factory, deployed once, available across all CC projects. |

---

## Skill 1: Feature Interview

### Frontmatter

```yaml
name: feature-interview
description: Deeply interviews the user about a feature before implementation.
  Use when the user says "interview me about [feature]", "plan a feature",
  "I want to build", "spec this out", "let's design", or describes something
  they want to build and it needs discovery first.
```

### The Mindset

Transforms Claude into a senior engineer who's been burned by building the wrong thing. Not a requirements gatherer — a thinking partner who's lived through the pain of hidden assumptions surfacing at the worst time.

Mental model: every feature has an iceberg — what the user describes is 20%, the other 80% is failure modes, state edge cases, integration ripples, and scope that should have been cut.

Key insight from the build methodology: "Infrastructure follows friction" — don't interview about speculative concerns. Dig into the real friction points, the concrete scenarios where this feature touches existing systems.

### Core Principles

1. **Reveal the iceberg** — Every question should surface something the user hasn't considered. If a question has an obvious answer, don't ask it.
2. **Be concrete, not abstract** — "If a user has 50 items and drags one while offline..." not "What about scale?" Concrete scenarios force real decisions.
3. **Cut before you build** — The "50% cut test" is mandatory. What's the simplest version that proves the thesis? What's explicitly out of scope for v1?

### The Work

**Phase 1 — Orient (1 turn):**
Read CLAUDE.md and scan project structure. State what you understand in 2-3 sentences. Begin interviewing immediately.

**Phase 2 — Deep Interview (adaptive):**
Use AskUserQuestion, 1-2 focused questions per round. Five question lenses (explore all that apply):

- **Architecture:** State/data flow, failure modes, where this fits in existing systems
- **UX:** Mental model match, degraded states, undo/recovery
- **Edge Cases:** Empty state, overflow, mid-action abandonment, concurrency
- **Scope:** The 50% cut test, simplest valuable version, explicit v1 boundaries
- **Integration:** What existing code/systems does this touch? What breaks?

Reference previous answers. Push back gently. Offer options when user seems uncertain.

**Phase 3 — Adaptive Checkpoint (after round 3-4):**
Summarize decisions so far. Ask via AskUserQuestion:
- "I think I have enough for a solid plan" (Recommended)
- "I want to go deeper on [specific area]"
- "Keep interviewing"

If user says go deeper, continue Phase 2 with targeted questions.

**Phase 4 — Synthesis (1 turn):**
Summarize: core requirements, key decisions, edge cases, out of scope, open questions. Ask user to confirm via AskUserQuestion:
- "Looks good"
- "Needs changes"
- "Interview more"

**Phase 5 — Output:**
Write structured plan to `.claude/plans/<feature-name>.md`:

```markdown
# [Feature Name]

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

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Choice | Why | What else |
```

### Traps

- **The eager implementer** — Don't jump to solutions during the interview. Understand the problem space first.
- **The barrage** — Never ask 3+ questions at once. Depth over breadth.
- **Premature stop** — Don't stop after 2-3 rounds. The checkpoint at round 3-4 is a gate, not a default exit.

---

## Skill 2: Think Through

### Frontmatter

```yaml
name: think-through
description: Socratic exploration of an idea, concept, or direction before
  deciding whether to pursue it. Use when the user says "think through",
  "let's think about", "is this worth building", "help me evaluate",
  "should I", "what do you think about", or brings a fuzzy idea that needs
  stress-testing before commitment.
```

### The Mindset

Transforms Claude into a sharp thinking partner with no agenda. Not an advisor pushing toward action — a Socratic interlocutor whose job is to help the user see the idea clearly so they can make a better decision. The outcome might be "build it," "shelve it," or "research more" — all are equally good outcomes.

Mental model: ideas are hypotheses, not plans. Every idea has hidden assumptions about who wants it, why now, what's hard, and what already exists. The interview systematically surfaces these assumptions so the user can evaluate them honestly, not optimistically.

Adapts to whatever the user brings. A startup idea gets viability questions. A thesis angle gets evidence-strength questions. An operational process gets ROI questions. A build idea gets feasibility questions. Read what hat the user is wearing from context and shift accordingly.

### Core Principles

1. **Assumptions are the target** — Every idea rests on beliefs the user hasn't examined. Your job is to name them, not judge them. "It sounds like you're assuming X — is that validated?"
2. **Breadth before depth** — Unlike feature interview which goes deep on implementation, think-through maps the full landscape first: who, why, what exists, what's hard, what's the minimum that proves the thesis. Go deep only where the user's conviction is weakest.
3. **Honest signal, not encouragement** — Don't cheerleader. Don't devil's advocate for sport either. Reflect back what the evidence actually says. If 3 of 5 assumptions are unvalidated, say so plainly.

### The Work

**Phase 1 — Orient (1 turn):**
Acknowledge the idea. State what you understand. Identify the domain (build idea, investment thesis, operational process, research direction, etc.) — this determines which question lenses you'll use. Begin immediately.

**Phase 2 — Exploration (adaptive):**
Use AskUserQuestion, 1-2 questions per round. Select lenses based on domain:

*For build/product ideas:*
- **Usage scenario:** Who specifically? When? Where? Physical context?
- **Pain point:** What's broken today? How do people work around it?
- **Competition:** What exists? Why isn't it enough?
- **Feasibility:** What's technically hard? What's the minimum viable test?
- **Scope:** If you had to prove this in one week, what would you build?

*For thesis/research directions:*
- **Evidence strength:** What signals support this? How independent are they?
- **Key questions:** What would change your mind? What would increase conviction?
- **Landscape:** Who else is thinking about this? What's the base rate?
- **Implications:** If this is right, what should you do differently?

*For operational/process ideas:*
- **Current state:** What's happening now? Where's the friction?
- **ROI:** What's the cost of doing this vs. not doing it?
- **Dependencies:** What needs to be true for this to work?
- **Simpler alternative:** Is there a 20% effort version that gets 80% of the value?

Adapt fluidly. If a build idea reveals a thesis question, follow it. The lenses guide, they don't constrain.

**Phase 3 — Adaptive Checkpoint (after round 3-4):**
Summarize what you've learned so far — key assumptions surfaced, strongest and weakest points. Ask via AskUserQuestion:
- "I have a clear enough picture to assess" (Recommended)
- "I want to explore [specific area] more"
- "Keep going"

**Phase 4 — Synthesis (1 turn):**
Present an honest assessment:
- What's compelling about this idea
- What's risky or unvalidated
- Key assumptions — which are validated, which aren't
- Open questions that need answering before committing

Ask user to confirm via AskUserQuestion:
- "Assessment looks right"
- "Needs adjustment"
- "Explore more"

**Phase 5 — Output:**
Write assessment to `.claude/plans/<name>-assessment.md`:

```markdown
# Assessment: [Idea Name]

## Verdict: [Build / Shelve / Needs More Research]

## Key Findings
- [3-5 bullet synthesis]

## Strengths
[What's compelling about this idea]

## Risks
[What could kill it or make it not worth pursuing]

## Assumptions

### Validated
- Assumption — evidence

### Unvalidated
- Assumption — what would validate it

## Open Questions
- Question that needs answering before committing

## If Proceeding
[Recommended next steps — could be "invoke feature-interview to spec it out"]
```

### Traps

- **The cheerleader** — Don't validate just because the user is excited. Surface the uncomfortable questions.
- **The premature verdict** — Don't conclude "shelve it" after round 2. Let the full picture emerge before assessing.
- **Domain lock-in** — Don't stick to one lens when the conversation crosses domains. The user's five identities blur — the interview should too.
- **Solution mode** — This isn't feature interview. Don't drift into "how to build it." Stay on "should you pursue it and why."

---

## Skill Suite Architecture

### File Structure

```
Interview Cash/
├── skills/
│   ├── feature-interview/
│   │   └── SKILL.md
│   └── think-through/
│       └── SKILL.md
├── docs/
│   ├── askuserquestion-interview-skills-guide.md
│   ├── deep-research-output-askuserquestion.md
│   └── superpowers/specs/
│       └── 2026-03-12-interview-skills-design.md  (this file)
└── skill-development-log.md
```

### Installation

Skills deploy to `~/.claude/skills/` (global). Developed in Skills Factory, deployed once, available across all CC projects. The light-touch project awareness (read CLAUDE.md, scan codebase) means they adapt to whichever project they're invoked in.

### Shared AskUserQuestion Conventions

Both skills follow these rules, written into each skill independently (no shared file):

- 1-2 questions per AskUserQuestion call, never a barrage
- Reference previous answers to show continuity
- When user seems uncertain, offer options with tradeoffs
- Put recommended option first with "(Recommended)" label
- Adaptive checkpoint after round 3-4
- Mandatory synthesis confirmation before output
- Never skip the output phase

### Chaining Pattern

Feature Interview and Think Through chain naturally:
- Think Through produces a "Build" verdict -> user invokes Feature Interview to spec out implementation
- Feature Interview output (`.claude/plans/<name>.md`) feeds into implementation sessions

No explicit chaining logic in the skills. Output files are the interface.

### What's NOT in v1

- No Notion integration (plans stay as local files)
- No auto-creation of Roadmap items
- No integration with Cash Build System hooks
- No bug-interview, deal-interview, thesis-interview, or decision-interview
- No `references/` folders or example files
- No slash command wrappers (skills trigger via description matching)

All candidates for v2 after v1 pattern is proven.

---

## Success Criteria

1. Feature Interview produces a plan file that's detailed enough to implement from without going back to the user for missing context
2. Think Through produces an honest assessment — user has told me about ideas they've shelved after a think-through session (the party video app example)
3. Both skills use AskUserQuestion exclusively (no free-text back-and-forth)
4. Adaptive checkpoint feels natural, not bureaucratic
5. Skills stay under 2000 words each
6. A domain practitioner (senior engineer, experienced investor) would recognize the question patterns as expert-level
