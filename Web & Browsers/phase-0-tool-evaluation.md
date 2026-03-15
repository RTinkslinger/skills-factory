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
- **Safari:** works? / fails?
- **Chrome:** works? / fails?
- **Arc:** works? / fails?
- **Domain filtering:** possible?
- **Netscape format:** yes/no?
- **Limitations:**

### 6b. browser_cookie3 (Python)
- **Install:** `pip install browser_cookie3`
- **Safari keychain access:**
- **Chrome Safe Storage:**
- **Domain filtering:**
- **Output format:**

### 6c. Direct SQLite
- **Chrome cookie DB location:**
- **Encryption handling:**
- **Domain filtering:**
- **Reliability:**

### 6d. Compiled Binary (if available)
- **Tool:**
- **Results:**

### Comparison Matrix

| Method | Safari | Chrome | Arc | Domain Filter | Netscape Output | Cron-safe | Encryption Handled |
|---|---|---|---|---|---|---|---|
| yt-dlp | | | | | | | |
| browser_cookie3 | | | | | | | |
| Direct SQLite | | | | | | | |
| Compiled binary | | | | | | | |

### Winner
- **Method:**
- **Rationale:**

### Failure Scenario
- **Scenario:** Cookie extraction fails on locked Safari keychain
- **Expected:** Error message, not corrupted output
- **Actual:**

---

## 7. Playwright MCP (Baseline)

**Version:** (via plugin)

### Test Scenarios

#### 7a. Same Navigation Flow as Stagehand (for comparison)
- **Latency:**
- **Token count:**
- **Comparison to Stagehand:**

### Verdict
- **Baseline documented:**
- **Notes:**

---

## Phase 0 Failure Scenarios Summary

| # | Scenario | Expected | Actual | Pass? |
|---|---|---|---|---|
| 1 | Chrome DevTools MCP fails to connect | Actionable error | | |
| 2 | Firecrawl empty on content-rich page | Graceful fallback | | |
| 3 | browser-use exceeds 60s timeout | Timeout fires | | |
| 4 | Cookie extraction on locked keychain | Error, not corrupt | | |
| 5 | Browserbase session creation fails | Clear error | | |
