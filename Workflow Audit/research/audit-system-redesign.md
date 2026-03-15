# Audit System Redesign — Research Synthesis

**Date:** 2026-03-14
**Problem:** Current correction/frustration detection is regex-based and catastrophically noisy (100/115 sessions flagged). Error extraction returns 0. Audit findings are ungrouped individual instances, not patterns.

---

## Key Research Findings

### 1. KAIST Dissatisfaction Taxonomy (Kim et al., arxiv 2311.07434)

Studied 307 ChatGPT conversations from 107 users, found 511 dissatisfactions. **7 categories:**

| Category | Frequency | Severity |
|----------|-----------|----------|
| Poor intent understanding | Most frequent | Medium |
| Information accuracy | Medium | **Most severe** |
| Insufficient knowledge | Medium | Medium |
| Incompleteness | Medium | Low |
| Refusal to answer | Low | High |
| Inconsistency | Low | Medium |
| Bias/safety | Low | Low |

**User correction tactics (4 categories, 13 codes):**
- **Prompt Reusing (T1-T3):** Re-using identical prompt, requesting "more/another", adding ALL CAPS emphasis
- **Intent Concretization (T4-T7):** Providing detailed instructions, additional context, format/tone conditions
- **Error Identification (T8-T10):** Pointing out errors ("that's wrong"), providing correct answer, asking confirmation ("are you sure?")
- **Task Adaptation (T11-T13):** Changing approach, simplifying task, giving up

**Key insight:** Users most often CONCRETIZE INTENT (add detail), not express frustration. Detection systems that look for anger miss the most common correction pattern.

### 2. Bot Experience Score (Calabrio) — Signal-Based Approach

Score starts at 100, drops for behavioral SIGNALS (not keywords):
- **Bot repetition** — AI repeats itself
- **Customer paraphrase** — User rephrases the same question
- **Abandonment** — User leaves mid-conversation
- **Negative sentiment** — AI-detected, not regex

**Key insight:** Behavioral signals (rephrasing, abandonment) are more reliable than keyword matching.

### 3. Conversation Quality Metric (Galileo)

Binary GOOD/BAD classification analyzing tone, engagement, sentiment across entire session.

**Common error:** "Mislabeling external frustration as bot-directed" — users expressing frustration about their problem (not about the AI) get misclassified.

### 4. Google Cloud — Log Analysis with Vector Search

- Convert semi-structured logs to **natural language summaries** before embedding
- **Aggregation** reduces volume 20:1 (multiple events → single summary)
- **NL conversion** makes semantics searchable (2KB JSON → 200-char sentence)
- Subject matter expert selects which fields to extract

### 5. Developer Tool Analytics (JetBrains/Pragmatic Engineer)

SPACE framework applied to AI tools:
- **Satisfaction:** How do developers feel? (surveys, not just logs)
- **Activity:** AI usage patterns, accept/reject events
- **Efficiency:** Where AI saves time vs. creates overhead

**Key insight:** "Logs tell you WHAT; surveys/interviews tell you WHY." Mixed methods required. Telemetry reveals patterns; root cause requires context.

### 6. CodeWatcher (Basha et al., arxiv 2510.11536)

IDE telemetry capturing fine-grained developer actions with LLM code tools:
- Event types: Insertion, Deletion, Copy, Paste, Focus/Unfocus
- Classifies code as AI-Generated (>95% similarity), AI-Modified (80-95%), User-Written (<80%)
- Uses fuzzy similarity metric between final code and historical snapshots

---

## Redesign Principles

### P1: Signal-Based Detection, Not Keyword Regex

Replace regex with **behavioral signals** detected from session structure:

| Signal | Confidence | Detection Method |
|--------|------------|-----------------|
| User rephrasing (same intent, different words) | High | Semantic similarity between consecutive user messages |
| Tool failure → retry → success cycle | High | Structural: tool name + exit code sequence |
| Explicit negation + reference to prior action | High | "no/don't/stop" + mention of what AI did |
| Session abandonment after error | High | /exit or session end within 2 messages of error |
| Directive correction language | Medium | Tight patterns: "I said X not Y", "that's wrong", "I meant" |
| Frustration intensifiers | Medium | `!!!` or profanity (NOT `[A-Z]{3,}` which catches acronyms) |
| Repeated tool failures (3+ same tool) | Low | Count per tool in session |
| High error density (>5 errors in <10 tool uses) | Low | Ratio calculation |

### P2: Cluster by Pattern, Not Individual Instance

Don't report "Session X had a correction" — report "Claude misunderstands project context instructions across 5 sessions in 2 projects."

Clustering approach:
1. Extract correction messages from all sessions
2. Embed them
3. Cluster by semantic similarity (e.g., DBSCAN or simple cosine threshold)
4. Name each cluster by its dominant theme
5. Report: "Pattern P1: [theme] — occurred N times across M sessions"

### P3: Cross-Reference with Memory System

The highest-value finding: **corrections that repeat but have no corresponding feedback memory.**

- Extract all correction messages
- Search cc-memories for related feedback memories
- Corrections WITHOUT memories = genuine gap = high-severity finding
- Corrections WITH memories that still repeat = memory being ignored = critical finding

### P4: Fix Error Extraction Against Real Data

Debug by reading actual JSONL entries, not guessing the structure. The preprocessor assumed `data.toolName` and `data.result` but the actual schema may differ.

### P5: Use Severity Thresholds

| Severity | Criteria |
|----------|----------|
| Critical | Pattern repeats across 5+ sessions AND no feedback memory exists |
| High | Pattern repeats across 3+ sessions |
| Medium | Pattern appears in 2 sessions |
| Low | Single-session finding |
| Info | Metric without actionable finding |

---

## Implementation Plan

### Phase A: Fix Preprocessor (signal extraction)
1. Remove broken regex (`FRUSTRATION_INDICATORS`, `CORRECTION_PATTERNS`)
2. Add structural signal extraction per session
3. Debug error extraction against real JSONL entries
4. Add session-level metrics: error density, tool failure sequences

### Phase B: Fix Audit Engine (pattern intelligence)
1. Replace individual-finding model with pattern-clustering model
2. Add memory cross-reference (corrections without memories = finding)
3. Implement severity thresholds (frequency × recurrence)
4. Improve report format: pattern → evidence → action

### Phase C: Future — LLM-Assisted Classification
1. `--deep` flag sends user messages to Haiku for classification
2. Each message classified as: instruction, correction, frustration, acknowledgment
3. Eliminates regex entirely, but costs ~$0.35 per full run
