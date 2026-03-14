# Frontend Skill & MCP System Reference

> A complete reference for the Claude Code frontend infrastructure that eliminates component hallucination, enforces design systems, and verifies accessibility across any project.

---

## System Architecture

```
                          ALWAYS LOADED (via CLAUDE.md)
                    +---------------------------------+
                    | Frontend Design Guidelines      |
                    | Frontend Production Standards    |
                    |   (6 rules, always enforced)     |
                    +---------------------------------+
                                  |
                    +-------------+-------------+
                    |                           |
              TRIGGERED SKILLS              MCP SERVERS
          (invoked per-task)           (live data sources)
        +------------------+       +-------------------+
        | design-system-   |<----->| shadcn MCP        |
        | enforcer         |       | (component API)   |
        +------------------+       +-------------------+
        | a11y-audit       |<----->| Figma MCP         |
        +------------------+       | (design tokens)   |
                |                  +-------------------+
                |                  | Playwright         |
                +----------------->| (a11y tree,        |
                                   |  screenshots,      |
                                   |  keyboard test)    |
                                   +-------------------+
                                         |
                  +----------------------+
                  |
          AESTHETIC LAYER (reference doc)
        +---------------------------+
        | FRONTEND_DESIGN_RECKONER  |
        | (390 lines, design voice) |
        +---------------------------+
```

---

## What's Installed & Where

### MCP Servers (in `~/.mcp.json`)

| Server | Command | Purpose |
|--------|---------|---------|
| **shadcn** | `npx shadcn@latest mcp` | Live component registry queries. Prevents hallucinating props/variants. |
| **figma** | `npx figma-developer-mcp --stdio` | Extracts design data from Figma files. Requires `FIGMA_API_KEY` env var. |
| **Playwright** | Global plugin (`~/.claude/plugins/`) | Browser automation: accessibility tree, screenshots, keyboard testing. |

### Skills (in `~/.claude/skills/`)

| Skill | File | Trigger Phrases |
|-------|------|-----------------|
| **design-system-enforcer** | `~/.claude/skills/design-system-enforcer/SKILL.md` | "build a form", "create a page", "add a component", "implement this design", "build a login form", "create a card", "add a modal", "build a table", "create a nav", any Figma URL |
| **a11y-audit** | `~/.claude/skills/a11y-audit/SKILL.md` | "check accessibility", "audit a11y", "WCAG audit", "WCAG 2.2", "screen reader test", "check touch targets", "keyboard navigation test" |

### Always-On Rules (in `~/.claude/CLAUDE.md`)

| Section | What It Enforces |
|---------|------------------|
| **Frontend Design Guidelines** | No AI slop, no Inter/Roboto/Arial, distinctive typography, dominant color palettes, purposeful motion |
| **Frontend Production Standards** | 6 sub-sections covering component library, styling patterns, responsive, performance, accessibility, anti-patterns |

### Reference Doc (in `~/.claude/`)

| File | Purpose |
|------|---------|
| **FRONTEND_DESIGN_RECKONER.md** | 390-line aesthetic guide. Design voice, typography rules, color theory, motion principles, layout patterns. Referenced by design-system-enforcer skill. |

---

## How the System Works Together

### Scenario 1: "Build a pricing page with 3 tiers"

1. **design-system-enforcer** triggers (matches "build a...page")
2. **Pre-flight: Component grounding**
   - Queries shadcn MCP: `view_items_in_registries` for Card, Button, Badge
   - Gets install command: `get_add_command_for_items` if missing
3. **Build phase**
   - Uses shadcn Card/Button/Badge (not custom components)
   - Follows CLAUDE.md production standards: `cn()`, mobile-first, CSS vars
   - Follows RECKONER aesthetic direction: distinctive fonts, no purple gradients
4. **Post-build: A11y verification**
   - Playwright `browser_navigate` + `browser_snapshot` for accessibility tree
   - Checks: landmarks, heading hierarchy, button names, label associations
   - Auto-fixes critical issues (e.g., missing aria-labels)
5. **Post-build: Visual verification**
   - Screenshots at 375px (mobile) and 1280px (desktop)
   - Presents both to user for sign-off

### Scenario 2: "Implement this Figma design" (with URL)

1. **design-system-enforcer** triggers (matches Figma URL)
2. **Figma token extraction**
   - `mcp__figma__get_figma_data` with file key + node ID from URL
   - Extracts: colors, typography, spacing, border styles from the frame
   - Maps to CSS custom properties (e.g., `--figma-bg-cream: #FBFBF5`)
3. **Component grounding**
   - Analyzes Figma structure, identifies matching shadcn components
   - Queries registry to verify they exist
4. **Build with extracted tokens**
   - All colors reference CSS vars, not hardcoded hex
   - Shadcn components themed with Figma tokens
5. **A11y + Visual verification** (same as Scenario 1)

### Scenario 3: "Run an accessibility audit on localhost:3000"

1. **a11y-audit** triggers (matches "accessibility audit")
2. **Pass 1: Structure**
   - `browser_navigate` to URL
   - `browser_snapshot` for accessibility tree
   - Checks: landmarks (banner, nav, main), headings (h1 first, sequential), interactive names, form labels, image alt text
3. **Pass 2: Interaction**
   - `browser_press_key` Tab repeatedly
   - `browser_snapshot` after each tab to track focus position
   - Checks: focus visibility, focus order, focus traps, keyboard operability
4. **Pass 3: Visual**
   - `browser_resize` to 375px, 768px, 1280px
   - `browser_take_screenshot` at each width
   - `browser_evaluate` to measure touch targets (>= 44x44px)
   - Checks: text reflow, contrast, touch target sizes
5. **Report** grouped by severity: Critical > Serious > Moderate
6. **Auto-fix** critical and serious issues, re-verify with `browser_snapshot`

---

## Verification Checklist for New Projects

Run these checks to confirm the full system is working in any new frontend project.

### 1. shadcn MCP is responding

**Test:** Ask Claude: "What variants does the shadcn Button have?"

**Expected:** Claude queries `mcp__shadcn__view_items_in_registries` and returns actual registry data (variant names, file count, dependencies), NOT hallucinated props.

**Failure mode:** If Claude describes Button props from memory without calling the MCP, the shadcn server isn't connected. Check `~/.mcp.json` has the shadcn entry.

### 2. Figma MCP is responding

**Test:** Provide a Figma file URL (format: `figma.com/design/<fileKey>/...`) and ask Claude to describe the design.

**Expected:** Claude calls `mcp__figma__get_figma_data` and returns structured node data (frames, text content, fills, layouts), NOT a guess based on the URL.

**Failure mode:**
- `403 Forbidden` = FIGMA_API_KEY is invalid or expired. Regenerate at figma.com/developers.
- `404 Not Found` = wrong file key format. Must be from `/design/` or `/file/` URLs, NOT `/community/` URLs (those need to be duplicated to your drafts first).
- Connection error = figma-developer-mcp not installed. Run `npx figma-developer-mcp --stdio` manually to test.

### 3. Playwright a11y tree works

**Test:** Ask Claude to navigate to any URL and take an accessibility snapshot.

**Expected:** `browser_snapshot` returns a YAML tree with roles (`banner`, `navigation`, `main`, `heading`, `button`, `link`), accessible names, and hierarchy.

**Failure mode:** If Playwright tools aren't available, the plugin isn't installed. Check `~/.claude/plugins/` for the playwright directory.

### 4. design-system-enforcer triggers

**Test:** In a new Claude Code session inside a frontend project, say: "Build a login form".

**Expected:** Claude announces it's using the design-system-enforcer skill, then:
- Queries shadcn for Form, Input, Label, Button components
- Uses `cn()` and mobile-first responsive patterns
- Runs `browser_snapshot` for a11y verification after building
- Takes screenshots at 375px + 1280px

**Failure mode:** If the skill doesn't trigger, check `~/.claude/skills/design-system-enforcer/SKILL.md` exists and has correct frontmatter.

### 5. a11y-audit triggers

**Test:** With a dev server running, say: "Run an accessibility audit on localhost:3000".

**Expected:** Claude announces it's using the a11y-audit skill, then runs all 3 passes (structure, interaction, visual) and produces a severity-grouped report.

**Failure mode:** Same as #4 — check skill file exists at `~/.claude/skills/a11y-audit/SKILL.md`.

### 6. Production standards enforced without prompting

**Test:** Ask Claude to build any component (e.g., "Add a card component"). Do NOT mention production rules.

**Expected output follows all of these:**

| Standard | What to Look For |
|----------|-----------------|
| shadcn components | Imports from `@/components/ui/`, not custom-built equivalents |
| `cn()` helper | Conditional classes use `cn()`, not template literals |
| Mobile-first | Base styles are mobile, breakpoints layer up: `sm:`, `md:`, `lg:` |
| CSS vars for tokens | Colors use `var(--...)` or Tailwind tokens, not hardcoded hex |
| Transform-only animation | Hover/transition effects use `transform`/`opacity`, not `width`/`height` |
| Semantic HTML | Uses `<button>`, `<a>`, `<header>`, `<main>`, `<nav>` — not `<div onClick>` |
| `key` props | List-rendered elements have `key` attributes |
| Focus states | Interactive elements have `focus-visible:` styles |
| Touch targets | Buttons/links are >= 44x44px |
| No banned fonts | Uses project font or distinctive choice, never Inter/Roboto/Arial |

---

## MCP Tool Quick Reference

### shadcn MCP Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `mcp__shadcn__view_items_in_registries` | View component details (name, type, files) | Before building any UI element |
| `mcp__shadcn__get_item_examples_from_registries` | Get usage examples | When unsure how to use a component |
| `mcp__shadcn__get_add_command_for_items` | Get CLI install command | When component isn't in project yet |
| `mcp__shadcn__search_items_in_registries` | Search by keyword | When unsure which component to use |
| `mcp__shadcn__list_items_in_registries` | List all available items | For discovery |
| `mcp__shadcn__get_project_registries` | Check project's registries | To see what's configured |
| `mcp__shadcn__get_audit_checklist` | Audit component usage | For reviewing existing code |

### Figma MCP Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `mcp__figma__get_figma_data` | Get file/node structure, styles, text, fills, layouts | Extracting design tokens and understanding layout |
| `mcp__figma__download_figma_images` | Download SVG/PNG assets from a file | When design has icons or images to export |

**Figma URL anatomy:**
```
https://www.figma.com/design/dokFO8euCt7EqU6BEr4231/My-Project?node-id=0-1
                              ^^^^^^^^^^^^^^^^^^^^^^^^                  ^^^
                              fileKey                                   nodeId (use "0-1" format)
```

**Important:** Community URLs (`figma.com/community/file/...`) don't work with the API. Duplicate the file to your drafts first to get a `/design/` URL.

### Playwright Tools (for a11y)

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `browser_navigate` | Load a URL | First step in any verification |
| `browser_snapshot` | Get accessibility tree (YAML) | **The primary a11y tool** — shows what screen readers see |
| `browser_press_key` | Press keyboard keys (Tab, Enter, Escape) | Keyboard navigation testing |
| `browser_resize` | Set viewport dimensions | Testing at 375px, 768px, 1280px |
| `browser_take_screenshot` | Capture visual state | Visual verification, responsive checks |
| `browser_evaluate` | Run JS in page context | Measuring touch targets, checking computed styles |

---

## File Locations Summary

```
~/.mcp.json                                        # shadcn + Figma MCP server configs
~/.claude/CLAUDE.md                                # Frontend Design Guidelines + Production Standards
~/.claude/FRONTEND_DESIGN_RECKONER.md              # 390-line aesthetic reference
~/.claude/skills/design-system-enforcer/SKILL.md   # Component grounding + build + verify skill
~/.claude/skills/a11y-audit/SKILL.md               # 3-pass accessibility audit skill
~/.claude/plugins/.../playwright/                   # Browser automation plugin (global)
```

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Claude hallucsinates component props | shadcn MCP not connected | Verify `~/.mcp.json` has shadcn entry. Restart Claude Code. |
| Figma returns 403 | API key invalid/expired | Regenerate at figma.com/developers, update `FIGMA_API_KEY` in `~/.mcp.json` |
| Figma returns 404 | Wrong URL format | Use `/design/` or `/file/` URLs, not `/community/` URLs |
| Skill doesn't auto-trigger | Trigger phrase not matched | Say exact phrases from skill description, or invoke manually: "Use the design-system-enforcer skill" |
| `browser_snapshot` unavailable | Playwright plugin missing | Check `~/.claude/plugins/` for playwright directory |
| Code doesn't follow production rules | CLAUDE.md not loaded | Verify `~/.claude/CLAUDE.md` has "Frontend Production Standards" section |
| Ugly "AI slop" output | RECKONER not referenced | Verify `~/.claude/FRONTEND_DESIGN_RECKONER.md` exists and is referenced in CLAUDE.md |
| a11y audit misses issues | Only ran Pass 1 | Request "full WCAG audit" to get all 3 passes (structure + interaction + visual) |

---

## What This System Does NOT Do

| Gap | Why | Workaround |
|-----|-----|------------|
| Automated axe-core scanning | Would require a separate MCP server to build and maintain | Playwright `browser_snapshot` catches ~70% of issues. For deeper scanning, install `axe-playwright` in project and run via Bash. |
| Figma named variable extraction | `get_figma_data` returns fills/styles inline, not as named variables | Manually map extracted hex values to CSS custom properties (the skill guides this). |
| CI/CD accessibility gates | Outside Claude Code's scope | Use the a11y-audit skill findings to set up axe-core in your CI pipeline. |
| Cross-browser testing | Playwright runs Chromium only in MCP mode | Audit covers structure + keyboard which are browser-agnostic. Visual issues may vary in Safari/Firefox. |
| Design-to-pixel-perfect code | Figma extraction is structural, not visual | The system extracts tokens and structure. Fine-tuning spacing/alignment is manual. |

---

*Built: March 2026 | Skills Factory > Frontend Skills & MCPs*
*Validated: Pricing page test, Figma-to-code team page, full a11y audit with auto-fixes*
