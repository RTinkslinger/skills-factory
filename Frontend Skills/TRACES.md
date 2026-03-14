# Build Traces

## Project Summary

Global Claude Code frontend infrastructure shipped across 2 iterations. Key deliverables: shadcn MCP + Figma MCP configured, Frontend Production Standards in CLAUDE.md (6 sub-sections), design-system-enforcer skill (component grounding, Figma tokens, build, a11y verify, visual verify), a11y-audit skill (3-pass: structure, interaction, visual). Validated end-to-end: pricing page test, Figma-to-code pipeline (team page from real Figma file), full a11y audit with auto-fixes (heading hierarchy, touch targets). All 17 plan items complete except item 11 (auto-trigger needs fresh session test by user).

## Milestone Index

| # | Iterations | Focus | Key Decisions |
|---|------------|-------|---------------|
| - | - | - | *No milestones yet* |

*Full details: `traces/archive/milestone-N.md`*

---

## Current Work (Milestone 1 in progress)

### Iteration 1 - 2026-03-06
**Phase:** Phase 1-4: Full system build
**Focus:** MCP foundation, production standards, skills creation, validation testing

**Changes:**
- `~/.mcp.json` (added Figma MCP server with figma-developer-mcp + FIGMA_API_KEY env var)
- `~/.claude/CLAUDE.md` (added Frontend Production Standards section — 6 sub-sections)
- `~/.claude/skills/design-system-enforcer/SKILL.md` (created — ~1200 words, SKILL-CRAFT methodology)
- `~/.claude/skills/a11y-audit/SKILL.md` (created — ~1100 words, SKILL-CRAFT methodology)
- `test-project/src/app/pricing/page.tsx` (validation pricing page using shadcn Card/Button/Badge)
- `skill-development-log.md` (created — full development log)

**Decisions:**
- figma-developer-mcp (Framelink) for Figma MCP -> most maintained, 39 versions
- Token via env field not CLI arg -> security (not in process listings)
- Skills use Mindset-first structure (SKILL-CRAFT) -> expertise transfer, not checklists
- Playwright-native a11y (browser_snapshot) -> no extra MCP to maintain

**Next:** Verify Figma MCP after Claude Code restart. Run design-system-enforcer in a real session (not self-test). Tune skill triggers if needed. Clean up test-project.

---

### Iteration 2 - 2026-03-06
**Phase:** Phase 4: Validation & Tuning
**Focus:** Figma MCP verification, Figma-to-code pipeline, a11y audit, skill trigger tuning, production standards verification

**Changes:**
- `test-project/src/app/team/page.tsx` (created — Figma-to-code implementation using Card/Badge/Button + Figma tokens)
- `test-project/src/app/globals.css` (added Figma design tokens as CSS custom properties)
- `~/.claude/skills/design-system-enforcer/SKILL.md` (widened trigger keywords: login form, card, modal, table, nav)
- `~/.claude/skills/a11y-audit/SKILL.md` (added trigger keywords: WCAG 2.2, touch targets, keyboard navigation)
- `frontend-skill-mcp-system-plan.md` (updated items 9-14 to DONE status)

**Decisions:**
- Figma MCP uses `get_figma_data` not `get_design_context` (different API than originally expected) -> works fine
- Figma community URLs don't work (need `/design/` or `/file/` format with short key) -> documented
- h1→h2 heading hierarchy (not h1→h3) for card titles -> proper WCAG compliance
- Touch targets enforced at 44px minimum via `min-h-[44px]` -> cleaner than padding hacks

**Next:** Item 11 auto-trigger needs new-session verification by user. All other items complete. Project effectively done.

---
