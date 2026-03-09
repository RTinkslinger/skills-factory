# Skill Craft: Expert-First Skill Development

> The art of transferring expertise, not writing instructions.

---

## The Philosophy

**Skills don't teach Claude what to do. They teach Claude how to think.**

A skill should transform Claude from a general-purpose assistant into a domain expert. Not by giving it steps to follow, but by transferring the mental models, intuitions, and judgment calls that experts carry.

### Four Core Truths

1. **Expertise Transfer, Not Instructions**
   - Make Claude *think* like an expert, not follow a checklist
   - Transfer mental models, not procedures
   - Give Claude the "why" so it can derive the "how"

2. **Flow, Not Friction**
   - Produce output, not intermediate documents
   - Every step should move toward the deliverable
   - If it doesn't produce value, cut it

3. **Voice Matches Domain**
   - Sound like a practitioner, not documentation
   - A finance skill should read like a CFO thinks
   - A design skill should feel like a senior designer's internal monologue

4. **Focused Beats Comprehensive**
   - Constrain ruthlessly
   - Every section earns its place
   - A 500-word skill that nails one thing beats a 5000-word skill that covers everything

---

## The Process

### 1. Understanding

**Goal:** Define the skill's territory with clarity.

Ask:
- What specific problem does this skill solve?
- What would a user say that should trigger this skill?
- What does success look like?
- What should this skill explicitly *not* do?

**Output:** One paragraph that an expert would nod at.

### 2. Exploring

**Goal:** Find where Claude fails without guidance.

Do:
- Try the task without any skill
- Note where Claude hesitates, asks unnecessary questions, or takes wrong paths
- Identify the specific knowledge gaps

**Output:** List of failure modes and knowledge gaps.

### 3. Research

**Goal:** Go deep on the domain.

Do:
- Study how practitioners actually work
- Find the tacit knowledge that experts don't write down
- Identify the decision frameworks experts use
- Collect real examples, not theoretical ones

**Output:** Raw notes, examples, patterns from actual practice.

### 4. Synthesis

**Goal:** Extract principles from research.

Do:
- Distill patterns into transferable mental models
- Identify the 3-5 key insights that change everything
- Find the "one weird trick" experts know
- Separate the essential from the comprehensive

**Output:** Core principles that fit on one page.

### 5. Drafting

**Goal:** Write the initial skill.

Rules:
- Start with the mental model, not the procedure
- Write in the voice of the domain
- Include only what earns its place
- Aim for 1000-2000 words (less is better)

Structure:
```
# [Skill Name]

[One sentence: what this skill makes Claude]

## The Mindset
[How an expert thinks about this domain]

## Core Principles
[3-5 key insights that change everything]

## The Work
[What to actually do - but driven by principles, not steps]

## Patterns
[Common situations and how an expert handles them]

## Traps
[What looks right but isn't - expert judgment calls]
```

### 6. Self-Critique

**Goal:** Test against quality criteria.

Checklist:
- [ ] Does it transfer expertise or just give instructions?
- [ ] Does reading it make you *think differently* about the domain?
- [ ] Could you remove 30% and still have the essence?
- [ ] Does it sound like documentation or like an expert thinking?
- [ ] Does every section earn its place?
- [ ] Would an expert recognize themselves in it?

### 7. Iterating

**Goal:** Fix gaps, incorporate feedback, tighten.

Do:
- Cut everything that doesn't transfer expertise
- Strengthen the mental models
- Add examples only where understanding requires them
- Get domain expert feedback if possible

### 8. Testing

**Goal:** Use the skill on a real scenario.

Do:
- Run a real task with the skill loaded
- Watch for: hesitation, wrong assumptions, unnecessary questions
- Note where the skill helps and where it doesn't
- Compare output quality to expert output

**Success Criteria:**
- Claude moves with confidence
- Output matches expert quality
- No unnecessary detours

### 9. Finalizing

**Goal:** Codify the optimal structure.

Do:
- Lock in the structure that worked
- Document any supporting resources needed
- Write the description/triggers for auto-loading
- Archive research for future iterations

---

## The Structure

```
skill-name/
├── SKILL.md            # The expertise transfer (required)
├── references/         # Deep-dive material (loaded as needed)
├── examples/           # Real-world examples (not tutorials)
└── scripts/            # Utilities that experts would have
```

### SKILL.md Anatomy

```yaml
---
name: skill-name
description: This skill should be used when the user asks to "X", "Y", or "Z".
  Transforms Claude into [expert type] for [domain].
---
```

```markdown
# [Domain] Expertise

[One line: the transformation this skill creates]

## The Mindset

[How experts think about this domain. Not what they do, but how
they see. The mental models that drive their decisions.]

## Core Principles

[3-5 insights that separate experts from novices. Each should
change how you approach problems in this domain.]

## The Work

[What actually gets done. But framed around the principles,
not as disconnected steps. Each action flows from understanding.]

## Patterns

[Common situations. How an expert recognizes them.
What they do. Why that's the right call.]

## Traps

[What looks right but isn't. The mistakes that seem reasonable.
The judgment calls that require expertise.]
```

### What Goes Where

**SKILL.md (always loaded when triggered)**
- Mental models and mindset
- Core principles (the 3-5 insights)
- Essential patterns and traps
- ~1000-2000 words

**references/ (loaded when Claude needs depth)**
- Detailed examples with analysis
- Edge cases and advanced patterns
- Technical specifications
- Historical context

**examples/ (loaded for specific scenarios)**
- Real artifacts from real work
- Before/after comparisons
- Annotated examples

**scripts/ (executed without reading)**
- Utilities an expert would have
- Validation tools
- Generation helpers

---

## Anti-Patterns

### The Checklist Skill
**Symptom:** Reads like a procedure manual.
**Problem:** Claude follows steps without understanding.
**Fix:** Ask "what mental model would make these steps obvious?"

### The Encyclopedia Skill
**Symptom:** Comprehensive coverage of everything.
**Problem:** No focus, Claude drowns in information.
**Fix:** Cut 50%. Then cut another 30%.

### The Documentation Skill
**Symptom:** Sounds like official docs.
**Problem:** No expert voice, no tacit knowledge.
**Fix:** Rewrite as if explaining to a capable peer.

### The Procedure Skill
**Symptom:** Heavy on "do this, then that."
**Problem:** Doesn't transfer judgment.
**Fix:** Replace procedures with principles + examples.

---

## Quality Signals

**Strong Skill:**
- You learn something reading it
- An expert would say "yeah, that's how I think about it"
- Claude moves with confidence when using it
- Output matches expert quality
- Could explain *why* to do something, not just what

**Weak Skill:**
- Reads like documentation
- Lists steps without reasoning
- Claude still asks clarifying questions
- Output is competent but generic
- Heavy on procedure, light on judgment

---

## The Test

After writing a skill, ask:

> "If I gave this to a smart person who knew nothing about the domain,
> would they start *thinking* like an expert, or just *following* like a novice?"

If the answer is "following," the skill needs work.

---

## Example Transformation

### Before (Instruction-based)
```markdown
## How to Write Cold Emails

1. Research the prospect
2. Write a compelling subject line
3. Open with a hook
4. Explain your value proposition
5. Include a clear CTA
6. Keep it under 150 words
```

### After (Expertise-based)
```markdown
## The Mindset

Cold email is pattern interruption. The recipient's default is delete.
Your job is to create enough curiosity to earn a response, not to sell.

## Core Principle

**Relevance beats cleverness.** A boring email that's clearly relevant
gets replies. A clever email that could be sent to anyone gets deleted.

The expert question: "What do I know about THIS person that makes
THIS message specifically for THEM?"

## The Work

Before writing: Find the hook. What's happening in their world right now
that makes you relevant? New funding, job change, company news, content
they published. If you can't find a hook, don't send the email.

The email itself: One insight, one question. The insight proves you
understand their world. The question opens a conversation. Everything
else is noise.

## Trap

The "value proposition" trap. Novices explain what they offer. Experts
know the recipient doesn't care what you offer. They care what's
relevant to their current situation.
```

---

## Integration with Standard Process

This methodology works alongside the technical skill structure. Use the standard structure (`SKILL.md`, `references/`, etc.) but fill it with expertise, not instructions.

The technical checklist (frontmatter, triggers, file structure) handles *how skills are loaded*.

This methodology handles *what skills contain*.

Both are necessary. Neither is sufficient alone.
