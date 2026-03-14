# Task Run Results

**Run ID:** trun_4719934bf63647789e01dfaa8f737733
**Status:** ✅ completed
**Processor:** ultra-fast
**Created:** 2026-03-13T03:01:13.833115Z
**Modified:** 2026-03-13T03:04:26.785880Z

## Output

# Mastering Spec-Driven Development: A Strategic Guide to Claude Code Interview Skills

## Executive Summary

The default behavior of AI coding agents is "eager compliance"—diving straight into implementation based on surface-level prompts and unstated assumptions. To build robust, production-ready features, developers must flip this script using spec-driven development and the `AskUserQuestion` tool. 

By forcing Claude into a structured, multi-round interview phase before any code is written, developers can surface hidden architectural edge cases, clarify tradeoffs, and generate a binding specification document. This guide synthesizes best practices from top open-source implementations to provide a comprehensive framework for building interview skills, managing tool constraints, and orchestrating seamless handoffs between discovery and implementation.

## 1. AskUserQuestion: The Technical Specification

The `AskUserQuestion` tool is the foundational mechanism for interactive spec-driven development. When Claude needs more direction on a task with multiple valid approaches, it calls the AskUserQuestion tool [1]. 

### 1.1 Tool Schema and Parameter Constraints
To utilize this capability in custom workflows, you must explicitly configure it. If you specify a tools array, include AskUserQuestion for this to work [1]. While the exact schema enforces strict limits to ensure UI stability, the core parameters include:
* **Questions Array**: A batch of questions to present to the user. Best practices dictate limiting this to 1–4 questions per call to prevent UI overflow.
* **Options Array**: Multiple-choice answers for each question (typically 2–4 options), alongside a free-text "Other" fallback.
* **PreviewFormat**: Optional formatting directives (like markdown or HTML) to render visual mockups alongside choices.

### 1.2 Return Format and Permission Handling
When the user responds, the answers are mapped back to the tool consumer. The agent SDK processes these responses through a permission wrapper (e.g., `PermissionResultAllow`), which updates the input payload with the user's explicit selections. This ensures that the agent's subsequent context window contains a structured, immutable record of the user's decisions.

## 2. The 10-Round Interview Methodology

Surface-level Q&A fails to uncover the "unknown unknowns" of a codebase. A robust interview skill must explicitly forbid obvious questions and mandate a deep, iterative probing process.

### 2.1 The 5-Phase Socratic Template
To achieve architectural depth, structure your interview prompts using a phased approach:
1. **Explore**: Read the codebase and understand the broad context.
2. **Deepen**: Ask about usage scenarios, target audiences, and core pain points.
3. **Validate**: Propose edge cases and ask how the system should handle failures.
4. **Prioritize**: Force tradeoffs (e.g., speed vs. consistency, memory vs. compute).
5. **Gate**: Summarize the findings and require explicit user approval before proceeding.

### 2.2 Avoiding the "Obvious Question" Trap
Standard prompts often result in trivial questions (e.g., "What color should the button be?"). To counter this, your system prompt must explicitly instruct the agent to avoid obvious questions and instead focus on hidden assumptions and constraints. 

### 2.3 Completion Criteria
An interview should not end arbitrarily. Define clear completion criteria, such as filling out a specific "Risk Register" or reaching a state where all acceptance criteria are unambiguous. Only then should the agent transition to writing the spec.

## 3. Analysis of Best-in-Class Open Source Skills

The open-source community has pioneered several highly effective patterns for Claude Code interviews. You can learn how to build Claude Code skills that interview users before implementing features by studying these repositories [2].

### 3.1 Neonwatty's `claude-skills` Repository
Jeremy Watt's repository provides reusable skills for Claude Code that leverage interactive questioning [3]. Key implementations include:
* **`feature-interview`**: Conducts deep Q&A about requirements, then writes an implementation plan [3].
* **`bug-interview`**: Performs systematic bug diagnosis and writes an investigation plan before touching code [3].
* **`think-through`**: Facilitates Socratic exploration of technical ideas (apps, products, tools) to vet concepts before development [3].

### 3.2 Thariq's Interview Command Gist
For rapid, iterative spec writing, Thariq's gist offers a concise, aggressive prompting strategy. The core instruction commands the agent to: "Read this plan file $1 and interview me in detail using the AskUserQuestionTool about literally anything: technical implementation, UI & UX, concerns, tradeoffs, etc. but make sure the questions are not obvious. Be very in-depth and continue interviewing me continually until it's complete, then write the spec to the file." [4]

### 3.3 Comparative Analysis of Interview Patterns

| Approach | Primary Goal | Gating Mechanism | Best Use Case |
| :--- | :--- | :--- | :--- |
| **Neonwatty (`claude-skills`)** | Reusable, multi-phase discovery | Explicit approval before writing | Complex feature architecture & bug diagnosis |
| **Thariq (Gist)** | Rapid, iterative spec writing | Continuous loop until "complete" | Quick task-level specs and plan refinement |

*Takeaway: Use Neonwatty's structured approach for heavy architectural lifting, and Thariq's continuous loop for rapid, ad-hoc planning.*

## 4. The Spec-Based Development Workflow

The ultimate goal of the interview is to produce a binding specification document that serves as a contract for the implementation phase.

### 4.1 The Handoff Mechanics
The workflow follows a strict sequence: **Interview → Spec Document → New Session → Implementation**. 
Once the interview concludes, the agent writes a `spec.md` file. Crucially, the current session should then be terminated. A fresh session is started, primed *only* with the newly minted spec. This prevents the implementation agent from being confused by the sprawling, conversational context of the interview phase.

### 4.2 Structuring the Spec Output
A high-quality spec generated from an interview should include:
* **Goals & Non-Goals**: What is being built, and explicitly what is *out* of scope.
* **Context & Assumptions**: Decisions made during the interview.
* **Acceptance Criteria**: Testable conditions for success.
* **Implementation Steps**: A step-by-step technical plan.

## 5. Plan Mode vs. Custom Skills

Developers must choose between using Claude Code's native Plan Mode or building custom `.claude/skills/SKILL.md` files.

### 5.1 Strategic Tradeoffs

| Feature | Plan Mode | Custom Skills (`SKILL.md`) |
| :--- | :--- | :--- |
| **Setup & Overhead** | Zero setup; built into the CLI. | Requires writing and maintaining markdown files. |
| **Control & Flexibility** | Limited to general planning behaviors. | Total control over interview phases, constraints, and output formats. |
| **Repeatability** | Ad-hoc; varies by session. | Highly repeatable; enforces team-wide standards. |

*Takeaway: Use Plan Mode for quick, low-stakes clarifications. Invest in Custom Skills for critical workflows like bug diagnosis or major feature planning.*

## 6. Advanced Patterns and Chaining

To maximize the value of the Agent SDK—which allows you to give Claude a task and let the SDK run the loop with built-in file, shell, and web tools [5] —you can implement advanced orchestration patterns.

### 6.1 Persistent Context via CLAUDE.md
Interview outputs are ephemeral if not anchored. Advanced skills use the final round of the interview to auto-generate updates to the project's `CLAUDE.md` file, ensuring that architectural decisions persist across all future developer sessions.

### 6.2 Skill Chaining
Skills can be chained together for end-to-end automation. For example, a debugging workflow can start with `bug-interview` to gather reproduction steps, automatically trigger a `reproduce` skill to verify the error in the shell, and finally hand off to a `fix` skill to implement the patch.

## 7. Anti-Patterns and Fatigue Management

When building interview skills, avoid these common pitfalls:
* **The "Shallow Loop"**: Allowing the agent to stop after 1-2 questions. You must explicitly prompt for a minimum number of rounds or specific criteria to prevent premature implementation.
* **User Fatigue**: Asking 10 questions in a single prompt overwhelms the user. Batch questions logically (e.g., 2-3 at a time) and use progressive summarization to show the user what has been decided so far.
* **The Eager Implementer**: Failing to implement a hard "Gate." If the agent is allowed to write code before the user explicitly approves the final spec, the entire purpose of the interview is defeated. Always require a final `AskUserQuestion` confirmation before executing file writes.

## References

1. *Handle approvals and user input - Claude API Docs*. https://platform.claude.com/docs/en/agent-sdk/user-input
2. *Claude Code Skills Tutorial: AskUserQuestion for Better Prompts*. https://neonwatty.com/posts/interview-skills-claude-code/
3. *Fetched web page*. https://github.com/neonwatty/claude-skills
4. *Fetched web page*. https://gist.github.com/robzolkos/40b70ed2dd045603149c6b3eed4649ad
5. *Fetched web page*. https://docs.anthropic.com
