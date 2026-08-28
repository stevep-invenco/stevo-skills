#!/usr/bin/env bash
# Usage: jsondiff.sh <first.json> <second.json> [--no-sort]
#
# Pretty-prints both JSON files (sorting keys by default), then opens VS Code's
# side-by-side diff. Inputs can be raw/minified — they get reformatted to a
# fresh workspace under /tmp/jsondiff-<timestamp>/ so the originals are
# untouched.
#
# --no-sort: skip `jq -S` (use when key order itself is meaningful)

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <first.json> <second.json> [--no-sort]" >&2
  exit 2
fi

FIRST_IN="$1"
SECOND_IN="$2"
SORT_FLAG="-S"
if [[ "${3:-}" == "--no-sort" ]]; then
  SORT_FLAG=""
fi

for f in "$FIRST_IN" "$SECOND_IN"; do
  if [[ ! -f "$f" ]]; then
    echo "error: not a file: $f" >&2
    exit 1
  fi
done

for cmd in jq code; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "error: '$cmd' not on PATH" >&2
    exit 1
  fi
done

WORKDIR="/tmp/jsondiff-$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p "$WORKDIR"

FIRST_OUT="$WORKDIR/first.json"
SECOND_OUT="$WORKDIR/second.json"

if ! jq $SORT_FLAG . "$FIRST_IN" > "$FIRST_OUT"; then
  echo "error: failed to parse $FIRST_IN as JSON" >&2
  exit 1
fi
if ! jq $SORT_FLAG . "$SECOND_IN" > "$SECOND_OUT"; then
  echo "error: failed to parse $SECOND_IN as JSON" >&2
  exit 1
fi

echo "workspace: $WORKDIR"
code --diff "$FIRST_OUT" "$SECOND_OUT"
