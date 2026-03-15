# Web & Frontend Skills Portfolio — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete web skills portfolio (8 specialists + 1 router + 3 frontend updates) that gives CC, CAI, and Agent SDK agents human-level web capabilities — browsing, extraction, search, QA, monitoring, and authenticated access.

**Architecture:** Three-tier model — Layer 1 (shared MCP tools) feeds Layer 2 (specialist reference docs in `~/.claude/skills/web-router/references/`) orchestrated by Layer 3 (web-router SKILL.md). Each specialist encodes a 6-dimension tool selection framework. Skills are developed in Skills Factory using SKILL-CRAFT methodology, then deployed to `~/.claude/skills/`.

**Tech Stack:** Markdown (SKILL-CRAFT skills), Bash (cookie sync, deploy scripts), MCP servers (Playwright, Chrome DevTools, Firecrawl, Stagehand), YAML (observability logs), SQLite (droplet state)

**Spec:** `docs/superpowers/specs/2026-03-14-web-frontend-skills-portfolio-design.md`

**Dependency graph:**
```
Phase 0 (Tool Eval) ──→ Phase 1 (Foundation) ──→ Phase 2 (Extraction) ──→ Phase 4 (Watch)
                                                 ├──→ Phase 3 (Quality) ──┘
Phase 5 (Frontend Refresh) — independent, parallel to P1-P4
```

---

## File Structure

### Source (Skills Factory)

```
Web & Browsers/
  phase-0-tool-evaluation.md          ← Phase 0 deliverable: tool eval report
  layer-1-toolset.md                  ← Phase 0 deliverable: Layer 1 decision record
  web-router/
    skill-development-log.md          ← SKILL-CRAFT dev log
    SKILL.md                          ← web-router skill (deployed to ~/.claude/skills/web-router/)
  browse/
    skill-development-log.md
    browse.md                         ← reference doc (deployed to references/)
  scrape/
    skill-development-log.md
    scrape.md
  search/
    skill-development-log.md
    search.md                         ← v3, evolves from existing search-router
  qa/
    skill-development-log.md
    qa.md
  auth/
    skill-development-log.md
    auth.md
    auth-service-registry.md          ← living doc: per-service auth strategies
    scripts/
      cookie-sync.sh                  ← Mac → droplet cookie sync
  perf-audit/
    skill-development-log.md
    perf-audit.md
  watch/
    skill-development-log.md
    watch.md
  tool-selection.md                   ← shared 6-dimension framework reference
  baselines/
    phase-0-baseline.md               ← tool eval results as regression baseline
    phase-1-baseline.md
    phase-2-baseline.md
    phase-3-baseline.md
    phase-4-baseline.md
    phase-5-baseline.md
```

### Deployment Target (CC)

```
~/.claude/skills/web-router/
  SKILL.md                            ← only file with trigger descriptions
  references/
    browse.md
    scrape.md
    search.md
    qa.md
    auth.md
    perf-audit.md
    watch.md
    tool-selection.md                 ← 6-dimension framework
```

### Deployment Target (Droplet — via deploy.sh)

```
/opt/ai-cos-mcp/skills/web-router/references/
  (same reference docs, rsync'd from Skills Factory)
```

### Frontend Skills (updates to existing)

```
~/.claude/skills/design-system-enforcer/SKILL.md  ← update in-place
~/.claude/skills/a11y-audit/SKILL.md               ← update in-place
~/.claude/CLAUDE.md                                 ← append CSS 2026 + anti-patterns sections
```

---

## Chunk 1: Phase 0 — Tool Evaluation

**Objective:** Hands-on evaluation of every Layer 1 tool. The 6-dimension framework can only be built on verified capabilities, not documentation claims. Produces two decision records that gate all subsequent phases.

### Task 1: Set up Phase 0 evaluation workspace

**Files:**
- Create: `Web & Browsers/phase-0-tool-evaluation.md`

- [ ] **Step 1: Create evaluation report template**

Create `Web & Browsers/phase-0-tool-evaluation.md` with sections for each tool:

```markdown
# Phase 0: Tool Evaluation Report

**Date:** YYYY-MM-DD
**Status:** In Progress

## Evaluation Criteria (per tool)

| Criterion | Method |
|---|---|
| Reliability | 3 runs of same scenario, count failures |
| Latency | Measure wall-clock time for standard task |
| Token cost | Count tokens consumed (from MCP response metadata) |
| Output quality | Manually assess: complete? structured? clean? |
| Failure mode | What happens when it breaks? Timeout? Error? Silent fail? |

## Tools Evaluated

### Chrome DevTools MCP
- **Version:** (pin this)
- **Config:** (exact ~/.mcp.json entry)
- **Test scenario:** Navigate to HN, fill search, run Lighthouse, inspect network
- **Results:** ...
- **Failure scenario:** Chrome process not running → expected: actionable error
- **Verdict:** Include / Exclude / Conditional

### Firecrawl MCP
...

### browser-use
...

### Browserbase
...

### Stagehand v3
- **Caching test:** Repeat nav flow 3x. 2nd+ run must be >=30% faster with cached selector in debug log.
...

### Cookie extraction
- **Candidates:** compiled binary, browser_cookie3, direct SQLite, yt-dlp
- **Test:** Extract cookies for 3 domains from Safari, Chrome, Arc
- **Pass:** Netscape format, Playwright accepts, authenticated page loads
...

### Playwright MCP (baseline)
...
```

- [ ] **Step 2: Commit workspace setup**

```bash
git add "Web & Browsers/phase-0-tool-evaluation.md"
git commit -m "phase-0: evaluation report template"
```

### Task 2: Evaluate Chrome DevTools MCP

**Files:**
- Modify: `Web & Browsers/phase-0-tool-evaluation.md`

- [ ] **Step 1: Install Chrome DevTools MCP with pinned version**

Check the latest stable version, then add to `~/.mcp.json`:
```json
{"chrome-devtools": {"command": "npx", "args": ["-y", "chrome-devtools-mcp@<pinned-version>"]}}
```

Run: `npx chrome-devtools-mcp@<version> --help` to verify installation.

- [ ] **Step 2: Test Chrome DevTools MCP — navigation + form fill**

Open Chrome manually. In CC:
- Use `browser_navigate` to go to a test site
- Use `browser_snapshot` to capture accessibility tree
- Use `browser_fill_form` to fill a search field
- Use `browser_click` to submit

Record: latency, token count, success/failure.

- [ ] **Step 3: Test Chrome DevTools MCP — Lighthouse audit**

In CC:
- Navigate to a public URL
- Run Lighthouse via Chrome DevTools MCP
- Capture: LCP, INP, CLS, FCP, TTFB scores

Record results.

- [ ] **Step 4: Test Chrome DevTools MCP — failure scenario**

Kill Chrome process, then attempt to use Chrome DevTools MCP.
Expected: actionable error message, not silent hang.
Record actual behavior.

- [ ] **Step 5: Document results in evaluation report**

Fill in the Chrome DevTools MCP section with all findings. Pin the version tested.

- [ ] **Step 6: Commit**

```bash
git add "Web & Browsers/phase-0-tool-evaluation.md"
git commit -m "phase-0: Chrome DevTools MCP evaluation complete"
```

### Task 3: Evaluate Firecrawl MCP

**Files:**
- Modify: `Web & Browsers/phase-0-tool-evaluation.md`

- [ ] **Step 1: Install Firecrawl MCP with pinned version**

Add to `~/.mcp.json` with `FIRECRAWL_API_KEY` from env:
```json
{"firecrawl": {"command": "npx", "args": ["-y", "firecrawl-mcp@<pinned-version>"], "env": {"FIRECRAWL_API_KEY": "..."}}}
```

- [ ] **Step 2: Test scrape — 3 site types (SaaS, blog, e-commerce)**

For each site type:
- Call Firecrawl scrape tool with URL
- Assess: clean markdown? all content captured? no junk?
Record latency, token count, quality per site.

- [ ] **Step 3: Test schema extraction (Firecrawl extract)**

Define a schema (e.g., `{name, price, features}`) and extract from a pricing page.
Assess: all fields populated? correct types? missing data flagged?

- [ ] **Step 4: Test Firecrawl agent mode**

Run agent mode on a multi-page extraction task.
Assess: multi-page navigation? structured output? completion rate?

- [ ] **Step 5: Failure scenario — empty page extraction**

Point Firecrawl at a page with no meaningful content (e.g., a 404 page).
Expected: graceful empty result, not error or hallucinated content.

- [ ] **Step 6: Document results and commit**

```bash
git add "Web & Browsers/phase-0-tool-evaluation.md"
git commit -m "phase-0: Firecrawl MCP evaluation complete"
```

### Task 4: Evaluate browser-use

**Files:**
- Modify: `Web & Browsers/phase-0-tool-evaluation.md`

- [ ] **Step 1: Install browser-use**

```bash
pip install browser-use
```

Set up as MCP server if applicable, or test via direct Python integration.

- [ ] **Step 2: Test autonomous multi-step task**

Task: "Search for a product on Amazon, compare prices with another retailer, extract results."
Record: completion rate, token cost, latency, quality of output.

- [ ] **Step 3: Failure scenario — 60s timeout on simple task**

If browser-use exceeds 60s on a simple navigation task, verify timeout handling.

- [ ] **Step 4: Document results and commit**

```bash
git add "Web & Browsers/phase-0-tool-evaluation.md"
git commit -m "phase-0: browser-use evaluation complete"
```

### Task 5: Evaluate Browserbase

**Files:**
- Modify: `Web & Browsers/phase-0-tool-evaluation.md`

- [ ] **Step 1: Create Browserbase account and configure API key**

Sign up at browserbase.com. Add API key to env vars.

- [ ] **Step 2: Test isolated session creation and persistence**

Create a session, navigate to a site, close session, re-open — verify state persists.

- [ ] **Step 3: Test anti-detection on a bot-hostile site**

Use Browserbase to access a site known for bot detection.
Assess: detection evaded? session stable? pricing viable?

- [ ] **Step 4: Failure scenario — session creation fails**

Test with invalid API key / exhausted quota.
Expected: clear error, not silent null session.

- [ ] **Step 5: Document results and commit**

```bash
git add "Web & Browsers/phase-0-tool-evaluation.md"
git commit -m "phase-0: Browserbase evaluation complete"
```

### Task 6: Evaluate Stagehand v3 + Playwright baseline

**Files:**
- Modify: `Web & Browsers/phase-0-tool-evaluation.md`

- [ ] **Step 1: Verify Stagehand v3 via existing plugin**

Run a navigation flow using Stagehand act/extract/observe.
Record baseline latency and token count.

- [ ] **Step 2: Caching test — repeat 3 times**

Repeat the same navigation flow 3 times.
Pass criteria: 2nd+ run at least 30% faster, debug log confirms cached selector reuse.

- [ ] **Step 3: Playwright baseline — same flow**

Run identical flow via Playwright MCP.
Record latency and token count for comparison.

- [ ] **Step 4: Document results and commit**

```bash
git add "Web & Browsers/phase-0-tool-evaluation.md"
git commit -m "phase-0: Stagehand + Playwright evaluation complete"
```

### Task 7: Evaluate cookie extraction methods

**Files:**
- Modify: `Web & Browsers/phase-0-tool-evaluation.md`

- [ ] **Step 1: Test yt-dlp method (current hack)**

```bash
yt-dlp --cookies-from-browser safari --cookies /tmp/test-cookies.txt
```

Assess: which domains work? Netscape format? limitations?

- [ ] **Step 2: Test browser_cookie3 Python library**

```python
import browser_cookie3
cj = browser_cookie3.safari(domain_name=".example.com")
```

Assess: Safari keychain access? Chrome Safe Storage? domain filtering?

- [ ] **Step 3: Test direct SQLite reading of Chrome cookie DB**

Locate Chrome cookie DB, query directly.
Assess: encryption handling? Safe Storage decryption? reliability?

- [ ] **Step 4: Test compiled binary approach (if available)**

Research gstack's approach or similar. Test if applicable.

- [ ] **Step 5: Assess each method against production criteria**

| Method | Safari | Chrome | Arc | Domain filter | Netscape output | Cron-safe | Encryption handled |
|---|---|---|---|---|---|---|---|
| yt-dlp | ? | ? | ? | ? | ? | ? | ? |
| browser_cookie3 | ? | ? | ? | ? | ? | ? | ? |
| Direct SQLite | ? | ? | ? | ? | ? | ? | ? |
| Compiled binary | ? | ? | ? | ? | ? | ? | ? |

Winner becomes the auth specialist's cookie sync foundation.

- [ ] **Step 6: Document results and commit**

```bash
git add "Web & Browsers/phase-0-tool-evaluation.md"
git commit -m "phase-0: cookie extraction evaluation complete"
```

### Task 8: Write Layer 1 toolset decision record

**Files:**
- Create: `Web & Browsers/layer-1-toolset.md`

This is the transition gate from Phase 0 to Phase 1.

- [ ] **Step 1: Create decision record**

```markdown
# Layer 1 Toolset — Decision Record

**Date:** YYYY-MM-DD
**Input:** Phase 0 evaluation report

## Included in Layer 1

| Tool | Version | Role | Key Finding |
|---|---|---|---|
| Playwright MCP | x.x.x | Deterministic automation, baseline | ... |
| Chrome DevTools MCP | x.x.x | Rich inspection, Lighthouse, debugging | ... |
| Firecrawl MCP | x.x.x | Extraction, crawl, search | ... |
| ... | ... | ... | ... |

## Excluded from Layer 1

| Tool | Reason |
|---|---|
| ... | ... |

## Conditional Inclusion

| Tool | Condition | When to Re-evaluate |
|---|---|---|
| ... | ... | ... |

## Cookie Extraction Winner

**Method:** [winner]
**Rationale:** ...

## Impact on 6-Dimension Framework

Any surprises from evaluation that change how dimensions are weighted or tools are recommended.
```

- [ ] **Step 2: Commit and tag**

```bash
git add "Web & Browsers/layer-1-toolset.md"
git commit -m "phase-0: Layer 1 toolset decided — gate passed"
git tag phase-0-eval
```

### Task 9: Phase 0 failure scenarios verification

**Files:**
- Modify: `Web & Browsers/phase-0-tool-evaluation.md`

- [ ] **Step 1: Verify all 5 Phase 0 failure scenarios from design doc**

Run each scenario documented in Section 9:
1. Chrome DevTools MCP fails to connect to Chrome process
2. Firecrawl returns empty result on content-rich page
3. browser-use exceeds 60s on simple task
4. Cookie extraction fails on locked Safari keychain
5. Browserbase session creation fails (invalid key)

Document actual behavior vs expected in the evaluation report.

- [ ] **Step 2: Create Phase 0 baseline**

Create `Web & Browsers/baselines/phase-0-baseline.md` documenting tool capabilities verified.

- [ ] **Step 3: Final commit**

```bash
git add "Web & Browsers/phase-0-tool-evaluation.md" "Web & Browsers/baselines/phase-0-baseline.md"
git commit -m "phase-0: all evaluations + failure scenarios complete"
```

---

## Chunk 2: Phase 1 — Foundation (auth + browse + web-router)

**Objective:** Build the three foundational skills: auth (session management), browse (navigation), and web-router (orchestration). These are the core that all other phases build on.

**Prerequisites:** Phase 0 complete (layer-1-toolset.md exists). Droplet RAM upgrade communicated via cross-sync.

### Task 10: Build shared tool-selection reference doc

**Files:**
- Create: `Web & Browsers/tool-selection.md`

- [ ] **Step 1: Write 6-dimension framework as reference doc**

Extract the 6-dimension framework from the design doc (Section 4) and write it as a standalone reference doc. This file is loaded by the router alongside specialist docs.

Include:
- All 6 dimensions with decision tables
- Dimension conflict resolution priority order
- Combination principle
- "Protect My Account" principle
- Observability log schema (including failure block)
- Degradation note

Use SKILL-CRAFT voice: expert practitioner tone, not documentation.

- [ ] **Step 2: Commit**

```bash
git add "Web & Browsers/tool-selection.md"
git commit -m "phase-1: 6-dimension tool selection reference doc"
```

### Task 11: Build auth specialist (SKILL-CRAFT)

**Files:**
- Create: `Web & Browsers/auth/skill-development-log.md`
- Create: `Web & Browsers/auth/auth.md`
- Create: `Web & Browsers/auth/auth-service-registry.md`
- Create: `Web & Browsers/auth/scripts/cookie-sync.sh`

- [ ] **Step 1: Create development log**

Initialize `Web & Browsers/auth/skill-development-log.md` per SKILL-CRAFT methodology.

- [ ] **Step 2: SKILL-CRAFT Understanding phase**

Define auth specialist's territory:
- Problem: AI agents need authenticated web access across environments
- Trigger: "log in to", "set up auth for", or invoked by other specialists
- Success: correct auth layer selected, session established, real accounts protected
- NOT: browsing itself, data extraction, credential storage

Document in dev log.

- [ ] **Step 3: SKILL-CRAFT Exploring phase**

Test auth tasks without the skill. Note where Claude:
- Tries to use real browser sessions unsafely
- Doesn't know about cookie sync infrastructure
- Mishandles session isolation
- Picks wrong auth layer for a service

Document failure modes in dev log.

- [ ] **Step 4: SKILL-CRAFT Research + Synthesis**

Study: gstack's cookie approach, Browserbase session model, OAuth refresh patterns.
Extract principles, document in dev log.

- [ ] **Step 5: Draft auth.md reference doc**

Write the auth specialist reference doc with SKILL-CRAFT voice:
- Layered auth model (6 layers with escalation)
- Per-service strategy selection logic
- Cookie sync infrastructure spec
- Safety principles (protect real sessions)
- Environment paths (CC/CAI/Agent SDK)
- Staleness detection (>30d cookies, >90d API keys)

Include YAML frontmatter: `version: 1.0.0`

- [ ] **Step 6: Create auth-service-registry.md**

```markdown
# Auth Service Registry

| Service | Best Layer | Notes | Last Verified |
|---|---|---|---|
| GitHub | API keys/tokens | Personal access tokens | YYYY-MM-DD |
| Google (Gmail, Cal) | OAuth + MCP | Already connected via MCPs | YYYY-MM-DD |
| Notion | API keys/tokens | Integration token | YYYY-MM-DD |
| YouTube | Cookie sync | Safari → droplet, 1-2 week expiry | YYYY-MM-DD |
```

- [ ] **Step 7: Write cookie-sync.sh**

Based on Phase 0 cookie extraction winner. Script must:
- Accept domain list as argument
- Extract cookies using winning method
- Filter to specified domains
- Stage to `~/.ai-cos/cookies/` (chmod 600)
- Push to droplet via rsync over Tailscale
- Log success/failure

```bash
#!/bin/bash
# Cookie Sync — Mac → Droplet
# Usage: cookie-sync.sh domain1.com domain2.com
# ...
```

Make executable: `chmod +x Web\ \&\ Browsers/auth/scripts/cookie-sync.sh`

- [ ] **Step 8: SKILL-CRAFT Self-critique + iterate**

Review auth.md against quality criteria:
- Does it transfer expertise or just give instructions?
- Does it sound like an auth engineer, not a README?
- Could 30% be cut?
- Would a security practitioner recognize themselves in it?

Revise as needed. Update dev log.

- [ ] **Step 9: Commit**

```bash
git add "Web & Browsers/auth/"
git commit -m "phase-1: auth specialist — SKILL-CRAFT complete"
```

### Task 12: Build browse specialist (SKILL-CRAFT)

**Files:**
- Create: `Web & Browsers/browse/skill-development-log.md`
- Create: `Web & Browsers/browse/browse.md`

- [ ] **Step 1: Create development log**

- [ ] **Step 2: SKILL-CRAFT Understanding + Exploring**

Define territory: navigation, interaction, form filling, dynamic content handling.
Test browsing tasks without skill, document failure modes.

- [ ] **Step 3: SKILL-CRAFT Research + Synthesis**

Study: Playwright patterns, Stagehand act/extract/observe, Chrome DevTools MCP capabilities (from Phase 0 results).

- [ ] **Step 4: Draft browse.md reference doc**

Write with SKILL-CRAFT voice:
- 6-dimension tool selection applied to browsing
- Environment paths (CC/CAI/Agent SDK)
- Key patterns: navigate-and-verify, fill-and-submit, multi-tab, authenticated browse
- Dynamic content handling (SPAs, lazy loading, infinite scroll)
- Verification patterns (screenshot, DOM check, console errors)
- Human escalation triggers (CAPTCHA, 2FA, sensitive confirmations)

Include YAML frontmatter: `version: 1.0.0`

- [ ] **Step 5: SKILL-CRAFT Self-critique + iterate**

Review against quality criteria. Revise. Update dev log.

- [ ] **Step 6: Commit**

```bash
git add "Web & Browsers/browse/"
git commit -m "phase-1: browse specialist — SKILL-CRAFT complete"
```

### Task 13: Build web-router skill (SKILL-CRAFT)

**Files:**
- Create: `Web & Browsers/web-router/skill-development-log.md`
- Create: `Web & Browsers/web-router/SKILL.md`

- [ ] **Step 1: Create development log**

- [ ] **Step 2: SKILL-CRAFT Understanding + Exploring**

Define territory: task classification, environment detection, specialist invocation, composite task routing.
Test routing tasks without skill, document where Claude picks wrong tools.

- [ ] **Step 3: Draft SKILL.md**

Write the web-router skill with SKILL-CRAFT voice:

```markdown
---
name: web-router
description: [comprehensive trigger description covering all web tasks]
version: 1.0.0
---

# Web Router — Master Orchestrator

[Task classification matrix]
[Composite task handling — max 3 reference docs per task]
[Environment detection (CC/CAI/Agent SDK)]
[Specialist invocation patterns]
[Routing decision logging]
[Scaling ceiling — 10 specialists max]
```

- [ ] **Step 4: SKILL-CRAFT Self-critique + iterate**

- [ ] **Step 5: Commit**

```bash
git add "Web & Browsers/web-router/"
git commit -m "phase-1: web-router skill — SKILL-CRAFT complete"
```

### Task 14: Deploy Phase 1 skills to CC

**Files:**
- Deploy to: `~/.claude/skills/web-router/SKILL.md`
- Deploy to: `~/.claude/skills/web-router/references/auth.md`
- Deploy to: `~/.claude/skills/web-router/references/browse.md`
- Deploy to: `~/.claude/skills/web-router/references/tool-selection.md`

- [ ] **Step 1: Create deployment directory**

```bash
mkdir -p ~/.claude/skills/web-router/references/
```

- [ ] **Step 2: Copy skill files**

```bash
cp "Web & Browsers/web-router/SKILL.md" ~/.claude/skills/web-router/SKILL.md
cp "Web & Browsers/auth/auth.md" ~/.claude/skills/web-router/references/auth.md
cp "Web & Browsers/browse/browse.md" ~/.claude/skills/web-router/references/browse.md
cp "Web & Browsers/tool-selection.md" ~/.claude/skills/web-router/references/tool-selection.md
```

- [ ] **Step 3: Verify deployment**

```bash
ls -la ~/.claude/skills/web-router/
ls -la ~/.claude/skills/web-router/references/
```

Expected: SKILL.md + 3 reference docs.

### Task 15: Phase 1 testing gate

**Files:**
- Create: `Web & Browsers/baselines/phase-1-baseline.md`

Run ALL test scenarios from design doc Section 9 Phase 1 testing gate.

- [ ] **Step 1: Test CC — browse activation**

In a new CC session: "Navigate to HN, search for 'Claude', extract top 3 results"

Required signals: (1) browse specialist activated by router, (2) tool selection logged with all 6 dimensions, (3) results contain >=3 items with title+URL fields.

- [ ] **Step 2: Test CC — auth activation**

"Log into [test site] and extract dashboard data"

Required signals: (1) auth specialist activated, (2) cookie/session established, (3) data extracted.

- [ ] **Step 3: Test CC — routing classification**

Verify web-router logs routing decisions. Check composite task classification works.

- [ ] **Step 4: Test CC — observability log verification**

Required: (1) log file exists at `~/.claude/web-logs/`, (2) valid YAML, (3) all required fields present.

- [ ] **Step 5: Test CAI — search via MCP**

In Claude.ai: "Search for [topic]"
Required: (1) search tool activated, (2) results with sources.

- [ ] **Step 6: Test CAI — scrape via Firecrawl**

In Claude.ai: "Scrape [public URL]"
Required: (1) Firecrawl responds, (2) clean output.

- [ ] **Step 7: Run Phase 1 failure scenarios (6)**

1. URL returns 403 → graceful error
2. Expired cookie → auth escalation
3. MCP timeout → fallback activates
4. Rate-limited (429) → backoff + retry
5. Browserbase session fails → fallback to local
6. Ambiguous task → classification logged, reasonable default

- [ ] **Step 8: Rollback drill**

Intentionally revert auth.md to a previous version. Verify: rollback clean, skill still functions, process documented.

- [ ] **Step 9: Document baseline and commit**

Create `Web & Browsers/baselines/phase-1-baseline.md` with all test results.

```bash
git add "Web & Browsers/baselines/phase-1-baseline.md"
git commit -m "phase-1: testing gate passed — baseline documented"
git tag phase-1-foundation
```

- [ ] **Step 10: Cross-sync to AI CoS**

Add cross-sync message:
```json
{"type": "task", "content": "Phase 1 shipped: browse + auth + web-router skills deployed to CC. MCPs configured: Chrome DevTools, Firecrawl. Action needed: upgrade droplet to $24/mo (4GB), install Chrome, configure Playwright, set up cookie sync cron.", "priority": "normal"}
```

---

## Chunk 3: Phase 2 — Extraction (scrape + search v3)

**Objective:** Build scrape specialist and evolve search-router to v3 with environment awareness and observability.

**Prerequisites:** Phase 1 complete (browse + auth deployed, web-router routing works).

### Task 16: Build scrape specialist (SKILL-CRAFT)

**Files:**
- Create: `Web & Browsers/scrape/skill-development-log.md`
- Create: `Web & Browsers/scrape/scrape.md`

- [ ] **Step 1: SKILL-CRAFT full cycle**

Follow Understanding → Exploring → Research → Synthesis → Drafting → Self-Critique → Iterating.

Key expertise to encode:
- When to use Firecrawl vs Playwright DOM parsing vs Stagehand extract() vs WebFetch
- Schema-driven extraction (user-defined fields → typed JSON)
- Pagination handling (detect "next page", systematic crawl)
- Boundary principle: scrape handles EXTRACTION only, delegates navigation to browse
- Key patterns: schema extraction, bulk crawl, navigated extraction, authenticated extraction

- [ ] **Step 2: Commit**

```bash
git add "Web & Browsers/scrape/"
git commit -m "phase-2: scrape specialist — SKILL-CRAFT complete"
```

### Task 17: Evolve search to v3 (SKILL-CRAFT)

**Files:**
- Modify: `Web & Browsers/search-router/SKILL.md` (rename to `Web & Browsers/search/search.md`)
- Create: `Web & Browsers/search/skill-development-log.md`

- [ ] **Step 1: Copy existing search-router as base**

```bash
mkdir -p "Web & Browsers/search/"
cp "Web & Browsers/search-router/SKILL.md" "Web & Browsers/search/search.md"
```

- [ ] **Step 2: Apply v3 deltas to search.md**

Changes from v2:
- Environment awareness (CAI may lack some tools)
- Firecrawl search added as a tier
- Observability logging (which tool, why, outcome)
- Integration with browse skill for "search then navigate to result"

Preserve: all v2 routing logic, cost optimization, Context7-first.

- [ ] **Step 3: SKILL-CRAFT Self-critique + iterate**

- [ ] **Step 4: Commit**

```bash
git add "Web & Browsers/search/"
git commit -m "phase-2: search v3 specialist — evolved from v2"
```

### Task 18: Deploy Phase 2 + testing gate

**Files:**
- Deploy: `~/.claude/skills/web-router/references/scrape.md`
- Deploy: `~/.claude/skills/web-router/references/search.md`
- Create: `Web & Browsers/baselines/phase-2-baseline.md`

- [ ] **Step 1: Deploy**

```bash
cp "Web & Browsers/scrape/scrape.md" ~/.claude/skills/web-router/references/scrape.md
cp "Web & Browsers/search/search.md" ~/.claude/skills/web-router/references/search.md
```

- [ ] **Step 2: Run Phase 2 test scenarios (5 pass criteria)**

1. Schema extraction: "Extract all pricing plans from [SaaS site] as JSON"
2. Bulk crawl: "Crawl [site] and extract all blog post titles + dates"
3. Search v3 routing: "Research [topic] deeply"
4. CAI extraction: "Extract data from [URL]"
5. Agent SDK: Runner calls Firecrawl to extract company profile

- [ ] **Step 3: Run Phase 2 failure scenarios (5)**

1. Rate-limited mid-crawl → graceful partial results + retry
2. Firecrawl empty on content-rich page → fallback to Playwright
3. Search no results from primary → fallback chain activates
4. Schema mismatch (expected 5 fields, got 3) → partial result flagged
5. 500+ pages discovered → depth limit fires, user prompted

- [ ] **Step 4: Document baseline and commit**

```bash
git add "Web & Browsers/baselines/phase-2-baseline.md"
git commit -m "phase-2: testing gate passed"
git tag phase-2-extraction
```

- [ ] **Step 5: Cross-sync to AI CoS**

```json
{"type": "task", "content": "Phase 2 shipped: scrape + search v3. Firecrawl MCP on droplet enables IngestAgent extraction. Test: runner calls Firecrawl to extract company profile page.", "priority": "normal"}
```

---

## Chunk 4: Phase 3 — Quality (qa + perf-audit)

**Objective:** Build QA testing specialist and performance audit specialist.

**Prerequisites:** Phase 1 complete (browse needed for navigation during QA).

### Task 19: Build qa specialist (SKILL-CRAFT)

**Files:**
- Create: `Web & Browsers/qa/skill-development-log.md`
- Create: `Web & Browsers/qa/qa.md`

- [ ] **Step 1: SKILL-CRAFT full cycle**

Key expertise to encode:
- Four testing modes: diff-aware, full, quick (30s smoke), regression
- Health scoring (8 categories, weighted — from design doc Section 5.5)
- Framework-specific patterns (Next.js hydration, Rails N+1, WordPress plugins, SPA state)
- Tool palette: browse (navigation), Chrome DevTools MCP (console, network, perf), Playwright (screenshots, a11y)
- Output format: structured report with health score, issues, screenshots, console health, regression delta

- [ ] **Step 2: Commit**

```bash
git add "Web & Browsers/qa/"
git commit -m "phase-3: qa specialist — SKILL-CRAFT complete"
```

### Task 20: Build perf-audit specialist (SKILL-CRAFT)

**Files:**
- Create: `Web & Browsers/perf-audit/skill-development-log.md`
- Create: `Web & Browsers/perf-audit/perf-audit.md`

- [ ] **Step 1: SKILL-CRAFT full cycle**

Key expertise to encode:
- Three-pass methodology: Measure (Lighthouse, CrUX), Diagnose (trace analysis, render blocking, long tasks), Prescribe (ranked fixes with impact)
- CSS 2026 perf wins: scroll-driven animations > JS libs, anchor positioning > Popper, container queries > JS responsive
- Dual use: web auditing (public URL) + frontend code auditing (during build)
- Tool palette: Chrome DevTools MCP (Lighthouse, perf traces, CrUX), Playwright (viewport testing), browse (navigation)

- [ ] **Step 2: Commit**

```bash
git add "Web & Browsers/perf-audit/"
git commit -m "phase-3: perf-audit specialist — SKILL-CRAFT complete"
```

### Task 21: Deploy Phase 3 + testing gate

**Files:**
- Deploy: `~/.claude/skills/web-router/references/qa.md`
- Deploy: `~/.claude/skills/web-router/references/perf-audit.md`
- Create: `Web & Browsers/baselines/phase-3-baseline.md`

- [ ] **Step 1: Deploy**

```bash
cp "Web & Browsers/qa/qa.md" ~/.claude/skills/web-router/references/qa.md
cp "Web & Browsers/perf-audit/perf-audit.md" ~/.claude/skills/web-router/references/perf-audit.md
```

- [ ] **Step 2: Run Phase 3 test scenarios (5 pass criteria)**

Including QA calibration: run QA on page with planted defects, verify score decreases and defects appear.

- [ ] **Step 3: Run Phase 3 failure scenarios (6)**

1. localhost down → diagnostic message
2. Lighthouse timeout on heavy page → partial results + warning
3. Chrome DevTools MCP disconnects → reconnection attempt
4. 50+ issues found → prioritized output
5. No frontend changes on diff-aware → "no changes detected"
6. CDN-cached metrics → CDN detection noted

- [ ] **Step 4: Baseline + commit + tag**

```bash
git tag phase-3-quality
```

- [ ] **Step 5: Cross-sync to AI CoS**

---

## Chunk 5: Phase 4 — Intelligence (watch)

**Objective:** Build monitoring specialist for tracking website changes over time.

**Prerequisites:** Phase 2 (scrape) + Phase 3 (perf-audit for perf monitoring type).

### Task 22: Build watch specialist (SKILL-CRAFT)

**Files:**
- Create: `Web & Browsers/watch/skill-development-log.md`
- Create: `Web & Browsers/watch/watch.md`

- [ ] **Step 1: SKILL-CRAFT full cycle**

Key expertise:
- Core pattern: baseline capture → periodic re-check → diff → alert
- Monitoring types: content change, price change, availability, visual change, performance regression
- State storage: JSON files (CC), SQLite (Agent SDK/droplet)
- Environment paths: CC (manual), CAI (via MCP), Agent SDK (cron)
- Tool palette: browse (navigation), scrape (extraction), perf-audit (perf monitoring)

- [ ] **Step 2: Commit**

```bash
git add "Web & Browsers/watch/"
git commit -m "phase-4: watch specialist — SKILL-CRAFT complete"
```

### Task 23: Deploy Phase 4 + testing gate

**Files:**
- Deploy: `~/.claude/skills/web-router/references/watch.md`
- Create: `Web & Browsers/baselines/phase-4-baseline.md`

- [ ] **Step 1: Deploy and test**

Test scenarios + 5 failure scenarios (404 on second check, below-threshold diff, SQLite lock, structural-but-no-content change, stale baseline).

- [ ] **Step 2: Baseline + commit + tag**

```bash
git tag phase-4-intelligence
```

- [ ] **Step 3: Cross-sync to AI CoS**

---

## Chunk 6: Phase 5 — Frontend Refresh (parallel)

**Objective:** Update existing frontend skills with CSS 2026 patterns, Vite 8 knowledge, and WCAG 2.2 best practices. Independent of Phases 1-4.

### Task 24: Update design-system-enforcer

**Files:**
- Read: `~/.claude/skills/design-system-enforcer/SKILL.md`
- Modify: `~/.claude/skills/design-system-enforcer/SKILL.md`
- Source backup: `Frontend Skills/design-system-enforcer-v2/SKILL.md`

- [ ] **Step 1: Read current skill and identify gaps**

Compare current skill against design doc Section 5.9 deltas:
- CSS 2026 patterns (container queries, :has(), native nesting, oklch, scroll-driven animations, view transitions, anchor positioning)
- Vite 8 knowledge (grounded via Context7, not baked-in)
- Anti-drift failsafes (Context7 queries, shadcn MCP, reference docs)
- New anti-patterns

- [ ] **Step 2: Apply updates to skill**

Edit the skill in-place, preserving existing patterns that are still valid.

- [ ] **Step 3: Commit atomically**

```bash
git add "Frontend Skills/design-system-enforcer-v2/"
git commit -m "phase-5: design-system-enforcer updated with CSS 2026 + Vite 8"
```

### Task 25: Update a11y-audit

**Files:**
- Read: `~/.claude/skills/a11y-audit/SKILL.md`
- Modify: `~/.claude/skills/a11y-audit/SKILL.md`

- [ ] **Step 1: Apply updates from design doc Section 5.10**

- Chrome DevTools MCP Lighthouse accessibility audit
- web.dev accessibility course patterns
- WCAG 2.2 AA touch targets (44x44px min, 48px recommended mobile)
- Deeper keyboard testing
- `prefers-reduced-motion` enforcement

- [ ] **Step 2: Commit atomically**

### Task 26: Update CLAUDE.md production standards

**Files:**
- Modify: `~/.claude/CLAUDE.md`

- [ ] **Step 1: Append CSS 2026 Baseline section**

From design doc Section 5.11. Add after existing Frontend Production Standards.

- [ ] **Step 2: Append Build Tool Default section**

- [ ] **Step 3: Append Frontend Anti-Patterns (Updated 2026-03) section**

- [ ] **Step 4: Commit atomically**

### Task 27: Phase 5 testing gate

**Files:**
- Create: `Web & Browsers/baselines/phase-5-baseline.md`

- [ ] **Step 1: Test — "Build a pricing page component"**

Required: container queries, oklch colors, no AOS, Vite scaffold.

- [ ] **Step 2: Test — "Audit accessibility of [component]"**

Required: Chrome DevTools Lighthouse, WCAG 2.2, 44px touch targets flagged.

- [ ] **Step 3: Run Phase 5 failure scenarios (5)**

1. Context7 unreachable → fallback with staleness warning
2. shadcn MCP outdated → version check
3. Below-baseline CSS features → Browserslist check
4. CLAUDE.md edit conflict → atomic commit
5. Design vs a11y conflict → precedence noted

- [ ] **Step 4: Baseline + commit + tag**

```bash
git tag phase-5-frontend
```

---

## Post-Completion

### Task 28: Final deployment verification

- [ ] **Step 1: Verify all reference docs deployed**

```bash
ls ~/.claude/skills/web-router/references/
```

Expected: auth.md, browse.md, scrape.md, search.md, qa.md, perf-audit.md, watch.md, tool-selection.md (8 files)

- [ ] **Step 2: Verify router SKILL.md deployed**

```bash
cat ~/.claude/skills/web-router/SKILL.md | head -5
```

- [ ] **Step 3: Verify updated frontend skills**

```bash
head -5 ~/.claude/skills/design-system-enforcer/SKILL.md
head -5 ~/.claude/skills/a11y-audit/SKILL.md
```

- [ ] **Step 4: Update Notion roadmap — all phases shipped**

Move all phase items to Shipped status in Notion Build Roadmap.

- [ ] **Step 5: Cross-sync final status**

```json
{"type": "status", "content": "Web & Frontend Skills Portfolio complete. All 8 specialists + router + 3 frontend updates deployed. CC, CAI, and Agent SDK surfaces covered.", "priority": "normal"}
```
