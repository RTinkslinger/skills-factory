# LEARNINGS.md

Trial-and-error patterns discovered during Claude Code sessions.
Patterns confirmed 2+ times graduate to CLAUDE.md during milestone compaction.

## Active Patterns

### 2026-03-15 - Sprint 1
- Tried: `pip3 install browser-use` (system pip3, /usr/bin/pip3) — failed: pip version 21.2.4 too old, can't find package
  Then tried: `/opt/homebrew/bin/pip3 install` — failed: PEP 668 externally-managed-environment error (Python 3.14 via Homebrew)
  Works: `brew install uv` then `uv venv /tmp/phase0-eval && source /tmp/phase0-eval/bin/activate && uv pip install browser-use browser_cookie3`
  Context: Homebrew Python 3.14 is externally managed. Always use uv + venv for pip installs, never system pip.
  Confirmed: 1x

### 2026-03-14 - Sprint 2
- Tried: Firecrawl JSON extraction (`formats: ["json"]` with `jsonOptions`) on a page behind an age gate (Steam BG3)
  Expected: Empty fields or error when content is inaccessible
  Actual: Firecrawl **hallucinated** structured data — returned "Hades" at "$24.99" for a Baldur's Gate 3 URL
  Root cause: URL redirected to `/agecheck/`, extraction couldn't find matching content, LLM fabricated plausible data
  Fix: Always validate `metadata.url` against requested URL (detect redirects) and `metadata.statusCode` before trusting JSON extraction results. Discard if URL changed or status != 200.
  Confirmed: 1x

- Tried: Firecrawl markdown scrape on image-heavy SaaS page (linear.app/features)
  Expected: Meaningful feature descriptions
  Actual: ~95% image URLs, almost no text content
  Works better: Use Playwright for JS-heavy/image-heavy pages, reserve Firecrawl for text-heavy content (blogs, docs, articles)
  Confirmed: 1x

- Tried: Assumed browser-use needs ANTHROPIC_API_KEY (checked env vars, keychain, project files — not found, declared "blocked")
  Actual: browser-use has its own cloud API at api.browser-use.com with a `bu_` prefixed key (BROWSER_USE_API_KEY). User had the key all along.
  Fix: Don't assume tool dependencies — check the tool's actual config format. browser-use SDK has `BROWSER_USE_CLOUD_API_URL` and its own key format.
  Confirmed: 1x

- Tried: Skipped Jina Reader and WebFetch from evaluation, went straight to building skills
  Actual: Jina Reader turned out to be the best extraction tool (6/6 URLs, FREE, fastest, best Cloudflare penetration)
  Fix: Evaluate ALL tools from the design doc before building. Don't pick a thin stack because 2-3 tools worked.
  Confirmed: 1x
