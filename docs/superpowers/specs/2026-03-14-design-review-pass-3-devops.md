# Design Review Pass 3 — DevOps Engineer

**Date:** 2026-03-14
**Reviewer:** Claude Opus 4.6 (DevOps Engineer lens)
**Document:** `docs/superpowers/specs/2026-03-14-web-frontend-skills-portfolio-design.md`

---

## Strengths

- Rollback procedure is concrete and executable
- Cookie sync transport (rsync over Tailscale) is sound
- Agent SDK `load_specialist()` pattern is operationally simple
- Phase 0 blocking gate prevents building on unverified assumptions

---

## Findings

### FINDING 1 — BLOCKING: Droplet RAM upgrade is a prerequisite, not optional

**Issue:** 1GB RAM droplet + existing services (~400-600MB) + Chrome (~300-600MB active) = OOM. Installing Playwright on current droplet will kill ai-cos-mcp.
**Fix:** Upgrade to 2GB minimum (4GB preferred) BEFORE installing Chrome. Phase 1 blocker. $12 → $24/mo.

### FINDING 2 — BLOCKING: Cookie sync silent failure modes

**Issue:** Mac sleep suspends cron (cookies never sync). Tailscale disconnect = rsync fails silently. Droplet uses stale cookies with no alert.
**Fix:** (a) Cookie age check on droplet (mtime comparison before use), (b) `caffeinate -s` during sync, (c) heartbeat `last_sync.json` on droplet, runners check at startup.

### FINDING 3 — MAJOR: No MCP server process supervision on droplet

**Issue:** Chrome DevTools MCP crashes if Chrome isn't running. No restart logic. Tool call errors with no recovery.
**Fix:** Every MCP server gets a systemd unit. Post-deploy verification. Liveness health check.

### FINDING 4 — MAJOR: Cookie staging in /tmp/ is world-readable

**Issue:** `/tmp/cookies/` is world-readable on macOS. Session credentials for LinkedIn/banking exposed between extraction and rsync.
**Fix:** Extract to `chmod 600` file in `~/.ai-cos/cookies/`, never `/tmp/`.

### FINDING 5 — MAJOR: Extending ai-cos-mcp with browser ops is a fault isolation failure

**Issue:** Chrome crash inside ai-cos-mcp kills Notion tools, calendar, everything. Not symmetric options — separate process is required.
**Fix:** Resolve as decision NOW: separate web-tools MCP. Chrome ops must not share process with ai-cos-mcp.

### FINDING 6 — MAJOR: deploy.sh is unspecified

**Issue:** No source path, rsync flags, idempotency, failure handling. Partial deploy = Mac/droplet on divergent skill versions.
**Fix:** Specify fully. Post-deploy checksum verification. `DEPLOYED_VERSION` file on both targets.

### FINDING 7 — MAJOR: Secret rotation procedure undocumented

**Issue:** 5+ services with API keys in .env (droplet) + env vars (Mac) + ~/.mcp.json. No rotation procedure, no manifest of where keys live.
**Fix:** Create `~/.ai-cos/secrets-manifest.md`. Document rotation: update .env → update Mac → restart MCPs.

### FINDING 8 — MINOR: SQLite state excluded from disaster recovery

**Fix:** Document what's lost if droplet dies. Backup via DO snapshots or `sqlite3 .dump` to Mac.

### FINDING 9 — MINOR: Silent missing specialist doc in load_specialist()

**Fix:** Add `logging.warning()` for missing docs. Startup check lists expected specialists, logs missing.

### FINDING 10 — MINOR: Unpinned MCP versions break without warning

**Fix:** Pin versions: `firecrawl-mcp@1.x.x`, `chrome-devtools-mcp@x.x.x`. Update intentionally.

---

## Summary

| # | Severity | Issue |
|---|---|---|
| 1 | BLOCKING | RAM upgrade is Phase 1 prerequisite |
| 2 | BLOCKING | Cookie sync silent failures (Mac sleep, Tailscale) |
| 3 | MAJOR | No MCP process supervision on droplet |
| 4 | MAJOR | Cookie staging in world-readable /tmp/ |
| 5 | MAJOR | ai-cos-mcp + browser ops = fault isolation failure |
| 6 | MAJOR | deploy.sh unspecified, partial deploy risk |
| 7 | MAJOR | Secret rotation undocumented |
| 8 | MINOR | SQLite state not in DR plan |
| 9 | MINOR | Silent missing specialist doc |
| 10 | MINOR | Unpinned MCP versions |
