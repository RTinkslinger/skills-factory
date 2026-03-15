#!/bin/bash
# One-command re-index pipeline
# Run before each workflow audit to ensure data is fresh.
#
# Usage:
#   ./scripts/reindex.sh              # Full reprocess + reindex
#   ./scripts/reindex.sh --incremental # Only new/changed files

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

MODE="${1:---incremental}"

echo "=== QMD Re-index Pipeline ==="
echo "Mode: $MODE"
echo ""

# Step 1: Preprocess JSONL data
echo "[1/3] Preprocessing JSONL data..."
python3 "$SCRIPT_DIR/preprocess-jsonl.py" $MODE

# Step 2: Update qmd index (picks up new/changed files)
echo ""
echo "[2/3] Updating qmd index..."
qmd update

# Step 3: Generate embeddings for new documents
echo ""
echo "[3/3] Embedding new documents..."
qmd embed

echo ""
echo "=== Re-index complete ==="
qmd status 2>/dev/null | head -8 || true
