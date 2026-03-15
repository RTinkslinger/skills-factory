# Web & Frontend Skills Portfolio — Design Document

> Make CC, CAI, and custom agents use the web as well as a human — unhindered, programmatic, best-in-class.

**Date:** 2026-03-14
**Status:** Draft (Pass 3 review fixes applied)
**Review history:** Pass 1 (subagent reviewer), Pass 2 (systems architect), Pass 3 (triple-lens: architect + QA + DevOps) — see `docs/superpowers/specs/2026-03-14-design-review-pass-3-consolidated.md`
**Projects involved:** Skills Factory (primary), AI CoS CC ADK (consumer + integration), global CC config (~/.claude/)

---

## 1. Vision & North Star

**The problem:** Claude's web capabilities are fragmented. CC has Playwright, Stagehand, WebSearch, WebFetch — but no orchestration telling it when to use what. CAI has WebSearch and WebFetch plus MCP connectors — but can't browse, interact, or extract at depth. Custom agents (Agent SDK on droplet) have full OS access but no web skill framework. Frontend skills exist (design-system-enforcer, a11y-audit) but drift from 2026 web standards.

**The north star:** Any surface where Claude operates (CC terminal, CAI chat, Agent SDK runner) should be able to:
- Browse any website, including authenticated and bot-protected sites
- Extract structured data from any web source
- Search with intelligence (right tool for right query)
- Test web applications with structured QA methodology
- Monitor websites for changes over time
- Build frontend code using 2026 web standards with zero drift

**Core principles:**
- Unhindered web access — as capable as a human
- Best-in-class output — objective achievement over cost optimization
- No drift — deterministic outcomes via grounded skills (reference docs, live queries, MCP data)
- Elaborate, layered systems — robust auth, fallback chains, observability
- Skills add orchestration value — tools change underneath, expertise routing persists
- Infrastructure serves the objective — never downscope to fit today's constraints

---

## 2. Architecture

### Three-Tier Model

```
LAYER 3: ORCHESTRATION
  web-router (master)
    Classifies task type (browse/scrape/search/qa/monitor)
    Detects environment (CC / CAI / Agent SDK)
    Invokes specialist with environment context
    Logs routing decisions for observability

LAYER 2: SPECIALIST SKILLS
  8 web specialists + 3 frontend updates (see Section 5)
  Each specialist:
    Focused domain expertise (anti-drift via narrow scope)
    Environment-aware (different tool paths per surface)
    6-dimension tool selection reasoning (see Section 4)
    Observability: logs tool selection, reasoning, outcomes
    Fallback chains built into expertise, not hardcoded

LAYER 1: SHARED TOOLS
  Browser Automation:  Playwright MCP, Chrome DevTools MCP,
                       Stagehand/Browserbase, browser-use, Computer Use API
  Web Extraction:      Firecrawl MCP, WebFetch, Jina Reader
  Search:              Context7, WebSearch, Exa, Parallel, Firecrawl search
  Frontend Grounding:  shadcn MCP, Figma MCP, Context7 (Vite/React/Tailwind docs)
  Auth Infrastructure: Browserbase (isolated sessions, proxies), cookie management,
                       API key/OAuth management
```

### Environment Detection

| Environment | Detection Signal | Available Tools | Skill Delivery |
|---|---|---|---|
| **CC (Claude Code)** | Bash tool available, file system access, plugin system | Everything: MCPs + CLI binaries + hooks + plugins | Skills in ~/.claude/skills/ |
| **CAI (Claude.ai)** | No Bash, no file system, MCP connectors via remote endpoints | MCPs only (via mcp.3niac.com or other remote connectors) | Skill knowledge via project instructions or MCP tool descriptions |
| **Agent SDK** | Python/TS runtime, `anthropic` SDK, full OS access on VM | MCPs (local or remote) + CLI + direct API calls + computer use | Runners read reference docs from `/opt/ai-cos-mcp/skills/` at startup, include as system prompt context (see below) |

**Agent SDK skill delivery (concrete mechanism):**

```python
# Runner startup pattern — loads relevant specialist knowledge into system prompt
import pathlib

SKILLS_DIR = pathlib.Path("/opt/ai-cos-mcp/skills/web-router/references")

def load_specialist(name: str) -> str:
    """Load a specialist reference doc as system prompt context."""
    path = SKILLS_DIR / f"{name}.md"
    if path.exists():
        return path.read_text()
    return ""

# Example: IngestAgent loads scrape + browse + auth specialists
system_prompt = f"""You are the IngestAgent. Your job is to extract structured data from URLs.

{load_specialist("scrape")}
{load_specialist("browse")}
{load_specialist("auth")}
{load_specialist("tool-selection")}
"""
```

**Deployment:** Reference docs are synced from Skills Factory to droplet via `deploy.sh` (rsync). Same files that live in `~/.claude/skills/web-router/references/` on Mac are deployed to `/opt/ai-cos-mcp/skills/web-router/references/` on droplet. Single source of truth — two deployment targets.

### Cross-Environment Principle

Don't force shared architecture. Each environment gets the best implementation for its constraints. The shared foundation is:
1. **MCP tools** — same MCP servers accessible from all environments
2. **Expertise patterns** — same reasoning about when/how to use tools
3. **Observability format** — same logging structure for learning across surfaces

---

## 3. Tool Ecosystem

### Browser Automation Tools

| Tool | What It Does | Cost Model | Setup Location | CC | CAI | Agent SDK |
|---|---|---|---|---|---|---|
| **Playwright MCP** (Microsoft) | Structured automation via a11y tree, cross-browser, auto-wait | Free (open source) | ~/.mcp.json or per-project .mcp.json | Yes (plugin) | Possible (remote MCP) | Yes (npm install) |
| **Chrome DevTools MCP** (Google) | 29 tools: input, navigation, emulation, perf, network, debug. Connects to live Chrome sessions. | Free (open source) | ~/.mcp.json: `npx chrome-devtools-mcp@latest` | Yes | Possible (remote MCP) | Yes (npm install) |
| **Stagehand v3** (Browserbase) | AI-native Playwright: act/extract/observe, auto-caching selectors, 44% faster | Free OSS, Browserbase cloud paid | CC: plugin (browserbase/agent-browse). Agent SDK: npm install | Yes (installed) | No (needs runtime) | Yes |
| **browser-use** | Full LLM control, 89% WebVoyager, stealth, multi-model, 80K+ stars | Free OSS, cloud paid | CC: pip install + MCP server. Agent SDK: pip install | Yes | Possible (MCP server) | Yes |
| **Browserbase** | Cloud browser infra: anti-detection, proxy rotation, persistent sessions, session recording | Usage-based (free trial) | API key in env vars. SDK: npm/pip install | Yes (via Stagehand) | Via MCP | Yes |
| **Computer Use API** | Pixel-level desktop control via screenshots + mouse/keyboard | Anthropic API costs | Beta header in API calls. Needs VM with display. | No (CC is terminal) | No | Yes (with Xvfb/VM) |

### Web Extraction Tools

| Tool | What It Does | Cost Model | Setup |
|---|---|---|---|
| **Firecrawl MCP** | 6 tools: scrape, crawl, search, extract, map, agent. Clean markdown output. | 500 free credits, then $16/mo | `npx -y firecrawl-mcp` + API key |
| **WebFetch** (built-in) | Simple URL → content | Free (built-in) | No setup needed |
| **Jina Reader** | URL → clean markdown | Free tier | API call or MCP |

### Search Tools (existing, documented in search-router)

| Tool | Cost | Best For |
|---|---|---|
| Context7 | Free | Library/framework docs |
| WebSearch | Free | General facts, current events |
| Exa | ~$0.005-0.008/query | Semantic search, code, companies, people |
| Parallel | $0.004-2.40/query | Multi-source synthesis, deep research, data enrichment |
| Firecrawl search | Per-credit | Search + scrape in one call |

### Frontend Grounding Tools (existing)

| Tool | Purpose | Status |
|---|---|---|
| shadcn MCP | Component registry queries, prevents prop hallucination | Configured |
| Figma MCP | Design context extraction from Figma files | Configured (FIGMA_API_KEY) |
| Context7 | Live docs for Vite, React, Tailwind, any library | Installed (plugin) |

### Configuration Summary

**New tools to configure globally (~/.mcp.json):**
- Chrome DevTools MCP: `npx -y chrome-devtools-mcp@<pinned-version>` (pin version — never `@latest` in production)
- Firecrawl MCP: `npx -y firecrawl-mcp@<pinned-version>` (needs FIRECRAWL_API_KEY, pin version)

**Version pinning policy:** All MCP servers in `~/.mcp.json` must use pinned versions (e.g., `@1.2.3`), not `@latest`. Update versions intentionally — unpinned versions break without warning when upstream publishes breaking changes.

**New tools to evaluate and potentially configure:**
- browser-use MCP server: `pip install browser-use-mcp-server` (needs evaluation)
- Browserbase: account setup, API key, evaluate pricing (needs evaluation)

**Already configured:**
- Playwright MCP (via plugin)
- Stagehand (via browserbase/agent-browse plugin)
- shadcn MCP, Figma MCP, Context7, Exa, Parallel

---

## 4. Tool Selection Decision Framework

Specialist skills don't hardcode tool choices. They reason across six dimensions per task:

### Dimension 1: Speed Requirement

| Need | Best Tool(s) | Why |
|---|---|---|
| Sub-second, deterministic | Playwright (cached selectors) | No LLM overhead, pure automation |
| Seconds, repeatable | Stagehand (auto-caching after first run) | AI selects, then caches for replay |
| Seconds, one-off | Chrome DevTools MCP | Rich inspection, single interaction |
| Minutes acceptable | browser-use (full LLM reasoning) | Thorough, autonomous, plans multi-step |

### Dimension 2: Site Hostility

| Level | Signals | Best Tool(s) | Why |
|---|---|---|---|
| Cooperative | Public API, no bot detection | Playwright headless, Firecrawl, WebFetch | Fast, cheap, no evasion needed |
| Moderate | Basic bot detection, rate limits | Stagehand + Browserbase stealth | AI-native + anti-detection |
| Hostile | Aggressive anti-bot, CAPTCHAs | browser-use with residential proxies | Full LLM control adapts to challenges |
| Adversarial | Fingerprinting, behavioral analysis | Browserbase persistent sessions + proxy rotation | Isolated identity, human-like fingerprints |
| Nuclear | Will eject real user auth | Browserbase isolated session, NEVER real profile | Protect real account at all costs |

### Dimension 3: Auth Sensitivity

| Scenario | Approach | Key Principle |
|---|---|---|
| No auth needed | Any tool, headless fine | Simplest path wins |
| Auth needed, low risk | Cookie injection into headless session | gstack-inspired cookie import |
| Auth needed, rate-limit risk | Browserbase isolated session | Protect real account from rate limiting |
| Auth needed, will trigger 2FA | Native Chrome with real profile, human confirms | Some auth requires human in the loop |
| Auth via API available | Skip browser entirely, direct API call | Best path: no browser needed |
| Risk of session ejection | Browserbase with separate identity | Never risk breaking user's real session |

### Dimension 4: Task Complexity

| Complexity | Best Tool(s) | Why |
|---|---|---|
| Single action (click, read, fill) | Playwright or Stagehand | Deterministic, fast |
| Multi-step known flow | Stagehand act() chain | AI + caching = reliable replay |
| Multi-step unknown flow | browser-use autonomous mode | Plans, reasons, adapts |
| Cross-application (desktop) | Computer Use API | Only option for non-web |
| Debugging/inspection | Chrome DevTools MCP | Console, network, DOM, perf |

### Dimension 5: Token/Cost Efficiency

| Scenario | Best Tool(s) | Token Impact |
|---|---|---|
| Bulk/repeated operations | Playwright CLI (not MCP) | 27K tokens vs 114K MCP (75% savings) |
| One-off rich inspection | Chrome DevTools MCP | Verbose but worth it for depth |
| Background autonomous | browser-use cloud | Parallel execution, managed infra |
| Simple page read | WebFetch or Firecrawl | Minimal tokens, clean output |

### Dimension 6: Output Format / Consumer Type

| Output Need | Best Tool(s) | Why |
|---|---|---|
| Structured JSON (typed fields) | Firecrawl extract (schema mode), Stagehand extract() | Schema-driven extraction, typed output |
| Clean markdown (readable prose) | Firecrawl scrape, Jina Reader, WebFetch | Optimized for clean text output |
| Raw HTML (DOM preservation) | Playwright page.content(), Chrome DevTools MCP | Full DOM when structure matters |
| Visual / screenshot | Playwright screenshot, Chrome DevTools MCP | Visual evidence, screenshot comparison |
| Streaming (real-time) | browser-use (live observation), Computer Use API | Progressive output as task runs |

### Dimension Conflict Resolution

When dimensions contradict (e.g., hostile site + sub-second speed), resolve using this priority order:

1. **Auth Safety** (highest) — never compromise real user sessions
2. **Site Hostility** — match evasion to detection level
3. **Task Complexity** — use tools that handle the required steps
4. **Output Format** — match consumer expectations
5. **Speed** — optimize within constraints above
6. **Cost** (lowest) — minimize only after other dimensions are satisfied

**Hard constraints win over soft preferences.** Auth Safety and Site Hostility are hard constraints — they eliminate tools from consideration. Speed and Cost are soft preferences — they rank remaining options. If a dimension eliminates ALL tools, escalate to the user.

### Combination Principle

A single task may use multiple tools in sequence:
- Browserbase sets up isolated session with proxies
- Stagehand navigates and fills forms (fast, cached)
- Chrome DevTools MCP inspects network response for debugging
- Firecrawl extracts clean data from the result page

### The "Protect My Account" Principle

Any action on an authenticated site where failure could:
- Eject the real user from their session
- Trigger rate limiting on the real account
- Break auth tokens that other tools/services depend on
- Trigger 2FA that disrupts the user's workflow

**MUST** use an isolated session (Browserbase, separate Chrome profile). Never the user's real session. This is non-negotiable.

### Observability

Every tool selection gets logged (canonical format — YAML for readability, stored as structured data):
```yaml
timestamp: 2026-03-15T10:30:00Z
specialist: scrape
task: "extract pricing from [site]"
environment: CC
dimensions:
  speed: seconds
  hostility: moderate
  auth: none
  complexity: single
  output_format: clean-markdown
  cost: low
tool_selected: firecrawl
reasoning: "no auth, structured extraction, Firecrawl agent mode ideal"
fallback_used: false
outcome: success
latency_ms: 3200
tokens_used: 450
failure:                    # present only when outcome != success
  primary_error: "403 Forbidden"
  fallback_chain: ["firecrawl → stagehand → browser-use"]
  first_success_at: "browser-use"  # null if all failed
  graceful_degradation: "returned cached data from previous scrape"
```

**Log storage:**

| Environment | Storage | Location | Persistence |
|---|---|---|---|
| CC | Append-only YAML files | `~/.claude/web-logs/{specialist}-{YYYY-MM}.yml` | Persists across sessions. Monthly rotation. |
| Agent SDK (droplet) | SQLite | `/opt/ai-cos-mcp/web-logs.db` | Table: `tool_logs(id, timestamp, specialist, task, environment, dimensions_json, tool_selected, reasoning, fallback_used, outcome, latency_ms, tokens_used)` |
| CAI | Not logged locally | Via MCP tool if ai-cos-mcp has logging endpoint | Stored on droplet if MCP-based |

**Degradation principle:** Logging is best-effort. Never block the primary task for observability. If log file is unwritable, log to stderr and continue. If YAML serialization fails, write raw text. Observability failure must never cause task failure.

**In CC:** After each web operation, the specialist appends a YAML entry to the log file. Bash tool writes the entry. This is the raw data the learning loop needs.

**Learning loop:** Logs reviewed during TRACES.md compaction (every 3 iterations). Patterns confirmed 2+ times graduate to skill refinements. Universal patterns graduate to CLAUDE.md. Anti-patterns added to specialist's "Traps" section. LEARNINGS.md captures the pattern discovery; log files provide the raw evidence.

---

## 5. Skill Portfolio

### Web & Browsers (8 specialists + 1 router)

#### 5.1 `web-router` — Master Orchestrator

**Purpose:** Thin routing layer. Classifies task type, detects environment, invokes the right specialist.

**Triggers:** Any web-related task. "go to", "browse", "scrape", "extract", "check site", "monitor", "test", "QA", "search for", "find", "research", "watch", "log in to"

**What it does:**
1. Parse the user's request to identify task type(s)
2. Detect the current environment (CC/CAI/Agent SDK)
3. Check if auth is needed (references auth skill)
4. Invoke the appropriate specialist(s) with full context
5. Log the routing decision

**What it does NOT do:** Execute web tasks. No browser interactions. No data extraction. Pure routing.

**Composite task classification:** Many user requests span multiple specialists. The router classifies composite tasks and loads the right combination of reference docs (max 3 per task to stay within context budget):

| Composite Pattern | Example | Reference Docs Loaded |
|---|---|---|
| Auth + Browse | "Log into LinkedIn and check my messages" | auth, browse |
| Browse + Scrape | "Go to the pricing page and extract all plans" | browse, scrape |
| Auth + Browse + Scrape | "Log into Notion and extract my task list" | auth, browse, scrape |
| Search + Scrape | "Find competitor pricing pages and extract data" | search (routes), scrape |
| Auth + Watch | "Monitor my portfolio on [site] for changes" | auth, watch (watch delegates to browse/scrape) |
| QA + Perf | "Full audit of localhost:3000" | qa, perf-audit |
| Browse + Scrape + Watch | "Monitor competitor pricing with login" | auth, watch, scrape |

**Rule:** If a task needs >3 specialists, decompose into sequential sub-tasks. The router logs composite classification alongside routing decisions.

**Scaling ceiling:** The router is designed for up to 10 specialists. If specialist count exceeds 10, decompose into sub-routers (e.g., `web-browse-router`, `web-data-router`) with the master router dispatching to sub-routers. This is a future concern — current count is 8+1.

**Activation model:** web-router is the **sole entry point** for all web tasks in CC. It is the ONLY SKILL.md registered in `~/.claude/skills/web-router/`. Specialist knowledge lives as **reference docs** inside `~/.claude/skills/web-router/references/`:

```
~/.claude/skills/web-router/
  SKILL.md              ← the only file with trigger descriptions
  references/
    browse.md           ← navigation & interaction expertise
    scrape.md           ← extraction expertise
    search.md           ← search routing (evolves from search-router v2)
    qa.md               ← testing methodology
    auth.md             ← session management & layered auth
    perf-audit.md       ← Core Web Vitals & performance
    watch.md            ← monitoring & change detection
    tool-selection.md   ← 6-dimension decision framework
```

**Why not separate skills:** CC's skill system activates ALL skills with matching triggers simultaneously. There is no trigger shadowing or skill-invokes-skill mechanism. If browse, scrape, and web-router all trigger on "go to website", Claude sees three conflicting skill instructions. Reference docs inside the router's directory eliminate this — the router loads the appropriate reference based on task classification.

**Implication for source code in Skills Factory:** Each specialist is developed as its own folder (`Web & Browsers/browse/`, `Web & Browsers/scrape/`, etc.) for development tracking and SKILL-CRAFT methodology. At deployment, the specialist's content becomes a reference doc inside web-router's directory.

**CAI:** Routing logic encoded in project instructions. Specialist knowledge summarized in project context.
**Agent SDK:** Runners read reference docs from a defined path at startup and include as system prompt context (see Section 7).

**Environment awareness:**
- CC: can invoke any specialist, all tools available
- CAI: routes to MCP-compatible paths only, flags if task needs tools unavailable in CAI
- Agent SDK: routes with full OS access assumptions

**Design pattern:** Like search-router — teaches Claude the decision tree, not a code execution layer.

---

#### 5.2 `browse` — Navigation & Interaction Specialist

**Purpose:** Navigate websites, interact with elements, fill forms, click, scroll — the core "use the web like a human" capability.

**Triggers:** "go to", "navigate to", "open", "click", "fill", "log in", "interact with", "browse"

**Expertise encodes:**
- The 6-dimension tool selection framework (Section 4) applied to browsing tasks
- When to use headless vs native Chrome vs Browserbase isolated sessions
- How to handle dynamic content (SPAs, lazy loading, infinite scroll)
- How to verify actions succeeded (screenshot, DOM check, console errors)
- When to escalate to human (CAPTCHA, 2FA, sensitive confirmations)

**Tool palette:** Playwright MCP, Chrome DevTools MCP, Stagehand, browser-use, Browserbase, Computer Use API

**Environment paths:**
- CC: Full palette. Prefers Playwright for deterministic single-action ops, Stagehand for repeatable flows (auto-caches after first run), browser-use for autonomous multi-step with unknown flows. Tool selection per 6-dimension framework, not hardcoded preferences.
- CAI: Playwright MCP or Chrome DevTools MCP via remote connector. Limited to MCP-accessible operations.
- Agent SDK: Full palette + Computer Use API as fallback. Can install Chrome on VM.

**Key patterns:**
- "Navigate and verify": go to URL → screenshot → verify content loaded → proceed
- "Fill and submit": identify form fields → fill → screenshot → submit → verify outcome
- "Multi-tab workflow": open tabs → switch between them → aggregate results
- "Authenticated browse": auth skill provides session → browse in that session → clean up

**Observability:** Logs tool selected, site hostility assessment, auth method used, success/failure, latency, screenshots captured.

---

#### 5.3 `scrape` — Extraction Specialist

**Purpose:** Extract structured or unstructured data from websites. Single pages, bulk crawls, or targeted extraction.

**Triggers:** "extract", "scrape", "crawl", "get data from", "pull info from", "get all [items] from"

**Expertise encodes:**
- When to use Firecrawl (bulk, clean markdown, structured JSON) vs Playwright DOM parsing (interactive page, need to navigate first) vs Stagehand extract() (surgical, specific elements) vs WebFetch (simple static page)
- Schema-driven extraction: user defines desired fields, skill produces typed JSON
- Pagination handling: detect "next page", crawl systematically
- Rate limiting awareness: respect robots.txt, add delays for polite crawling
- Data quality: validate extracted data, flag inconsistencies

**Tool palette:** Firecrawl MCP (primary), Playwright, Stagehand extract(), WebFetch, Jina Reader

**Environment paths:**
- CC: All tools. Firecrawl MCP as primary, browse skill for authenticated extraction.
- CAI: Firecrawl MCP via remote connector. WebFetch for simple pages.
- Agent SDK: All tools + direct Firecrawl API for bulk operations.

**Boundary principle:** Scrape handles EXTRACTION LOGIC only. When a scraping task requires navigation (clicking pagination, filling search forms, scrolling to load more, logging in), scrape ALWAYS delegates to browse. Clean separation: browse = interaction with the page, scrape = pulling data out of the page. This prevents both specialists from duplicating navigation logic and ensures the 6-dimension tool selection for navigation happens in one place (browse).

**Key patterns:**
- "Schema extraction": user provides desired fields → skill selects extraction tool → returns typed JSON
- "Bulk crawl": Firecrawl map (discover URLs) → batch scrape → aggregate (no navigation needed — Firecrawl handles it)
- "Navigated extraction": browse navigates to target state (login, search, paginate) → scrape extracts from resulting page
- "Authenticated extraction": auth provides session → browse navigates in that session → scrape extracts
- "Competitive intelligence": scrape multiple competitor pages → structured comparison

---

#### 5.4 `search` — Evolved search-router v3

**Purpose:** Route search queries to the optimal tool based on query type, complexity, and environment.

**Triggers:** "search for", "look up", "find", "research", "what is", "how to", "documentation", "deep research"

**What changes from v2:**
- Environment awareness (CAI may not have Exa/Context7 depending on MCP config)
- Firecrawl search added as a tier (search + scrape in one call)
- Observability logging (which tool selected, why, outcome quality)
- Integration with browse skill for "search then navigate to result" workflows

**Preserves:** All v2 routing logic, cost optimization, Context7-first for library docs.

**Base file:** Existing `Web & Browsers/search-router/SKILL.md` (v2) is the base. Only the deltas above are applied — this is a patch, not a rewrite. The v2 decision matrix, cost-benefit table, and fallback strategy remain unchanged.

---

#### 5.5 `qa` — Web App Testing Specialist

**Purpose:** Systematically test web applications. Find bugs, verify features, produce structured reports.

**Triggers:** "QA", "test this", "find bugs", "check if working", "dogfood", "regression test"

**Expertise encodes (inspired by gstack, our own implementation):**

**Four testing modes:**
1. **Diff-aware** (automatic on feature branches): analyze git diff → identify affected pages → test those pages → verify changes match intent
2. **Full** (systematic exploration): visit every reachable page, document issues, produce health score
3. **Quick** (30-second smoke test): homepage + top 5 nav targets, check loads/console errors/broken links
4. **Regression** (comparative): run full mode → compare against saved baseline → report deltas

**Health scoring (8 categories, weighted):**

| Category | Weight | What's Checked |
|---|---|---|
| Console Errors | 15% | JS errors, warnings, unhandled rejections |
| Broken Links | 10% | 404s, dead links, missing resources |
| Visual Issues | 10% | Layout breaks, overflow, misalignment |
| Functional Bugs | 20% | Forms not submitting, buttons not working, state issues |
| UX Problems | 15% | Confusing flows, missing feedback, poor error messages |
| Performance | 10% | Slow loads, large bundles, render blocking |
| Content Quality | 5% | Typos, placeholder text, missing content |
| Accessibility | 15% | a11y tree issues, keyboard nav, contrast |

**Framework-specific patterns:** Next.js (hydration errors, _next/data), Rails (N+1, CSRF), WordPress (plugin conflicts), SPAs (state persistence, history).

**Tool palette:** browse skill (navigation), Chrome DevTools MCP (console, network, perf), Playwright (screenshots, a11y tree)

**Output:** Structured report with: health score, issues (severity + screenshot + repro steps), console health summary, regression delta (if baseline exists).

---

#### 5.6 `auth` — Session Management Specialist

**Purpose:** Manage authentication across all web tools and environments. The layered auth model.

**Triggers:** "log in to", "set up auth for", "access my account on", or invoked by other specialists when auth is needed.

**The layered auth model (top = best, bottom = fallback):**

| Layer | When to Use | How It Works | Persistence |
|---|---|---|---|
| **API keys/tokens** | Service has an API (Notion, Linear, GitHub, etc.) | Direct API call, no browser needed | Long-lived, stored in env vars |
| **OAuth apps** | Service supports OAuth (Google, GitHub, Slack, etc.) | OAuth flow → refresh token → auto-renew | Weeks-months, auto-refreshable |
| **Persistent sessions** (Browserbase) | Cloud agent needs durable browser sessions | Browserbase session with stored cookies/storage | Days-weeks, managed by Browserbase |
| **Cookie sync** (Mac → cloud) | Service only works with browser cookies | Cron on Mac extracts cookies → rsync/API to droplet | Hours-days, requires periodic refresh |
| **Real browser session** | 2FA required, no other option | Native Chrome with real profile, human confirms | Session-length, manual |
| **Graceful degradation** | All above fail | Report what failed, suggest alternatives, proceed unauthenticated where possible | N/A |

**Per-service strategies (to be discovered and documented during build):**

| Service Category | Likely Best Layer | Notes |
|---|---|---|
| Productivity (Notion, Linear, GitHub) | API keys/tokens | These all have APIs. No browser needed. |
| Google (Gmail, Calendar, Drive) | OAuth + MCP | Already connected via MCPs in AI CoS |
| Social (LinkedIn, X/Twitter) | Cookie sync + stealth browsing | No API for reading. Bot-hostile. Browserbase needed. |
| E-commerce/banking | Browserbase isolated session | High risk. Never use real session. |
| General SaaS | Per-service assessment | Evaluate on first access, document strategy |
| YouTube | Cookie sync | Already proven (Safari → droplet rsync, 1-2 week expiry) |

**Cookie sync infrastructure:**

```
LOCAL MAC (cron job, e.g. daily or on-demand)
  ├── Extract cookies from real browser (Safari/Chrome/Arc)
  │   Method: Production cookie extraction tool (see Phase 0 evaluation)
  │   Or: browser-specific cookie extraction tool
  ├── Filter to relevant domains (not all cookies)
  ├── Stage to ~/.ai-cos/cookies/ (chmod 600, NEVER /tmp/)
  ├── Encrypt in transit
  └── Push to droplet via rsync over Tailscale
       rsync ~/.ai-cos/cookies/ root@aicos-droplet:/opt/ai-cos-mcp/cookies/

DROPLET
  ├── Receives cookie files per-domain
  ├── Loads into browser tools (Playwright, Stagehand, browser-use) on demand
  └── Tracks expiry, logs when cookies fail
```

**Cookie sync script spec:**

| Aspect | Decision |
|---|---|
| Language | Bash (simple, cron-friendly, matches existing deploy.sh pattern) |
| Trigger | Cron on Mac (daily default, configurable) + on-demand CLI invocation |
| Extraction method | **Phase 0 evaluation determines this.** Candidates: (1) compiled binary (gstack pattern — most reliable, handles keychain/encryption), (2) Python `browser_cookie3` library (cross-browser, maintained), (3) direct SQLite reading of Chrome/Arc/Brave cookie DBs, (4) `yt-dlp --cookies-from-browser` (current hack — limited to what yt-dlp supports). The yt-dlp method is a proven starting point from the YouTube pipeline but is NOT production-grade for arbitrary domains. The winner must handle: Safari keychain encryption, Chrome Safe Storage encryption, domain-level filtering, and Netscape format output. |
| Output format | Netscape cookie format (`.txt`) — this is what Playwright's `storageState`, Stagehand, and browser-use all accept natively |
| Domain filtering | Script accepts domain list as argument. Only exports cookies matching specified domains. |
| Transport | `rsync -avz --rsh="ssh" /tmp/cookies/ root@aicos-droplet:/opt/ai-cos-mcp/cookies/` over Tailscale |
| Droplet loading | Playwright: `context.add_cookies()` from parsed Netscape file. Stagehand/browser-use: cookie file path in config. |
| Location | `Web & Browsers/auth/scripts/cookie-sync.sh` (source in Skills Factory), deployed to Mac + droplet |

**Auth service registry:**
Discovered per-service auth strategies are documented in `Web & Browsers/auth/auth-service-registry.md` — a living document updated as new services are onboarded. Format: `| Service | Best Layer | Notes | Last Verified |`

**Staleness detection:** The auth skill checks the `Last Verified` date before using any registry strategy. Thresholds: cookies >30 days = stale (re-extract), API keys >90 days = review (may still be valid but check), OAuth tokens = auto-refresh (no manual staleness). Stale entries are flagged to the user before proceeding. The skill can still use a stale strategy with a warning, but never silently.

**Safety principles:**
- Never store raw credentials in skill files. Env vars and vault references only.
- Human confirmation for: first-time auth to new services, payment actions, account changes.
- Isolated sessions for anything that could damage real auth.
- Credential rotation awareness: log when tokens/cookies expire, alert user.

---

#### 5.7 `perf-audit` — Performance Specialist

**Purpose:** Measure, diagnose, and prescribe fixes for web performance. Core Web Vitals expert.

**Triggers:** "check performance", "Core Web Vitals", "Lighthouse", "is this fast", "optimize performance", "page speed"

**Three-pass methodology:**

1. **Measure:** Run Lighthouse via Chrome DevTools MCP. Capture LCP, INP, CLS, FCP, TTFB. Compare to CrUX data (real user metrics) if available.

2. **Diagnose:** Analyze trace data. Identify: render-blocking resources, unoptimized images, excessive JS where CSS suffices (scroll animations, tooltip positioning, parent toggling), layout shift causes, long tasks blocking main thread.

3. **Prescribe:** Specific, actionable fixes ranked by impact. Knows CSS 2026 perf wins: scroll-driven animations over JS libs (drop AOS = -45KB), anchor positioning over Popper.js, container queries over JS-driven responsive logic, native CSS nesting over preprocessor overhead.

**Tool palette:** Chrome DevTools MCP (Lighthouse, performance traces, CrUX), Playwright (viewport testing, screenshot comparison), browse skill (page navigation)

**Dual use:** Works for both:
- Web auditing: "How fast is this public URL?" (any surface)
- Frontend code auditing: "Is this generated code performant?" (CC during build)

---

#### 5.8 `watch` — Monitoring Specialist

**Purpose:** Monitor websites for changes over time. Detect content changes, price changes, availability, competitor moves, site status.

**Triggers:** "monitor", "watch", "track changes", "alert me if", "keep an eye on", "check periodically"

**Core pattern:**
```
SETUP: Capture baseline (URL + extraction schema + check interval + alert threshold)
LOOP:  Re-check at interval → extract current state → diff against baseline
       If diff exceeds threshold → alert
       Update baseline for next comparison
```

**Monitoring types:**
- Content change: text/HTML diff, new items appearing
- Price change: specific field tracking with threshold
- Availability: is the site/page/product available?
- Visual change: screenshot comparison (pixel diff)
- Performance regression: periodic Lighthouse runs (uses perf-audit)

**Tool palette:** browse skill (navigation), scrape skill (extraction), perf-audit skill (for performance monitoring), cron/scheduling infrastructure

**Cloud agent fit:** Natural cron job on the droplet. Scheduled monitoring tasks that run autonomously and alert via existing channels (cross-sync, Notion, future WhatsApp).

**Environment paths:**
- CC: One-off monitoring setup, manual re-checks
- CAI: Can configure via MCP, check results via MCP
- Agent SDK: Scheduled cron jobs on droplet, autonomous operation

**State storage:**

| Environment | Storage | Location | Format |
|---|---|---|---|
| CC | JSON files | `.watch/` in project root or `~/.claude/watch/` | Per-monitor JSON: `{url, schema, interval, threshold, baseline, last_check, last_diff}` |
| Agent SDK (droplet) | SQLite | `/opt/ai-cos-mcp/watch.db` | Table: `monitors(id, url, schema, interval, threshold, baseline_json, last_check, last_diff_json, status)` |
| CAI | Via MCP | Stored on droplet (Agent SDK path), queried via MCP tool | Same SQLite, accessed through ai-cos-mcp tool |

Baselines include: extracted data snapshot (JSON), screenshot hash (for visual monitoring), Lighthouse score (for perf monitoring). SQLite on droplet is preferred for Agent SDK because cron jobs need atomic reads/writes and state must survive restarts.

---

### Frontend Skills (3 updates)

#### 5.9 `design-system-enforcer` — UPDATE

**What changes:**

**CSS 2026 patterns added:**
- Container queries over breakpoint variants: `@container` instead of viewport media queries for component-level responsiveness
- `:has()` over JS parent toggling: parent selector eliminates class toggling JavaScript
- Native nesting over preprocessors: CSS nesting (120+ browser support) replaces Sass nesting
- oklch() + color-mix() over manual palettes: perceptually uniform colors, programmatic blending
- Scroll-driven animations over JS libs: `animation-timeline: scroll()` replaces AOS/ScrollReveal
- View transitions over framework transitions: `@view-transition { navigation: auto }` for page transitions
- Anchor positioning over positioning libs: CSS anchor positioning replaces Popper.js/Floating UI

**Vite 8 knowledge:**
- When scaffolding: always Vite, never CRA or webpack
- Grounded via Context7 (query Vite docs at trigger time, not baked-in knowledge)
- Reference doc with Rolldown, Environment API, console forwarding patterns

**Anti-drift failsafes:**
- Context7 queries for live component/library APIs (not baked-in knowledge)
- shadcn MCP for component verification (not hallucinated props)
- Reference docs loaded on skill trigger (current patterns, not training data)
- Explicit anti-patterns list (things NOT to generate)

**New anti-patterns:**
- Don't generate Sass for nesting or variables (native CSS now)
- Don't use AOS, ScrollReveal, Locomotive Scroll (CSS scroll-driven animations)
- Don't use Popper.js or Floating UI for basic tooltips (CSS anchor positioning)
- Don't use CRA or webpack for new projects (Vite)
- Don't use Autoprefixer for commonly supported properties (baseline 2026)

---

#### 5.10 `a11y-audit` — UPDATE

**What changes:**
- Chrome DevTools MCP Lighthouse accessibility audit added alongside Playwright a11y tree
- web.dev accessibility course patterns integrated (21 modules of best practices)
- WCAG 2.2 AA touch target: 44x44px minimum (48px recommended for mobile-primary)
- Deeper keyboard testing patterns from web.dev
- Animation/motion: `prefers-reduced-motion` enforcement from web.dev

---

#### 5.11 CLAUDE.md Production Standards — UPDATE

**New sections to add to ~/.claude/CLAUDE.md:**

```markdown
### CSS 2026 Baseline (Mandatory)
- Use container queries for component-level responsiveness, not viewport breakpoints
- Use :has() for parent-dependent styling, not JavaScript class toggling
- Use native CSS nesting, not Sass/Less (unless project already uses them)
- Use oklch() and color-mix() for color systems
- Use scroll-driven animations for scroll-linked effects, not JS libraries
- Use CSS anchor positioning for tooltips/popovers, not Popper.js

### Build Tool Default
- When scaffolding new projects, use Vite (not CRA, not webpack)
- Default browserslist: `defaults and fully supports es6-module`
- Or: `baseline widely available` for maximum compatibility

### Frontend Anti-Patterns (Updated 2026-03)
- No Sass for nesting/variables only (native CSS handles both)
- No AOS/ScrollReveal/Locomotive Scroll (CSS scroll-driven animations)
- No Popper.js/Floating UI for basic positioning (CSS anchor positioning)
- No Autoprefixer for grid/flexbox/transforms (baseline for 3+ years)
```

---

## 6. Auth Architecture (Deep Dive)

### The Problem

AI agents need to access authenticated websites. This is the hardest unsolved problem in the web skills portfolio. Every approach has failure modes:
- Cookies expire (hours to weeks depending on service)
- Tokens get revoked (rate limiting, suspicious activity detection)
- 2FA triggers from new IP/device
- Bot detection blocks automation
- Session ejection can break the real user's access

### The Layered Solution

No single auth method works for all services. The auth skill encodes a multi-layer approach:

```
For each service/site, the auth skill:
1. Checks if API access exists → use API (no browser needed)
2. Checks if OAuth is available → use OAuth flow
3. Checks if persistent session is viable → use Browserbase
4. Checks if cookie sync is configured → use imported cookies
5. Falls back to → real browser (human in loop) or graceful degradation
```

### Infrastructure Requirements

**On local Mac:**
- Cookie extraction script (runs on demand or cron)
- Supports: Safari, Chrome, Arc, Brave, Edge (via yt-dlp cookie extraction or dedicated tool)
- Filters cookies by domain (only export what's needed)
- Pushes to droplet via rsync over Tailscale

**On droplet:**
- Cookie storage directory: `/opt/ai-cos-mcp/cookies/` (per-domain or per-service files)
- Cookie loading into browser tools on demand
- Expiry tracking and alerting (log when cookies fail, notify user)
- Browserbase SDK for isolated sessions (requires account setup)

**In CC (local):**
- Can use real browser profile directly (gstack-inspired cookie import from installed browsers)
- Chrome DevTools MCP connects to existing Chrome session (with user's real auth)

**In CAI:**
- MCP-only auth. Limited to what MCP tools can provide.
- For services with MCP connectors (Notion, Gmail, Calendar) — already handled.
- For web browsing in CAI — depends on MCP server having auth context.

### Open Questions (Auth)

- [ ] Which cookie extraction tool is most reliable across browsers? (yt-dlp? dedicated tool? gstack's approach?)
- [ ] Browserbase pricing and session persistence limits for production use
- [ ] How to handle 2FA for cloud agent when human isn't available (queue + retry? pre-authorized devices?)
- [ ] Credential vault solution (1Password CLI? HashiCorp Vault? .env files sufficient?)
- [ ] Cookie expiry monitoring automation (detect failure, alert, auto-retry with fresh cookies)

---

## 7. Cloud Agent Integration (AI CoS)

### Context

The AI CoS runs on a DigitalOcean droplet (Ubuntu 24.04). Currently: ContentAgent (5-min cron) + SyncAgent (10-min cron) + ai-cos-mcp server (17 tools). Future planned runners: PostMeetingAgent, OptimiserAgent, IngestAgent. The system is ever-evolving — current architecture is not permanent form.

### What Cloud Agents Need from Web Skills

| Runner / Agent | Web Capabilities Needed | Priority |
|---|---|---|
| **IngestAgent** (planned) | URL → structured data extraction, screenshot → data, web page → profile | High — directly uses scrape + browse |
| **OptimiserAgent** (planned) | Company research, founder lookup, competitive analysis | High — uses search + scrape |
| **ContentAgent** (live) | Currently YouTube-only. Could expand to web sources (blogs, newsletters, podcasts) | Medium — uses scrape for new sources |
| **PostMeetingAgent** (planned) | Look up people/companies mentioned in meetings | Medium — uses search |
| **Monitoring tasks** | Watch competitor sites, track portfolio company pages | Medium — uses watch + scrape |
| **General autonomous browsing** | Any web task the AI CoS needs to perform | Long-term — uses full stack |

### Infrastructure Changes Needed on Droplet

**Browser runtime:**
- Install headless Chrome/Chromium on droplet
- Install Playwright browsers: `npx playwright install chromium`
- Install Node.js MCP servers (Chrome DevTools MCP, Firecrawl MCP)
- Optionally: Stagehand, browser-use (Python)

**MCP server architecture (DECIDED):**
- **Separate web-tools MCP process** on droplet. Chrome must NOT share a process with ai-cos-mcp.
- Rationale: Fault isolation — Chrome crash/OOM must not kill Notion/calendar/thesis tools.
- web-tools MCP runs as its own systemd service alongside ai-cos-mcp.
- Simple web tools (URL extraction, search) may still be added to ai-cos-mcp for convenience.
- Browser-dependent operations (Playwright, Stagehand, browser-use) always go through web-tools MCP.

**Resource considerations:**
- Headless Chrome needs ~100-300MB RAM minimum
- Current droplet: 1GB RAM — **MUST upgrade to $24/mo (4GB) BEFORE installing Chrome**
- 1GB + existing services (~500MB) + Chrome (~300-600MB) = OOM. This is a Phase 1 blocker.
- Communicate via cross-sync to AI CoS as a prerequisite task.
- Scaling tiers already documented in AI CoS SYSTEM-STATE.md

**Cookie infrastructure:**
- `/opt/ai-cos-mcp/cookies/` directory for per-domain cookie files (chmod 600)
- Loading mechanism for Playwright/Stagehand/browser-use
- Expiry monitoring in logs

**Process supervision (all MCP servers):**
- Every MCP server on the droplet gets a systemd unit file
- Post-deploy verification: `systemctl status <service>` confirms running
- Liveness health check: periodic curl/socket check, auto-restart on failure
- Services: `ai-cos-mcp.service`, `web-tools-mcp.service` (new, Phase 1)
- Logs: `journalctl -u <service>` for debugging

**Deployment spec (`deploy.sh`):**
- `rsync -avz --checksum --delete` from Skills Factory/AI CoS to droplet over Tailscale
- Pre-deploy: verify remote is reachable, backup current state
- Post-deploy: checksum verification, `systemctl restart <services>`, smoke test (health endpoint)
- Writes `DEPLOYED_VERSION` file on droplet with git commit hash + timestamp
- Secrets managed via `secrets-manifest.md`: lists every secret, where it lives, rotation schedule, who owns it

**Disaster recovery for SQLite state:**
- `web-logs.db` and `watch.db` are operational state — loss means losing monitoring baselines and log history
- Backup: DigitalOcean automated snapshots (weekly) + `sqlite3 .dump` cron (daily, to `/opt/ai-cos-mcp/backups/`)
- Recovery: restore from DO snapshot or re-import from dump file
- Acceptable loss: up to 24 hours of log data (not mission-critical)

### Tasks for AI CoS Project (Cross-Sync)

These tasks will be communicated via cross-sync messages as Skills Factory phases ship:

| Phase | Cross-Sync Message | AI CoS Task |
|---|---|---|
| Phase 1 | "browse + auth skills shipped" | Install Chrome on droplet, configure Playwright, set up cookie sync cron, test browse via MCP |
| Phase 2 | "scrape + search v3 shipped" | Configure Firecrawl MCP on droplet, wire into IngestAgent, test extraction |
| Phase 3 | "qa + perf-audit shipped" | Set up digest.wiki auto-QA, configure Lighthouse via Chrome DevTools MCP |
| Phase 4 | "watch skill shipped" | Set up monitoring cron jobs for portfolio/competitor sites |
| Ongoing | Auth layer updates | Configure per-service auth strategies as new services are added |

### Open Questions (Cloud Agent)

- [x] ~~Droplet RAM upgrade timing~~ — **DECIDED: Phase 1 prerequisite, $24/mo 4GB (Step 1.0)**
- [x] ~~ai-cos-mcp extension vs separate web-tools MCP server~~ — **DECIDED: Separate web-tools MCP (fault isolation)**
- [ ] Browserbase vs self-hosted browser on droplet for persistent sessions
- [ ] Computer Use API viability on droplet (needs Xvfb + display server)
- [ ] How Agent SDK runners call MCP tools (MCP client library vs HTTP calls to local server)

---

## 8. CAI Integration

### Current State

Claude.ai has:
- Built-in WebSearch and WebFetch
- Remote MCP connectors (connected to ai-cos-mcp at mcp.3niac.com/mcp)
- Project instructions (can encode skill knowledge)
- No terminal, no file system, no plugins, no hooks

### What CAI Can Use

| Tool | CAI Access | How |
|---|---|---|
| Firecrawl MCP | Yes | Add as remote MCP connector in CAI settings |
| Chrome DevTools MCP | Possible but limited | Would need to run on accessible server with remote MCP transport |
| Playwright MCP | Possible but limited | Same — needs accessible server |
| browser-use MCP | Possible | Run MCP server on droplet, expose via Cloudflare Tunnel |
| WebSearch/WebFetch | Yes | Built-in |
| Exa/Parallel | Yes | Already configured as MCPs in CAI |
| ai-cos-mcp tools | Yes | Already connected via mcp.3niac.com |

### CAI Integration Strategy

**Option A: Extend ai-cos-mcp with web tools**
Add web browsing/scraping tools to the existing ai-cos-mcp server on the droplet. CAI already connects to it. New tools appear automatically.

**Option B: Separate web-tools MCP on droplet**
New MCP server at e.g. `https://web.3niac.com/mcp`. CAI adds it as a second remote connector.

**Option C: Run web MCPs on droplet, expose via Cloudflare Tunnel**
Run Firecrawl MCP, Playwright MCP, or browser-use MCP on the droplet alongside ai-cos-mcp. Expose as separate Cloudflare Tunnel endpoint (e.g., `https://web.3niac.com/mcp`). CAI adds it as a remote MCP connector.

**NOTE:** Firecrawl MCP runs via `npx firecrawl-mcp` locally — there is NO hosted MCP endpoint from Firecrawl. Any CAI access to Firecrawl requires running it on a server with remote MCP transport.

**Decision (resolved):** Option C — separate web-tools MCP on droplet with its own Cloudflare Tunnel (e.g., `https://web.3niac.com/mcp`). This is consistent with the fault isolation decision in Section 7 (M10): Chrome must not share a process with ai-cos-mcp. Simple web tools (URL extraction, search) can still be added to ai-cos-mcp for convenience — browser-dependent operations go through web-tools MCP.

**Timing:** web-tools MCP setup begins in Phase 1 (alongside Chrome installation on droplet). CAI connector added once the Tunnel is live. Cross-sync message to AI CoS triggers this work.

### Tasks for CAI Setup

- [ ] Add Firecrawl MCP as remote connector in CAI
- [ ] Evaluate which web tools to add to ai-cos-mcp for CAI access
- [ ] Create CAI project instructions that encode web skill knowledge (search routing, tool selection)
- [ ] Test: "scrape [URL] and extract [fields]" works in CAI via Firecrawl MCP

### Open Questions (CAI)

- [ ] Can CAI connect to Chrome DevTools MCP running on the droplet?
- [ ] Latency impact of remote MCP calls for browser operations
- [ ] How to encode the 6-dimension decision framework in CAI project instructions (no skill system)
- [ ] Rate limits on remote MCP connectors in CAI

---

## 9. Build Order & Testing Gates

### Phase 0: Tool Evaluation (BLOCKING — must complete before Phase 1)

Hands-on evaluation of every tool in Layer 1. The 6-dimension framework can only be built on verified capabilities, not documentation claims.

**Evaluation targets:**

| Tool | What to Evaluate | Test Scenario | Pass Criteria |
|---|---|---|---|
| Chrome DevTools MCP | All 29 tools, latency, token usage | Navigate, fill form, run Lighthouse, inspect network on a test site | Tools work reliably, latency acceptable for interactive use |
| Firecrawl MCP | Scrape, crawl, search, extract, agent mode | Extract structured data from 3 different site types (SaaS, blog, e-commerce) | Clean output, schema extraction works, agent mode produces usable results |
| browser-use MCP | Reliability, token efficiency, autonomous planning | Multi-step task: search for product, compare prices, extract results | Completes task autonomously, token cost acceptable |
| Browserbase | Isolated sessions, proxy rotation, anti-detection, persistent sessions | Access a bot-hostile site (LinkedIn), maintain session across multiple commands | Session persists, bot detection evaded, pricing viable |
| Stagehand (existing) | Verify v3 features, auto-caching, act/extract/observe | Repeat a navigation flow 3 times, verify caching kicks in | 2nd+ run at least 30% faster, debug log confirms cached selector reuse |
| Cookie extraction | Extract cookies from Safari, Chrome, Arc | Export cookies for 3 domains, verify format, load into Playwright | Netscape format output, Playwright accepts cookies, authenticated page loads |
| Playwright MCP (existing) | Verify current capabilities, token cost baseline | Same navigation flow as Stagehand test | Baseline token cost and latency documented |

**Deliverable:** `Web & Browsers/phase-0-tool-evaluation.md` — results for each tool, recommendation for inclusion/exclusion in Layer 1, any surprises that affect the 6-dimension framework.

**Cookie extraction evaluation (elevated from open question):** This is NOT a minor evaluation. Production cookie handling requires:
1. Reliable extraction from multiple browsers (Safari keychain, Chrome SQLite, Arc)
2. Domain-level filtering (not dumping all cookies)
3. Netscape format output (compatible with Playwright, Stagehand, browser-use)
4. Automated refresh (cron-compatible, not manual)
5. Secure transport (encrypted, over Tailscale)

Evaluate: gstack's compiled binary approach, direct SQLite reading of browser cookie DBs, Python `browser_cookie3` library, `yt-dlp --cookies-from-browser` (current hack — assess limitations), and any other dedicated tools. The winner becomes the foundation of the auth specialist's cookie sync script.

**Phase 0 deliverables:**
1. `Web & Browsers/phase-0-tool-evaluation.md` — results for each tool, recommendation for inclusion/exclusion
2. `Web & Browsers/layer-1-toolset.md` — formal decision record: which tools made it into Layer 1, which were excluded and why. This is the transition gate from Layer 1 (tools) to Layer 2 (specialists). No specialist development begins until this document exists.

**Phase 0 testing gate:** Evaluation report complete. Layer 1 toolset decided. No skill development begins until tool capabilities are verified hands-on.

**Phase 0 failure scenarios (5):**
1. Chrome DevTools MCP fails to connect to Chrome process → verify error message is actionable, not silent hang
2. Firecrawl returns empty result on a page with clear content → verify fallback to WebFetch or Playwright
3. browser-use exceeds 60s timeout on a simple task → verify timeout handling, not infinite loop
4. Cookie extraction script fails on locked Safari keychain → verify error, not corrupted output
5. Browserbase session creation fails (API key invalid, quota exceeded) → verify error, not silent null session

---

### Phase 1: Foundation — auth + browse + web-router

**Step 1.0: Droplet RAM Upgrade (PREREQUISITE — must complete before any Chrome install)**
- Upgrade DigitalOcean droplet from $12/mo (1GB) to $24/mo (4GB)
- 1GB + existing services (~500MB) + Chrome (~300-600MB) = OOM
- Cross-sync to AI CoS as blocker: `{"type": "task", "content": "BLOCKER: Upgrade droplet to $24/mo (4GB) before any Chrome/Playwright install. Current 1GB will OOM.", "priority": "urgent"}`

**Step 1.1: Tool Configuration (based on Phase 0 results)**
- Pin all MCP versions in `~/.mcp.json` (not `@latest` — explicit versions for reproducibility)
- Install Chrome DevTools MCP globally: add to `~/.mcp.json` as `{"chrome-devtools": {"command": "npx", "args": ["-y", "chrome-devtools-mcp@1.x.x"]}}`
- Install Firecrawl MCP globally: add to `~/.mcp.json` as `{"firecrawl": {"command": "npx", "args": ["-y", "firecrawl-mcp@1.x.x"], "env": {"FIRECRAWL_API_KEY": "..."}}}` (canonical config method — all MCPs go in ~/.mcp.json, pinned versions)
- Verify existing Playwright MCP and Stagehand plugin work
- Evaluate browser-use MCP server: install, test, assess value
- Evaluate Browserbase: create account, test isolated sessions, assess pricing

**Step 1.2: Build `auth` specialist** (SKILL-CRAFT methodology)
- Development log in `Web & Browsers/auth/skill-development-log.md`
- Layered auth model (6 layers with escalation)
- Cookie extraction: production-grade tooling (see Phase 0 evaluation)
- Cookie sync script: `Web & Browsers/auth/scripts/cookie-sync.sh`
- Auth service registry: `Web & Browsers/auth/auth-service-registry.md`
- Safety principles (protect real sessions, human confirmation for sensitive actions)
- Deploys as: `~/.claude/skills/web-router/references/auth.md`

**Step 1.3: Build `browse` specialist** (SKILL-CRAFT methodology)
- Development log in `Web & Browsers/browse/skill-development-log.md`
- Encode 6-dimension tool selection framework as expertise
- Environment awareness (CC/CAI/Agent SDK paths)
- Reference docs for grounding (tool APIs, patterns)
- Uses auth specialist for authenticated browsing
- Deploys as: `~/.claude/skills/web-router/references/browse.md`

**Step 1.4: Build `web-router` skill**
- Development log in `Web & Browsers/web-router/skill-development-log.md`
- Task classification
- Environment detection
- Specialist invocation

**Testing Gate — Phase 1:**

| Surface | Test Scenario | Pass Criteria |
|---|---|---|
| CC | "Navigate to HN, search for 'Claude', extract top 3 results" | (1) browse specialist activated by router, (2) tool selection logged with all 6 dimensions, (3) results contain ≥3 items with title+URL fields |
| CC | "Log into [test site] and extract dashboard data" | (1) auth specialist activated, (2) cookie injected successfully, (3) dashboard data extracted with expected fields |
| CC | web-router correctly classifies and routes | (1) Routing decision logged as YAML, (2) correct specialist invoked, (3) composite task correctly classified if multi-specialist |
| CC | Observability log verification | (1) Log file exists at `~/.claude/web-logs/`, (2) valid YAML, (3) all required fields present (timestamp, specialist, task, environment, dimensions, tool_selected, reasoning, outcome) |
| CAI | "Search for [topic]" via MCP | (1) Search tool activated, (2) results returned with sources, (3) routing logged on droplet |
| CAI | "Scrape [public URL]" via Firecrawl MCP | (1) Firecrawl MCP responds, (2) clean markdown returned, (3) extraction matches expected content |
| Agent SDK | Runner loads browse reference doc and navigates URL | (1) Reference doc loaded into system prompt, (2) navigation succeeds, (3) tool selection reasoning in output |

**Phase 1 failure scenarios (6):**
1. URL returns 403 Forbidden → verify graceful error message, not raw HTTP dump
2. Expired cookie used for authenticated browse → verify auth escalation to next layer, not silent failure
3. MCP server timeout (Chrome DevTools MCP hangs) → verify 30s timeout fires, fallback activates
4. Rate-limited by target site (429) → verify backoff + retry, not immediate failure
5. Browserbase session creation fails → verify error, fallback to local Playwright
6. web-router receives ambiguous task ("check this site") → verify classification logged, reasonable default chosen

**Phase 1 rollback drill:** After first deployment to `~/.claude/skills/`, intentionally revert a reference doc to a previous version via `git checkout`. Verify: (1) rollback is clean, (2) skill still functions with older version, (3) process documented for future use.

**Cross-Sync to AI CoS:**
```json
{"type": "task", "content": "Phase 1 shipped: browse + auth + web-router skills deployed to CC. MCPs configured: Chrome DevTools, Firecrawl. Action needed: install Chrome on droplet, configure Playwright, set up cookie sync cron from Mac. Test scenario: runner calls Firecrawl MCP to extract company page data.", "priority": "normal"}
```

### Phase 2: Extraction — scrape + search v3

**Step 2.1: Build `scrape` skill**
**Step 2.2: Evolve `search` to v3**

**Testing Gate — Phase 2:**

| Surface | Test Scenario | Pass Criteria |
|---|---|---|
| CC | "Extract all pricing plans from [SaaS site] as JSON" | (1) Schema extraction returns typed JSON, (2) all expected fields present, (3) tool selection logged |
| CC | "Crawl [site] and extract all blog post titles + dates" | (1) Bulk crawl discovers ≥5 pages, (2) extraction returns title+date for each, (3) no duplicate entries |
| CC | "Research [topic] deeply" | (1) search v3 routes to correct tool, (2) observability log written, (3) results include ≥3 sources |
| CAI | "Extract data from [URL]" via Firecrawl MCP | (1) Firecrawl MCP responds in CAI, (2) clean structured output, (3) matches CC output quality |
| Agent SDK | Runner calls Firecrawl MCP to extract a company profile page | (1) Structured data returned, (2) matches expected schema fields, (3) tool selection reasoning logged |

**Phase 2 failure scenarios (5):**
1. Rate-limited during bulk crawl (429 on page 3 of 10) → verify graceful partial results + retry, not total failure
2. Firecrawl returns empty extraction for a page with clear content → verify fallback to Playwright DOM parsing
3. Search query returns no results from primary tool → verify fallback chain activates (Context7 → WebSearch → Exa)
4. Schema extraction mismatches (expected 5 fields, got 3) → verify partial result flagged, not silently accepted
5. Crawl discovers 500+ pages (unexpected scope) → verify depth/count limit fires, user prompted before continuing

**Cross-Sync to AI CoS:**
```json
{"type": "task", "content": "Phase 2 shipped: scrape + search v3. Firecrawl MCP on droplet enables IngestAgent to extract structured data from URLs. Test: have a runner call Firecrawl to extract a company profile page."}
```

### Phase 3: Quality — qa + perf-audit

**Step 3.1: Build `qa` skill** (4 modes, health scoring, framework-specific)
**Step 3.2: Build `perf-audit` skill** (3-pass: measure, diagnose, prescribe)

**Testing Gate — Phase 3:**

| Surface | Test Scenario | Pass Criteria |
|---|---|---|
| CC | "QA test localhost:3000" | (1) Full QA report generated, (2) health score is numeric 0-100, (3) ≥1 screenshot captured, (4) issues have severity + description |
| CC | "Run diff-aware QA on this branch" | (1) Git diff analyzed, (2) only changed pages tested, (3) report scoped to affected areas |
| CC | "Audit performance of digest.wiki" | (1) Lighthouse score returned, (2) CrUX data if available, (3) ≥3 specific prescriptions with expected impact |
| CC | QA calibration: run QA on page with planted defects | (1) Health score decreases vs clean baseline, (2) planted defects appear in issue list, (3) severity ratings match expected (critical bug = critical, not minor) |
| CAI | "Check performance of [public URL]" | (1) perf-audit returns Lighthouse scores via MCP, (2) prescriptions returned, (3) format matches CC output quality |

**Phase 3 failure scenarios (6):**
1. localhost:3000 is down when QA runs → verify diagnostic message ("server not responding"), not cryptic Playwright error
2. Lighthouse audit times out on heavy page → verify partial results returned + timeout warning
3. Chrome DevTools MCP disconnects mid-audit → verify reconnection attempt, graceful partial report
4. QA finds 50+ issues → verify prioritized output (critical first), not overwhelming dump
5. Diff-aware QA on branch with no frontend changes → verify "no frontend changes detected" message, not empty report
6. Performance audit on site behind CDN returns cached metrics → verify CDN detection noted in report

**Cross-Sync to AI CoS:**
```json
{"type": "task", "content": "Phase 3 shipped: qa + perf-audit. digest.wiki can now be auto-audited for performance. Chrome DevTools MCP on droplet enables Lighthouse runs. Consider: add perf monitoring to pipeline output."}
```

### Phase 4: Intelligence — watch

**Step 4.1: Build `watch` skill** (baseline, periodic check, diff, alert)

**Testing Gate — Phase 4:**

| Surface | Test Scenario | Pass Criteria |
|---|---|---|
| CC | "Watch [competitor] pricing page for changes" | (1) Baseline captured as JSON, (2) diff mechanism detects changes on re-check, (3) alert format is actionable |
| Agent SDK | Scheduled monitoring task runs on cron | (1) Cron executes autonomously, (2) state persists in SQLite, (3) alert fires on detected change |

**Phase 4 failure scenarios (5):**
1. Monitored URL returns 404 on second check → verify alert fires with "page removed" message, not crash
2. Content changes but diff is below threshold → verify no false alert, threshold logic works
3. SQLite DB locked during concurrent cron + manual check → verify graceful retry, not corruption
4. Monitored site changes structure (new DOM) but same content → verify no false positive from structural diff
5. Watch baseline is 30+ days old → verify staleness warning, offer to re-baseline

**Cross-Sync to AI CoS:**
```json
{"type": "task", "content": "Phase 4 shipped: watch skill. Cloud agent can run scheduled monitoring. Set up cron for portfolio company page monitoring. Alert via existing channels."}
```

### Phase 5: Frontend Refresh (parallel to phases 1-4)

**Step 5.1: Update design-system-enforcer** (CSS 2026, Vite 8, anti-drift)
**Step 5.2: Update a11y-audit** (web.dev patterns, Chrome DevTools, WCAG 2.2)
**Step 5.3: Update CLAUDE.md production standards** (CSS anti-patterns, Vite default, Browserslist)

**CLAUDE.md merge safety:** CLAUDE.md changes in Phase 5 are committed atomically — one commit per section update, between phases, not mid-phase. This prevents partial updates from affecting other skills during active development.

**Testing Gate — Phase 5:**

| Surface | Test Scenario | Pass Criteria |
|---|---|---|
| CC | "Build a pricing page component" | (1) Uses container queries (not media queries), (2) oklch colors, (3) no AOS/ScrollReveal, (4) Vite scaffold if new project |
| CC | "Audit accessibility of [component]" | (1) Uses Chrome DevTools Lighthouse, (2) WCAG 2.2 AA checks, (3) 44px touch targets flagged |

**Phase 5 failure scenarios (5):**
1. Context7 unreachable when querying Vite docs → verify fallback to baked-in knowledge with staleness warning
2. shadcn MCP returns outdated component API → verify component version checked, not blindly used
3. Generated CSS uses features below baseline → verify Browserslist check fires, not silent incompatibility
4. CLAUDE.md edit conflicts with existing rules → verify atomic commit, not partial merge
5. Design system enforcer and a11y audit conflict on a recommendation → verify precedence noted (a11y wins for accessibility, design for aesthetics)

**Cross-Sync to AI CoS:**
```json
{"type": "note", "content": "Frontend skills updated with CSS 2026 patterns and Vite 8 knowledge. Any frontend work in AI CoS (digest.wiki, action frontend) benefits automatically."}
```

---

## 10. Cross-Project Workflow

### Projects Involved

| Project | Role | What Happens Here |
|---|---|---|
| **Skills Factory** | Primary build | Skills designed, built, tested for CC. MCP tool evaluation. Design docs and specs. |
| **AI CoS CC ADK** | Consumer + integration | Cloud agent integration. Droplet setup. MCP server extensions. Runner web capabilities. |
| **Global CC config** (~/.claude/) | Deployment target | Skills deployed to ~/.claude/skills/. MCPs configured in ~/.mcp.json. CLAUDE.md updated. |
| **Claude.ai** | Consumer | MCP connectors configured. Project instructions updated. Testing on CAI surface. |

### Sync Protocol

Skills Factory and AI CoS are cross-synced projects. The messaging system (`.claude/sync/inbox.jsonl`) is the coordination mechanism.

**When Skills Factory ships a phase:**
1. Skills deployed to global CC config
2. Testing completed on CC and CAI
3. Cross-sync message sent to AI CoS project with: what shipped, what MCPs are needed, what infrastructure changes are needed, test scenario
4. Aakash picks up AI CoS tasks in AI CoS project with CC

**When AI CoS needs web capabilities (reverse direction):**

Cross-sync message format (AI CoS → Skills Factory):
```json
{"type": "task", "content": "AI CoS needs [capability] for [runner/agent]. Context: [what the runner does, what web task it needs]. Current workaround: [if any]. Priority: [how this affects AI CoS build phases].", "priority": "normal|urgent"}
```

Trigger scenarios for reverse messages:
- Runner development discovers a web capability gap → message to Skills Factory
- Droplet infrastructure change affects web tools → message to Skills Factory
- MCP tool fails in production → message with failure details to Skills Factory
- New service needs auth setup → message with service details to Skills Factory

Skills Factory prioritizes accordingly (may reorder phases or add to current sprint).

**Non-linear development is expected.** Aakash may:
- Work on Phase 1 skills in Skills Factory
- Switch to AI CoS to set up droplet infrastructure
- Come back to Skills Factory for Phase 2
- Jump to AI CoS to wire IngestAgent with Firecrawl
- Work on Phase 5 frontend updates in Skills Factory while Phase 3 is in progress

The phase numbering is dependency order, not calendar order. Phases 1-4 are sequential (each builds on prior). Phase 5 is independent and can happen anytime.

---

## 11. Observability & Learning Loop

### What Gets Logged

Every specialist skill logs its tool selection reasoning in a structured format:

```yaml
timestamp: 2026-03-15T10:30:00Z
specialist: browse
task: "navigate to linkedin.com/in/john-doe and extract profile"
environment: CC
dimensions:
  speed: seconds
  hostility: hostile (LinkedIn bot detection)
  auth: cookie-sync (LinkedIn session)
  complexity: multi-step (navigate → scroll → extract)
  output_format: structured-json
  cost: medium
tool_selected: browserbase + stagehand
reasoning: "LinkedIn detects headless. Browserbase isolated session protects real auth. Stagehand for navigation + extraction."
fallback_used: false
outcome: success
latency_ms: 8400
tokens_used: 2100
```

### Learning Loop

```
Logs accumulate per-specialist
  → Review during TRACES.md compaction (every 3 iterations)
  → Patterns confirmed 2+ times → graduate to skill refinements
  → Universal patterns → graduate to CLAUDE.md
  → Anti-patterns → add to skill's "Traps" section
  → Tool selection model evolves based on real outcomes
```

### What We Track Over Time

- Which tools succeed/fail for which site categories
- Auth method reliability per service
- Latency benchmarks per tool per task type
- Token cost trends
- Fallback chain activation frequency (should decrease as primary selections improve)

---

## 12. Versioning & Rollback

### The Problem

21 deliverables across 4 locations. Skills are .md files — a bad update can degrade Claude's output quality silently. "No drift" and "deterministic outcomes" require version control and regression detection.

### Version Control

- **Skills Factory git repo** is the source of truth for all skill content. Every skill update is a commit.
- **Git tags** mark phase completions: `phase-0-eval`, `phase-1-foundation`, etc.
- **Each specialist reference doc** carries a version header: `version: 1.0.0` in YAML frontmatter.

### Regression Testing

Every skill update MUST be tested against the same test scenarios used for initial validation (from the Testing Gates in Section 9) before deploying to `~/.claude/skills/`.

**Structural regression comparison (for non-deterministic LLM output):**

LLM output varies between runs — same skill + same scenario produces different wording. Regression testing uses structural field matching, not text comparison:

1. **Required signals:** Each test scenario defines 3-5 required signals that MUST appear in output (e.g., `tool_selected: firecrawl`, extracted JSON has `price` field, report includes `health_score`). These are structural, not textual.
2. **Field matching:** Specific output fields must match expected types/values (e.g., health score is numeric 0-100, extracted JSON has all schema fields, routing log has all 6 dimensions).
3. **Negative signals:** Things that must NOT appear (e.g., hallucinated tool names, empty extraction fields, missing fallback activation on expected failure).

Codified in `phase-N-baseline.md` as: `| Scenario | Required Signals (3-5) | Field Matches | Negative Signals |`

**Process:**
1. Update specialist reference doc in Skills Factory
2. Run the phase's test scenarios in CC
3. Check required signals present, field matches correct, negative signals absent
4. If regression detected: revert in git, investigate, fix, re-test
5. Only deploy to `~/.claude/skills/` after test pass

### Rollback

If a deployed skill produces worse results than before:
1. `git log` in Skills Factory → find last known-good commit
2. `git checkout <commit> -- <file>` → restore the specific reference doc
3. Copy restored file to `~/.claude/skills/web-router/references/`
4. Log the regression in LEARNINGS.md

### Baseline Documentation

After each phase passes its testing gate, document the baseline:
- Test scenario
- Expected output quality
- Actual output (screenshot or text sample)
- Tool selection made

Stored in `Web & Browsers/baselines/phase-N-baseline.md`.

---

## 13. Unknowns & Open Questions

### Technical Unknowns

- [ ] browser-use MCP server reliability and token efficiency in practice
- [ ] Browserbase pricing viability for ongoing use (vs self-hosted browser on droplet)
- [ ] Chrome DevTools MCP latency when running on droplet via remote MCP
- [ ] Computer Use API viability on droplet without GPU/display
- [ ] Cookie extraction reliability across browsers (Safari, Chrome, Arc)
- [ ] Firecrawl agent mode quality for complex multi-page extraction

### Architecture Unknowns

- [x] ~~Extend ai-cos-mcp vs separate web-tools MCP on droplet~~ — **DECIDED: Separate web-tools MCP (Section 7, M10)**
- [ ] How Agent SDK runners consume MCP tools (client library vs HTTP)
- [ ] CAI project instructions capacity for encoding decision framework
- [x] ~~Droplet RAM upgrade timing for browser runtime~~ — **DECIDED: Phase 1 prerequisite, $24/mo 4GB (Section 9, B5)**

### Process Unknowns

- [ ] Build velocity: how long does each skill take with SKILL-CRAFT methodology?
- [ ] Testing: how to automated cross-surface testing (CC + CAI + Agent SDK)?
- [ ] How to keep decision framework evolving without it becoming stale?

---

## 14. Deliverables Summary

| # | Deliverable | Type | Lives In | Target Environment |
|---|---|---|---|---|
| 1 | `web-router` skill | Skill (SKILL.md) | ~/.claude/skills/web-router/ + Skills Factory source | CC primarily, knowledge in CAI |
| 2 | `browse` reference doc | Reference doc (browse.md) | ~/.claude/skills/web-router/references/ + Skills Factory source | CC primarily, knowledge in CAI |
| 3 | `scrape` reference doc | Reference doc (scrape.md) | ~/.claude/skills/web-router/references/ + Skills Factory source | CC + CAI (via Firecrawl MCP) |
| 4 | `search` v3 reference doc | Reference doc (search.md) | ~/.claude/skills/web-router/references/ + Skills Factory source | CC + CAI |
| 5 | `qa` reference doc | Reference doc (qa.md) | ~/.claude/skills/web-router/references/ + Skills Factory source | CC primarily |
| 6 | `auth` reference doc + scripts | Reference doc (auth.md) + scripts | ~/.claude/skills/web-router/references/ + Skills Factory source | CC + Agent SDK |
| 7 | `perf-audit` reference doc | Reference doc (perf-audit.md) | ~/.claude/skills/web-router/references/ + Skills Factory source | CC + CAI (via Chrome DevTools MCP) |
| 8 | `watch` reference doc | Reference doc (watch.md) | ~/.claude/skills/web-router/references/ + Skills Factory source | CC + Agent SDK (cron) |
| 9 | `design-system-enforcer` update | Skill update | ~/.claude/skills/ + Skills Factory source | CC |
| 10 | `a11y-audit` update | Skill update | ~/.claude/skills/ + Skills Factory source | CC |
| 11 | CLAUDE.md production standards update | Config update | ~/.claude/CLAUDE.md | CC (always loaded) |
| 12 | Chrome DevTools MCP config | MCP config | ~/.mcp.json | CC + potentially droplet |
| 13 | Firecrawl MCP config | MCP config | ~/.mcp.json + droplet | CC + CAI + Agent SDK |
| 14 | Browserbase evaluation + config | Service config | Env vars + SDK | CC + Agent SDK |
| 15 | browser-use evaluation + config | Tool config | pip install + MCP server | CC + Agent SDK |
| 16 | Cookie sync script | Script | Skills Factory + droplet | Mac → droplet |
| 17 | Cookie extraction tooling | Script/binary | Mac local | Mac |
| 18 | AI CoS droplet web infra | Infrastructure | AI CoS project | Droplet |
| 19 | AI CoS MCP extensions (if needed) | MCP server code | AI CoS project | Droplet |
| 20 | CAI MCP connector configs | Config | CAI settings | CAI |
| 21 | CAI project instructions for web | Documentation | CAI project | CAI |

---

## 15. Research Sources

Key sources that informed this design:

- [MCP Benchmark: Top MCP Servers for Web Access](https://aimultiple.com/browser-mcp) — Bright Data, Firecrawl, Browserbase benchmarks
- [Agentic Browser Landscape 2026](https://www.nohackspod.com/blog/agentic-browser-landscape-2026) — Complete guide to AI browser tools
- [Browser Automation in Claude Code: 5 Tools Compared](https://www.heyuan110.com/posts/ai/2026-01-28-claude-code-browser-automation/) — Playwright vs Stagehand vs browser-use vs Agent Browser vs DevTools MCP
- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) — 29-tool MCP server for browser debugging
- [Ghost Browser Agent](https://github.com/mourad-ghafiri/ghost-browser-agent) — Stealth browsing via Chrome Extension
- [gstack](https://github.com/garrytan/gstack) — Garry Tan's skill architecture for CC (browse, QA, cookie import)
- [browser-use](https://browser-use.com/) — 80K+ stars, autonomous browser agent framework
- [Stagehand v3](https://www.browserbase.com/blog/stagehand-v3) — AI-native Playwright, 44% faster
- [Anthropic Computer Use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) — Pixel-level desktop control API
- [CUA.ai](https://cua.ai/) — Managed computer use sandboxes
- [State of CSS 2026](https://www.codercops.com/blog/state-of-css-2026) — Container queries, :has(), scroll animations baseline
- [Vite 8](https://vite.dev/blog/announcing-vite8) — Rolldown bundler, Environment API
- [web.dev](https://web.dev/) — Google's web development reference (12 courses, Core Web Vitals, a11y)
- [Firecrawl MCP](https://github.com/firecrawl/firecrawl-mcp-server) — 6-tool web scraping MCP server
