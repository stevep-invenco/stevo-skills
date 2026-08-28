# Plan: `worklog summary` command

## Context

The work-log CLI currently only supports the write path (`worklog entry -d <date> <headline>`). To make logged entries useful, we need a read path that lets a calling agent retrieve entries within a date range so it can summarise/narrate them.

The agent caller resolves natural-language ranges ("yesterday", "last week") into concrete dates, so the CLI takes explicit `--from` / `--to` only — no presets.

This is the second vertical slice and should mirror the architecture established by slice 001 (`create-entry`): Domain → Use Case → Adapters → Infrastructure, dependency rule pointing inward, errors as values, boundary parsing via Zod.

## CLI Contract

```
worklog summary --from <YYYY-MM-DD> --to <YYYY-MM-DD>
```

- Both options required; both inclusive.
- Output: flat list, one line per entry, format `YYYY-MM-DD  <headline>` (two-space separator).
- Sort: by `occurredOn` descending; ties broken by `loggedAt` descending (most-recently-logged first within a day).
- Empty range: print a one-line message (e.g. `No entries in range.`) to stdout, exit 0.
- Date parse error or storage error: render to stderr, exit 2 (matches `entry` presenter).
- `from > to`: not a domain error — repository returns empty, presenter shows the empty message. No special validation needed.

## Architecture

New slice name: `summary` (matches the user-facing command). Follows the same layout as `create-entry`.

### Files to create

**Domain layer** — no changes. The `Entry` entity already carries everything needed.

**Application layer** — new use case under `src/application/use-cases/summary/`:
- `summary.input-port.ts` — `SummaryInputPort` with `execute(req): Promise<Result<SummaryResponse, SummaryFailure>>`.
- `summary.output-port.ts` — `SummaryOutputPort<TView>` with `presentSuccess` / `presentFailure`; defines `SummaryFailure = { kind: 'invalid-date'; raw: string } | LoadError`.
- `summary.interactor.ts` — calls `repository.findInRange(from, to)`, sorts entries, projects to response DTO.
- `summary.interactor.test.ts` — covers: empty result, single-day result, multi-day sort order, tie-break by `loggedAt`, storage error propagation.
- `dto/summary-request.ts` — `{ from: CalendarDate; to: CalendarDate }`.
- `dto/summary-response.ts` — `{ entries: Array<{ occurredOn: CalendarDate; headline: string }> }`. Project to only the fields the presenter needs; do not leak `id`/`loggedAt` outward.

**Adapter layer** — new CLI files under `src/adapters/cli/`:
- `summary.controller.ts` — parses `from` and `to` strings via injected `ParseDate`, builds the request DTO, calls the interactor, passes `Result` to presenter. Same construction pattern as `create-entry.controller.ts`.
- `summary.controller.test.ts` — mock input port + presenter; verify both date-string parse failures route through `presentFailure` with the right raw string; success path forwards the typed dates unchanged.
- `summary.presenter.ts` — `SummaryCliPresenter` implementing `SummaryOutputPort<SummaryCliViewModel>`. View model shape: `{ outcome: 'success' | 'error'; message: string; exitCode: 0 | 2 }` (mirroring `CreateEntryCliViewModel`). Empty list → `No entries in range.` with exit 0. Non-empty → joined lines `YYYY-MM-DD  headline`. Failures → human messages, exit 2.
- `summary.presenter.test.ts` — covers: empty list, single entry, multiple entries (verify line ordering and separator), each failure kind.

**Infrastructure layer**:
- `src/infrastructure/cli/commands/summary.command.ts` — Commander wiring; mirrors `entry.command.ts`. Registers `--from` / `--to` as required options, calls `composeSummary`, writes view to stdout/stderr per outcome, exits with view code.

### Files to modify

- `src/application/ports/entry-repository.ts` — add `findInRange(from: CalendarDate, to: CalendarDate): Promise<Result<Entry[], LoadError>>`. Define `LoadError = { kind: 'storage-corrupt' | 'storage-io'; detail: string }` alongside the existing `SaveError` (parallel shape; keep separate so each method advertises only the failures it actually produces).

- `src/adapters/persistence/json-file-entry.repository.ts` — implement `findInRange`. Read the file (no lock needed — readers don't conflict with the rename-based atomic write), parse via the existing `parsePersistedEntries`, filter on `occurredOn >= from && occurredOn <= to` (string comparison is correct for ISO `YYYY-MM-DD`), and reconstruct `Entry` instances via `Entry.create` for each row. Missing file → `ok([])`.

- `src/adapters/persistence/json-file-entry.repository.test.ts` — extend with `findInRange` cases: missing file returns empty, file with mixed dates filters correctly to inclusive range, returns `Entry` instances (not raw rows), storage-corrupt and storage-io error paths.

- `src/infrastructure/cli/composition-root.ts` — add `composeSummary(filePath)` returning `{ controller }`. Reuses `JsonFileEntryRepository`, `parsePersistedEntries`, `parseDate`. No id-generator needed for the read path.

- `src/infrastructure/cli/bin/worklog.ts` — register the new command via `.addCommand(summaryCommand())`.

- `package.json` — remove the misleading `"build": "tsc --noEmit"` script. There is no compiled build step (the CLI runs via `tsx`); `typecheck` already covers `tsc --noEmit`. Keeping a duplicate `build` entry suggests a build artefact that doesn't exist.

- `plugins/work-log/skills/worklog/SKILL.md` — **extend the existing skill** (do not add a separate skill). Add coverage for the read path so a single skill governs all worklog interactions. Use the `/skill-creator:skill-creator` skill for guidance on description triggers, examples, and structure when making the edit. The expanded skill should:
  - Broaden the description's trigger phrases to cover read intents ("what did I work on", "summarise yesterday", "review last week's log", "show me my entries for X").
  - Document both CLI signatures: `worklog entry -d <date> "<headline>"` and `worklog summary --from <date> --to <date>`.
  - Explain how to resolve relative ranges to concrete `--from`/`--to` (single-day → both equal; "last week" → seven-day window ending today; etc.) — agent caller does the date math, CLI takes only ISO dates.
  - Preserve the existing "use the user's words verbatim" guidance for the write path.
  - Add an output rule for the read path: pass the CLI's stdout through to the user verbatim; do not re-summarise the lines yourself unless the user asks for a narrative.

### Reuse (do not reimplement)

- `parseDate` from `src/infrastructure/parsers/time.parsers.ts` — already returns `Result<CalendarDate, undefined>`; same `ParseDate` type alias used by `create-entry.controller.ts`. The summary controller takes the same dependency.
- `parsePersistedEntries` from `src/infrastructure/parsers/persisted-entry.parsers.ts` — same Zod parser used today on the write path.
- `Result` / `ok` / `err` from `src/shared/result.ts`.
- `Entry.create` for repo reconstruction.
- `JsonFileEntryRepository` (extend, not replace).

## Decided: duplicate the action-handler shell, file tech-debt follow-up

The `summary.command.ts` action handler duplicates the top-level `try/catch` + view-write + exit shell from `entry.command.ts`. **Keep the duplication for now** — the rule of three applies; abstracting from N=2 risks fitting a shape that doesn't survive command #3.

Capture the future decision in `pm/tickets/003-spike-cli-action-shell.md` (status `todo`) so it isn't forgotten. The ticket is framed as a spike-and-decide: when a third command lands, evaluate whether the shell genuinely stayed identical, then choose between extracting (e.g. a `runCli<TView>(handler)` helper in `src/infrastructure/cli/run-cli.ts`), keeping the duplication, or moving the responsibility somewhere else.

## Testing & Verification

**Unit tests** (red-green TDD per slice):
- `summary.interactor.test.ts` — sort order, tie-break, empty result, storage error.
- `summary.controller.test.ts` — date parse routing for both `from` and `to`.
- `summary.presenter.test.ts` — line formatting, empty message, each failure kind.
- `json-file-entry.repository.test.ts` (extension) — `findInRange` filter behaviour and error paths.

Run: `yarn test`.

**End-to-end smoke** (manual, after implementation):
```bash
WORKLOG_DATA_DIR=$(mktemp -d) yarn worklog entry -d 2026-05-01 "first thing"
WORKLOG_DATA_DIR=$(mktemp -d) ...  # seed a few entries across dates
yarn worklog summary --from 2026-05-01 --to 2026-05-06
```
Verify: lines sorted descending by date, two-space separator, exit 0; empty range prints message and exits 0; bad date prints to stderr with exit 2.

**Type check**: `yarn typecheck` (tsc --noEmit). There is no compiled build step.

## Tickets

- `pm/tickets/002-summary.md` — id `002`, title "Summary CLI command for date-range entry retrieval", status `todo`. Branch along the lines of `slice-02-summary`. This is the slice tracked by this plan.
- `pm/tickets/003-spike-cli-action-shell.md` — id `003`, title "Spike: decide on shared CLI action-handler shell", status `todo`. Spike-and-decide follow-up created alongside slice 002 to revisit the deferred extraction when a third command lands or earlier if the duplication causes friction.
