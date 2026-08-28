---
id: "002"
title: "Summary CLI command for date-range entry retrieval"
status: todo
created: 2026-05-06
started:
completed:
branch:
pr:
---

## Summary

Slice 001 proved out the write path (`worklog entry`). To make logged entries
useful, the CLI needs a read path so a calling agent can retrieve a window of
entries to summarise or narrate.

The shape was settled in conversation:
`worklog summary --from <YYYY-MM-DD> --to <YYYY-MM-DD>`, both options required
and inclusive. Output is a flat list — one line per entry, format
`YYYY-MM-DD  <headline>` — sorted by `occurredOn` descending (tie-break by
`loggedAt` descending). An empty range prints a single message and exits 0.

Key design decisions:

- **Presets ("yesterday", "last week") are out of scope.** The agent caller
  resolves natural-language ranges to ISO dates before invoking the CLI. The
  CLI takes only concrete dates.
- **Flat output, not grouped by date.** A nested format would push parsing
  complexity onto the agent for no gain. Flat lines are simple to emit and
  trivial for the agent to group/count if it wants.
- **Empty-range messaging belongs in the presenter.** The interactor returns
  an empty list — a valid result, not an error. Rendering
  "No entries in range." is a presentation choice, so a future JSON presenter
  could emit `[]` instead without changing the interactor.
- **Repository gains `findInRange`, not a new repository.** Mirrors the existing
  `save` shape (Result-typed, parallel `LoadError` union). Reading does not need
  the lockfile — the rename-based atomic write already gives readers a
  consistent view.
- **No date-fns.** ISO `YYYY-MM-DD` strings sort lexicographically and compare
  correctly with `>=` / `<=`. Adding a date library buys nothing here.
- **Action-handler try/catch shell stays duplicated for now.** Rule of three:
  with only two commands the right extraction shape is not yet visible.
  Captured as ticket 003.

## Plan

### New slice files (mirror `create-entry`)

**Application — `src/application/use-cases/summary/`**
- `summary.input-port.ts` — `SummaryInputPort.execute(req): Promise<Result<SummaryResponse, SummaryFailure>>`
- `summary.output-port.ts` — `SummaryOutputPort<TView>` + `SummaryFailure = { kind: 'invalid-date'; raw: string } | LoadError`
- `summary.interactor.ts` + `summary.interactor.test.ts`
- `dto/summary-request.ts` — `{ from: CalendarDate; to: CalendarDate }`
- `dto/summary-response.ts` — `{ entries: Array<{ occurredOn: CalendarDate; headline: string }> }` (project to only what the presenter needs; do not leak `id`/`loggedAt` outward)

**Adapters — `src/adapters/cli/`**
- `summary.controller.ts` + `.test.ts` — parses `from` / `to` via injected `ParseDate`; both parse failures route through `presentFailure` with the offending raw string
- `summary.presenter.ts` + `.test.ts` — `SummaryCliViewModel { outcome, message, exitCode }`; empty list → "No entries in range." exit 0; non-empty → joined `YYYY-MM-DD  headline` lines; failures → human messages, exit 2

**Infrastructure — `src/infrastructure/cli/commands/summary.command.ts`** — Commander wiring with `--from` / `--to` required options.

### Modifications

- `src/application/ports/entry-repository.ts` — add `findInRange(from, to): Promise<Result<Entry[], LoadError>>`. `LoadError` is a parallel union to `SaveError` (`'storage-corrupt' | 'storage-io'`).
- `src/adapters/persistence/json-file-entry.repository.ts` — implement `findInRange` (no lock; reuse `parsePersistedEntries`; reconstruct `Entry` instances via `Entry.create`; missing file → `ok([])`).
- `src/adapters/persistence/json-file-entry.repository.test.ts` — extend with cases for missing file, mixed-date filtering at inclusive bounds, returns `Entry` instances, both error paths.
- `src/infrastructure/cli/composition-root.ts` — add `composeSummary(filePath)`.
- `src/infrastructure/cli/bin/worklog.ts` — register `summaryCommand()`.
- `package.json` — remove the misleading `"build": "tsc --noEmit"` script. There is no compiled build step; `typecheck` already covers it. No external references to `yarn build` exist.
- `plugins/work-log/skills/worklog/SKILL.md` — extend (not replace) the existing skill so a single skill governs all worklog interactions. Use `/skill-creator:skill-creator` for guidance. Broaden trigger phrases to include read intents ("what did I work on", "summarise yesterday", "review last week"), document both CLI signatures, explain how the agent resolves relative ranges to ISO dates, preserve the existing "use the user's words verbatim" guidance for the write path, and add a rule: pass summary stdout through verbatim unless the user asks for a narrative.

### Reuse

- `parseDate` from `src/infrastructure/parsers/time.parsers.ts`
- `parsePersistedEntries` from `src/infrastructure/parsers/persisted-entry.parsers.ts`
- `Result` / `ok` / `err` from `src/shared/result.ts`
- `Entry.create` for repo reconstruction

### Verification

- `yarn test` — unit tests across the slice
- `yarn typecheck` — `tsc --noEmit` (no build step)
- Manual smoke: seed entries via `worklog entry` against a temp `WORKLOG_DATA_DIR`, then run `worklog summary --from … --to …` and verify ordering, separator, exit codes, and the empty-range message.

### Branch

`slice-02-summary`
