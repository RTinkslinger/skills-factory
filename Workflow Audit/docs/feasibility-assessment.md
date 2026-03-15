# Feasibility Assessment: QMD + CC Workflow Enrichment

**Date:** 2026-03-14
**Status:** Validated — all prerequisites met

---

## 1. System Requirements

| Requirement | Needed | Actual | Status |
|-------------|--------|--------|--------|
| Node.js | >= 22 | v24.12.0 | Pass |
| npm | any | 11.6.2 | Pass |
| Disk space | ~5GB (models + index) | 79GB free | Pass |
| RAM | ~2GB for models | 8GB (Apple Silicon unified) | Tight but viable |
| SQLite | Homebrew version | macOS built-in + brew available | Pass |

### RAM Considerations

QMD uses three local GGUF models via node-llama-cpp:

| Model | Purpose | Size in memory |
|-------|---------|----------------|
| embeddinggemma-300M-Q8_0 | Vector embeddings | ~300MB |
| qwen3-reranker-0.6b-q8_0 | Re-ranking search results | ~640MB |
| qmd-query-expansion-1.7B-q4_k_m | Query expansion | ~1.1GB |

**CLI mode** (recommended for our use): Models load/unload per-command. Peak usage ~1.5GB during `qmd query` (embedding + reranker loaded together). Safe on 8GB.

**MCP daemon mode**: Keeps models pinned in VRAM. ~2GB persistent allocation. Viable but tight on 8GB — would compete with Claude Code itself. Recommend CLI mode for Phase 1, evaluate MCP daemon after measuring real-world impact.

---

## 2. Data Inventory

### Directly Indexable (Markdown)

| Source | Location | Files | Lines | Notes |
|--------|----------|-------|-------|-------|
| Memory files | `~/.claude/projects/*/memory/*.md` | 19 | ~1,166 | User prefs, feedback, project context |
| Global CLAUDE.md | `~/.claude/CLAUDE.md` | 1 | ~250 | Operating principles, code quality rules |
| Project CLAUDE.md | Various project roots | 10+ | ~800+ | Per-project protocols, constraints |
| TRACES.md | CASH Build System projects | 4 | Template state | Will grow with usage |
| LEARNINGS.md | CASH Build System projects | 4 | Template state | Will grow with usage |
| Hook scripts | `.claude/hooks/` across 4 projects | 6 | ~200 | Enforcement automation |
| Skill files | Skills Factory subdirectories | ~10 | ~2,000+ | Skill definitions and methodology |
| CASH Build System docs | Skills Factory/Cash Build System/ | 4 | ~1,500 | Setup skill, version history, plans |
| Sync state files | `.claude/sync/` across 4 projects | ~12 | ~100 | Cross-project coordination |

**Subtotal: ~50+ files, ~6,000+ lines — indexable as-is with zero preprocessing.**

### Requires Preprocessing (JSONL → Markdown)

| Source | Location | Volume | Entries | Richness |
|--------|----------|--------|---------|----------|
| Conversation logs | `~/.claude/projects/*/*.jsonl` | 163MB | 113 sessions | Full tool usage, errors, decisions |
| Subagent logs | `~/.claude/projects/*/subagents/*.jsonl` | 53MB | 227 sessions | Parallel work patterns |
| history.jsonl | `~/.claude/history.jsonl` | 522KB | 1,707 prompts | User intent, project distribution |
| Sync inbox | `.claude/sync/inbox.jsonl` | ~2KB | ~13 entries | Cross-project messages |

**Subtotal: ~216MB raw JSONL — needs conversion pipeline.**

### Conversation JSONL Structure (from analysis)

Each conversation JSONL contains these entry types:

| Type | Content | Audit Value |
|------|---------|-------------|
| `user` | User prompts with timestamp, project, permission mode | **High** — shows intent, frustration, patterns |
| `assistant` | Claude responses with requestId, session context | **Medium** — shows what was attempted |
| `progress` | Tool use events (tool name, args, results) | **High** — shows tool patterns, failures |
| `system` | System messages, context loading | **Low** — mostly plumbing |
| `file-history-snapshot` | File state snapshots | **Medium** — shows what changed |
| `last-prompt` | Session end marker | **Low** — metadata only |

### history.jsonl Structure

Each entry: `{display, pastedContents, timestamp, project, sessionId}`
- `display`: The exact user prompt text
- `project`: Full path to working directory
- `timestamp`: Unix ms timestamp
- `sessionId`: Links to conversation JSONL filename

### Distribution of Work Across Projects

| Project | Sessions | Notes |
|---------|----------|-------|
| /Users/Aakash (home) | 454 | General tasks, system setup |
| Aakash AI CoS CC ADK | 286 | AI Chief of Staff development |
| docsend-deck-extractor | 135 | Document extraction tool |
| Flight Mode | 117 | Offline resilience system |
| openclaw-setup | 106 | Legal/contract tool |
| pdfbot | 105 | PDF processing |
| Claude Projects (root) | 77 | Cross-project work |
| CC - CAI sync | 73 | Cross-sync system |
| Cash Build System | 65 | Build system development |
| Gmail MCP | 61 | Email integration |
| Skills Factory | 48+ | Skill development |

---

## 3. QMD Capabilities Mapped to Our Needs

| Our Need | QMD Feature | Fit |
|----------|-------------|-----|
| Find patterns across conversation history | `qmd query` (hybrid search) | Excellent |
| Search for specific errors or frustrations | `qmd search` (BM25 keyword) | Excellent |
| Find semantically similar problems | `qmd vsearch` (vector search) | Excellent |
| Retrieve full context for a finding | `qmd get` / `qmd multi-get` | Excellent |
| Programmatic access from skills | CLI `--json` output or MCP server | Excellent |
| Add project-level context to results | `qmd context add` (hierarchical) | Excellent |
| Incremental updates as new data arrives | `qmd update` + `qmd embed` | Good |
| Filter by project or data type | Collections + `--collection` flag | Good |

### QMD Integration Modes

1. **CLI mode** (recommended Phase 1): Skill shells out to `qmd search/query --json`. Simple, no daemon.
2. **MCP server** (Phase 2+): Add to `.claude/settings.json`. Claude Code gets `query`, `get`, `multi_get`, `status` tools natively. Richer but RAM-heavy.

---

## 4. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| 8GB RAM pressure with MCP daemon | CC slowdown | Medium | Use CLI mode; MCP daemon optional |
| JSONL preprocessing loses nuance | Weaker audit insights | Low | Preserve raw user prompts verbatim; structured extraction captures key signals |
| Embedding 216MB takes long time | Slow initial setup | Medium | Embed in batches by collection; background process |
| qmd models download fails | Blocked setup | Low | Models auto-cached; retry-safe |
| Index grows stale | Outdated audit results | Medium | Hook-triggered or cron re-index before audit |
| Conversation JSONLs change every session | Index drift | Low | Incremental `qmd update` only processes changed files |

---

## 5. Estimated Resource Usage

| Operation | Time | Disk | RAM |
|-----------|------|------|-----|
| Install qmd + model download | 5-10 min | ~2.5GB | Minimal |
| Index all markdown files | < 1 min | ~5MB | Minimal |
| Preprocess 113 conversation JSONLs | 2-5 min | ~30-50MB output | Minimal |
| Embed all documents | 10-20 min | ~500MB index | ~1.5GB peak |
| Single `qmd query` | 2-5 sec | None | ~1.5GB peak |
| Full workflow audit run | 3-5 min | ~1MB report | ~1.5GB peak |

---

## 6. Conclusion

**Verdict: Fully feasible. No blockers.**

The main engineering effort is the JSONL preprocessing pipeline (~216MB of conversation data → searchable markdown). Everything else is configuration and collection setup. QMD's hybrid search (BM25 + vector + reranking) is an excellent fit for the kind of cross-cutting queries a workflow audit needs — "what patterns of frustration exist?", "which tools fail most often?", "what feedback has been given repeatedly?"

The 8GB RAM constraint is manageable with CLI mode and deliberate about MCP daemon usage.
