# Plan: Make Claude Code the Best Frontend Builder

## Context

Claude Code has a strong aesthetic foundation (FRONTEND_DESIGN_RECKONER.md + frontend-design plugin) but **no grounding infrastructure** — it halluccinates component props, invents outdated Tailwind patterns, and can't verify accessibility. The research (1,065 sources) identifies the core insight: **"Context-over-guessing"** — connecting Claude Code to live UI sources cuts hallucinations and enforces current APIs.

**Goal:** Global Claude Code setup where ANY frontend project gets distinctive, production-ready, accessible output.

**Constraints:** Framework-agnostic, Figma + freeform workflows, design distinctiveness + production-readiness.

**Research source:** `/Users/Aakash/Claude Projects/Aakash AI CoS CC ADK/docs/research/claude-code-frontend-ux-deep-research.md`

---

## Critique of v1 Plan: What's Over-Engineered

| Item | Verdict | Reasoning |
|------|---------|-----------|
| **ScreenshotOne MCP** | CUT | Playwright `browser_take_screenshot` already installed. Paid API duplicates existing capability. |
| **`figma-to-code` skill** | MERGE | Its workflow is just the Figma branch of `design-system-enforcer`. Separate skill creates "which do I use?" confusion. |
| **`frontend-production` skill** | CUT | Wraps existing frontend-design plugin with production rules. But production rules belong in CLAUDE.md (always loaded) not a skill (must be triggered). CLAUDE.md enforcement is strictly superior. |
| **PostToolUse a11y hook** | CUT | Fires after EVERY `.tsx` edit — hook fatigue. The design-system-enforcer skill already runs a11y as step 3. Hook duplicates skill workflow. Also: shell hooks can only echo reminders, can't actually run axe. |
| **Accessibility MCP** | REPLACE | Requires cloning a GitHub repo + building from source + maintaining. Playwright already has `browser_snapshot` (accessibility tree) and we can `npm install axe-playwright` in projects. Use Playwright-native a11y instead. |
| **RECKONER update** | MINIMAL | Adding MCP workflow to an aesthetic guide dilutes its purpose. MCP orchestration belongs in skills. At most, add 2 lines referencing the design-system-enforcer skill. |

### What Delivers 90% of the Value (The Essential 5)

1. **shadcn MCP** — Eliminates component hallucination. Single biggest quality uplift. ~15 min.
2. **Figma MCP** — Design-to-code grounding when designs exist. ~15 min.
3. **`design-system-enforcer` skill** — The orchestration brain. ONE skill that handles: shadcn grounding -> Figma tokens -> code -> a11y check. ~1 hr.
4. **CLAUDE.md Frontend Production Standards** — Always loaded, always enforced. Responsive, performance, anti-patterns, a11y. ~30 min.
5. **`a11y-audit` skill** — Standalone audit using Playwright (already installed). No extra MCP. ~30 min.

**Total: 5 items, ~2.5 hours, 2 files edited + 2 files created.**

---

## Execution Status (Updated 2026-03-06)

### Completed

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1 | shadcn MCP | SHIPPED | Was already in `~/.mcp.json`. Verified: returns structured component data from registry. |
| 2 | Figma MCP | SHIPPED | Configured in `~/.mcp.json` with `figma-developer-mcp` + `FIGMA_API_KEY` env var. Verified: returns structured node data (frames, text, fills, layouts). |
| 3 | Playwright a11y | SHIPPED | `browser_snapshot` confirmed returning full accessibility tree (ARIA roles, heading levels, names, states). |
| 4 | CLAUDE.md Frontend Production Standards | VERIFYING | Added to `~/.claude/CLAUDE.md` with 6 sub-sections: Component Library, Styling Patterns, Responsive, Performance, Accessibility, Anti-Patterns. |
| 5 | `design-system-enforcer` skill | VERIFYING | Created at `~/.claude/skills/design-system-enforcer/SKILL.md`. ~1200 words, SKILL-CRAFT methodology. Already registering in skill list. |
| 6 | `a11y-audit` skill | VERIFYING | Created at `~/.claude/skills/a11y-audit/SKILL.md`. ~1100 words, SKILL-CRAFT methodology. Already registering in skill list. |
| 7 | Validation: Pricing page component test | SHIPPED | Built pricing page in test-project using shadcn Card/Button/Badge. Full a11y audit passed (structure, keyboard, visual at 375px + 1280px). |
| 8 | Validation: Standalone a11y test | SHIPPED | Ran as part of pricing page test. 3-pass audit verified: landmarks, headings, button names, focus order, keyboard operability, responsive layout. |

### Remaining (Next Session)

| # | Item | Priority | What Needs to Happen |
|---|------|----------|----------------------|
| 9 | Verify Figma MCP responds | DONE | Tested with real file (dokFO8euCt7EqU6BEr4231). Returns full node tree: frames, text, fills, layouts, images. Auth + API working. |
| 10 | Figma-to-code validation test | DONE | Full pipeline verified: Figma tokens → CSS vars, shadcn Card/Badge/Button, a11y audit (3 issues auto-fixed), visual verification at 375px + 1280px. Built /team page from Figma file dokFO8euCt7EqU6BEr4231. |
| 11 | Real-session skill trigger test | PARTIAL | design-system-enforcer invoked and followed successfully in this session (Figma-to-code + a11y pipeline). True auto-trigger test requires a NEW conversation — user should test: open a frontend project, say "Build a login form", verify skill triggers without manual invocation. Trigger keywords are correct. |
| 12 | Real-session a11y trigger test | DONE | a11y-audit invoked and ran full 3-pass audit (structure, interaction, visual) on /team page. Found and auto-fixed: heading hierarchy skip, touch targets below 44px. Trigger keywords verified correct. |
| 13 | Tune skill trigger descriptions | DONE | Added more trigger keywords to both skills: design-system-enforcer got "build a login form", "create a card", "add a modal", "build a table", "create a nav". a11y-audit got "WCAG 2.2", "check touch targets", "keyboard navigation test". |
| 14 | Production standards enforcement test | DONE | Team page verified against all 10 production standards: shadcn components, CSS vars for tokens, mobile-first responsive, transform-only animation, semantic HTML, native interactives, list keys, a11y, no arbitrary colors, no banned fonts. All pass. |
| 15 | Clean up test-project | DONE | Kept for future testing. Contains /pricing (iteration 1 validation) and /team (Figma-to-code validation). No stale artifacts. |
| 16 | Disk space: clear npm cache | PARTIAL | `npm cache clean --force` succeeded (cache dir removed). Gained ~100MB. Home-level `~/node_modules` (266MB from stray stagehand install) still exists — user should run `rm -rf ~/node_modules ~/package.json ~/package-lock.json` to recover. 2.7GB free now. |
| 17 | RECKONER minimal update | DONE | Added "Companion Tools" section at bottom of RECKONER linking to design-system-enforcer skill. Updated date to March 2026. |

### Known Issues

| Issue | Severity | Details |
|-------|----------|---------|
| Lucide Check icons in a11y tree | Minor | `<Check aria-hidden="true">` shows as `img` in Playwright accessibility tree. Lucide may not be passing `aria-hidden` to the SVG element. No impact — icons are alongside text so no information is lost. |
| npm cache permission denied | Low | `~/.npm/_cacache` has files owned by root. `npm cache clean --force` fails without sudo. Not blocking. |
| Disk space tight | Low | 2.6GB free after cleanup. Large project scaffolding may hit ENOSPC again. Consider clearing `~/Library/Caches` or `~/node_modules` (accidental home-level install, 266MB). |

---

## File Structure (Final State)

```
~/.claude/
├── .mcp.json                              # EDIT: +shadcn, +figma MCP servers
├── CLAUDE.md                              # EDIT: +Frontend Production Standards section
├── FRONTEND_DESIGN_RECKONER.md            # EXISTS (no change, or 2-line addition)
├── skills/
│   ├── design-system-enforcer/
│   │   └── SKILL.md                       # CREATE: core orchestration skill
│   ├── a11y-audit/
│   │   └── SKILL.md                       # CREATE: standalone a11y audit
│   ├── email-agent/                       # EXISTS (unchanged)
│   └── search-router/                     # EXISTS (unchanged)
├── plugins/
│   └── cache/claude-plugins-official/
│       ├── frontend-design/               # EXISTS (unchanged — aesthetics layer)
│       ├── playwright/                    # EXISTS (unchanged — browser/a11y layer)
│       └── vercel/                        # EXISTS (unchanged — deploy layer)
└── settings.json                          # NO CHANGE (no hooks needed)
```

**Net new:** 2 skill files + 2 config edits. That's it.

---

## Phases & Steps

### Phase 1: MCP Foundation (~30 min)

**Goal:** Give Claude Code access to live component APIs and design tokens.

**Step 1.1: Install shadcn MCP**
- Read current `~/.claude/.mcp.json`
- Add shadcn MCP server entry
- Verify: restart Claude Code, ask "What variants does the shadcn Button have?" — should query MCP, not hallucinate

**Step 1.2: Install Figma MCP**
- Check if `FIGMA_TOKEN` env var exists; if not, prompt user to create one at figma.com/developers
- Add Figma MCP server entry to `~/.claude/.mcp.json`
- Verify: provide a Figma URL, ask Claude to describe the design — should return structured data from `get_design_context`

**Step 1.3: Verify Playwright a11y capabilities**
- Confirm Playwright plugin is active and `browser_snapshot` returns accessibility tree
- Test: navigate to any URL, run `browser_snapshot` — should return ARIA roles, names, states
- This replaces the need for a separate accessibility MCP server

### Phase 2: CLAUDE.md Frontend Standards (~30 min)

**Goal:** Production rules that are always loaded, always enforced, zero friction.

**Step 2.1: Add "Frontend Production Standards" section to `~/.claude/CLAUDE.md`**

Content to add:
- **Component library:** "When shadcn MCP is available, query it before writing custom UI components. Prefer shadcn/ui components over hand-rolled equivalents."
- **Styling patterns:** "Use `cva` (class-variance-authority) for component variants. Use `cn()` helper (tailwind-merge + clsx) for conditional classes. Never build dynamic class strings with template literals."
- **Responsive:** "Mobile-first. Base styles target mobile, layer up: `sm:` (640px), `md:` (768px), `lg:` (1024px), `xl:` (1280px)."
- **Performance:** "Never animate layout properties (width, height, top, left, margin, padding). Only animate `transform` and `opacity`. Use `will-change` sparingly."
- **Accessibility:** "WCAG 2.2 AA minimum. Color contrast >= 4.5:1 for normal text, >= 3:1 for large text. Touch targets >= 44x44px. All interactive elements must have visible focus states (ring or outline, >= 3:1 contrast). Semantic HTML first — only use ARIA when native HTML is insufficient."
- **Anti-patterns:** Consolidate existing rules from CLAUDE.md + RECKONER into one authoritative list. No purple gradients. No `outline: none` without replacement. No Inter/Roboto/Arial. No arbitrary colors outside tokens. No re-implementing shadcn components.

**Verify:** Start new conversation, ask Claude to build a card component — output should follow all rules without being prompted.

### Phase 3: Skills (~1.5 hrs)

**Goal:** Two skills that orchestrate the MCP tools into guided workflows.

**Step 3.1: Create `design-system-enforcer` skill**

File: `~/.claude/skills/design-system-enforcer/SKILL.md`

Frontmatter:
```yaml
---
name: design-system-enforcer
description: >
  Use when building web components, pages, forms, or any UI element.
  Enforces component library usage, design tokens, accessibility, and production-readiness.
  Triggers on: "build a form", "create a page", "add a component", "implement this design",
  or any frontend implementation task.
---
```

Skill body — the orchestrated workflow:
1. **Pre-flight: Component grounding**
   - If shadcn MCP available -> query registry for relevant components before coding
   - If component exists in registry -> use it (install if not yet in project)
   - If component doesn't exist -> proceed with custom, note in output
2. **Pre-flight: Design token extraction** (conditional)
   - If Figma URL/selection provided -> call `get_design_context` + `get_variable_defs`
   - Map Figma variables to CSS custom properties
   - Scope to ONE frame (avoid token bloat)
   - If no Figma -> skip, use project's existing tokens or sensible defaults
3. **Build: Code generation**
   - Follow CLAUDE.md Frontend Production Standards
   - Follow FRONTEND_DESIGN_RECKONER.md for aesthetic direction
   - Use `cva` + `cn()` patterns
   - Mobile-first responsive
4. **Post-build: Accessibility verification**
   - Use Playwright to navigate to the rendered page
   - Run `browser_snapshot` to get accessibility tree
   - Check: all interactive elements have accessible names, focus is managed, semantic HTML used
   - If critical issues found -> fix automatically and re-verify
   - If moderate issues -> flag to user
5. **Post-build: Visual verification**
   - Take screenshot with Playwright at mobile (375px) and desktop (1280px) widths
   - Present to user for visual sign-off

**Step 3.2: Create `a11y-audit` skill**

File: `~/.claude/skills/a11y-audit/SKILL.md`

Frontmatter:
```yaml
---
name: a11y-audit
description: >
  Use when auditing a frontend for accessibility, after completing UI work,
  or when user asks to check accessibility. Works on any running localhost URL.
---
```

Skill body:
1. Confirm target URL (default: localhost:3000)
2. Navigate with Playwright
3. Run `browser_snapshot` -> parse accessibility tree
4. Check against WCAG 2.2 AA criteria:
   - All images have alt text
   - All form inputs have labels
   - All interactive elements are keyboard-accessible
   - Color contrast (instruct to evaluate visible elements)
   - Focus management (tab through page)
   - Heading hierarchy (h1 -> h2 -> h3, no skips)
5. Run across 3 viewport widths: 375px, 768px, 1280px
6. Group findings by severity: Critical -> Serious -> Moderate
7. Auto-fix critical/serious if possible; present moderate to user
8. Re-run verification after fixes

### Phase 4: Validation & Tuning (~30 min)

**Goal:** End-to-end test that proves the system works together.

**Step 4.1: Component test**
- Start a fresh Next.js project (or any framework)
- Ask Claude Code: "Build a pricing page with 3 tiers"
- Expected behavior:
  - design-system-enforcer skill triggers
  - Queries shadcn MCP for Card, Button, Badge components
  - Follows CLAUDE.md production standards (cva, cn(), mobile-first)
  - Follows RECKONER aesthetic guidance (no AI slop)
  - Takes screenshot at mobile + desktop
  - Runs a11y check

**Step 4.2: Figma test** (if Figma token configured)
- Provide a Figma frame URL
- Ask Claude Code: "Implement this design"
- Expected: extracts tokens, maps to CSS vars, uses shadcn components

**Step 4.3: Standalone a11y test**
- Run dev server on any existing project
- Ask Claude Code: "Run an accessibility audit on localhost:3000"
- Expected: a11y-audit skill triggers, returns structured findings

**Step 4.4: Iterate on skill instructions**
- Based on test results, refine skill SKILL.md wording
- Common tuning: trigger descriptions, tool ordering, edge case handling

---

## Final Outputs Checklist

After all phases are complete, verify each item:

| # | Output | How to Verify | Status |
|---|--------|---------------|--------|
| 1 | shadcn MCP installed and responding | Ask "What props does shadcn Dialog accept?" -> structured response from MCP | [x] SHIPPED |
| 2 | Figma MCP installed and responding | Provide Figma URL -> returns design context | [x] SHIPPED |
| 3 | Playwright a11y working | `browser_snapshot` on any URL -> returns accessibility tree | [x] SHIPPED |
| 4 | CLAUDE.md has Frontend Production Standards | Read file, section exists with all 6 sub-rules | [x] SHIPPED |
| 5 | `design-system-enforcer` skill exists and triggers | Say "build a login form" -> skill activates, queries shadcn, checks a11y | [x] SHIPPED (workflow verified, auto-trigger needs new-session test) |
| 6 | `a11y-audit` skill exists and triggers | Say "audit accessibility on localhost:3000" -> skill activates, returns findings | [x] SHIPPED (full 3-pass audit verified) |
| 7 | No AI slop in output | Build any UI -> distinctive aesthetic, no purple gradients, no Inter font | [x] Validated (pricing page uses Geist font, no purple) |
| 8 | Production-ready code patterns | Generated code uses cva, cn(), mobile-first, no layout animations | [x] Validated (pricing page uses cn(), mobile-first, shadcn components) |
| 9 | Accessibility enforced | Generated UI has proper ARIA, focus states, contrast, semantic HTML | [x] Validated (full 3-pass a11y audit passed) |
| 10 | Figma-to-code works (if configured) | Figma URL -> code that uses project components + extracted tokens | [x] SHIPPED |

---

## What We're NOT Doing (and Why)

| Skipped Item | Why It's Fine |
|-------------|---------------|
| Accessibility MCP server | Playwright's `browser_snapshot` + skill instructions achieve 90% of axe-core. No clone/build/maintain burden. |
| ScreenshotOne MCP | Playwright `browser_take_screenshot` is already installed. Free, local, no API key. |
| `frontend-production` wrapper skill | Production rules in CLAUDE.md are always-on. A skill must be triggered — strictly inferior for enforcement. |
| `figma-to-code` separate skill | Merged into design-system-enforcer's conditional Figma path. One skill, not two. |
| PostToolUse hook | Shell hooks can only echo text, can't run axe. Skill workflow already includes a11y step. Hook adds noise. |
| RECKONER rewrite | It's already excellent for aesthetics. MCP orchestration belongs in skills, not a design guide. |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| shadcn MCP not available for user's framework | Skill degrades gracefully: "shadcn MCP unavailable, proceeding with CLAUDE.md rules only" |
| Figma token not configured | Skill skips Figma steps entirely, works in freeform mode |
| Token bloat from Figma | Skill instruction: "Scope to ONE frame. Use `get_variable_defs` not raw CSS dumps." |
| Skill trigger too broad/narrow | Phase 4 tuning — adjust description wording based on real trigger behavior |
| Playwright a11y less thorough than axe-core | Acceptable trade-off. If deeper a11y needed later, can add `axe-playwright` npm package to projects. |
