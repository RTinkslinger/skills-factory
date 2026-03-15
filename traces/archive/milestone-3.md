# Milestone 3: Phase 1-2 Deployment + Verification + Phase 0 Extended Eval
**Iterations:** 7-11 | **Dates:** 2026-03-14

## Summary
Deployed Phase 1 (auth + browse + web-router + tool-selection) and Phase 2 (scrape + search v3) as reference docs under `~/.claude/skills/web-router/`. Ran comprehensive head-to-head tool evaluation across 6 URL types — Jina Reader emerged as surprise winner (FREE, fastest, best Cloudflare penetration), reshaping the extraction cascade. browser-use re-added as fallback per user feedback. All three phases (0, 1, 2) verified by user and shipped.

## Key Decisions
- Phase 1 deployed as single skill with reference docs pattern (router SKILL.md + specialist .md files)
- Jina Reader is default extractor (FREE, 6/6 URLs). Cascade: Jina → Firecrawl scrape → Firecrawl extract → Playwright → browser-use
- browser-use kept as fallback (has its own cloud API with bu_ key, not ANTHROPIC_API_KEY)
- Search v3 adds Firecrawl search as middle tier + environment awareness
- Scrape uses content-type-driven tool selection
- 4 services added to auth registry: X, LinkedIn, Reddit, Substack

## Iteration Details

### Iteration 7 - 2026-03-14
**Phase:** Phase 1: Foundation (deployment)
**Focus:** Deploy Phase 1 skills to CC + close Phase 0 & Phase 1

**Changes:** `~/.claude/skills/web-router/` (SKILL.md + references/auth.md + references/browse.md + references/tool-selection.md deployed), `ROADMAP.md` (Phase 0 + Phase 1 → Verifying), Notion updated (both items → Verifying)
**Decisions:** Phase 1 deployed as single skill with reference docs pattern -> router SKILL.md triggers, loads specialist references on demand.

---

### Iteration 8 - 2026-03-14
**Phase:** Phase 2: Extraction
**Focus:** Scrape specialist + Search v3 + deploy

**Changes:** `Web & Browsers/scrape/` (scrape specialist — extraction patterns, Firecrawl guardrails, pagination), `Web & Browsers/search/` (search v3 — Firecrawl tier, environment awareness, observability, browse integration), `~/.claude/skills/web-router/references/` (scrape.md + search.md deployed)
**Decisions:** Scrape uses content-type-driven tool selection (text→Firecrawl, structured→extract, dynamic→Playwright). Search v3 adds Firecrawl search as middle tier between free WebSearch and expensive Parallel.

---

### Iteration 9 - 2026-03-14
**Phase:** Verification feedback
**Focus:** Add browser-use as fallback per user feedback

**Changes:** `Web & Browsers/layer-1-toolset.md` (browser-use added as Fallback), `Web & Browsers/tool-selection.md` (browser-use in Speed + Complexity dimensions), `Web & Browsers/browse/browse.md` (browser-use as Fallback 1), `Web & Browsers/phase-0-tool-evaluation.md` (verdict Skip→Fallback), redeployed to `~/.claude/skills/web-router/references/`
**Decisions:** browser-use kept as fallback for complex autonomous multi-step flows. Requires its own cloud API key (bu_ prefix).

---

### Iteration 10 - 2026-03-14
**Phase:** Phase 0: Extended tool evaluation
**Focus:** Comprehensive head-to-head eval — Jina Reader, WebFetch, browser-use cloud, Firecrawl across 6 URL types

**Changes:** `Web & Browsers/phase-0-tool-evaluation.md` (head-to-head results matrix), `Web & Browsers/layer-1-toolset.md` (Jina + WebFetch added as Core), `Web & Browsers/scrape/scrape.md` (Jina as default), `Web & Browsers/tool-selection.md` (updated dimensions), redeployed 3 reference docs
**Decisions:** Jina Reader is surprise winner (6/6 URLs, FREE, fastest, best CF penetration). Default cascade: Jina → Firecrawl scrape → Firecrawl extract → Playwright. browser-use cloud API works with bu_ key.

---

### Iteration 11 - 2026-03-14
**Phase:** Verification + Shipping
**Focus:** User verification of Phase 0/1/2 + ship all three

**Changes:** `Web & Browsers/auth/auth-service-registry.md` (added X, LinkedIn, Reddit, Substack), `ROADMAP.md` (Phase 0/1/2 → Shipped), Notion updated (3 items → Shipped)
**Verification results:** Phase 0 PASS, Phase 1 PASS, Phase 2 PASS. User feedback: add X/LinkedIn/Reddit/Substack to service registry; environment awareness should auto-update as MCPs are added.
