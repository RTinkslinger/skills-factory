# Auth Specialist — Development Log

## Overview
- **Purpose:** Give AI agents authenticated web access across environments (CC, CAI, Agent SDK) while protecting real user sessions
- **Scope:** Session management, cookie sync, auth layer selection, service registry
- **Methodology:** SKILL-CRAFT
- **Started:** 2026-03-14

## Topic 1: Understanding ✓

### Problem
AI agents need to access authenticated web content (Gmail, YouTube, GitHub, Notion, etc.) but:
- They can't log in interactively (no GUI, no password entry)
- Using real browser sessions risks ejecting the user
- Different services need different auth strategies
- Cookies expire, tokens rotate, sessions break
- Multiple environments (local Mac, remote droplet) need access

### Trigger
- "log in to [service]", "access my [account]", "set up auth for [site]"
- Invoked by other specialists (browse, scrape, watch) when they hit a login wall
- Cookie staleness detection (>30 days without refresh)

### Success Criteria
- Correct auth layer selected for the service
- Session established without disrupting user's real session
- Credentials never stored in code or logs
- Cookie sync infrastructure working Mac → droplet

### Out of Scope
- Browsing itself (that's the browse specialist)
- Data extraction (that's scrape)
- Credential storage/management (user manages their own credentials)
- OAuth token refresh implementation (uses existing MCP connections)

## Topic 2: Exploring ✓

### Where Claude Fails Without This Skill
1. **Tries to use real browser sessions** — opens Chrome, navigates to Gmail, risks breaking the user's active session
2. **Doesn't know about cookie infrastructure** — has no concept of browser_cookie3, cookie sync scripts, or the droplet's cookie store
3. **Mishandles session isolation** — doesn't think about Browserbase for risky auth operations
4. **Picks wrong auth layer** — tries cookie-based access for services that have API keys, or vice versa
5. **No staleness awareness** — uses cookies that expired weeks ago, gets mysterious 401s
6. **Environment confusion** — tries to extract cookies on the droplet (no browser), or tries to access localhost-only services remotely

## Topic 3: Research + Synthesis ✓

### Key Sources
- Phase 0 evaluation: browser_cookie3 is the cookie extraction winner (domain filtering, Safari + Chrome)
- gstack's approach: compiled macOS binary with keychain entitlements — overkill, browser_cookie3 handles it
- Browserbase: 0.24s session creation, 25 concurrent sessions, clear error handling
- Design doc Section 4: 6-layer auth model, "Protect My Account" principle

### Extracted Principles
1. **Layer escalation, not layer selection** — start at the simplest layer, escalate only when needed
2. **Domain-filtered cookies** — never export all cookies, only what's needed for the target service
3. **Isolation by default for risky operations** — Browserbase for anything that could break a session
4. **Living registry** — auth strategies per service, maintained as things change
5. **Staleness detection** — proactively check cookie age, don't wait for 401s

## Decisions Summary

| Decision | Choice | Rationale |
|---|---|---|
| Cookie extraction method | browser_cookie3 | Native domain filtering, handles Safari + Chrome encryption |
| Cookie transport | rsync over Tailscale | Encrypted tunnel, no exposed ports |
| Session isolation | Browserbase | Fast (0.24s), 25 concurrent, clear errors |
| Auth strategy registry | Markdown table | Simple, human-editable, version-controlled |
| Staleness threshold | 30 days cookies, 90 days API keys | Balance between security and convenience |

## Files Created
- `auth/skill-development-log.md` (this file)
- `auth/auth.md` (reference doc)
- `auth/auth-service-registry.md` (living doc)
- `auth/scripts/cookie-sync.sh` (cookie sync script)
