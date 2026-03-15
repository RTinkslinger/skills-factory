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
| Chrome DevTools MCP | | | | | | | |
| Firecrawl MCP | | | | | | | |
| browser-use | | | | | | | |
| Browserbase | | | | | | | |
| Stagehand v3 | | | | | | | |
| Cookie extraction | | | | | | | |
| Playwright MCP (baseline) | | | | | | | |

---

## 1. Chrome DevTools MCP

**Version:** TBD (pin after install)
**Config:** `~/.mcp.json` entry: `{"chrome-devtools": {"command": "npx", "args": ["-y", "chrome-devtools-mcp@<version>"]}}`

### Test Scenarios

#### 1a. Navigation + Form Fill
- **Task:** Open Chrome, navigate to Hacker News, fill search, submit
- **Expected:** Page loads, search field found, form submitted
- **Results:**

#### 1b. Lighthouse Audit
- **Task:** Navigate to a public URL, run Lighthouse audit
- **Expected:** LCP, INP, CLS, FCP, TTFB scores returned
- **Results:**

#### 1c. Network Inspection
- **Task:** Navigate to a page, inspect network requests
- **Expected:** Request list with URLs, status codes, sizes
- **Results:**

### Failure Scenario
- **Scenario:** Chrome DevTools MCP fails to connect (Chrome not running)
- **Expected:** Actionable error message, not silent hang
- **Actual:**

### Verdict
- **Include / Exclude / Conditional:**
- **Notes:**

---

## 2. Firecrawl MCP

**Version:** TBD
**Config:** `~/.mcp.json` entry with FIRECRAWL_API_KEY

### Test Scenarios

#### 2a. Scrape — SaaS site
- **URL:**
- **Results:**

#### 2b. Scrape — Blog
- **URL:**
- **Results:**

#### 2c. Scrape — E-commerce
- **URL:**
- **Results:**

#### 2d. Schema Extraction
- **Schema:** `{name, price, features}`
- **URL:**
- **Results:**

#### 2e. Agent Mode
- **Task:** Multi-page extraction
- **Results:**

### Failure Scenario
- **Scenario:** Empty page extraction (point at a 404 page)
- **Expected:** Graceful empty result, not error or hallucinated content
- **Actual:**

### Verdict
- **Include / Exclude / Conditional:**
- **Notes:**

---

## 3. browser-use

**Version:** TBD (pip install)

### Test Scenarios

#### 3a. Autonomous Multi-Step Task
- **Task:** Search for a product, compare prices, extract results
- **Completion rate:**
- **Token cost:**
- **Latency:**
- **Quality:**

### Failure Scenario
- **Scenario:** Exceeds 60s on simple navigation task
- **Expected:** Timeout handling, not infinite loop
- **Actual:**

### Verdict
- **Include / Exclude / Conditional:**
- **Notes:**

---

## 4. Browserbase

**Account:** TBD
**API Key:** (env var, not stored here)

### Test Scenarios

#### 4a. Session Creation + Persistence
- **Task:** Create session, navigate, close, re-open — verify state persists
- **Results:**

#### 4b. Anti-Detection
- **Task:** Access a bot-hostile site
- **Detection evaded?**
- **Session stable?**
- **Pricing viable?**

### Failure Scenario
- **Scenario:** Session creation fails (invalid API key / exhausted quota)
- **Expected:** Clear error, not silent null session
- **Actual:**

### Verdict
- **Include / Exclude / Conditional:**
- **Pricing assessment:**
- **Notes:**

---

## 5. Stagehand v3

**Version:** (via browserbase/agent-browse plugin)

### Test Scenarios

#### 5a. Navigation Flow (baseline)
- **Task:**
- **Latency (run 1):**
- **Token count (run 1):**

#### 5b. Caching Test (3 runs of same flow)
- **Run 1 latency:**
- **Run 2 latency:**
- **Run 3 latency:**
- **30% faster on 2nd+?**
- **Cached selector in debug log?**

### Verdict
- **Include / Exclude / Conditional:**
- **Notes:**

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
| 1 | Chrome DevTools MCP fails to connect | Actionable error | | |
| 2 | Firecrawl empty on content-rich page | Graceful fallback | | |
| 3 | browser-use exceeds 60s timeout | Timeout fires | | |
| 4 | Cookie extraction on locked keychain | Error, not corrupt | | |
| 5 | Browserbase session creation fails | Clear error | | |
