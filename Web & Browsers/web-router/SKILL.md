---
name: web-router
description: >
  Use for any web task: browsing websites, scraping content, extracting data,
  searching the web, filling forms, monitoring pages, auditing performance,
  accessing authenticated sites, or any task involving web pages or URLs.
  Triggers on: "browse", "navigate to", "go to website", "scrape", "extract from",
  "search for on the web", "check website", "monitor", "watch for changes",
  "log in to", "set up auth", "audit", "lighthouse", "check accessibility",
  "fill out form", "submit", or any URL mention.
version: 1.0.0
---

# Web Router

You're the entry point for all web tasks. Your job: figure out what kind of web task this is, load the right specialist reference docs, and hand off execution.

## Task Classification

Read the user's request and classify it:

| Task Type | Signals | Specialist | Reference Doc |
|---|---|---|---|
| **Browse** | "go to", "navigate", "click", "fill form", URL + interaction | browse | `references/browse.md` |
| **Scrape** | "extract", "scrape", "get data from", "pull content" | scrape | `references/scrape.md` |
| **Search** | "search for", "find", "look up", "research" | search | `references/search.md` |
| **Auth** | "log in", "set up auth", "authenticate", "cookies" | auth | `references/auth.md` |
| **QA** | "test", "check for bugs", "validate", "QA" | qa | `references/qa.md` |
| **Perf Audit** | "lighthouse", "performance", "core web vitals", "audit" | perf-audit | `references/perf-audit.md` |
| **Watch** | "monitor", "watch for changes", "alert when", "track" | watch | `references/watch.md` |

## Composite Tasks

Many requests combine multiple specialists. Load up to 3 reference docs per task.

**Examples:**
- "Log in to YouTube and scrape my subscriptions" → auth + browse + scrape (3 docs)
- "Search for competitor pricing and extract into a table" → search + scrape (2 docs)
- "Navigate to the dashboard and run a Lighthouse audit" → browse + perf-audit (2 docs)
- "Monitor this page for price changes" → watch (1 doc, but internally uses browse + scrape)

**Rule:** If more than 3 specialists apply, identify the primary task and start there. Chain tasks sequentially rather than loading everything at once.

## Auth Detection

Before starting any task, check: does this URL require authentication?

**Signs auth is needed:**
- URL contains paths like `/dashboard`, `/settings`, `/account`, `/my/`
- User says "my [something]" (my subscriptions, my orders)
- Previous attempt got a login redirect
- Domain is in the auth service registry as requiring auth

**If auth needed:** Load auth specialist first, establish session, then proceed with the main task.

## Environment Detection

Detect where you're running:

| Signal | Environment | Impact |
|---|---|---|
| Playwright MCP available | CC or CAI (Mac) | Full local browsing |
| `browser_snapshot` works | CC or CAI (Mac) | Local browser available |
| No local browser | Agent SDK (Droplet) | Use headless Playwright or Browserbase |
| `BROWSERBASE_API_KEY` set | Any (with cloud fallback) | Can create isolated sessions |

## Tool Selection

Every task goes through the 6-dimension framework. Read `references/tool-selection.md` when you need to decide between tools.

Quick heuristic (covers 80% of cases):
1. Static text content → Firecrawl scrape
2. Structured data extraction → Firecrawl extract
3. Interactive page (forms, clicks, navigation) → Playwright MCP
4. Quality/performance audit → Chrome DevTools Lighthouse
5. Multi-source research → Firecrawl agent
6. Bot-hostile site → Browserbase + Playwright

## Observability

Log every routing decision:

```yaml
timestamp: [now]
task: "[user's request]"
classification: [task type]
specialists_loaded: [list]
auth_required: [yes/no]
environment: [CC/CAI/AgentSDK]
```

Log to `~/.ai-cos/logs/web-tools/` if the directory exists. If not, log to stderr. Never fail a task because logging failed.

## Scaling Note

This router currently handles 7 specialists. The architecture supports up to 10 before the classification matrix needs restructuring. If you're adding specialist #11, rethink the routing — consider grouping specialists into categories with sub-routers.
