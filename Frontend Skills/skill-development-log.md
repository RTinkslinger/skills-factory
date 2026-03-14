# Frontend Skills & MCPs - Development Log

## Overview
- **Purpose:** Make Claude Code the best frontend builder via skills + MCP grounding
- **Scope:** 2 skills (design-system-enforcer, a11y-audit), 2 MCP servers (shadcn, Figma), production standards in CLAUDE.md
- **Methodology:** SKILL-CRAFT (expertise transfer, not instructions)

## Topic 1: MCP Foundation - Done
- shadcn MCP already installed globally at ~/.mcp.json, verified responding
- Figma MCP configured with figma-developer-mcp + FIGMA_API_KEY env var, awaiting restart verification
- Playwright browser_snapshot confirmed returning full accessibility trees with ARIA roles, heading levels, link targets

### Decisions
- Used figma-developer-mcp (Framelink) as the Figma MCP — most actively maintained (39 versions)
- Token passed via env field in .mcp.json (not CLI arg) for security

## Topic 2: Frontend Production Standards - Done
- Added ## Frontend Production Standards to ~/.claude/CLAUDE.md
- 6 sub-sections: Component Library, Styling Patterns, Responsive, Performance, Accessibility, Anti-Patterns
- Complements existing Frontend Design Guidelines (aesthetics/RECKONER) without duplication

### Decisions
- Kept as separate section from Frontend Design Guidelines — aesthetics vs production are different concerns
- Anti-patterns consolidated from plan + RECKONER into one authoritative list

## Topic 3: design-system-enforcer Skill - Done
- Created at ~/.claude/skills/design-system-enforcer/SKILL.md
- Expert voice: design systems engineer who grounds every decision in source of truth
- Structure: Mindset -> Core Principles -> The Work (before/during/after) -> Patterns -> Traps
- ~1200 words, follows SKILL-CRAFT methodology

### Decisions
- Organized "The Work" as before/during/after building (not numbered steps) — matches how experts think
- Included specific MCP tool references (shadcn queries, Figma extraction, Playwright verification)
- Framed Figma extraction as conditional ("when Figma URL is provided") — graceful degradation
- Emphasized "composition over creation" as core principle — prevents reimplementing shadcn

## Topic 4: a11y-audit Skill - Done
- Created at ~/.claude/skills/a11y-audit/SKILL.md
- Expert voice: accessibility specialist who sees barriers, not pages
- Structure: Mindset -> Core Principles -> The Work (3 passes) -> Patterns -> Traps
- ~1100 words, follows SKILL-CRAFT methodology

### Decisions
- Three-pass audit structure: Structure (tree) -> Interaction (keyboard) -> Visual (viewports)
- Severity triage: Critical -> Serious -> Moderate (not alphabetical/WCAG-order)
- Auto-fix critical/serious, flag moderate — matches how a11y specialists prioritize
- Three pattern variants: full audit, quick check, WCAG compliance — different depths for different asks

## Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Figma MCP package | figma-developer-mcp | Most maintained, Framelink is the known standard |
| Token storage | env field in .mcp.json | More secure than CLI args (not in process listing) |
| Production standards location | ~/.claude/CLAUDE.md section | Always-loaded > skill-triggered |
| Skill structure | Mindset-first (SKILL-CRAFT) | Expertise transfer, not checklists |
| A11y audit approach | Playwright-native (browser_snapshot) | No extra MCP server to maintain |

## Files Created
- `~/.mcp.json` — Updated with Figma MCP server
- `~/.claude/CLAUDE.md` — Updated with Frontend Production Standards
- `~/.claude/skills/design-system-enforcer/SKILL.md` — Design system enforcement skill
- `~/.claude/skills/a11y-audit/SKILL.md` — Accessibility audit skill
- `skill-development-log.md` — This file
