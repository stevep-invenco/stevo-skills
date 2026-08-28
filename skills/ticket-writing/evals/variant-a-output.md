---
id: "002"
title: "Summary CLI command for date-range entry retrieval"
status: todo
created: 2026-05-06
started:
completed:
branch: slice-02-summary
pr:
---

## Summary

The work-log CLI today only supports a write path: `worklog entry -d <date> <headline>` creates a log entry and persists it to disk. There is no way to read entries back. Without a read path, the data that goes in never comes out -- the tool is a write-only ledger.

This ticket adds the second vertical slice: `worklog summary --from <YYYY-MM-DD> --to <YYYY-MM-DD>`, a date-range query that retrieves entries and prints them as a flat, human-readable list. The primary consumer is an AI agent (the `worklog` skill), which resolves natural-language date expressions ("yesterday", "last week") into concrete ISO dates before calling the CLI. The CLI itself takes only explicit dates -- no presets, no relative expressions.

The design conversation settled several points worth narrating because the alternatives explain the shape of the command:

- **Flat output, not grouped.** The initial sketch grouped entries under date headers with indented lines beneath. The human challenged this: given that the caller is an agent that reformats anyway, nested structure adds complexity on both ends for no benefit. The final format is one entry per line, `YYYY-MM-DD  <headline>`, sorted by `occurredOn` descending. Ties within a day break by `loggedAt` descending (most-recently-logged first).

- **Human-readable text, not JSON.** The agent recommended JSON as the default (since the caller is an agent that parses structured data), but the human chose human-readable output. Given the limited functionality -- date and headline only -- the flat text format is simpler and sufficient for both human and agent consumption.

- **Empty range prints a message, exits 0.** The agent initially recommended print-nothing-and-exit-0 (the agent caller can infer empty from empty stdout). The human overrode this: an empty range outputs a simple message like `No entries in range.` and exits 0. This keeps the behavior explicit rather than relying on the caller to interpret silence.

- **Empty-message rendering is a presenter concern.** The human asked where the empty-range message belongs in the clean architecture. The interactor returns an empty list (a valid result, not an error). The presenter decides how to render it -- a CLI presenter prints the message, a hypothetical JSON presenter would emit `[]`. This keeps the interactor pure.

- **`from > to` is not validated.** If the caller passes a range where `from` is later than `to`, the repository simply returns no matches. The presenter renders the empty message. No special domain validation is needed for a logically impossible range.

- **Duplicate the action-handler shell, don't extract it.** The `summary.command.ts` file will duplicate the top-level `try/catch` + view-write + process-exit shell from `entry.command.ts`. Extracting a shared helper from N=2 examples risks fitting a shape that doesn't survive command #3. This duplication is captured as a deliberate tech-debt follow-up (ticket 003).

- **No date-fns dependency.** ISO `YYYY-MM-DD` strings sort lexicographically in chronological order. Range filtering uses simple string comparison (`>=` / `<=`). No date arithmetic or formatting is involved. Adding a library buys nothing.

- **Remove the misleading `build` script.** `package.json` contains both `"build": "tsc --noEmit"` and `"typecheck": "tsc --noEmit"` -- identical commands. There is no compiled build step (the CLI runs via `tsx`). The `build` entry suggests an artifact that doesn't exist and was flagged as misleading. It gets removed.

- **Extend the existing worklog skill, don't split it.** The agent recommended a separate `worklog-summary` skill (following the `log-notion` / `logs-notion` precedent). The human disagreed: one skill should govern all worklog interactions. The expanded skill broadens its triggers to cover read intents and documents both CLI signatures.

## Scope

### In Scope

- New `worklog summary --from <YYYY-MM-DD> --to <YYYY-MM-DD>` command, both options required, both dates inclusive
- Flat output format: one line per entry as `YYYY-MM-DD  <headline>` (two-space separator), sorted by `occurredOn` descending, ties broken by `loggedAt` descending
- Empty-range handling: prints `No entries in range.` to stdout, exits 0
- Error handling: date parse errors and storage errors render to stderr, exit 2 (matching `entry` presenter convention)
- `findInRange(from, to)` method added to the `EntryRepository` port and implemented in `JsonFileEntryRepository`
- `LoadError` type (`storage-corrupt | storage-io`) defined alongside existing `SaveError` -- separate types so each method advertises only its actual failure modes
- Composition root extended with `composeSummary(filePath)`
- `build` script removed from `package.json` (misleading duplicate of `typecheck`)
- Existing `worklog` skill updated to cover the read path: broadened triggers, both CLI signatures documented, guidance on resolving relative date ranges to concrete `--from`/`--to` values
- Unit tests for interactor, controller, presenter, and repository extension (red-green TDD)

### Out of Scope

- **Date presets or relative expressions** (`--yesterday`, `--last-week`) -- the agent caller resolves these to ISO dates before invoking the CLI
- **Configurable sort order** -- descending is the only behavior; configurability deferred until a use case emerges
- **JSON output format** -- the human chose human-readable text; a `--format json` flag is a future consideration
- **Extracting the shared action-handler shell** -- deliberately deferred per rule-of-three; tracked as ticket 003
- **Topics, tags, or any entry metadata beyond date and headline** -- the summary output intentionally shows only the two fields that exist today

### Related Work

- **001 (create-entry)** -- prerequisite; established the architecture, domain entities, repository, and CLI patterns that this slice mirrors
- **003 (spike: decide on shared CLI action-handler shell)** -- follow-up tech-debt ticket created alongside this slice to revisit the duplicated `try/catch` + exit shell when a third command lands

## Plan

### Behavioral Contract

```
worklog summary --from <YYYY-MM-DD> --to <YYYY-MM-DD>
```

| Scenario | stdout | stderr | exit code |
|----------|--------|--------|-----------|
| Entries found in range | `YYYY-MM-DD  <headline>\n` per entry, sorted `occurredOn` desc then `loggedAt` desc | -- | 0 |
| No entries in range | `No entries in range.` | -- | 0 |
| `from > to` (logically empty) | `No entries in range.` | -- | 0 |
| Invalid date string for `--from` or `--to` | -- | Human-readable parse error identifying the bad value | 2 |
| Storage I/O or corruption error | -- | Human-readable storage error | 2 |

Both `--from` and `--to` are required options. Both bounds are inclusive. Output uses a two-space separator between date and headline.

### Approach and Architectural Decisions

This slice follows the same clean architecture layering established by slice 001:

- **Domain layer** -- no changes. `Entry` already carries `occurredOn`, `loggedAt`, and `headline`.
- **Application layer** -- new `SummaryInteractor` implementing `SummaryInputPort`. Receives a request DTO with two `CalendarDate` values, calls `repository.findInRange(from, to)`, sorts the results in memory, and projects to a response DTO containing only `occurredOn` and `headline` (does not leak `id` or `loggedAt` outward). Returns `Result<SummaryResponse, SummaryFailure>`.
- **Adapter layer** -- new `SummaryController` (parses date strings via injected `ParseDate`, builds request DTO, calls interactor, passes result to presenter) and `SummaryCliPresenter` (renders success as flat lines, empty as message, failures as stderr text with exit code 2). View model shape mirrors `CreateEntryCliViewModel`: `{ outcome: 'success' | 'error'; message: string; exitCode: 0 | 2 }`.
- **Infrastructure layer** -- Commander wiring in `summary.command.ts`, composition root extended with `composeSummary`.
- **Repository extension** -- `findInRange` added to the `EntryRepository` port. Implementation reads the JSON file (no lock needed -- readers don't conflict with the rename-based atomic write), parses via existing `parsePersistedEntries`, filters on `occurredOn >= from && occurredOn <= to` (string comparison is correct for ISO dates), and reconstructs `Entry` instances via `Entry.create`. Missing file returns `ok([])`.

Key reuse points (do not reimplement):
- `parseDate` from `src/infrastructure/parsers/time.parsers.ts` -- same `ParseDate` type alias used by the entry controller
- `parsePersistedEntries` from `src/infrastructure/parsers/persisted-entry.parsers.ts`
- `Result` / `ok` / `err` from `src/shared/result.ts`
- `Entry.create` for repo-side reconstruction
- `JsonFileEntryRepository` (extend, not replace)

The action-handler shell in `summary.command.ts` (top-level `try/catch`, write view to stdout/stderr, call `process.exit`) duplicates `entry.command.ts` intentionally. See ticket 003 for the deferred extraction decision.

### Testing Strategy

**Unit tests** (red-green TDD, run via `yarn test`):

- `summary.interactor.test.ts` -- empty result returns success with empty entries array; single-day result returns correct projection; multi-day result is sorted `occurredOn` descending; same-day entries tie-break by `loggedAt` descending; storage error propagates as failure result
- `summary.controller.test.ts` -- mock input port and presenter; invalid `--from` string routes through `presentFailure` with the raw string; invalid `--to` string routes through `presentFailure`; valid dates forward typed `CalendarDate` values to the interactor unchanged
- `summary.presenter.test.ts` -- empty entries list renders `No entries in range.` with exit 0; single entry renders one line in `YYYY-MM-DD  headline` format; multiple entries render in correct order with two-space separator; each `SummaryFailure` kind renders appropriate message with exit 2
- `json-file-entry.repository.test.ts` (extension) -- `findInRange` with missing file returns empty array; file with mixed dates filters correctly to inclusive range; returned values are `Entry` instances (not raw rows); `storage-corrupt` and `storage-io` error paths

**Type check**: `yarn typecheck` (`tsc --noEmit`). There is no compiled build step.

**End-to-end smoke** (manual, after implementation):
```bash
# Seed entries across several dates
WORKLOG_DATA_DIR=$(mktemp -d) yarn worklog entry -d 2026-05-01 "first thing"
# ... seed more entries ...
yarn worklog summary --from 2026-05-01 --to 2026-05-06
# Verify: lines sorted descending, two-space separator, exit 0
# Verify: empty range prints message, exit 0
# Verify: bad date prints to stderr, exit 2
```

### Implementation Areas

**New files** (all following existing naming and layout conventions):

- Application use case: `src/application/use-cases/summary/` -- input port, output port, interactor, interactor tests, request DTO, response DTO
- CLI adapters: `src/adapters/cli/` -- summary controller, controller tests, summary presenter, presenter tests
- Infrastructure command: `src/infrastructure/cli/commands/summary.command.ts`

**Modified files:**

- `src/application/ports/entry-repository.ts` -- add `findInRange` method and `LoadError` type
- `src/adapters/persistence/json-file-entry.repository.ts` -- implement `findInRange`
- `src/adapters/persistence/json-file-entry.repository.test.ts` -- extend with `findInRange` test cases
- `src/infrastructure/cli/composition-root.ts` -- add `composeSummary` factory
- `src/infrastructure/cli/bin/worklog.ts` -- register summary command
- `package.json` -- remove `build` script
- `plugins/work-log/skills/worklog/SKILL.md` -- extend skill with read-path triggers, both CLI signatures, date-range resolution guidance
