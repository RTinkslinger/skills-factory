# From Guesswork to Guided Frontends: Wiring Claude Code with MCP, Skills, and AI-Friendly UI Systems

**Deep Research Report — March 6, 2026**
**Sources: 3,195 considered, 1,065 read (ultra tier)**

---

## Executive Summary

The gap between generic AI-generated UI and production-grade frontend engineering is bridged by **context**. Claude Code's 200K context window and industry-leading SWE-bench performance make it a powerhouse for complex refactoring, but without explicit guardrails, it will hallucinate component props or invent outdated Tailwind patterns.

The strategic unlock is **Context-over-guessing**: connecting Claude Code to live UI sources via the Model Context Protocol (MCP) cuts hallucinations and enforces current APIs.

**Key Strategic Insights:**

- **Grounding via MCP is Non-Negotiable:** The official shadcn MCP server exposes up-to-date component props and install flows directly to Claude Code. Figma's official MCP returns React and Tailwind code alongside design variables via `get_design_context` and `get_variable_defs`.
- **Code Connect Ties Design to Truth:** Figma MCP paired with Code Connect pipes your actual repository component APIs into the AI's output, ensuring generated code reuses `src/components/ui` rather than raw HTML divs.
- **Accessibility is Machine-Enforceable:** An a11y MCP server (like `Duds/accessibility-mcp`) exposes `axe_core` and Lighthouse checks as tools to gate UI diffs before they are finalized.
- **Community Figma MCPs Offer Specialized Workflows:** While the official Figma MCP is best for codegen, community tools like `grab/cursor-talk-to-figma-mcp` provide full read/write operations via WebSockets, and `GLips/Figma-Context-MCP` simplifies the Figma API into LLM-parsable layouts.
- **Borrow from Competitors:** While Claude Code excels at terminal-first pipelines, teams should emulate Windsurf's reusable "Workflows" using Claude Skills, and port Cursor's scoped `.cursor/rules` into `CLAUDE.md` to enforce design system compliance.

---

## 0. Quick Wins (48 hours): Baseline Claude Code -> "Design-Informed"

Wire it to your design system and Figma context with two MCP servers and a guardrail skill, then gate the output with accessibility checks.

**Step-by-Step Setup:**

1. **Add the shadcn MCP:**
```bash
claude mcp add --transport http shadcn https://www.shadcn.io/api/mcp
# OR: pnpm dlx shadcn@latest mcp init --client claude
```

2. **Add the Figma MCP (Remote Server):**
```json
{
  "mcpServers": {
    "figma": {
      "command": "mcp-server-figma",
      "env": { "FIGMA_ACCESS_TOKEN": "figd_..." }
    }
  }
}
```

3. **Add the Accessibility MCP (axe-core + Lighthouse):**
```json
{
  "mcpServers": {
    "accessibility": {
      "command": "node",
      "args": ["/absolute/path/to/accessibility-mcp/dist/index.js"]
    }
  }
}
```

4. **Create a Guardrail Skill (`.claude/skills/frontend-guard/SKILL.md`):**
Define instructions that force Claude to use these tools: "Before coding: query shadcn for component API; call figma.get_variable_defs. After coding: call accessibility axe_audit on local URL; fix critical/serious before finish."

**Outcome:** Claude will now "ask" shadcn for current props and variants, align styles to Figma variables, and auto-run axe/Lighthouse checks before proposing a PR.

---

## 1. MCP Servers to Ground Frontend Work

| Server Name | Repository / URL | What it Exposes | Setup |
| :--- | :--- | :--- | :--- |
| **Figma MCP (Official)** | `figma/mcp-server-guide` | `get_design_context` (React+Tailwind), `get_variable_defs`, Code Connect context | Add `mcp-server-figma` with `FIGMA_ACCESS_TOKEN` |
| **Talk to Figma** | `grab/cursor-talk-to-figma-mcp` | Read/modify via plugin; rich tools (`create_text`, `get_reactions`) | `bunx cursor-talk-to-figma-mcp@latest` |
| **GLips Figma-Context** | `GLips/Figma-Context-MCP` | Simplified, LLM-parsable layout/style data | `npx -y figma-developer-mcp` |
| **shadcn UI MCP (v4)** | `Jpisnice/shadcn-ui-mcp-server` | v4 components, blocks, multi-framework (React, Svelte, Vue) | `npx @jpisnice/shadcn-ui-mcp-server --github-api-key...` |
| **Shadcn Official MCP** | `ui.shadcn.com/docs/mcp` | Registry browsing and installation via natural language | `pnpm dlx shadcn@latest mcp init --client claude` |
| **Accessibility MCP** | `Duds/accessibility-mcp` | `axe_audit`, `lighthouse_audit`, `wave_audit` | `node dist/index.js` |
| **ScreenshotOne MCP** | `screenshotone/mcp` | `render-website-screenshot` | `node build/index.js` with `SCREENSHOTONE_API_KEY` |
| **Storybook MCP** | `stefanoamorelli/storybook-mcp-server` | Component discovery and prop inspection from Storybook | Start server; connect via MCP |

**Strategic Takeaways:**

- Default to the official Figma server for codegen and variables. Add Code Connect to ensure the AI reuses `src/components/ui`.
- Use the `Jpisnice` shadcn MCP with a GitHub token for higher rate limits to explore component structures and demos.
- Run the Accessibility MCP post-build to return normalized violations with severity and DOM selectors, forcing Claude to fix them in a loop.

---

## 2. Claude Code Skills, Plugins, and Hooks

### The `frontend-design` Skill (Official Anthropic)
Anthropic provides an official `frontend-design` skill that forces Claude to avoid generic "AI slop" aesthetics.
- **Source:** `anthropics/claude-code/plugins/frontend-design/skills/frontend-design/SKILL.md`
- **Implementation:** Requires Claude to commit to a bold aesthetic direction (e.g., brutally minimal, neo-brutalist, soft/pastel) before writing code.
- **Action:** Clone this and embed your specific design token CSS and mobile-first breakpoints into the instructions.

### Creating a `design-system-enforcer` Skill
```yaml
---
name: design-system-enforcer
description: Use when building web components, pages, or forms. Enforces shadcn/ui, tokens, and WCAG AA.
allowed-tools: Read, Grep, WebFetch, shadcn, figma
disable-model-invocation: false
---
```
Instructions: "Before coding, use the shadcn tool to confirm component availability. If missing, install it. When a Figma URL is present, call `figma.get_variable_defs` and map tokens. After coding, run `axe_audit` and fix 'critical/serious' issues."

### Claude Code Hooks (v2.1+)
- **`PreToolUse`**: Prompt for confirmation on any `npm install` or log shadcn component installations.
- **`PostEdit`**: Run the accessibility MCP on touched routes and attach the summary to the message.

---

## 3. CLAUDE.md Rules That Produce Better UI

Based on high-performing community examples like `elite-frontend-ux` and Cursor rules:

**Objectives & Architecture:** "All UI uses shadcn/ui + Tailwind. Prefer composition over configuration props. Avoid dynamic class strings; always use `cva` and `tailwind-merge` via the `cn()` helper."

**Design System & Tokens:** "Use components from `src/components/ui`. Load tokens from `src/styles/tokens.css` (HSL vars). Never eyeball spacing or pick arbitrary colors. Use `--space-4` (16px) and `--font-size-base`."

**Accessibility (Non-Negotiable):** "Meet WCAG 2.2 AA. Color contrast must be >= 4.5:1 for text. Touch targets >= 44x44px. All interactive elements MUST have visible focus states (3:1 contrast). First rule of ARIA: Don't use ARIA if native HTML works."

**Responsive Design:** "Mobile-first approach with Tailwind breakpoints (`sm`: 640px, `md`: 768px, `lg`: 1024px). Base styles are mobile, layer up with breakpoints."

**Anti-Patterns to Reject:** "NEVER use purple/blue gradients on white (AI cliche). NEVER use `outline: none` without a focus replacement. NEVER animate layout properties (width, height); only animate `transform` and `opacity`."

### Porting Cursor Rules
Cursor's `.cursor/rules` can be ported to Claude Code using tools like `cursorrules-to-claudemd` (C2C). Use nested `.claude/skills/` directories to mimic Cursor's directory-specific rule application.

---

## 4. AI-Friendly UI Libraries

| Library | API Style | A11y | LLM-Friendly Traits |
| :--- | :--- | :--- | :--- |
| **shadcn/ui** | Open code + CLI | Built atop Radix | Consistent variants, copy-pasteable code, "AI-Ready" design |
| **Radix Primitives** | Headless | WAI-ARIA APG aligned | Predictable props, ARIA baked-in |
| **Ark UI** | Headless | A11y patterns | Cross-framework parity (React, Vue, Solid) |
| **Headless UI** | Headless | Solid for core widgets | Simple patterns |
| **MUI** | Styled system | A11y docs | Examples-rich, highly adopted |
| **Chakra UI** | Styled components | A11y docs | Clear props |

**Recommended Baseline Stack:**
Next.js (App Router) + Tailwind CSS + shadcn/ui (Radix) + `class-variance-authority` (cva) + `tailwind-merge`

- `tailwind-merge` efficiently merges classes without style conflicts
- `cva` provides type-safe UI variants
- Both prevent LLMs from generating conflicting CSS rules

---

## 5. Design-to-Code Pipelines

- **Figma MCP + Code Connect (Best Fidelity):** Most robust pipeline. Output is React + Tailwind. By prompting "Generate my Figma selection using components from src/components/ui", Code Connect ensures the AI uses your actual repo components.
- **Anima (Best for Bootstrapping):** 1.7m users, generates React/HTML/Tailwind, supports shadcn patterns. Bootstrap initial layout, then refactor with Claude Code.
- **v0 by Vercel (Best for Rapid Prototyping):** Generates high-quality UIs using Next.js, Tailwind, shadcn/ui. Excellent for scaffolding, pull into local env for Claude Code refinement.
- **TeleportHQ & Locofy:** Selective use for static sections; manual rework often required.

**Gotcha:** Naive Figma-to-code runs are brittle and token-heavy. In Q1 2026 testing, Figma MCP + Claude Code hit context limits (~17.6k tokens) and required manual selector constraints to fix viewport widths. Scope Figma captures to one frame at a time.

---

## 6. UX Knowledge Base

Package authoritative guidelines as first-class, queryable resources:

- **WCAG 2.2:** W3C standard for accessibility success criteria
- **WAI-ARIA APG:** Authoring Practices Guide for accessible widget patterns
- **MDN ARIA Roles:** Semantic definitions for document structure and widgets

**Operationalizing:**
1. Create `/docs/ux/` directory with `wcag-refs.md`, `aria-patterns.md`, `mobile-first.md`
2. Create `/docs/ux/rules.json` with schema `{ruleId, category, severity, rationale, check, fix}`
3. Build lightweight "UX-KB" MCP server with `get_guideline(ruleId)` and `get_pattern(name)`
4. Add to `CLAUDE.md`: "Before finalizing any interactive component, query the UX-KB for the relevant ARIA APG pattern and self-critique your implementation against it."

---

## 7. Competitive Landscape

| Capability | Cursor | Windsurf | Claude Code | Action |
| :--- | :--- | :--- | :--- | :--- |
| **Rules & Context** | `.cursor/rules` (scoped), `AGENTS.md` | Workflows + rules | `CLAUDE.md` + `.claude/skills` | Port key `.cursorrules` to `CLAUDE.md`. Use nested skills for directory-specific rules |
| **Live Preview** | Limited | Strong (hot reload, click-to-edit) | CLI first | Run dev server in background; use `ScreenshotOne` MCP or Playwright hooks for visual diffs |
| **Multi-Agent Flows** | 8-parallel agents | Cascade Flows | Subagents via Skills | Define subagent teams in `AGENTS.md` |
| **Figma Integration** | Plugins + MCP | MCP | Official MCP | Adopt Code Connect; enforce "use components" in prompts |

---

## 8. Implementation Playbook

```bash
# 1. Initialize
npx create-next-app@latest
npx shadcn@latest init
npm install class-variance-authority tailwind-merge

# 2. MCP Configuration (.mcp.json)
{
  "mcpServers": {
    "shadcn": { "command": "npx", "args": ["shadcn@latest", "mcp"] },
    "figma": { "command": "mcp-server-figma", "env": { "FIGMA_ACCESS_TOKEN": "${FIGMA_TOKEN}" } },
    "accessibility": { "command": "node", "args": ["./node_modules/accessibility-mcp/dist/index.js"] }
  }
}
```

**Example prompt:** "Generate a responsive card from the selected Figma frame using the shadcn Card component. Map colors to our `--accent` and `--muted` CSS variables. Once generated, run the accessibility MCP audit on localhost:3000 and fix any violations."

---

## 9. Evaluation & CI

- **Accessibility:** Run `jest-axe` on components and Lighthouse CI on pages. Target: 0 critical/serious axe violations; Lighthouse a11y >= 95.
- **Design-System Adherence:** Measure % of components imported from `src/components/ui`. Target: 0 hallucinated props.
- **Responsiveness:** Playwright visual regression testing across 5 breakpoints. Target: < 1% visual mismatch.

CI: GitHub Action with Storybook + Playwright + `axe-core`. If build fails, feed summary log back to Claude Code via `PostEdit` hook for autonomous fixes.

---

## 10. Risk Register

- **Token Bloat:** Scope Figma captures to one frame. Use `get_variable_defs` not raw CSS dumps.
- **Hallucinated Components:** Force shadcn MCP registry check before writing code.
- **Security/IP Leaks:** Never hardcode tokens in `.mcp.json`; use env vars. Restrict `allowed-tools` in skill frontmatter.
- **Accessibility Debt:** Block PR merges on serious/critical `axe-core` findings.

---

## Key References

1. Figma MCP Server Guide: https://github.com/figma/mcp-server-guide
2. shadcn MCP: https://ui.shadcn.com/docs/mcp
3. Accessibility MCP: https://github.com/Duds/accessibility-mcp
4. Talk to Figma: https://github.com/grab/cursor-talk-to-figma-mcp
5. GLips Figma-Context: https://github.com/GLips/Figma-Context-MCP
6. shadcn v4 MCP: https://github.com/Jpisnice/shadcn-ui-mcp-server
7. Official frontend-design skill: https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md
8. elite-frontend-ux rules: https://gist.github.com/majidmanzarpour/8b95e5e0e78d7eeacd3ee54606c7acc6
9. awesome-cursorrules: https://github.com/PatrickJS/awesome-cursorrules
10. ScreenshotOne MCP: https://github.com/screenshotone/mcp
11. Storybook MCP: https://github.com/stefanoamorelli/storybook-mcp-server
12. Code Connect: https://help.figma.com/hc/en-us/articles/23920389749655-Code-Connect
13. Anima Figma Plugin: https://www.figma.com/community/plugin/857346721138427857
14. v0 by Vercel: https://v0.app/docs/
15. WCAG 2.2: https://www.w3.org/TR/WCAG22/
16. WAI-ARIA APG: https://www.w3.org/WAI/ARIA/apg/
