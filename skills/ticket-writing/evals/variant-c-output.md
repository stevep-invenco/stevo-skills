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

The work-log CLI only has a write path today (`worklog entry -d <date> <headline>`). Logged entries sit in a JSON file with no way to read them back. To make the tool useful for its primary consumer — an AI agent summarising what the user worked on — we need a read path that retrieves entries within a date range.

This came out of a conversation about what the next slice should look like. The initial proposal was for `worklog summary --from <YYYY-MM-DD> --to <YYYY-MM-DD>` with both flags required. The calling agent resolves natural-language ranges ("yesterday", "last week") into concrete ISO dates before invoking the CLI, so there's no reason for the CLI to carry preset logic — that complexity stays in the caller.

The main design tension was output format. The agent suggested JSON by default since the caller is a machine, but the human pushed back in favour of human-readable text: a flat list of `YYYY-MM-DD  headline` lines, one per entry. The reasoning was pragmatic — the agent can parse a flat text list just as easily, and the output stays inspectable when a human runs the command directly. The grouped-by-date output the agent initially mocked (date headers with indented entries beneath) was also rejected: nesting adds complexity on both sides without helping the agent, which doesn't need visual grouping.

Sort order landed on `occurredOn` descending (most recent day first), with ties on the same day broken by `loggedAt` descending (most recently logged first within a day). The human agreed with descending as the default and explicitly deferred making sort order configurable.

For empty ranges (including the `from > to` case), the human chose a simple one-line message (`No entries in range.`) printed to stdout with exit 0, overriding the agent's recommendation to print nothing and exit silently. The empty-range message is a presentation concern: the interactor returns an empty list (a valid result, not an error), and the presenter decides how to render it. A different presenter (e.g. JSON) could emit `[]` instead.

The conversation also surfaced several tangential decisions:

- **date-fns is not needed.** ISO `YYYY-MM-DD` strings sort lexicographically in chronological order, so range filtering with `>=` / `<=` on raw strings works correctly. No date arithmetic or formatting is involved. Adding a library buys nothing.
- **The `build` script in `package.json` is misleading.** It runs `tsc --noEmit` — identical to `typecheck` — but the CLI has no compiled build step (it runs via `tsx`). The plan originally referenced `yarn build` for verification; the human caught this and corrected it to `yarn typecheck`. The `build` script should be removed to avoid confusion.
- **The existing `worklog` skill should be extended**, not split into a separate `worklog-summary` skill. The agent had recommended a split (mirroring the `log-notion` / `logs-notion` pattern), but the human disagreed — one skill should govern all worklog interactions, with guidance for both the write and read paths.
- **The duplicated `try/catch` action-handler shell should stay duplicated for now.** The `summary.command.ts` action handler will duplicate the top-level `try/catch` + view-write + exit pattern from `entry.command.ts`. Abstracting from N=2 risks fitting a shape that doesn't survive command #3. A spike-and-decide follow-up is captured in ticket 003.

This is the second vertical slice and mirrors the architecture established by slice 001 (`create-entry`): Domain -> Use Cases -> Interface Adapters -> Frameworks & Drivers, dependency rule pointing inward, errors as values, boundary parsing via Zod.

## Scope

### In Scope

- New `worklog summary --from <YYYY-MM-DD> --to <YYYY-MM-DD>` CLI command with both options required
- Flat text output: one line per entry, format `YYYY-MM-DD  <headline>` (two-space separator), sorted by `occurredOn` descending then `loggedAt` descending
- Empty-range handling: print `No entries in range.` to stdout, exit 0
- Error handling: date parse errors and storage errors render to stderr, exit 2
- Full clean-architecture slice: interactor, controller, presenter, DTOs, port extensions
- `findInRange` method on the entry repository port and its JSON file implementation
- Composition root wiring for the new slice
- Unit tests per layer (interactor, controller, presenter, repository extension)
- Remove the misleading `build` script from `package.json`
- Extend the existing `worklog` skill to cover the read path (trigger phrases, CLI signature, date resolution guidance, output passthrough rule)

### Out of Scope

- **Date presets or natural-language parsing** — the agent caller resolves these before invoking the CLI
- **Configurable sort order** — descending is the only sort; configurability is deferred until there's a concrete need
- **JSON output format** — human-readable text only for now
- **Grouped-by-date output** — flat list was chosen over nested grouping
- **Extracting the duplicated action-handler shell** — deferred to ticket 003, framed as a spike-and-decide

### Related Work

- **001 — Log entry CLI with clean architecture** (done): the first slice that established the architecture this slice mirrors
- **003 — Spike: decide on shared CLI action-handler shell** (todo): tech-debt follow-up created alongside this ticket to revisit the duplicated `try/catch` pattern when a third command lands

## Plan

### Overview

The summary command is a read-path vertical slice that follows every convention established by the write-path slice 001. A calling agent supplies two ISO date strings; the CLI parses them, queries the repository for entries in the inclusive range, sorts them, and renders a flat text list.

**Behavioral contract:**

- `worklog summary --from 2026-05-01 --to 2026-05-06` prints one line per matching entry, format `YYYY-MM-DD  <headline>`, sorted by `occurredOn` descending then `loggedAt` descending.
- Both `--from` and `--to` are required. Missing either is a Commander parse error (handled by Commander itself).
- Empty result (including `from > to`): prints `No entries in range.` to stdout, exits 0. The repository returns an empty list for `from > to` naturally — no special validation is needed.
- Date parse failure or storage error: message to stderr, exit 2 (matching the `entry` presenter convention).
- The response DTO projects only `occurredOn` and `headline` — `id` and `loggedAt` are not leaked past the interactor.

**Architectural approach:**

The slice reuses the same layering as `create-entry`: Commander command file -> controller (parses boundary strings via injected `ParseDate`, builds request DTO, calls interactor, passes `Result` to presenter) -> interactor (calls `repository.findInRange`, sorts, projects to response DTO) -> presenter (renders view model with `outcome`, `message`, `exitCode`). The repository port gains a `findInRange` method; the JSON file implementation reads, parses via the existing `parsePersistedEntries`, filters on string comparison, and reconstructs `Entry` instances. The composition root wires everything without any new library imports.

**Key decisions:**

- **Flat text over JSON or grouped output** — the agent consumer doesn't need structure, and a human running the command directly gets something readable.
- **String comparison for date filtering** — ISO `YYYY-MM-DD` sorts lexicographically in chronological order; no date library needed.
- **Duplicate the action-handler shell** — rule of three; extract after command #3 (ticket 003).
- **Extend the worklog skill, don't split it** — one skill governs all worklog interactions.

### Execution Detail

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
- `summary.presenter.ts` — `SummaryCliPresenter` implementing `SummaryOutputPort<SummaryCliViewModel>`. View model shape: `{ outcome: 'success' | 'error'; message: string; exitCode: 0 | 2 }` (mirroring `CreateEntryCliViewModel`). Empty list -> `No entries in range.` with exit 0. Non-empty -> joined lines `YYYY-MM-DD  headline`. Failures -> human messages, exit 2.
- `summary.presenter.test.ts` — covers: empty list, single entry, multiple entries (verify line ordering and separator), each failure kind.

**Infrastructure layer**:
- `src/infrastructure/cli/commands/summary.command.ts` — Commander wiring; mirrors `entry.command.ts`. Registers `--from` / `--to` as required options, calls `composeSummary`, writes view to stdout/stderr per outcome, exits with view code.

**Files to modify:**

- `src/application/ports/entry-repository.ts` — add `findInRange(from: CalendarDate, to: CalendarDate): Promise<Result<Entry[], LoadError>>`. Define `LoadError = { kind: 'storage-corrupt' | 'storage-io'; detail: string }` alongside the existing `SaveError` (parallel shape; keep separate so each method advertises only the failures it actually produces).

- `src/adapters/persistence/json-file-entry.repository.ts` — implement `findInRange`. Read the file (no lock needed — readers don't conflict with the rename-based atomic write), parse via the existing `parsePersistedEntries`, filter on `occurredOn >= from && occurredOn <= to` (string comparison is correct for ISO `YYYY-MM-DD`), and reconstruct `Entry` instances via `Entry.create` for each row. Missing file -> `ok([])`.

- `src/adapters/persistence/json-file-entry.repository.test.ts` — extend with `findInRange` cases: missing file returns empty, file with mixed dates filters correctly to inclusive range, returns `Entry` instances (not raw rows), storage-corrupt and storage-io error paths.

- `src/infrastructure/cli/composition-root.ts` — add `composeSummary(filePath)` returning `{ controller }`. Reuses `JsonFileEntryRepository`, `parsePersistedEntries`, `parseDate`. No id-generator needed for the read path.

- `src/infrastructure/cli/bin/worklog.ts` — register the new command via `.addCommand(summaryCommand())`.

- `package.json` — remove the misleading `"build": "tsc --noEmit"` script. There is no compiled build step (the CLI runs via `tsx`); `typecheck` already covers `tsc --noEmit`. Keeping a duplicate `build` entry suggests a build artefact that doesn't exist.

- `plugins/work-log/skills/worklog/SKILL.md` — extend the existing skill (do not add a separate skill). Add coverage for the read path so a single skill governs all worklog interactions. Use the `/skill-creator:skill-creator` skill for guidance on description triggers, examples, and structure when making the edit. The expanded skill should:
  - Broaden the description's trigger phrases to cover read intents ("what did I work on", "summarise yesterday", "review last week's log", "show me my entries for X").
  - Document both CLI signatures: `worklog entry -d <date> "<headline>"` and `worklog summary --from <date> --to <date>`.
  - Explain how to resolve relative ranges to concrete `--from`/`--to` (single-day -> both equal; "last week" -> seven-day window ending today; etc.) — agent caller does the date math, CLI takes only ISO dates.
  - Preserve the existing "use the user's words verbatim" guidance for the write path.
  - Add an output rule for the read path: pass the CLI's stdout through to the user verbatim; do not re-summarise the lines yourself unless the user asks for a narrative.

**Reuse (do not reimplement):**

- `parseDate` from `src/infrastructure/parsers/time.parsers.ts` — already returns `Result<CalendarDate, undefined>`; same `ParseDate` type alias used by `create-entry.controller.ts`. The summary controller takes the same dependency.
- `parsePersistedEntries` from `src/infrastructure/parsers/persisted-entry.parsers.ts` — same Zod parser used today on the write path.
- `Result` / `ok` / `err` from `src/shared/result.ts`.
- `Entry.create` for repo reconstruction.
- `JsonFileEntryRepository` (extend, not replace).

**Testing and verification:**

Unit tests (red-green TDD per slice):
- `summary.interactor.test.ts` — sort order, tie-break, empty result, storage error.
- `summary.controller.test.ts` — date parse routing for both `from` and `to`.
- `summary.presenter.test.ts` — line formatting, empty message, each failure kind.
- `json-file-entry.repository.test.ts` (extension) — `findInRange` filter behaviour and error paths.

Run: `yarn test`.

End-to-end smoke (manual, after implementation):
```bash
WORKLOG_DATA_DIR=$(mktemp -d) yarn worklog entry -d 2026-05-01 "first thing"
WORKLOG_DATA_DIR=$(mktemp -d) ...  # seed a few entries across dates
yarn worklog summary --from 2026-05-01 --to 2026-05-06
```
Verify: lines sorted descending by date, two-space separator, exit 0; empty range prints message and exits 0; bad date prints to stderr with exit 2.

Type check: `yarn typecheck` (tsc --noEmit). There is no compiled build step.
