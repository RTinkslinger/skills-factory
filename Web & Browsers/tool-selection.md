---
version: 1.0.0
---

# Tool Selection Framework

You don't pick tools by name. You reason through six dimensions, and the right tool falls out. Every dimension narrows the field. When dimensions conflict, the priority order breaks the tie.

## The Six Dimensions

### 1. Speed Requirement

What's the latency budget?

| Need | Tool | Why |
|---|---|---|
| Sub-second, deterministic | Playwright (known selectors) | No AI overhead, pure automation |
| Seconds, repeatable | Playwright MCP (snapshot → act) | a11y tree gives reliable targets |
| Seconds, one-off inspection | Chrome DevTools MCP | Rich data, single interaction |
| Minutes acceptable | Firecrawl agent (async) | Autonomous multi-source research |
| Minutes, complex multi-step | browser-use (autonomous) | Full LLM reasoning for unpredictable flows |

### 2. Site Hostility

How hard is the site fighting you?

| Level | Signals | Tool | Why |
|---|---|---|---|
| Cooperative | Public content, no bot detection | Firecrawl scrape, Playwright headless | Fast, cheap, no evasion needed |
| Moderate | Rate limits, basic bot detection | Playwright + delays, Firecrawl stealth proxy | Respect rate limits, light evasion |
| Hostile | Anti-bot JS, CAPTCHA triggers | Browserbase session + Playwright connect | Isolated identity, residential proxy |
| Adversarial | Fingerprinting, behavioral analysis | Browserbase persistent session + proxy rotation | Human-like fingerprint, separate identity |

### 3. Auth Sensitivity

Is there a logged-in session at risk?

| Scenario | Approach | Principle |
|---|---|---|
| No auth needed | Any tool, headless fine | Simplest path wins |
| Auth needed, low risk | Cookie injection into Playwright context | browser_cookie3 domain-filtered export |
| Auth needed, rate-limit risk | Browserbase isolated session | Protect real account from rate limiting |
| Auth triggers 2FA | Human in the loop — escalate | Some auth requires human confirmation |
| API available | Skip browser entirely | Best path: no browser at all |
| Session ejection risk | Browserbase with separate identity | Never risk breaking user's real session |

### 4. Task Complexity

How many steps, and do you know them upfront?

| Complexity | Tool | Why |
|---|---|---|
| Single action (read, click, fill) | Playwright MCP | Deterministic, fast |
| Multi-step known flow | Playwright MCP (scripted sequence) | Reliable replay via a11y refs |
| Multi-step unknown flow | Playwright MCP + Claude reasoning | Claude decides actions, Playwright executes |
| Multi-step unknown, Playwright failing | browser-use (autonomous) | Fallback — full LLM reasoning with adaptive navigation |
| Cross-application | Computer Use API | Only option for non-web |
| Debugging/inspection | Chrome DevTools MCP | Console, network, DOM, performance |

### 5. Token/Cost Efficiency

What's the token budget?

| Scenario | Tool | Impact |
|---|---|---|
| Bulk/repeated operations | Playwright CLI (not MCP) | 75% token savings vs MCP snapshots |
| One-off rich inspection | Chrome DevTools MCP | Verbose but worth it for depth |
| Simple page read | Jina Reader or WebFetch | FREE, minimal tokens |
| Detailed page read | Firecrawl scrape (markdown) | 1 credit, more metadata |
| Structured data extraction | Firecrawl extract (JSON) | ~38 credits, schema-enforced output |
| Multi-source research | Firecrawl agent (async) | Autonomous, returns structured results |
| Complex autonomous task | browser-use cloud | 15-31s, cloud credits |

### 6. Output Format

What does the consumer need?

| Output Need | Tool | Why |
|---|---|---|
| Structured JSON | Firecrawl extract (schema mode) | Schema-driven, typed fields |
| Clean markdown (free) | Jina Reader | FREE, fastest, best Cloudflare penetration |
| Clean markdown (detailed) | Firecrawl scrape | More metadata, 1 credit |
| Quick AI summary | WebFetch | FREE, built-in, AI-processed |
| Raw HTML / DOM | Playwright page content | Full DOM when structure matters |
| a11y tree (interaction) | Playwright snapshot / Chrome DevTools snapshot | Element refs for clicking/filling |
| Visual / screenshot | Playwright screenshot | Visual evidence, comparison |
| Lighthouse scores | Chrome DevTools Lighthouse | A11y, SEO, best practices |
| Network data | Chrome DevTools network panel | Request/response inspection |

## Conflict Resolution

When dimensions contradict, resolve in this order:

1. **Auth Safety** (highest) — never compromise real user sessions
2. **Site Hostility** — match evasion to detection level
3. **Task Complexity** — use tools that handle the required steps
4. **Output Format** — match consumer expectations
5. **Speed** — optimize within constraints above
6. **Cost** (lowest) — minimize only after other dimensions are satisfied

**Hard constraints win over soft preferences.** Auth Safety and Site Hostility eliminate tools from consideration. Speed and Cost rank the remaining options. If all tools are eliminated, escalate to the user.

## Combination Principle

A single task often uses multiple tools in sequence:

1. browser_cookie3 extracts session cookies (domain-filtered)
2. Browserbase creates an isolated session (if hostile site)
3. Playwright navigates and interacts (fast, deterministic)
4. Chrome DevTools inspects network response (if debugging)
5. Firecrawl extracts clean data from the result page

Each tool does what it's best at. No single tool does everything.

## "Protect My Account" Principle

Any action on an authenticated site where failure could:
- Eject the real user from their session
- Trigger rate limiting on the real account
- Break auth tokens that other services depend on
- Trigger 2FA that disrupts the user's workflow

**MUST** use an isolated session (Browserbase, separate profile). Never the user's real session. Non-negotiable.

## Firecrawl Guardrails

Firecrawl's JSON extraction will fabricate data when it can't access content. Before trusting any Firecrawl JSON result:

1. Check `metadata.statusCode` — must be 200
2. Check `metadata.url` against the requested URL — if different, content was redirected
3. If either check fails, discard results and fall back to Playwright

This is not optional. Firecrawl hallucination was confirmed during Phase 0 evaluation.

## Observability

Every tool selection gets logged:

```yaml
timestamp: 2026-03-15T10:30:00Z
specialist: scrape
task: "extract pricing from [site]"
environment: CC
dimensions:
  speed: seconds
  hostility: cooperative
  auth: none
  complexity: single
  output_format: structured-json
  cost: low
tool_selected: firecrawl-extract
reasoning: "no auth, structured extraction needed, cooperative site"
fallback_used: false
outcome: success
latency_ms: 3200
tokens_used: 450
failure:                    # present only when outcome != success
  primary_error: "403 Forbidden"
  fallback_chain: ["firecrawl → playwright"]
  final_tool: playwright
  resolved: true
```

Log location: `~/.ai-cos/logs/web-tools/` (YAML files, one per day). Degradation mode (if log dir missing): log to stderr, don't fail the task.
