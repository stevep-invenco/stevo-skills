---
name: handoff
description: "Dump current session state to a HANDOFF.md a fresh session can resume from. Auto-excludes the file from git via .git/info/exclude (never commits the workflow into the project's .gitignore). Use when the session has grown too large or you need to /clear without losing task progress."
argument-hint: [optional-path]
---

# Handoff — write a session continuation doc, never commit it

Produce a single distilled markdown artifact (~100-300 lines, NOT a re-serialization of the conversation) that lets a fresh session resume cleanly. This is a workflow file: it lives in the working tree, gets read by the next session, and **must never enter git history**. The skill enforces that with `.git/info/exclude` (per-clone, invisible to teammates) before writing.

Optional argument: `$ARGUMENTS` — a custom path for the handoff file. Defaults to `HANDOFF.md` in the current repo root (`git rev-parse --show-toplevel`).

## Step 0 — Idempotently exclude HANDOFF*.md from git

Before writing anything, ensure the handoff filename pattern is in `.git/info/exclude` so accidental `git add HANDOFF*` won't track it. Use `.git/info/exclude` (per-clone, untracked), NOT `.gitignore` (would commit a personal workflow into the project for every collaborator).

```bash
ROOT=$(git rev-parse --show-toplevel)
EXCLUDE="$ROOT/.git/info/exclude"
mkdir -p "$ROOT/.git/info"
touch "$EXCLUDE"
grep -qxF 'HANDOFF.md' "$EXCLUDE" || echo 'HANDOFF.md' >> "$EXCLUDE"
grep -qxF 'HANDOFF-*.md' "$EXCLUDE" || echo 'HANDOFF-*.md' >> "$EXCLUDE"
```

If not in a git repo (`git rev-parse` fails), skip this step but warn the user — the handoff file will sit in cwd untracked-by-default but without the belt-and-suspenders guard.

If `$ARGUMENTS` provides a custom filename that doesn't match `HANDOFF*.md`, also append that exact filename to `.git/info/exclude`.

## What to write

Keep it tight. The goal is a distilled artifact a fresh session reads in one pass — bullets, file paths, line numbers, decisions. Not a transcript.

### 1. Goal

One sentence. What is this session trying to accomplish? Re-read the original top-level prompt to anchor this — don't drift into what you happen to be doing right now.

### 2. Tasks

Call `TaskList` and dump the full current state as markdown checkboxes, grouped by status. Preserve task IDs so the fresh session can recreate them with `TaskCreate`.

```
- [x] #1 Completed task — (brief outcome if non-obvious)
- [~] #3 In-progress task — (current sub-step)
- [ ] #4 Pending task
- [ ] #5 Pending task
```

If there are no tasks, write "No active tasks" and reconsider whether a handoff is even useful.

**Record only what's actually still open.** Before writing an item as pending — especially one carried forward from a previous `HANDOFF.md` — confirm it's genuinely undone (read the artifact, diff the code, query the PR). Tick anything this session completed. A done-but-still-unchecked item makes the next session redo or undo finished work; this is the single most common way a handoff misleads.

### 3. Key decisions & context

Bullet list of non-obvious decisions made in this session that a fresh session would need to know. Examples: "chose PostgreSQL over SQLite because of concurrent writes", "skipped the auth layer — handled by upstream proxy", "M1 review found a race condition in X, fixed in commit abc123".

Skip anything already obvious from the code or git history. This section is for what's in your head, not in the repo.

### 4. Current state

- Run `git status` and `git log --oneline -10`, include the results.
- List uncommitted files grouped by what's in progress on each.
- Note any running background processes (paper trading bots, dev servers, watchers, Monitor tasks) and how to find/stop them.

### 5. Next action

What's the very next thing to do? Be specific and executable — "implement the order-book snapshot tests in `src/market/book.test.ts`" not "continue work on the market module".

### 6. Gotchas & blockers

Anything that would trip up a fresh session: flaky tests, env vars needed, services that must be running, API quirks discovered, failed approaches to avoid, surprising state on the live system that doesn't match repo state.

### 7. Resume prompt

A copy-pasteable prompt block for the fresh session. Format:

```
Read HANDOFF.md in this directory. Rebuild the task list from the "Tasks" section using TaskCreate for each pending/in-progress item (preserve the IDs mentioned if possible). Load the "Key decisions", "Current state", and "Gotchas" sections as context. Then start on the "Next action" item — but first verify each open item is genuinely still undone (read the artifact / diff / PR); an unchecked box may already be done. Surface any mismatch instead of silently redoing the work.
```

## After writing

1. Confirm the file was written. Show a one-line summary: path, task counts, size in lines.
2. Put the §7 Resume prompt on the macOS clipboard so the user's cutover is `/clear` → Cmd+V. Extract exactly the prompt body (no code fences, no surrounding prose) from the §7 block and pipe it to `pbcopy`:

   ```
   printf '%s' "<the §7 prompt text, verbatim>" | pbcopy
   ```

   If `pbcopy` is unavailable (non-macOS), skip silently and mention it in step 3 so the user falls back to manual copy.
3. Tell the user in one line: `HANDOFF.md written (<N> lines, <M> tasks). Resume prompt on clipboard — /clear then Cmd+V.` When `pbcopy` was skipped, say so and point to §7.
4. **Do NOT run `/clear` automatically.** The user decides when to cut over — they may want to review or edit the handoff first.
5. **Do NOT `git add` or commit the handoff file.** Step 0 already added it to `.git/info/exclude`; `git add HANDOFF.md` will still track it explicitly if forced, so don't do it.

## Don't

- Don't dump the entire conversation history or tool outputs verbatim. Summarize.
- Don't include code snippets longer than a few lines — reference file paths and line numbers instead.
- Don't write a handoff for a session that hasn't done meaningful work yet (< 5 real prompts).
- Don't add `HANDOFF*.md` to the project's `.gitignore` — that's the wrong tool. The skill uses `.git/info/exclude` precisely because the rule is personal, not project-wide.
