# QMD Ready Reckoner

Quick reference for QMD (Query Markdown Documents) — local semantic search over markdown files.

## Installation

- **Package:** `@tobilu/qmd` v2.0.1
- **Binary:** `qmd` (via npm global)
- **Config:** `~/.config/qmd/index.yml`
- **Database:** `~/.cache/qmd/index.sqlite`
- **Models:** EmbeddingGemma 300M (embedding), Qwen3-Reranker 0.6B (reranking), qmd-query-expansion 1.7B (query expansion) — all GGUF, Metal-accelerated

## Core Commands

```bash
# Search
qmd search "your query"                    # hybrid search (FTS + vector + rerank)
qmd search "query" -c collection-name      # search specific collection
qmd search "query" --files                 # show file paths only

# Browse
qmd ls                                     # list all indexed documents
qmd ls collection-name                     # list docs in a collection
qmd get qmd://collection/path/to/file.md   # retrieve a document
qmd get "#abc123"                          # retrieve by docid

# Index
qmd index                                  # reindex all collections
qmd index -c collection-name               # reindex one collection

# Status
qmd status                                 # index health, collection info, model info
```

## Collection Management

```bash
qmd collection list                        # list all collections
qmd collection add /path/to/dir --name X   # add a collection
qmd collection remove name                 # remove a collection
qmd collection rename old new              # rename
qmd collection show name                   # show details
qmd collection include name                # include in default queries
qmd collection exclude name                # exclude from default queries
qmd collection update-cmd name 'cmd'       # set pre-index command
```

## Collection Config (YAML)

Source of truth: `~/.config/qmd/index.yml`

```yaml
collections:
  my-collection:
    path: /absolute/path/to/directory
    pattern: "**/*.md"              # glob pattern for files
    ignore: ["node_modules/**"]     # optional exclusions
    includeByDefault: true          # searched by default?
    update: "git pull"              # optional pre-index command
    context:
      "": "Top-level description"
      "/subpath": "More specific context for files under subpath"
```

## Architecture

```
~/.config/qmd/index.yml (YAML — source of truth)
        │
        ▼ syncConfigToDb()
~/.cache/qmd/index.sqlite
        ├── store_collections     (collection definitions)
        ├── documents             (file records, keyed by collection+path)
        ├── content               (file bodies, keyed by hash — deduplicated)
        └── content_vectors       (embeddings, keyed by hash+seq — deduplicated)
```

### Key internals

- **Document identity:** `UNIQUE(collection, path)` — same file in two collections = two document rows
- **Content dedup:** Content and embeddings are keyed by file hash. If the same file is in multiple collections, content and vectors are stored once.
- **Search pipeline:** FTS → vector search → RRF (Reciprocal Rank Fusion) → reranker → results
- **Cross-collection dedup:** RRF merges results by file path — same file from different collections becomes one result with blended score
- **Context field:** Metadata-only. Returned with results but has zero impact on ranking, indexing, or embedding. Useful for downstream consumers (e.g., LLM reading results), not for QMD's search engine.

## Virtual URIs

```
qmd://collection-name/path/to/file.md
```

Abstracts filesystem paths for portable references. Used with `qmd get`, `qmd ls`.

## MCP Server

```bash
qmd mcp                                   # stdio transport (for Claude Code)
qmd mcp --http                            # HTTP daemon (localhost:8181)
qmd mcp --http --daemon                   # background daemon
```

Exposes tools: `query`, `get`, `multi_get`, `status`

## SDK (Programmatic)

```typescript
import { createStore } from '@tobilu/qmd'

const store = await createStore({
  dbPath: './index.sqlite',
  config: {
    collections: {
      docs: { path: '/path/to/docs', pattern: '**/*.md' }
    }
  }
})

await store.addCollection('name', { path: '/path', pattern: '**/*.ts' })
await store.removeCollection('name')
const results = await store.query('search terms')
```

## Resource Footprint

- **Database:** ~12MB for ~470 files with ~1200 vectors
- **GPU:** Metal-accelerated on Apple Silicon
- **RAM:** Models loaded on demand, fit within 5.3GB VRAM budget
- **Indexing:** Incremental — only re-embeds changed files (hash comparison)

## Tips

- Use `-c` flag to scope searches when you know which collection has what you need
- `qmd search --files` is useful for piping results into other tools
- Collections with `includeByDefault: false` are only searched when explicitly requested with `-c`
- The `update` command runs before reindexing — useful for `git pull` on tracked collections
- Context strings don't affect search quality but are useful metadata for LLMs consuming results
