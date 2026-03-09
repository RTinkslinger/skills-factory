# Email Agent Skill - Development Log

> Skill development interview and decisions log
> Started: January 10, 2026

---

## Overview

**Skill Purpose:** Give agents human-like email capabilities using AgentMail infrastructure.

**Scope:**
- Global skill for all Claude projects
- Primary use: Claude Agent SDK agents (autonomous, conversational)
- Secondary use: Reference patterns for programmatic/application email

**Methodology:** SKILL-CRAFT (expertise transfer, not instructions)

---

## Topic 1: Vision ✓

### The Autonomy Model

**Core insight:** Make Claude think like a "confident collaborator" - acts decisively when it knows, asks when it doesn't, learns from human's judgment, gradually earns more autonomy.

**Confidence-based decision making:**

| Confidence Level | Action |
|------------------|--------|
| HIGH | Act autonomously |
| MODERATE-HIGH | Act, but log for human review |
| MODERATE | Draft, don't send (human approves) |
| LOW | Flag for human attention (human handles) |
| NEAR-BOTTOM | Defer entirely (don't touch) |

**Certainty types:**
- **Factual/Scope certainty:** Achieved through communication (ask if unsure)
- **Alignment certainty:** Learned from history (pattern matching on past human decisions)

**Initial confidence hierarchy (for new agents):**

| Scenario | Default Confidence | Default Action |
|----------|-------------------|----------------|
| Routine reply to known contact, known topic | HIGH | Act autonomously |
| New contact, simple inquiry | MODERATE-HIGH | Act, log for review |
| Known contact, unfamiliar topic | MODERATE | Draft for approval |
| Anything involving money, commitments, sensitive info | LOW | Flag for human |
| Complaints, conflicts, legal mentions | NEAR-BOTTOM | Defer entirely |

**The Learning Loop:**
Agent starts conservative → observes how human handles flagged items → builds alignment memory → gradually expands autonomous zone over time.

**Human-Agent Relationship:**
- Human is collaborator, not boss
- Human is final guide when agent is uncertain
- Agent optimizes for human satisfaction

**Key capabilities to transfer:**
1. **Cognitive:** Reading context, understanding intent, deciding what matters
2. **Relational:** Remembering who people are, relationship history, appropriate tone
3. **Judgmental:** When to reply, what warrants response, when to escalate
4. **Organizational:** Lighter touch - context-specific to future agents

---

## Topic 2: Two Contexts Problem ✓

### Decision: Two Separate Concerns

**Agent Context (Skill):**
- Conversational, autonomous
- Confidence-based decision making
- Relationship awareness
- Memory and learning
- "Check my inbox and handle what you can"

**Application Context (Reference Architecture):**
- Programmatic, deterministic
- Pattern-based (retry, queue, log)
- No relationship management
- "Send this notification to these users"

### Implementation Approach

**Option A selected:** Single skill with references folder
- `SKILL.md` - The confident collaborator expertise
- `references/infrastructure.md` - Programmatic patterns

**Plus:** Standalone reference folder at `/Users/Aakash/Claude Projects/Documents/Agentmail Refs/` for projects that only need infrastructure patterns.

**Files created in Agentmail Refs:**
- `agentmail-overview.md` - What AgentMail is, features
- `agentmail-api-reference.md` - All endpoints, methods
- `agentmail-quickstart.md` - Get sending in 5 minutes
- `agentmail-infrastructure-patterns.md` - Production patterns

---

## Topic 3: Identity & Ownership ✓

### Identity Model

**Context-dependent** with **Agent as Entity** as primary mode.
- Sometimes agent is entity (own identity)
- Sometimes proxy (on behalf of human)
- Sometimes assistant ("I'm Alex's assistant...")

**Multi-agent:** Each agent has its own inbox.

### Identity Persistence

**Decision:** Builder controls identity; skill provides mechanism.

The skill defines:
- Identity schema
- Identity loading pattern
- Default behavior
- Identity ↔ Memory relationship

The skill does NOT dictate:
- Where identity is stored (builder's choice)
- Per-project vs global vs dynamic (builder's choice)
- How many agents share identity (builder's choice)

### Identity Schema (Final)

```
Required:
- name: string          # What the agent calls itself
- email: string         # AgentMail address
- inbox_id: string      # For API operations
- persona: string       # Few sentences defining style/approach

Optional (builder-provided):
- sample_emails: file   # Reference to examples document
- [extensions]          # Builder can add their own
```

### Default Behavior

If builder doesn't provide identity → **Prompt for identity setup**

### Identity Mutability

**Fixed once loaded.**

Rationale:
- Core identity (email, name, inbox_id) must be fixed for threading, trust
- Persona base is fixed; behavioral adaptations go in memory, not identity
- Simplicity for V1; evolution is V2 concern

---

## Topic 4: Memory ✓

### Memory Priority (Contact-Centric)

```
1. Contacts ─────────────┐
   │                     │ ROOT - all memory anchors here
   ├─→ 2. Conversation History (with contact)
   ├─→ 3. Tasks/Follow-ups (about contact)
   ├─→ 4. Instructions/Preferences (per contact or global)
   └─→ 5. Alignment Memory (learned from interactions)
```

**Key insight:** Contacts is the root. Memory is relationship-centric.

### Memory ↔ Identity Link

**Memory is tied to identity.**
- Each identity has its own memory
- Same agent code + different identity = different memories
- Same identity across instances = shared memory

### Remember vs Lookup Philosophy

**Core principle:** "Remember interpretations, lookup facts."

| Data Type | Where? | Why |
|-----------|--------|-----|
| Raw email content | Lookup (AgentMail) | Source of truth |
| Email metadata | Lookup (AgentMail) | Factual, queryable |
| Thread structure | Lookup (AgentMail) | AgentMail manages |
| Learned preferences | Remember | Interpretation |
| Extracted knowledge | Remember | Derived insight |
| Tasks/commitments | Remember | Agent's obligations |
| Relationship context | Remember | Agent's perspective |
| Alignment learnings | Remember | How human handled cases |

**The distinction:**
- **AgentMail = The RECORD** (what happened, objective, immutable)
- **Memory = The UNDERSTANDING** (what it means, subjective, accumulated)

### Memory Update Triggers

```
Email received:
  → Query AgentMail for content
  → Extract insights
  → Store interpretations in memory
  → Don't duplicate raw content

Email sent:
  → Log commitments made
  → Update contact last-interaction
  → Note alignment decisions

Periodically:
  → Refresh contact metadata
  → Clean up completed tasks
```

### Memory Bootstrap

**Default:** Cold start (build memory over time)

**Option:** Inherit memory from existing agent
- Enables agent continuity/succession
- Builder chooses what to inherit
- Snapshot (copy), not link

**Inheritance defaults:**
- Contacts: Yes (relationship knowledge valuable)
- Knowledge: Yes (learned facts still relevant)
- Tasks: Maybe (context-specific)
- Alignment Memory: Maybe (depends on same human collaborator)

---

## Topic 5: Failure Modes ✓

### Failure Modes Identified

| Failure Mode | Addressed By |
|--------------|--------------|
| Generic responses | Topic 4: Memory (relationship context) |
| No memory | Topic 4: Memory system |
| Missed follow-ups | Topic 4: Tasks/commitments in memory |
| Wrong confidence | Topic 1: Confidence model |
| No escalation sense | Topic 1: Confidence hierarchy + escalation triggers |
| Tone deafness | Topic 3: Persona + Topic 4: Contact preferences |
| Threading failures | Topic 2: AgentMail handles threading |
| Over-communication | Topic 1: Judgmental capability |

Plus implicit failures from Topics 1-4 (alignment learning, identity awareness, memory philosophy, etc.)

### Risk Priority

All risks matter equally:
- Embarrassment
- Relationship damage
- Commitment breach
- Legal/compliance risk ← **Most critical**
- Reputation damage

### Always-Escalate Triggers

**Financial:**
- Transaction commitments
- Contracts
- Invoices
- Payment requests

**Legal:**
- Explicit legal language (lawsuit, attorney, litigation, subpoena, etc.)

**Customizable:** Builders can add their own escalation keywords list.

### Escalation Mechanism

**Draft mode** selected.
- Agent drafts response but won't send without human approval
- Agent still contributes value
- Human maintains control
- Creates learning opportunity

### Graduated Autonomy Model

```
Escalations 1-9 (same type, same contact):
  → Draft mode
  → Human approves/edits
  → Agent logs to alignment memory
  → Confidence rises VERY slowly

Escalation 10+ (same type, same contact):
  → Agent asks: "Should I handle these autonomously for this contact?"
  → Human explicitly grants or denies autonomy
  → Autonomy is per-contact, per-escalation-type
```

Key: Agent asks, doesn't assume. Human controls autonomy upgrades.

---

## Topic 6: Success Scenario ✓

### Skill Positioning

**Horizontal capability:** The skill provides "how to handle email well" (domain-agnostic)
**Vertical specifics:** Builder provides "what this agent does with email" (domain-specific)

### Best Practices (Domain-Agnostic)

**1. Triggering Agent Work:**
- Event-driven (webhook) is ideal
- Also support: scheduled, manual, backlog processing
- Idempotency: never process same message twice
- Priority awareness: urgent before backlog

**2. Session Start (Checking Inbox):**
```
1. Load identity → Who am I?
2. Load session context → What was I doing?
3. Check pending tasks → What am I waiting on?
4. Fetch new messages → What's new?
5. Triage → Categorize by urgency, type, confidence
6. Build work queue → Priority order
```

**3. Routine Email Handling:**
```
1. Context loading → Sender lookup, relationship history
2. Understanding → Intent, sentiment, action items
3. Confidence check → Apply model
4. Response → Compose with persona if HIGH confidence
5. Memory update → Contact, knowledge, tasks
```

**4. Handling Uncertainty:**
- Recognize signals: new contact, unfamiliar topic, ambiguous intent
- Apply confidence model (draft/flag/defer based on level)
- Capture what made it uncertain
- Never guess when stakes high

**5. Escalation Handling:**
- Detect triggers (financial, legal, custom)
- Enter draft mode immediately
- Flag with context for human
- Log outcome for alignment learning
- At threshold (10): ask about autonomy upgrade

**6. Session End:**
- Complete or checkpoint in-progress work
- Create session summary
- Flush memory updates
- Document open items for handoff

**7. What Persists:**
| Persists | Lookup Instead |
|----------|----------------|
| Relationship info, preferences | Raw email content |
| Learned knowledge | Message metadata |
| Tasks, commitments | Thread structure |
| Alignment learnings | - |
| Session summaries | - |

### Differentiator

What makes agent email "better than expected":
- **Persona**: Consistent voice, context-appropriate
- **Short-term memory**: Knows what happened in conversation
- **Long-term memory**: Remembers across sessions, learns preferences

The "wow moment": Agent naturally references past interactions, adjusts tone based on learned preferences.

### Builder Success (10x Easier)

Memory and persona that are easy to:
- **Build**: Clear schema, good defaults
- **Modify**: Change without rebuilding
- **Control**: Visibility into what agent knows
- **Evolve**: Guide learning over time

### Success Criteria

The skill succeeds when:
1. Agent operates with right autonomy level
2. Persona feels natural and consistent
3. Memory creates relationship continuity
4. Escalations handled safely with graduated autonomy
5. Builder can iterate easily on persona and memory

---

## Decisions Summary

| Decision | Choice |
|----------|--------|
| Skill approach | Single skill + references folder |
| Primary mode | Agent as entity (confident collaborator) |
| Confidence model | 5-tier with learning loop |
| Identity schema | name, email, inbox_id, persona (required) |
| Identity mutability | Fixed once loaded |
| Memory structure | Contact-centric (root) |
| Memory ownership | Tied to identity |
| Memory philosophy | Remember interpretations, lookup facts |
| Memory bootstrap | Cold start default, inheritance optional |
| Escalation triggers | Financial + Legal (customizable) |
| Escalation mechanism | Draft mode |
| Graduated autonomy | After 10 similar escalations, ask to upgrade |
| Skill positioning | Horizontal capability (domain-agnostic) |
| Differentiator | Persona + Memory (short & long term) |
| Builder 10x | Easy to build/modify/control/evolve memory & persona |

---

## Phase: Understanding ✓

All 6 interview topics complete:
1. Vision ✓
2. Two Contexts Problem ✓
3. Identity & Ownership ✓
4. Memory ✓
5. Failure Modes ✓
6. Success Scenario ✓

---

## Phase: Exploring ✓

### Scenario Analysis

| Scenario | Gaps Confirmed |
|----------|----------------|
| First email to new contact | Identity loading, persona, memory check, confidence |
| Reply to known contact | Contact memory, preferences, task tracking |
| Financial commitment request | Escalation triggers, draft mode, alignment memory |
| Ambiguous email | Uncertainty signals, confidence tiers, flagging |
| Session handoff | Session lifecycle, persistence, handoff protocol |
| Builder setup | Schema clarity, setup guidance, builder experience |

### Gaps Summary

| Gap Category | Confirmed |
|--------------|-----------|
| Identity & Persona | ✓ |
| Memory (contacts, knowledge) | ✓ |
| Confidence Model | ✓ |
| Escalation & Safety | ✓ |
| Learning & Alignment | ✓ |
| Session Lifecycle | ✓ |
| Builder Experience | ✓ |

**Conclusion:** All gaps from Understanding phase confirmed. No major new gaps discovered.

---

## Phase: Research ✓

### Sources Studied
- Executive assistant email management best practices
- Email triage and prioritization systems
- Professional communication and tone matching
- Sales follow-up cadence and timing
- Escalation frameworks

### Key Practitioner Insights

**The 60-70% Rule (from EAs):**
Skilled assistants handle 60-70% independently. Maps to our confidence model.

**The Four D's (Triage):**
Delete, Do (<2 min), Delegate, Defer (schedule)

**Tone Matching:**
- Mirror recipient's style
- Greeting sets tone
- B2B = professional, B2C = warm
- Reference previous interactions naturally

**Follow-up Persistence (Sales):**
- 80% of sales require 5+ follow-ups
- 70% of responses come from emails 2-4
- Every follow-up must add value
- Day 1 → Day 3 → Day 7 → Day 10-14 cadence

**Escalation Triggers:**
- Tried normal channels first
- Reasonable time elapsed
- Stakes warrant escalation
- Always propose solutions, not just problems

### Tacit Knowledge Extracted

| Expert Instinct | What They Know |
|-----------------|----------------|
| When to respond | Urgent = now, Important = scheduled, Routine = batch |
| When to wait | Silence is sometimes strategic |
| Reading between lines | Tone, brevity, delay all signal something |
| When persistence = value | Follow-up isn't annoying if you add value |
| When to stop | After 4-5 attempts, respect silence |
| Relationship > transaction | Every email builds or erodes relationship |
| Context is everything | Same words, different relationship = different meaning |

---

## Phase: Synthesis ✓

### The Five Core Principles

**Principle 1: The Confident Collaborator**
Act decisively when you know. Ask when you don't. Learn from every interaction.
- HIGH confidence → Act
- MODERATE → Draft/log for review
- LOW → Flag for human
- Target: 60-70% handled independently
- Growth through demonstrated alignment

**Principle 2: Relationship Is The Root**
Every email exists in relationship context. Contacts are the center of everything.
- Contact is the root node for all memory
- Same words = different meaning based on who
- Tone matching is respect, not mimicry
- Before sending: Does this build or erode?

**Principle 3: Remember Understanding, Lookup Facts**
Your value is interpretation, not storage. Memory is what you learned, not what was said.
- Memory = understanding (preferences, knowledge, commitments, alignment)
- Record = facts (email content, metadata, threads)
- Don't duplicate. Interpret.

**Principle 4: Every Email Builds or Erodes**
No email is neutral. Every send either adds value or costs trust.
- Follow-up only with value to add
- "Just checking in" = withdrawal
- After 4-5 value-adds with no response, respect silence
- Match tone, pace, formality to recipient

**Principle 5: Know Your Limits, Protect The Principal**
Some things are never autonomous. Escalation is not failure, it's judgment.
- Financial/Legal = automatic escalation
- Draft mode = cheap insurance
- Autonomy is earned through 10+ similar escalations
- Agent asks for autonomy upgrades, never assumes

---

## Phase: Drafting ✓

### Files Created

**Skill Location:** `~/.claude/skills/email-agent/`

**Core Skill:**
- `SKILL.md` - Main expertise transfer (~1800 words)
  - The Five Principles
  - Session Lifecycle
  - Identity schema
  - Memory operations
  - Patterns and Traps

**Reference Files:**
- `references/memory-schema.md` - Complete database schema
  - Contacts, Knowledge, Tasks, Alignment Memory, Sessions, Instructions
  - Views for common queries
  - Common operations
  - PostgreSQL migration notes

- `references/session-lifecycle.md` - Detailed session management
  - Session start sequence
  - Email processing flow
  - Escalation flow
  - Session end sequence
  - Trigger patterns

- `references/escalation-config.md` - Escalation configuration
  - Default triggers (financial, legal)
  - Custom trigger configuration
  - Detection logic
  - Graduated autonomy settings
  - Monitoring and reporting

- `references/builder-setup.md` - Builder guide
  - AgentMail setup
  - Memory setup (SQLite/PostgreSQL)
  - Identity configuration
  - Custom escalation config
  - Testing checklist

- `references/infrastructure.md` - AgentMail infrastructure
  - Points to Agentmail Refs folder
  - Quick reference for MCP setup
  - Common patterns

---

## Phase: Self-Critique ✓

### Issues Identified

**Priority 1 (Must Fix):**
1. ~~"You" language throughout SKILL.md~~ → Fixed to imperative form
2. ~~Missing example files (identity, escalation config)~~ → Created

**Priority 2 (Should Fix):**
1. ~~Session Lifecycle too detailed in SKILL.md~~ → Condensed, moved details to references

### Fixes Applied

1. **Language fix** - Changed all second-person language to imperative form:
   - "Every email you send" → "Every email sent"
   - "Your value is interpretation" → "The value is interpretation"
   - "Act decisively when you know" → "Act decisively when certain"

2. **Session Lifecycle condensed** - Reduced detailed code blocks to 3-line summary, pointing to `references/session-lifecycle.md` for full detail

3. **Example files created:**
   - `examples/identity-example.md` - Complete agent identity with persona and sample emails
   - `examples/escalation-config-example.yaml` - Full escalation config with custom triggers

---

## Phase: Iterating ✓

No additional iteration needed - Self-Critique fixes addressed all identified issues.

---

## Phase: Testing ✓

### Test Scenario

Simulated an agent with Alex Chen identity receiving a pricing inquiry email.

**Email received:**
- From: sarah.jones@techstartup.io
- Subject: Pricing question - Team plan
- Content: 3 questions about cost, discounts, trial

### Agent Behavior Observed

| Check | Result |
|-------|--------|
| Confidence model | ✓ Assessed MODERATE-HIGH, capped for new contact |
| Escalation detection | ✓ Caught 3 financial triggers (pricing, cost, discount) |
| Action decision | ✓ Entered draft mode, didn't send autonomously |
| Persona application | ✓ Used Alex Chen's style, bullet points, clear next steps |
| Graduated autonomy | ✓ Referenced 10-similar threshold for future autonomy |
| Placeholder discipline | ✓ Left financials for human instead of guessing |

### Conclusion

Skill transfers expertise correctly. Agent demonstrated:
- Proper escalation behavior for financial content
- Persona-aligned drafting
- Understanding of the confidence model
- Awareness of the learning loop

---

## Phase: Finalizing ✓

### Final Skill Structure

```
~/.claude/skills/email-agent/
├── SKILL.md (8.5KB)
├── examples/
│   ├── identity-example.md
│   └── escalation-config-example.yaml
├── references/
│   ├── builder-setup.md
│   ├── escalation-config.md
│   ├── infrastructure.md
│   ├── memory-schema.md
│   └── session-lifecycle.md
└── scripts/ (empty)
```

### Word Counts

- SKILL.md body: ~1,800 words (target: 1,500-2,000) ✓
- Total references: ~12,000 words (progressive disclosure working)

### Quality Checklist

- [x] Frontmatter: name and description present
- [x] Description: Third-person with trigger phrases
- [x] Body: Imperative form throughout
- [x] Length: Under 2,000 words
- [x] References: All detailed content moved appropriately
- [x] Examples: Complete and realistic
- [x] Progressive disclosure: Core in SKILL.md, details in references

### Skill Complete

---

## Post-Finalization: Builder Guide Enhancement

### Changes Made

**1. `references/builder-setup.md`** - Comprehensive rewrite
- Added visual setup checklist
- Step-by-step commands with copy-paste code blocks
- Time estimates for each step
- Troubleshooting section
- PostgreSQL migration guide
- References quick-setup.sh script

**2. `examples/identity-example.md`** - Added 2 more templates
- Example 1: Sales Development Agent (Alex Chen) - existing, enhanced
- Example 2: Research Analyst Agent (Atlas) - NEW
- Example 3: Customer Support Agent (Jordan) - NEW
- Added template structure guide
- Added customization checklist
- Added domain-specific additions table

**3. `scripts/quick-setup.sh`** - NEW
- Bootstraps complete agent directory
- Creates identity.md template
- Creates escalation-config.yaml template
- Initializes SQLite database with full schema
- Provides next-steps guidance
- Color-coded output
- Safety check for existing directories

---

## Files Created

**Skill Factory:**
- `/Users/Aakash/Claude Projects/Skills Factory/SKILL-CRAFT.md` - Skill development methodology
- `/Users/Aakash/Claude Projects/Skills Factory/CLAUDE.md` - Project-level auto-load config
- `/Users/Aakash/Claude Projects/Skills Factory/Mailing Skill/skill-development-log.md` (this file)

**Agentmail Refs:**
- `/Users/Aakash/Claude Projects/Documents/Agentmail Refs/agentmail-overview.md`
- `/Users/Aakash/Claude Projects/Documents/Agentmail Refs/agentmail-api-reference.md`
- `/Users/Aakash/Claude Projects/Documents/Agentmail Refs/agentmail-quickstart.md`
- `/Users/Aakash/Claude Projects/Documents/Agentmail Refs/agentmail-infrastructure-patterns.md`

**Email Agent Skill:**
- `~/.claude/skills/email-agent/SKILL.md` - Main skill file (227 lines)
- `~/.claude/skills/email-agent/references/memory-schema.md` - Database schema (324 lines)
- `~/.claude/skills/email-agent/references/session-lifecycle.md` - Session flows (403 lines)
- `~/.claude/skills/email-agent/references/escalation-config.md` - Escalation config reference (379 lines)
- `~/.claude/skills/email-agent/references/builder-setup.md` - Comprehensive builder guide (693 lines) ← Enhanced
- `~/.claude/skills/email-agent/references/infrastructure.md` - AgentMail infrastructure (199 lines)
- `~/.claude/skills/email-agent/examples/identity-example.md` - 3 identity templates (461 lines) ← Enhanced
- `~/.claude/skills/email-agent/examples/escalation-config-example.yaml` - Sample escalation config (104 lines)
- `~/.claude/skills/email-agent/scripts/quick-setup.sh` - Bootstrap script (326 lines) ← NEW

**Total: 3,116 lines across 9 files**

---

## Final Skill Summary

### What the Skill Provides

**Expertise (SKILL.md):**
- Confident collaborator mindset
- 5-tier confidence model
- Relationship-centric memory philosophy
- Escalation patterns and graduated autonomy
- Session lifecycle patterns

**For Builders:**
- Quick-setup script (5-minute bootstrap)
- Step-by-step setup guide with exact commands
- 3 identity templates (Sales, Research, Support)
- Escalation configuration examples
- Database schema with indexes and views
- Troubleshooting guide

### Skill Boundaries

| Skill Handles (Expertise) | Builder Handles (Infrastructure) |
|---------------------------|----------------------------------|
| How to think about email | AgentMail account + API key |
| Confidence model | MCP server configuration |
| Escalation patterns | Database setup |
| Persona alignment | Identity customization |
| Relationship memory | Domain-specific triggers |

---

*Last updated: Builder guide enhancement complete*
