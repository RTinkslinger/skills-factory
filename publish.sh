#!/bin/bash
# publish.sh — Publish skills from Skills Factory to ~/.claude/
# Usage: ./publish.sh [--dry-run] [--force]

set -euo pipefail

CLAUDE_DIR="$HOME/.claude"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Publish Manifest ──────────────────────────────────────────────
# Format: source_path:target_subdirectory:target_filename
# source_path is relative to Skills Factory root
# target_subdirectory is relative to ~/.claude/
MANIFEST=(
  "Cash Build System/setup-cash-build-system-v1.0-beta.md:commands:setup-cash-build-system.md"
  "Cash Build System/cash-build-system-version-history.md:documents:cash-build-system-version-history.md"
)

# ── Parse args ────────────────────────────────────────────────────
DRY_RUN=false
FORCE=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --force)   FORCE=true ;;
    --help|-h)
      echo "Usage: ./publish.sh [--dry-run] [--force]"
      echo ""
      echo "  --dry-run  Show what would change without copying"
      echo "  --force    Skip confirmation prompt"
      exit 0
      ;;
    *) echo "Unknown arg: $arg"; exit 1 ;;
  esac
done

# ── Diff and publish ──────────────────────────────────────────────
changed=0
skipped=0
published=0

echo ""
echo "Skills Factory → ~/.claude/ publish"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for entry in "${MANIFEST[@]}"; do
  IFS=':' read -r src_rel target_dir target_file <<< "$entry"
  src="$SCRIPT_DIR/$src_rel"
  dst="$CLAUDE_DIR/$target_dir/$target_file"

  if [[ ! -f "$src" ]]; then
    echo "⚠ MISSING: $src_rel"
    echo "  Source file not found, skipping."
    echo ""
    ((skipped++))
    continue
  fi

  # Ensure target directory exists
  mkdir -p "$CLAUDE_DIR/$target_dir"

  if [[ ! -f "$dst" ]]; then
    echo "NEW: $target_dir/$target_file"
    echo "  ← $src_rel"
    echo ""
    ((changed++))
  elif diff -q "$src" "$dst" > /dev/null 2>&1; then
    echo "✓ $target_dir/$target_file (unchanged)"
    echo ""
    continue
  else
    echo "CHANGED: $target_dir/$target_file"
    echo "  ← $src_rel"
    diff --color=auto -u "$dst" "$src" 2>/dev/null | head -30 || true
    echo ""
    ((changed++))
  fi
done

if [[ $changed -eq 0 ]]; then
  echo "Nothing to publish. All files are up to date."
  exit 0
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$changed file(s) to publish, $skipped skipped"
echo ""

if [[ "$DRY_RUN" == true ]]; then
  echo "(dry run — no files copied)"
  exit 0
fi

if [[ "$FORCE" != true ]]; then
  read -rp "Publish? (y/n) " confirm
  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
  fi
fi

# ── Copy files ────────────────────────────────────────────────────
for entry in "${MANIFEST[@]}"; do
  IFS=':' read -r src_rel target_dir target_file <<< "$entry"
  src="$SCRIPT_DIR/$src_rel"
  dst="$CLAUDE_DIR/$target_dir/$target_file"

  [[ ! -f "$src" ]] && continue
  if [[ -f "$dst" ]] && diff -q "$src" "$dst" > /dev/null 2>&1; then
    continue
  fi

  mkdir -p "$CLAUDE_DIR/$target_dir"
  cp "$src" "$dst"
  echo "Published: $target_dir/$target_file"
  ((published++))
done

echo ""
echo "Done. $published file(s) published."
