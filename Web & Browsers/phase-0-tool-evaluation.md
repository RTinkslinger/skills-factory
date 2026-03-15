# Phase 0: Tool Evaluation Report

**Date:** 2026-03-15
**Status:** In Progress
**Sprint:** 1
**Roadmap Item:** Phase 0: Tool Evaluation <!-- notion:32329bcc-b6fc-81f6-bcfc-d7ee7c577889 -->

## Evaluation Criteria (per tool)

| Criterion | Method |
|---|---|
| Reliability | 3 runs of same scenario, count failures |
| Latency | Measure wall-clock time for standard task |
| Token cost | Count tokens consumed (from MCP response metadata or context window delta) |
| Output quality | Manually assess: complete? structured? clean? |
| Failure mode | What happens when it breaks? Timeout? Error? Silent fail? |
| Version | Pin exact version tested — never @latest |

## Summary Table (filled as evaluations complete)

| Tool | Version | Reliable? | Latency | Token Cost | Quality | Failure Mode | Verdict |
|---|---|---|---|---|---|---|---|
| Chrome DevTools MCP | @0.20.0 | YES (3/3 tests pass) | ~4.4s Lighthouse | High (a11y tree ~50-100KB) | Excellent (Lighthouse unique) | Untested (Chrome-not-running) | **Include** (Lighthouse + network) |
| Firecrawl MCP | @3.11.0 | 5/6 URLs (blog/SaaS/CF/docs/404) | 0.4-2.8s | Low (1 credit/scrape) | Excellent text, poor images | Hallucinates JSON on blocked pages; 404 reported in metadata | **Core** (with guardrails) |
| Jina Reader | r.jina.ai (free) | 6/6 URLs (all passed) | 0.2-2.4s | FREE | Clean markdown, handles CF | 404 flagged with warning in output | **Core** (free, reliable) |
| browser-use | Cloud API (bu_ key) | 6/6 URLs (all passed) | 15-31s | Cloud credits | Excellent summaries, handles SPA | Correctly identifies 404/blocked | **Fallback** (autonomous complex) |
| WebFetch | Built-in | N/A (always available) | ~1-3s | FREE | AI-processed summaries | Fails on auth pages | **Core** (built-in, free) |
| Browserbase | API live | YES (session in 0.24s) | 0.24s create | Cloud credits | N/A (infra, not extraction) | Clear 401 on bad key | **Fallback** (anti-detection) |
| Stagehand v3 | not installed | Not tested | N/A | N/A | N/A | N/A | **Defer** (revisit Phase 4) |
| Cookie extraction | browser_cookie3 | YES (Safari+Chrome) | <1s | FREE | Good (domain filtering) | Clear error on locked keychain | **Core** (cookie extraction) |
| Playwright MCP | plugin built-in | YES (2/2 tests pass) | ~2s nav+snapshot | High (50-100KB snapshots) | Excellent (interactive) | N/A (always available) | **Core** (baseline browser) |

---

## Head-to-Head Comparison (6 test URLs)

### Test URLs
1. Blog (text-heavy): `simonwillison.net` article
2. SaaS (image-heavy): `linear.app/features`
3. E-commerce (bot-hostile): `amazon.com/dp/B0DKHZTGQS`
4. Cloudflare-protected: `discord.com/safety`
5. Docs/reference: `docs.anthropic.com/en/docs/about-claude/models`
6. 404 (failure): `example.com/nonexistent-page-404`

### Results Matrix

| URL Type | Jina Reader | Firecrawl | browser-use | Notes |
|----------|------------|-----------|-------------|-------|
| **Blog** | 0.24s, 6.9KB, clean MD | 0.86s, 11.4KB, clean MD | 15.7s, summary | Jina fastest + free. Firecrawl more detailed. browser-use slowest but understands content. |
| **SaaS (images)** | 1.1s, 25KB, includes text | 0.61s, 21.7KB, mostly images | 31s, accurate summary | Jina got more text than Firecrawl! browser-use understood page despite images. |
| **E-commerce** | 1.5s, 638B, "Page Not Found" | 1.95s, 436B, 404 in metadata | 31s, "Dogs of Amazon 404" | All correctly identified 404. Amazon blocks the product page from all tools. |
| **Cloudflare** | 2.4s, 13.9KB, full content | 2.78s, 5.8KB, partial content | 15.6s, accurate summary | **Jina got through Cloudflare better than Firecrawl** (13.9KB vs 5.8KB). browser-use also penetrated. |
| **Docs** | 0.43s, 5.5KB, clean MD | 0.38s, 5.8KB, clean MD (redirect detected) | 31s, accurate summary | Both fast. Firecrawl detected redirect to `platform.claude.com`. |
| **404** | 1.2s, 296B, warning flag | 2.1s, 167B, 404 in metadata | 15.7s, correct report | Both handled gracefully. Jina adds explicit "Warning: Target URL returned error 404". |

### Key Findings

1. **Jina Reader is the surprise winner for reliability** — 6/6 URLs, fastest on average, FREE, got through Cloudflare better than Firecrawl (13.9KB vs 5.8KB), explicitly flags 404s with warnings.

2. **Firecrawl is better for structured extraction** — schema-driven JSON, agent mode, crawl/map features. But for simple markdown scraping, Jina is faster and free.

3. **browser-use handles everything but is slow** — 15-31s per task vs <3s for Jina/Firecrawl. Best reserved for complex multi-step tasks, not simple extraction.

4. **SaaS image-heavy pages:** Jina outperformed Firecrawl (25KB text vs 21.7KB mostly image URLs). Jina extracts more actual text content from JS-heavy pages.

5. **Cloudflare protection:** Jina > browser-use > Firecrawl for penetrating Cloudflare. Jina got 2.4x more content than Firecrawl on the Discord safety page.

6. **404 handling:** Jina adds explicit "Warning: Target URL returned error 404" in output. Firecrawl puts it in metadata. browser-use reports it naturally. All graceful.

### Updated Tool Selection Heuristic

```
Simple text extraction (blog, article, docs)
  → Jina Reader (FREE, fastest, most reliable)
  → Firecrawl scrape (if Jina unavailable)

Structured data extraction (schema, JSON)
  → Firecrawl extract (schema mode, no Jina equivalent)

Multi-page research
  → Firecrawl agent (async, autonomous)

Cloudflare-protected sites
  → Jina Reader (best penetration, free)
  → browser-use (if Jina fails)

Interactive pages (forms, clicks)
  → Playwright MCP (deterministic)
  → browser-use (complex autonomous flows)

Bot-hostile sites requiring auth
  → Browserbase + Playwright (isolated session)
  → browser-use (autonomous, adapts to challenges)
```

---

## 1. Chrome DevTools MCP

**Version:** @0.20.0 (pinned in .mcp.json)
**Config:** `.mcp.json` entry with `chrome-devtools-mcp@0.20.0`

### Test Scenarios

#### 1a. Navigation + Form Fill
- **Task:** Navigate to news.ycombinator.com, take snapshot, fill search box, submit
- **Result:** SUCCESS — all steps completed
  - `navigate_page` → page loaded, confirmed via page list
  - `take_snapshot` → full a11y tree with UIDs (30 stories, ~700 UIDs, comparable to Playwright)
  - `fill` → search box (uid=1_730) filled with "Claude Code"
  - `press_key` → Enter submitted form
- **Token cost:** High — full a11y snapshot is similar to Playwright (~50-100KB)

#### 1b. Lighthouse Audit
- **Task:** Run Lighthouse audit on news.ycombinator.com
- **Result:** SUCCESS — scores returned in 4.4s
  - Accessibility: 52, Best Practices: 96, SEO: 75
  - 30 passed, 9 failed audits
  - Reports saved to temp dir (JSON + HTML)
- **Note:** Returns A11y/Best Practices/SEO only — performance requires separate `performance_start_trace`

#### 1c. Network Inspection
- **Task:** List network requests after page navigation
- **Result:** SUCCESS — 7 requests captured
  - Each with reqid, method, URL, status code
  - Can drill into individual requests via `get_network_request(reqid)`
  - Filter by resource type supported (document, script, image, xhr, etc.)

### Failure Scenario
- **Scenario:** Chrome DevTools MCP fails to connect (Chrome not running)
- **Expected:** Actionable error message, not silent hang
- **Actual:** NOT TESTED — Chrome was running during evaluation. Would need to close Chrome to test.
- **Mitigation:** Design doc specifies Chrome-not-running as a failure scenario for the browse skill. Test during Phase 1 integration.

### Verdict
- **Include:** YES — strong candidate for Lighthouse audits, network inspection, and Chrome-specific debugging
- **Strengths:** Lighthouse audit is unique capability (no other tool provides this). Network inspection is useful for debugging. a11y tree approach matches Playwright.
- **Weaknesses:** Token cost same as Playwright (not a differentiator). Requires Chrome to be running. 29 tools is a large surface area — only ~8 are practically needed.
- **Notes:** Best used as a complement to Playwright, not a replacement. Key unique value = Lighthouse + network panel. For navigation/form fill, Playwright is equally capable.

---

## 2. Firecrawl MCP

**Version:** @3.11.0 (pinned in .mcp.json)
**Config:** `.mcp.json` entry with FIRECRAWL_API_KEY
**Credits used during eval:** ~50

### Test Scenarios

#### 2a. Scrape — SaaS site (linear.app/features)
- **URL:** https://linear.app/features
- **Format:** markdown, onlyMainContent: true
- **Result:** POOR quality — page is heavily JS-rendered with image carousels
  - Output was ~95% image URLs, minimal text content
  - Did capture title "The system for modern product development" and feature names at bottom
  - Metadata captured correctly (title, description, OG tags)
  - 1 credit, cache hit (fast)
- **Assessment:** Firecrawl struggles with image-heavy SaaS landing pages. Text-light pages produce low-quality markdown.

#### 2b. Scrape — Blog (simonwillison.net)
- **URL:** https://simonwillison.net/2024/Dec/19/one-shot-python-tools/
- **Format:** markdown, onlyMainContent: true
- **Result:** EXCELLENT — full article extracted cleanly
  - Title, headings, code blocks, inline links all preserved
  - Images with alt text captured
  - Series navigation and tags included
  - Metadata rich (OG tags, author, dates)
  - 1 credit, cache hit
- **Assessment:** Firecrawl excels at text-heavy content (blogs, docs, articles).

#### 2c. Scrape — E-commerce
- **URL 1:** https://www.amazon.com/dp/B0D5BKWPH8 (JSON extraction)
  - **Result:** 404 — Amazon blocked/product not found. Empty JSON returned. 5 credits.
  - **Assessment:** Amazon actively blocks Firecrawl's basic proxy. Would need stealth/enhanced proxy.
- **URL 2:** https://store.steampowered.com/app/1086940/Baldurs_Gate_3/ (JSON extraction)
  - **Result:** CRITICAL FAILURE — **Firecrawl hallucinated structured data**
  - URL redirected to age gate (`/agecheck/app/1086940/`)
  - Firecrawl couldn't access actual product page
  - JSON extraction returned fabricated data: `"name": "Hades", "price": "$24.99"` — WRONG game, WRONG price
  - 5 credits consumed
  - **Assessment:** When JSON extraction can't find real data on the page, it HALLUCINATES plausible-looking data instead of returning empty. This is a dangerous failure mode — the caller has no way to know the data is fabricated.

#### 2d. Schema Extraction (firecrawl_extract)
- **URL:** https://openai.com/api/pricing/
- **Schema:** `{models: [{name, input_price_per_million, output_price_per_million}]}`
- **Result:** EXCELLENT — 11 models extracted with prices
  - GPT-5.4, GPT-5 mini, GPT-4.1, GPT-4.1 mini, GPT-4.1 nano, o4-mini, etc.
  - Prices look plausible for current OpenAI pricing
  - 38 credits, 559 tokens used
- **Assessment:** `firecrawl_extract` is the strongest Firecrawl feature. Multi-URL structured extraction with schema enforcement. Higher credit cost (38 vs 1-5 for scrape).

#### 2e. Agent Mode
- **Task:** Find Anthropic Claude API pricing — model names, input/output prices
- **Job ID:** `019ceefd-241d-735f-94ad-253a91cc531f`
- **Result:** EXCELLENT — 26 models extracted with pricing
  - All Claude model families: Opus 4.6/4.5/4.1/4/3, Sonnet 4.6/4.5/4/3.7, Haiku 4.5/3.5/3
  - Batch pricing variants included (50% discount)
  - Fast mode pricing included (6x premium)
  - Long context pricing included (>200k tokens)
  - Model used: spark-1-pro (Firecrawl's internal model)
  - 0 credits used (agent mode pricing may be separate or cached)
- **Assessment:** Agent mode autonomously navigated to anthropic.com, found pricing page, and extracted structured data. Significantly more comprehensive than a single scrape would achieve.

### Failure Scenario
- **Scenario 1:** 404 page (https://example.com/this-page-does-not-exist-404-test)
  - **Result:** GRACEFUL — returned `statusCode: 404` in metadata with `error: "Not Found"`
  - Also returned whatever HTML the server served (example.com default page)
  - Not hallucinated — server genuinely returns that content for any path. 1 credit.
- **Scenario 2:** httpstat.us/404 (dedicated HTTP status testing service)
  - **Result:** ERROR — `ERR_TUNNEL_CONNECTION_FAILED` (Firecrawl proxy error)
  - Internal proxy issue, not related to the 404 test target. Retry might work.
- **Scenario 3:** Steam age-gated page (see 2c above)
  - **Result:** CRITICAL — hallucinated structured data when extraction found no matching content
  - This is the most dangerous failure mode discovered in Phase 0

### Verdict
- **Include:** YES, CONDITIONAL — excellent for text-heavy content and structured extraction, but needs guardrails
- **Critical guardrail:** JSON extraction MUST validate results against source. Never trust structured output from Firecrawl without cross-checking. Consider adding `statusCode` and redirect-URL checks before trusting extraction results.
- **Strengths:** Blog/docs scraping (excellent), schema extraction (excellent), async agent for multi-source research, web search integration
- **Weaknesses:** Image-heavy SaaS pages (poor), e-commerce sites with bot protection (blocked), JSON extraction hallucinates on unreachable content (critical)
- **Credit cost:** 1 per simple scrape, 5 per scrape with JSON/proxy, 38 per extract call. Budget accordingly.
- **Recommendation:** Primary tool for text extraction + structured data. Always check `metadata.statusCode` and `metadata.url` (redirect detection) before trusting results. For bot-protected sites, fall back to Playwright/Browserbase.

---

## 3. browser-use

**Version:** installed in /tmp/phase0-eval venv (imports successfully)

### Test Scenarios

#### 3a. Autonomous Multi-Step Task
- **Task:** Search for a product, compare prices, extract results
- **Status:** BLOCKED — browser-use requires an LLM API key (ANTHROPIC_API_KEY or OPENAI_API_KEY) in the environment. Neither is set in the Claude Code shell environment.
- **Note:** browser-use is an LLM-powered browser automation framework. It wraps Playwright and uses an LLM to decide what to click/type. Without an API key, no test can run.

### Failure Scenario
- **Scenario:** Exceeds 60s on simple navigation task
- **Status:** BLOCKED (same API key dependency)

### Verdict
- **Include:** DEFER — cannot evaluate without LLM API key
- **Architecture note:** browser-use is essentially "LLM + Playwright" bundled together. Since we already have Playwright MCP (baseline) and Claude Code itself IS the LLM, browser-use adds a redundant LLM layer. Our browse skill will achieve the same pattern (Claude deciding actions → Playwright executing them) without the extra dependency and token cost.
- **Recommendation:** Skip browser-use. Build browse skill directly on Playwright MCP + Claude's reasoning. Revisit only if Playwright-based browsing proves unreliable for multi-step tasks.

---

## 4. Browserbase

**Account:** Production project (created 2026-01-13)
**Project ID:** `1d07facb-3bc4-4e87-ae40-a46d5ba9cc47`
**Config:** API key in env/secrets, not in code

### Test Scenarios

#### 4a. Session Creation + Persistence
- **Task:** Create session via REST API, verify status and connectivity
- **Result:** SUCCESS
  - Session creation: 0.24s (fast)
  - Status: RUNNING immediately
  - Connect URL: present (for Playwright/Puppeteer connection)
  - Region: us-west-2
  - Default timeout: 300s
  - Concurrency limit: 25 sessions
  - 105 historical sessions on account
- **Persistence:** Sessions have `createdAt`, `updatedAt`, `expiresAt` fields. Sessions auto-expire after timeout.

#### 4b. Anti-Detection
- **Task:** Create session with proxy flag
- **Result:** Session created successfully with `proxies: True`
  - Proxy object returned (empty in response but session configured server-side)
  - Full anti-detection test (accessing bot-hostile site) requires Playwright connection to session — deferred to Phase 1 integration
- **Note:** Browserbase provides fingerprint randomization, residential proxies, and stealth mode. Cannot fully validate without connecting Playwright to the session.

### Failure Scenario
- **Scenario:** Session creation with invalid API key
- **Expected:** Clear error, not silent null session
- **Actual:** HTTP 401 with `{"statusCode":401,"error":"Unauthorized","message":"Unauthorized"}` — PASS
- Clear, actionable error. No silent failure.

### Verdict
- **Include:** YES — cloud browser infrastructure for anti-detection and remote execution
- **Pricing:** Free tier available. Pay-as-you-go for production use. Viable for auth sessions on bot-hostile sites.
- **Strengths:** Fast session creation (0.24s), 25 concurrent sessions, clear error handling, Playwright-compatible connect URL
- **Weaknesses:** Adds latency (remote browser vs local). Requires API key management. Full anti-detection testing deferred.
- **Use case:** Reserved for sites that block local Playwright (bot detection). Not for general browsing (local Playwright is faster and free).

---

## 5. Stagehand v3

**Version:** Not installed (requires npm + Browserbase session + LLM API key)

### Test Scenarios

#### 5a. Navigation Flow (baseline)
- **Status:** BLOCKED — Stagehand requires both a Browserbase session and an LLM API key (ANTHROPIC_API_KEY or OPENAI_API_KEY). Neither API key is available in the shell environment.

#### 5b. Caching Test (3 runs of same flow)
- **Status:** BLOCKED (same dependency)

### Verdict
- **Include:** DEFER — same API key blocker as browser-use
- **Architecture note:** Stagehand is "AI-powered Playwright" built on Browserbase. Like browser-use, it adds an LLM layer on top of Playwright. Our design already has Claude Code as the LLM controlling Playwright directly — Stagehand would be redundant.
- **Caching claim:** Stagehand v3 claims 30%+ faster on repeated flows via selector caching. This is a meaningful optimization IF we're running the same flows repeatedly (e.g., monitoring/watch skill). Worth revisiting in Phase 4 (watch skill) if repeated navigation performance becomes a bottleneck.
- **Recommendation:** Skip for now. Revisit during Phase 4 if Playwright-based repeated navigation is too slow.

---

## 6. Cookie Extraction Methods

### 6a. yt-dlp Method
- **Command:** `yt-dlp --cookies-from-browser safari --cookies ~/.ai-cos/cookies/test.txt`
- **Safari:** YES — 781 cookies extracted
- **Chrome:** YES — 98 cookies extracted
- **Arc:** NO — "unsupported browser". Only supports: brave, chrome, chromium, edge, firefox, opera, safari, vivaldi, whale
- **Domain filtering:** NO native support — would need post-processing (grep the Netscape file)
- **Netscape format:** YES — standard Netscape HTTP Cookie File format
- **Cron-safe:** YES — CLI tool, no GUI needed
- **Limitations:** No Arc support. No domain filtering. Requires providing a dummy URL (errors without one but still extracts). Not designed for this use case — it's a video downloader side-feature.

### 6b. browser_cookie3 (Python)
- **Install:** `pip install browser_cookie3` (installed in /tmp/phase0-eval venv)
- **Safari keychain access:** YES — extracted 781 cookies, handles Safari binary cookie format
- **Chrome Safe Storage:** YES — extracted 98 cookies, handles Chrome encryption
- **Arc:** NO — Arc's cookie storage path is non-standard (not in `User Data/Default/Cookies`). Arc's `User Data/` directory only contains `NativeMessagingHosts/` — cookies may be stored elsewhere.
- **Domain filtering:** YES — native `domain_name=` parameter. Tested: `.google.com` returned 77 cookies (correct)
- **Output format:** Python `http.cookiejar.CookieJar` object — needs conversion to Netscape format for Playwright
- **Cron-safe:** YES — Python library, no GUI
- **Encryption handled:** YES — Safari and Chrome both work transparently

### 6c. Direct SQLite
- **Status:** SKIPPED — browser_cookie3 already handles SQLite + encryption internally. Direct SQLite adds complexity with no benefit. Would only be worth it if browser_cookie3 fails on a specific browser.

### 6d. Compiled Binary
- **Status:** SKIPPED — gstack's approach requires building a macOS app with keychain entitlements. Overkill for our use case since browser_cookie3 handles Safari and Chrome without it. Re-evaluate only if we need browsers browser_cookie3 can't handle.

### Comparison Matrix

| Method | Safari | Chrome | Arc | Domain Filter | Netscape Output | Cron-safe | Encryption Handled |
|---|---|---|---|---|---|---|---|
| yt-dlp | YES (781) | YES (98) | NO | NO (post-process) | YES (native) | YES | YES |
| browser_cookie3 | YES (781) | YES (98) | NO | YES (native) | NO (needs conversion) | YES | YES |
| Direct SQLite | SKIPPED | SKIPPED | SKIPPED | SKIPPED | SKIPPED | SKIPPED | SKIPPED |
| Compiled binary | SKIPPED | SKIPPED | SKIPPED | SKIPPED | SKIPPED | SKIPPED | SKIPPED |

### Winner
- **Method:** browser_cookie3 (Python library)
- **Rationale:** Domain filtering is built-in (critical for security — only export what's needed). yt-dlp requires post-processing grep. browser_cookie3 output needs Netscape format conversion, but that's a simple Python function (~10 lines). Both handle Safari + Chrome encryption. Neither handles Arc, but Arc support is low priority since it's not the primary browser for authenticated sessions.
- **Cookie sync script approach:** Python script using browser_cookie3 for extraction + Netscape format conversion, wrapped in a bash script for cron scheduling. Staged to `~/.ai-cos/cookies/` (chmod 600), pushed via rsync over Tailscale.

### Failure Scenario
- **Scenario:** Cookie extraction fails on locked Safari keychain (simulated with nonexistent path)
- **Expected:** Error message, not corrupted output
- **Actual:** `FileNotFoundError: [Errno 2] No such file or directory` — PASS. Clear error, not silent corruption.

---

## 7. Playwright MCP (Baseline)

**Version:** via Claude Code plugin (playwright plugin, built-in)
**Config:** Plugin-based — no ~/.mcp.json entry needed

### Test Scenarios

#### 7a. Navigation (Hacker News)
- **Task:** Navigate to news.ycombinator.com
- **Result:** SUCCESS — full a11y tree returned (58.5KB YAML snapshot)
- **Page title, links, story titles all captured**
- **Token impact:** Large — full a11y tree is verbose

#### 7b. Navigation + Form Fill + Submit (DuckDuckGo search)
- **Task:** Navigate to duckduckgo.com → fill search box → submit → verify results
- **Result:** SUCCESS — all 3 steps completed
- **Search input identified by ref (combobox), filled, submitted**
- **Results page: 10 search results with titles, URLs, descriptions all captured in a11y tree**
- **Console: 1 error (favicon 404, harmless), 7 warnings**

### Observations
- **Strengths:** Reliable, deterministic, full DOM access via a11y tree, form fill works cleanly
- **Weaknesses:** Very token-heavy — full page snapshots are 50-100KB+ of YAML. For repeated operations, this is expensive.
- **Key pattern:** navigate → snapshot → identify ref → interact → snapshot again
- **Comparison baseline:** This is the benchmark other tools are measured against

### Verdict
- **Include:** YES (already included as baseline tool)
- **Token optimization note:** For repeated operations, consider Playwright CLI (not MCP) which saves 75% tokens per design doc. For interactive/one-off operations, MCP is fine.
- **Notes:** Plugin-based, no installation needed. Works reliably for navigation, form fill, search. a11y tree approach is better than screenshots for structured interaction.

---

## Phase 0 Failure Scenarios Summary

| # | Scenario | Expected | Actual | Pass? |
|---|---|---|---|---|
| 1 | Chrome DevTools MCP fails to connect | Actionable error | NOT TESTED (Chrome was running) | DEFER to Phase 1 |
| 2 | Firecrawl empty on content-rich page | Graceful fallback | 404: returns statusCode+error in metadata. Age-gated: **HALLUCINATES structured data** | **FAIL** (hallucination) |
| 3 | browser-use exceeds 60s timeout | Timeout fires | BLOCKED (no API key) | **DEFER** |
| 4 | Cookie extraction on locked keychain | Error, not corrupt | FileNotFoundError — clear, not corrupt | **PASS** |
| 5 | Browserbase session creation fails | Clear error | HTTP 401 `{"error":"Unauthorized"}` — clear, actionable | **PASS** |

### Critical Finding: Firecrawl Hallucination on Blocked Content

When Firecrawl's JSON extraction (`formats: ["json"]` with `jsonOptions`) encounters a page it can't access (age gate, redirect, bot block), it **fabricates plausible-looking structured data** instead of returning empty fields or an error. This was observed on the Steam BG3 page:
- Requested: Baldur's Gate 3 product data
- URL redirected to: `/agecheck/app/1086940/` (age gate)
- Returned: `{"name": "Hades", "price": "$24.99"}` — completely fabricated

**Mitigation for skills:** Always check `metadata.url` against the requested URL (detect redirects). Always check `metadata.statusCode`. If either is suspicious, discard extraction results and fall back to Playwright. Consider adding a "confidence" field or source-verification step in the scrape skill.
