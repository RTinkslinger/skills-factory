# Web Tools MCP — Handoff Guide for AI CoS

*Context document for the AI CoS CC ADK project to pick up the cloud/CAI deployment of web skills.*

## What Exists (CC — Complete)

The Web & Frontend Skills Portfolio is **fully built and deployed in CC**:

- **Router:** `~/.claude/skills/web-router/SKILL.md` — classifies tasks, loads specialist reference docs
- **8 specialist reference docs** in `~/.claude/skills/web-router/references/`:
  - `auth.md` — 6-layer auth escalation, 14-service registry, cookie-sync script
  - `browse.md` — Navigate→Snapshot→Act→Verify pattern, Playwright MCP primary
  - `scrape.md` — tiered extraction: Jina(FREE)→Firecrawl→Playwright→browser-use
  - `search.md` — 4-tier routing: Context7/WebSearch→Firecrawl→Exa→Parallel
  - `tool-selection.md` — 6-dimension framework with conflict resolution
  - `qa.md` — 4 modes, 8-category health scoring, framework-specific patterns
  - `perf-audit.md` — 3-pass Measure/Diagnose/Prescribe, CSS 2026 wins
  - `watch.md` — 5 monitoring types, baseline→check→diff→alert cycle
- **Updated frontend skills:** `design-system-enforcer` (CSS 2026), `a11y-audit` (WCAG 2.2)
- **Source files:** `~/Claude Projects/Skills Factory/Web & Browsers/` (git tracked)
- **Phase 0 evaluation data:** `Web & Browsers/phase-0-tool-evaluation.md` (head-to-head results for 9 tools)

**Key tool evaluation results (from Phase 0):**
- Jina Reader: 6/6 URLs, FREE, fastest, best Cloudflare penetration — default extractor
- Firecrawl: good but hallucinates JSON on blocked pages (mandatory metadata validation)
- browser-use: cloud API with `bu_` key at api.browser-use.com (NOT ANTHROPIC_API_KEY)
- Browserbase: isolated sessions for bot-hostile sites
- Chrome DevTools MCP: Lighthouse, perf traces, network panel

## What Was Designed But Never Built (Cloud)

The design doc's north star: *"Any surface where Claude operates (CC, CAI, Agent SDK) should be able to browse, scrape, search, QA, monitor."* The cloud infrastructure to make this work was specified but never implemented.

### Reference Documents

Read these sections of the design doc for full specifications:

| Topic | File | Section/Lines |
|---|---|---|
| **Full design doc** | `docs/superpowers/specs/2026-03-14-web-frontend-skills-portfolio-design.md` | — |
| **Architecture (3-tier model)** | Same | Section 2, lines 34-50 |
| **Environment-specific tool access** | Same | Section 3 (tool availability table), lines 113-120 |
| **Agent SDK skill delivery** | Same | Lines 71-98 (concrete mechanism for loading reference docs into agent runners) |
| **Droplet infrastructure** | Same | Section 7, lines 770-816 |
| **MCP architecture decision** | Same | Lines 778-783, 862-876 |
| **CAI integration strategy** | Same | Section 8, lines 839-891 |
| **Cross-sync task table** | Same | Lines 817-828 |
| **Cookie sync spec** | Same | Lines 514-544 |
| **Cookie sync script** | `Web & Browsers/auth/scripts/cookie-sync.sh` | Full file (executable) |
| **Auth service registry** | `Web & Browsers/auth/auth-service-registry.md` | 14 services with per-service strategies |
| **Layer 1 toolset** | `Web & Browsers/layer-1-toolset.md` | 9-tool architecture with tiered extraction |

### 1. Droplet RAM Upgrade (BLOCKER)

**Current:** 1GB ($12/mo)
**Required:** 4GB ($24/mo)
**Why:** Chrome/Playwright needs 100-300MB, existing services use ~500MB. 1GB = OOM guaranteed.
**Design doc ref:** Lines 785-790

This blocks everything else. Do this first.

### 2. web-tools MCP on Droplet

**Decision (already made):** Separate MCP server, NOT extending ai-cos-mcp.
**Rationale:** Fault isolation — Chrome crash must not kill Notion/calendar/thesis tools.
**Endpoint:** `https://web.3niac.com/mcp` (via Cloudflare Tunnel)
**systemd service:** `web-tools-mcp.service` alongside `ai-cos-mcp.service`
**Design doc ref:** Lines 778-783, 862-876

**What the MCP should expose:**
- `web-browse` — Navigate to URL, take snapshot, interact (wraps Playwright)
- `web-scrape` — Extract content from URL (uses Jina→Firecrawl cascade)
- `web-search` — Search the web (routes between available tools)
- `web-qa` — QA test a URL (health score, console errors, visual issues)
- `web-perf` — Lighthouse audit + Core Web Vitals
- `web-monitor-setup` — Create a watch baseline
- `web-monitor-check` — Re-check monitors, report diffs

**The specialist reference docs** (`Web & Browsers/*.md`) contain the expertise logic for each tool. The MCP tools implement the patterns described in those docs.

### 3. Chrome/Playwright on Droplet

**After RAM upgrade:**
```bash
# Install Chrome
apt-get install -y chromium-browser  # or google-chrome-stable

# Install Playwright
npx playwright install chromium

# Install Node.js MCP servers
npm install -g @anthropic/chrome-devtools-mcp
npm install -g @anthropic/firecrawl-mcp  # needs FIRECRAWL_API_KEY
```

**Design doc ref:** Lines 772-776

### 4. Cookie Sync Infrastructure

**What exists:** `Web & Browsers/auth/scripts/cookie-sync.sh` — uses browser_cookie3 to extract cookies from Safari, filter by domain, stage to `~/.ai-cos/cookies/` (chmod 600).

**What's missing:**
1. **Deploy to cron on Mac** — daily run, extracts cookies for configured domains
2. **Transport:** `rsync -avz ~/.ai-cos/cookies/ root@aicos-droplet:/opt/ai-cos-mcp/cookies/` over Tailscale
3. **Droplet receiving end:** `/opt/ai-cos-mcp/cookies/` directory (chmod 600)
4. **Loading into Playwright:** `context.add_cookies()` from parsed Netscape format files
5. **Expiry monitoring:** Log when cookies fail, alert user to re-extract

**Design doc ref:** Lines 514-544, 792-795

### 5. Reference Doc Deployment to Droplet

**The same reference docs that live in CC need to be on the droplet:**

```bash
# In deploy.sh, add:
rsync -avz ~/.claude/skills/web-router/references/ \
  root@aicos-droplet:/opt/ai-cos-mcp/skills/web-router/references/
```

Agent SDK runners read these at startup and include as system prompt context.
**Design doc ref:** Lines 71-98

### 6. CAI Integration

CAI can't read `~/.claude/skills/`. It needs web tools via MCP:

- **Add web-tools MCP** as remote connector in CAI settings (once Tunnel is live)
- **Add Firecrawl MCP** as remote connector (runs on droplet via `npx firecrawl-mcp`)
- **Encode routing logic** in CAI project instructions (summarized version of web-router)
- **Open questions:** Chrome DevTools MCP latency via remote, rate limits on remote MCP connectors

**Design doc ref:** Section 8, lines 839-891

## API Keys (Already Available)

| Service | Key Location |
|---|---|
| Firecrawl | `.mcp.json` in projects (`fc-2feed5aba35d4a26b95118a1ea4d9e89`) |
| Browserbase | API key: `bb_live_bqAccAg28aAxJEuzIQUBsxQxUCk`, Project: `1d07facb-3bc4-4e87-ae40-a46d5ba9cc47` |
| browser-use | `BROWSER_USE_API_KEY=bu_9M8EHe9L6Nk5APCt1XDxNA_bawIshtjXPMbuHXTeJxY` |

## Suggested Build Order

1. **Droplet RAM upgrade** ($12→$24) — blocker, do immediately
2. **Install Chrome + Playwright** on droplet
3. **Build web-tools MCP** — start with `web-scrape` (Jina+Firecrawl) and `web-browse` (Playwright)
4. **Expose via Cloudflare Tunnel** at `web.3niac.com/mcp`
5. **Deploy reference docs** to `/opt/ai-cos-mcp/skills/`
6. **Connect CAI** — add remote MCP connector
7. **Cookie sync** — deploy cron + transport + loading
8. **Add remaining tools** — qa, perf, monitor
