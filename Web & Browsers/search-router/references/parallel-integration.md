# Parallel AI Integration Reference

## API Endpoints

| Endpoint | Purpose | Auth Header |
|----------|---------|-------------|
| `https://api.parallel.ai/v1beta/search` | Web search | `x-api-key: $PARALLEL_API_KEY` |
| `https://api.parallel.ai/v1beta/extract` | URL extraction | `x-api-key: $PARALLEL_API_KEY` |
| `https://api.parallel.ai/v1/tasks/runs` | Task creation | `x-api-key: $PARALLEL_API_KEY` |
| `https://api.parallel.ai/v1/tasks/runs/{id}` | Task status | `x-api-key: $PARALLEL_API_KEY` |
| `https://api.parallel.ai/chat/completions` | Chat (OpenAI-compatible) | `Authorization: Bearer $PARALLEL_API_KEY` |

## MCP Servers

```json
// Search MCP
{
  "type": "http",
  "url": "https://search-mcp.parallel.ai/mcp",
  "headers": {
    "Authorization": "Bearer $PARALLEL_API_KEY"
  }
}

// Task MCP
{
  "type": "http",
  "url": "https://task-mcp.parallel.ai/mcp",
  "headers": {
    "Authorization": "Bearer $PARALLEL_API_KEY"
  }
}
```

---

## Search API Examples

### Basic Search
```bash
curl https://api.parallel.ai/v1beta/search \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -H "parallel-beta: search-extract-2025-10-10" \
  -d '{
    "objective": "Find the latest information about Parallel Web Systems",
    "search_queries": [
      "Parallel Web Systems products",
      "Parallel Web Systems announcements"
    ],
    "max_results": 10,
    "excerpts": {
      "max_chars_per_result": 10000
    }
  }'
```

### Search Response Structure
```json
{
  "search_id": "search_e749586f-...",
  "results": [
    {
      "url": "https://example.com/page",
      "title": "Page Title",
      "publish_date": "2025-01-01",
      "excerpts": ["LLM-optimized text excerpts..."]
    }
  ],
  "warnings": null,
  "usage": [{"name": "sku_search", "count": 1}]
}
```

---

## Task API Examples

### Quick Lookup (lite processor)
```bash
curl https://api.parallel.ai/v1/tasks/runs \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "input": "Stripe",
    "task_spec": {"output_schema": "The founding year"},
    "processor": "lite"
  }'
```

### Structured Enrichment (base processor)
```bash
curl https://api.parallel.ai/v1/tasks/runs \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "input": {"company_name": "Stripe", "website": "stripe.com"},
    "processor": "base",
    "task_spec": {
      "input_schema": {
        "type": "json",
        "json_schema": {
          "type": "object",
          "properties": {
            "company_name": {"type": "string"},
            "website": {"type": "string"}
          }
        }
      },
      "output_schema": {
        "type": "json",
        "json_schema": {
          "type": "object",
          "properties": {
            "founding_year": {"type": "string"},
            "employee_count": {"type": "string"},
            "total_funding": {"type": "string"},
            "ceo_name": {"type": "string"}
          }
        }
      }
    }
  }'
```

### Deep Research Report (core/ultra processor)
```bash
curl https://api.parallel.ai/v1/tasks/runs \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "input": "Create a comprehensive market research report on the HVAC industry in the USA",
    "processor": "ultra",
    "task_spec": {
      "output_schema": {"type": "text"}
    }
  }'
```

### Task Status Polling
```bash
# Get task status
curl https://api.parallel.ai/v1/tasks/runs/{run_id} \
  -H "x-api-key: $PARALLEL_API_KEY"

# Response includes: status, output, basis (citations)
```

---

## Task Spec Output Types

| Type | Schema | Use Case |
|------|--------|----------|
| Text string | `"The founding date in MM-YYYY format"` | Simple lookups |
| JSON schema | `{"type": "json", "json_schema": {...}}` | Structured data |
| Text schema | `{"type": "text"}` | Markdown reports |
| Auto | `{"type": "auto"}` or omit `task_spec` | Let processor decide |

---

## Research Basis (Citations)

Every Task API response includes a `basis` object with:
- **citations**: Source URLs and excerpts
- **reasoning**: How the answer was derived
- **confidence**: Confidence level for each field

```json
{
  "output": {"founding_year": "2010"},
  "basis": {
    "founding_year": {
      "citations": [
        {
          "url": "https://example.com",
          "excerpt": "Founded in 2010..."
        }
      ],
      "reasoning": "Multiple sources confirm...",
      "confidence": "high"
    }
  }
}
```

---

## Claude Code Plugin Commands

After installing the Parallel plugin:

| Command | Description |
|---------|-------------|
| `/parallel:search <query>` | Web search |
| `/parallel:extract <url>` | Extract content from URL |
| `/parallel:research <topic>` | Deep research task |
| `/parallel:enrich <data>` | Enrich entities with web data |
| `/parallel:status <run_id>` | Check task status |
| `/parallel:result <run_id>` | Get task results |
| `/parallel:setup` | Install CLI and authenticate |

---

## Python SDK Examples

```python
from parallel import Parallel

client = Parallel(api_key="PARALLEL_API_KEY")

# Search
results = client.search.search(
    objective="Find information about...",
    search_queries=["query1", "query2"],
    max_results=10
)

# Task (sync)
task_run = client.task_run.create(
    input="Stripe",
    task_spec={"output_schema": "The founding year and total funding"},
    processor="base"
)
result = client.task_run.result(task_run.run_id, api_timeout=3600)
print(result.output)

# Task (async with polling)
task_run = client.task_run.create(input="Topic", processor="ultra")
while True:
    status = client.task_run.get(task_run.run_id)
    if status.status == "completed":
        print(status.output)
        break
    time.sleep(5)
```

---

## TypeScript SDK Examples

```typescript
import Parallel from "parallel-web";

const client = new Parallel({ apiKey: "PARALLEL_API_KEY" });

// Search
const results = await client.search.search({
  objective: "Find information about...",
  search_queries: ["query1", "query2"],
  max_results: 10
});

// Task
const taskRun = await client.taskRun.create({
  input: "Stripe",
  task_spec: { output_schema: "The founding year" },
  processor: "base"
});
const result = await client.taskRun.result(taskRun.run_id);
console.log(result.output);
```

---

## Pricing Quick Reference

| Product | Tier | Cost/Query | Cost/1K |
|---------|------|------------|---------|
| Search | Base | $0.004 | $4 |
| Search | Pro | $0.009 | $9 |
| Task | Lite | $0.005 | $5 |
| Task | Base | $0.01 | $10 |
| Task | Core | $0.025 | $25 |
| Task | Pro | $0.10 | $100 |
| Task | Ultra | $0.30 | $300 |
| Task | Ultra2x | $0.60 | $600 |
| Task | Ultra4x | $1.20 | $1,200 |
| Task | Ultra8x | $2.40 | $2,400 |
| Chat | — | $0.005 | $5 |

**Free tier**: 20,000 requests

---

## Error Handling

Common errors:
- `401`: Invalid API key
- `429`: Rate limited
- `400`: Invalid request (check task_spec schema)

Task-specific:
- `status: "failed"`: Check `error` field in response
- Timeout: Increase `api_timeout` or use async polling

---

## Best Practices

1. **Start with Search API** for quick lookups before escalating to Task
2. **Use lite/base processors** for simple queries to save cost
3. **Use core+ processors** when multi-hop reasoning is needed
4. **Always check the basis** for citations and confidence
5. **Use structured output schemas** when you need specific fields
6. **Poll async tasks** rather than blocking on long-running tasks
