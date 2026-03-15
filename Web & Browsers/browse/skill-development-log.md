# Browse Specialist — Development Log

## Overview
- **Purpose:** Navigate, interact with, and extract information from web pages using Playwright MCP as the primary tool
- **Scope:** Navigation, form filling, clicking, multi-tab, dynamic content, authenticated browsing
- **Methodology:** SKILL-CRAFT
- **Started:** 2026-03-14

## Topic 1: Understanding ✓

### Problem
AI agents need to interact with web pages — navigate, fill forms, click buttons, handle dynamic content. Without guidance:
- Claude uses screenshots when a11y snapshots would be better
- Claude doesn't verify actions succeeded (no snapshot after interaction)
- Claude doesn't handle SPAs, lazy loading, or infinite scroll
- Claude doesn't know when to escalate to human (CAPTCHA, 2FA)
- Claude doesn't think about token cost of repeated snapshots

### Trigger
- "go to [URL]", "navigate to", "open [site]"
- "fill out [form]", "click [button]", "search for [query] on [site]"
- Any task requiring interactive web browsing
- Invoked by web-router when task classification = interactive browsing

### Success Criteria
- Page navigated and content verified via snapshot
- Forms filled and submitted with verification
- Dynamic content handled (wait for load, scroll, retry)
- Token-efficient (minimize unnecessary snapshots)
- Human escalation when needed (CAPTCHA, 2FA)

### Out of Scope
- Text extraction from static pages (that's scrape)
- Auth/session management (that's auth)
- Quality auditing (that's qa/perf-audit)
- Monitoring/watching (that's watch)

## Topic 2: Exploring ✓

### Where Claude Fails Without This Skill
1. **No verify-after-act pattern** — fills a form but doesn't check if submission succeeded
2. **Screenshot-first thinking** — takes screenshots when a11y snapshots give better data for interaction
3. **No SPA awareness** — navigates to a React app and wonders why the snapshot is empty
4. **Unbounded snapshots** — takes full page snapshots when only a section is relevant
5. **No fallback chain** — if Playwright fails, doesn't know to try Chrome DevTools or Browserbase
6. **CAPTCHA panic** — hits a CAPTCHA and either gives up or tries to solve it (both wrong)

## Topic 3: Research + Synthesis ✓

### Key Sources
- Phase 0: Playwright MCP baseline (100% reliable, ~50-100KB snapshots)
- Phase 0: Chrome DevTools MCP (same a11y tree approach, Lighthouse unique)
- Design doc: browse specialist patterns (navigate-and-verify, fill-and-submit)

### Extracted Principles
1. **Snapshot → Act → Snapshot** — always verify actions with a follow-up snapshot
2. **a11y tree over screenshots** — snapshots give refs for interaction, screenshots are for visual evidence only
3. **Wait for ready** — SPA pages need a wait after navigation before the snapshot has meaningful content
4. **Minimal snapshots** — don't snapshot the whole page if you only need one element
5. **Fallback chain** — Playwright → Chrome DevTools → Browserbase → human escalation

## Decisions Summary

| Decision | Choice | Rationale |
|---|---|---|
| Primary tool | Playwright MCP | 100% reliable in Phase 0, deterministic |
| Interaction model | a11y snapshot refs | Better than screenshots for interaction targeting |
| Verification | Post-action snapshot | Confirm actions succeeded before proceeding |
| SPA handling | Wait + retry snapshot | Dynamic content needs time to render |
| Human escalation | CAPTCHA, 2FA, sensitive confirms | Don't try to solve what requires a human |

## Files Created
- `browse/skill-development-log.md` (this file)
- `browse/browse.md` (reference doc)
