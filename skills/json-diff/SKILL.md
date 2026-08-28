---
name: json-diff
description: Open a side-by-side diff of two JSON blobs in VS Code. Use whenever the user pastes (or says they will paste) two JSON values to compare — phrases like "diff these two jsons", "json diff", "compare these payloads", "what changed between these", "before/after json", or any time the user provides two JSON objects and wants to see the differences. Also trigger when the user labels two blobs as "first" and "second" (or "before" and "after", "old" and "new") and the content is JSON. Prefer this skill over inline textual diffing — VS Code's diff view handles large nested JSON far better than chat output.
---

# json-diff

Open two JSON blobs in VS Code's side-by-side diff, with object keys sorted so the diff isn't drowned in serializer-order noise.

## Workflow

1. **Get the two blobs** from the conversation. They'll usually be labeled "first"/"second" (or "before"/"after", "old"/"new"). If only one is provided, ask for the other before continuing.

2. **Write each blob to a file** using the Write tool — into `/tmp/jsondiff-in-<timestamp>/first.raw.json` and `.../second.raw.json`. Use the Write tool, not shell heredocs; large blobs and embedded quotes make heredocs fragile.

3. **Run the bundled script** to format and open the diff:
   ```bash
   bash "$CLAUDE_SKILL_DIR/scripts/jsondiff.sh" <first.raw.json> <second.raw.json>
   ```
   If `$CLAUDE_SKILL_DIR` isn't set in your environment, use the absolute path: `~/.claude/skills/json-diff/scripts/jsondiff.sh`.

   The script: validates inputs, runs `jq -S` on each, writes pretty-printed copies to a fresh `/tmp/jsondiff-<timestamp>/` workspace, then opens `code --diff` on them. It prints the workspace path on success and exits non-zero with a clear message if `jq` can't parse the input or `code`/`jq` are missing.

4. **Summarize the substantive changes** in chat in 2–4 lines — status flips, new array entries, field-value changes the user probably cares about. Skip pure timestamp churn (`updatedAt` and friends) unless that's the actual subject. The VS Code window is the artifact; the chat summary is just orientation.

## Why sort keys

Two JSON payloads from the same API often serialize fields in different orders. A naïve text diff lights up every line. Sorting keys (`jq -S`) collapses that noise so only real value changes show. This is almost always what the user wants.

If the user explicitly cares about key order (rare), pass `--no-sort` to the script.

## When the user wants something else

- **Structural / semantic diff** that ignores array reordering: suggest `difft` instead of `code --diff`. Same shape of workflow, swap the final command.
- **More than two blobs**: `code --diff` only takes two. Suggest opening the workspace as a folder and comparing pairwise.
- **Output to a file** (e.g. for a PR description): run `diff -u` on the script's pretty-printed outputs and paste the result.

## Cleanup

The script doesn't auto-delete its workspace — the user may want to re-open or share the files. `/tmp/` is cleared on reboot, which is enough.
