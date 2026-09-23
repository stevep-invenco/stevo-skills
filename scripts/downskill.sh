#!/usr/bin/env bash
# ~/.agents/skills/ is shared with invenco-skills and the skills CLI cannot
# tell their owners apart, so only names present under skills/ are removable.
# Omitting --agent targets every agent, which is what lets the CLI delete the
# shared copy in ~/.agents/skills/ as well as the per-agent links.
#
# Usage: pnpm downskill <skill> [<skill>...]
set -euo pipefail

cd "$(dirname "$0")/.."

if [ $# -eq 0 ]; then
  echo "usage: pnpm downskill <skill> [<skill>...]" >&2
  exit 1
fi

unknown=()
for name in "$@"; do
  [ -f "skills/$name/SKILL.md" ] || unknown+=("$name")
done

if [ ${#unknown[@]} -gt 0 ]; then
  echo "error: not a stevo-skills skill: ${unknown[*]}" >&2
  echo "Only skills with skills/<name>/SKILL.md in this repo can be removed." >&2
  exit 1
fi

pnpm exec skills remove "$@" --global --yes
