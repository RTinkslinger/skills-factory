---
name: search-router
description: Use this skill when performing web searches, researching information online, looking up documentation, or finding current information. Triggers include "search for", "look up", "find", "research", "what is", "how to", "documentation", "deep and wide search", "deep and wide search on web", or any query requiring external web information. Routes intelligently between Context7 (free library docs), native WebSearch (free general), Exa (fast semantic), and Parallel (deep research) based on query complexity.
version: 2.0.0
---

# Intelligent Search Router v2

Route search queries to the optimal tool based on query type, complexity, and depth requirements.

## Available Tools (Priority Order)

| Tool | Cost | Speed | Best For |
|------|------|-------|----------|
| Context7 | FREE | Fast | Specific library/framework documentation |
| Native WebSearch | FREE | Medium | Simple facts, current events |
| Exa Code Context | $0.006/query | Sub-350ms | General code search, cross-library patterns |
| Exa Web Search | $0.005/query | Sub-350ms | Semantic research, people, comparisons |
| Exa Company Research | $0.008/query | Fast | Company-specific information |
| **Parallel Search** | $0.004-0.009/query | 1-70s | LLM-optimized excerpts, cross-referenced facts |
| **Parallel Task** | $0.005-2.40/query | 5s-25min | Deep research, reports, data enrichment |

---

## Quick Decision Matrix

| Query Type | Route To | Why |
|------------|----------|-----|
| Specific library docs | **Context7** | FREE, specialized, authoritative |
| Simple facts | Native WebSearch | FREE, adequate |
| Current events | Native WebSearch | Real-time, free |
| Cross-library code | Exa Code Context | Semantic search across sources |
| Company research | Exa Company Research | Specialized index |
| People/founders | Exa Web Search | Semantic search |
| **Multi-source synthesis** | **Parallel Search** | Cross-referenced, LLM-optimized |
| **Deep research/reports** | **Parallel Task** | Multi-hop reasoning, citations |
| **Data enrichment** | **Parallel Task** | Structured output, evidence-based |

---

## Tier 1: Code/Documentation Routing (FREE First)

### STEP 1: Is it about a specific library/framework?

**YES → Use Context7** (FREE)
1. Call `mcp__plugin_context7_context7__resolve-library-id` with library name
2. Call `mcp__plugin_context7_context7__query-docs` with libraryId and query

**Triggers for Context7:**
- Library/framework names: React, Next.js, Vue, Supabase, Prisma, Express, etc.
- "How to X in [library]"
- "[Library] documentation"
- "[Library] examples"
- API usage for specific packages

**Examples → Context7:**
- "How to use useState in React" → Context7 (library: react)
- "Supabase RLS examples" → Context7 (library: supabase)
- "Next.js App Router middleware" → Context7 (library: next.js)

### STEP 2: Is it general/cross-library code search?

**YES → Use Exa Code Context** (`mcp__exa__get_code_context_exa`)

**Triggers:**
- No specific library mentioned
- Comparing approaches across libraries
- General best practices
- Implementation patterns

**Examples → Exa Code Context:**
- "Authentication best practices for APIs"
- "How to implement rate limiting"
- "Database indexing strategies"

---

## Tier 2: Quick Information (FREE/Low Cost)

### Simple Facts / Current Events → Native WebSearch
- Weather, prices, scores
- Breaking news
- Basic knowledge questions
- Real-time information

### Company Research → Exa Company Research
```
mcp__exa__company_research_exa
numResults: 3 (basic) or 5 (comprehensive)
```
- "Tell me about [company]"
- Funding, products, business model

### People/Founders → Exa Web Search
```
mcp__exa__web_search_exa
type: "auto"
numResults: 8
```
- "[Person name] background"
- Career history, achievements

---

## Tier 3: Deep Research (Parallel AI)

### When to Escalate to Parallel

**Triggers for Parallel Search API:**
- Query requires **synthesizing multiple sources**
- Need **LLM-optimized excerpts** (not just links)
- Need **cross-referenced, verified facts**
- Existing tools return insufficient results

**Triggers for Parallel Task API:**
- "deeply research..."
- "comprehensive report on..."
- "exhaustive analysis of..."
- "due diligence on..."
- "market research for..."
- "competitive landscape..."
- Need for **structured data with citations**
- Multi-hop reasoning required
- Publication-quality output needed

### Parallel Search API

**Best for:** Fast, high-quality web search with excerpts

```bash
# Via CLI (if plugin installed)
/parallel:search "query"

# Via API
curl https://api.parallel.ai/v1beta/search \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -H "parallel-beta: search-extract-2025-10-10" \
  -d '{
    "objective": "Research goal in natural language",
    "search_queries": ["query1", "query2"],
    "max_results": 10,
    "excerpts": {"max_chars_per_result": 10000}
  }'
```

### Parallel Task API Processors

| Processor | Cost/1K | Latency | Use Case |
|-----------|---------|---------|----------|
| **lite** | $5 | 5-60s | Basic retrieval, quick lookups |
| **base** | $10 | 15-100s | Simple research, single-source |
| **core** | $25 | 1-5min | Complex research, multi-hop |
| **pro** | $100 | 3-9min | Exploratory research |
| **ultra** | $300 | 5-25min | Extensive deep research |
| **ultra2x-8x** | $600-2,400 | 5-25min | Maximum compute |

### Processor Selection Logic

```
Query complexity:
├── "Find X's founding year" → lite ($5/1K)
├── "Research X and summarize" → base ($10/1K)
├── "Compare X vs Y vs Z with details" → core ($25/1K)
├── "Full market analysis of [industry]" → pro/ultra ($100-300/1K)
└── "Enterprise due diligence report" → ultra+ ($300+/1K)
```

### Parallel Task Usage

```bash
# Via CLI (if plugin installed)
/parallel:research "topic"

# Via API (report output)
curl https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "input": "Topic to research",
    "processor": "core",
    "task_spec": {"output_schema": {"type": "text"}}
  }'

# Via API (structured output)
curl https://api.parallel.ai/v1/tasks/runs \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "input": {"company": "Stripe"},
    "processor": "base",
    "task_spec": {
      "output_schema": {
        "type": "json",
        "json_schema": {
          "type": "object",
          "properties": {
            "founding_year": {"type": "string"},
            "total_funding": {"type": "string"}
          }
        }
      }
    }
  }'
```

---

## Complete Decision Flowchart

```
START: Classify query
│
├── CODE/DOCS QUERY?
│   ├── Specific library mentioned?
│   │   └── YES → Context7 (FREE)
│   └── General code/cross-library?
│       └── YES → Exa Code Context ($0.006)
│
├── SIMPLE FACT / CURRENT EVENT?
│   └── YES → Native WebSearch (FREE)
│
├── COMPANY QUERY?
│   ├── Basic info → Exa Company Research ($0.008)
│   └── Deep analysis → Parallel Task (base) ($0.01)
│
├── PEOPLE/SEMANTIC QUERY?
│   └── YES → Exa Web Search ($0.005)
│
├── MULTI-SOURCE SYNTHESIS NEEDED?
│   └── YES → Parallel Search API ($0.004-0.009)
│       "Compare...", "Research options for..."
│
├── DEEP RESEARCH / REPORT NEEDED?
│   ├── Quick research → Parallel Task (lite/base) ($0.005-0.01)
│   ├── Thorough research → Parallel Task (core) ($0.025)
│   ├── Full report → Parallel Task (pro/ultra) ($0.10-0.30)
│   └── Enterprise/mission-critical → Parallel Task (ultra2x-8x)
│
└── DEFAULT → Native WebSearch (FREE)
```

---

## Fallback Strategy

1. Context7 fails (library not found) → Try Exa Code Context
2. Exa returns insufficient results → Try Parallel Search
3. Need more depth than Parallel Search → Escalate to Parallel Task
4. All fail → Inform user, suggest query refinement

---

## Cost-Benefit Summary

| Scenario | Best Choice | Cost | Rationale |
|----------|-------------|------|-----------|
| React hooks docs | Context7 | FREE | Specialized |
| "Bitcoin price" | Native WebSearch | FREE | Real-time |
| "What is Stripe?" | Exa Company | $0.008 | Quick lookup |
| "Sam Altman bio" | Exa Web Search | $0.005 | Semantic |
| "Compare 5 CRM tools" | Parallel Search | $0.009 | Multi-source |
| "CRM market report" | Parallel Task (core) | $0.025 | Synthesis |
| "Full industry analysis" | Parallel Task (ultra) | $0.30 | Exhaustive |

---

## Setup: Enable Parallel

### Option 1: Install Plugin (Recommended)
```bash
/plugin marketplace add parallel-web/parallel-agent-skills
/plugin install parallel
/parallel:setup
```

### Option 2: Add MCP Servers
Add to `~/.claude/settings.local.json`:
```json
{
  "mcpServers": {
    "parallel-search": {
      "type": "http",
      "url": "https://search-mcp.parallel.ai/mcp"
    },
    "parallel-task": {
      "type": "http",
      "url": "https://task-mcp.parallel.ai/mcp"
    }
  }
}
```

### Option 3: Direct API
Set `PARALLEL_API_KEY` and use curl/SDK.

---

## Parallel Performance Benchmarks

Why use Parallel for deep research?

| Benchmark | Parallel | GPT-5 | Others |
|-----------|----------|-------|--------|
| RACER (expert research) | **96%** win rate | 66% | — |
| BrowseComp (multi-hop) | **58%** accuracy | 38% | — |
| WISER-Atomic | **77%** @ $25 CPM | — | o3: 69% |

Parallel is purpose-built for multi-hop web research with evidence synthesis.

---

See `references/routing-logic.md` for detailed examples.
