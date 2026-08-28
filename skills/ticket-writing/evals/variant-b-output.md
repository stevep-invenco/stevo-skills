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

## Context

The work-log CLI currently has a single vertical slice: the write path (`worklog entry -d <date> <headline>`), delivered in ticket 001. That slice proved out the clean architecture skeleton end-to-end but left no way to retrieve what was logged. Without a read path, entries go in and never come back out -- making the tool a write-only store.

The immediate consumer is an AI agent (the `worklog` skill) that needs to answer questions like "what did I work on yesterday?" or "summarise last week." The agent resolves natural-language date references into concrete ISO dates, then calls the CLI with explicit `--from` / `--to` flags. This means the CLI itself doesn't need preset shortcuts like `--yesterday` or `--last-week` -- the caller always knows the dates.

The conversation that shaped this slice started with a question about CLI ergonomics: what should the command look like? The initial recommendation was `worklog summary --from <YYYY-MM-DD> --to <YYYY-MM-DD>`, both options required, no implicit "today" default. The human agreed.

The next decision was output format. The agent sketched grouped output (date headers with indented entries underneath) and offered a choice between structured JSON (agent-friendly) and human-readable text. The human chose human-readable and proposed limiting output to date + headline only, given the tool's current scope. The agent pushed back on grouping: since the caller is an agent that reformats anyway, nested structure adds complexity on both ends for no benefit. A flat list -- one line per entry, `YYYY-MM-DD  headline` -- is simpler to produce and simpler to parse. The human agreed.

Sort order was settled as `occurredOn` descending (most recent first), with ties broken by `loggedAt` descending (most recently logged first within a day). Making sort configurable was explicitly deferred.

For empty ranges (no entries match), the agent initially recommended printing nothing and exiting 0, since the agent can infer "empty" from empty stdout. The human overrode this: print a simple empty message (`No entries in range.`) and exit 0. This is a presentation concern -- the interactor returns an empty list (a valid result, not an error), and the presenter decides how to render it. A future JSON presenter could emit `[]` instead. This keeps the interactor pure.

One architectural question surfaced during planning: the `summary.command.ts` action handler will duplicate the top-level `try/catch` + view-write + exit shell from `entry.command.ts`. The options were to extract now into a shared `runCli<TView>(handler)` helper, or to duplicate and revisit later. The human chose duplication -- the rule of three applies; abstracting from N=2 risks fitting a shape that doesn't survive command #3. This decision is tracked as a separate spike in ticket 003.

Two other items were resolved during the conversation:
- **date-fns is not needed.** ISO `YYYY-MM-DD` strings sort lexicographically in chronological order, so range filtering with `>=` / `<=` works on the string form. No date formatting or arithmetic is involved.
- **The `build` script in `package.json` is misleading.** It runs `tsc --noEmit` -- identical to the `typecheck` script. There is no compiled build step (the CLI runs via `tsx`). The `build` script should be removed to avoid implying a build artefact that doesn't exist. Verification uses `yarn typecheck`, not `yarn build`.

Related tickets:
- [001-create-entry](001-create-entry.md) -- prerequisite; established the architecture this slice extends
- [003-spike-cli-action-shell](003-spike-cli-action-shell.md) -- follow-up; spike to decide whether the duplicated action-handler shell should be extracted once a third command lands

## Scope

### In Scope

- `worklog summary --from <YYYY-MM-DD> --to <YYYY-MM-DD>` command with both options required
- Flat, human-readable output: one line per entry, format `YYYY-MM-DD  <headline>` (two-space separator)
- Sort by `occurredOn` descending, ties broken by `loggedAt` descending
- Empty-range message (`No entries in range.`) to stdout, exit 0
- Date parse errors and storage errors rendered to stderr, exit 2 (matching existing `entry` presenter convention)
- `findInRange` method on the entry repository port and its JSON-file implementation
- Removal of the misleading `build` script from `package.json`
- Extension of the existing `worklog` skill to cover the read path (triggers, CLI signature, date-resolution guidance, output handling rules)
- Unit tests for interactor, controller, presenter, and repository extension
- Red-green TDD throughout

### Out of Scope

- **Date presets** (`--yesterday`, `--last-week`) -- the agent caller resolves these to concrete dates before invoking the CLI.
- **Configurable sort order** -- descending is the only sort for now.
- **Grouped or structured output** (JSON, nested date headers) -- flat text is sufficient for the current consumer. A JSON presenter could be added later without touching the interactor or controller.
- **Extraction of the duplicated action-handler shell** -- deliberately deferred; tracked in ticket 003.
- **`from > to` validation** -- not a domain error. The repository returns empty, the presenter shows the empty message. No special validation needed.

### Related Work

- **001** (prerequisite) -- architecture skeleton and write path
- **003** (follow-up) -- spike on shared CLI action-handler shell

## Execution Plan

### Overview

#### Behavioral contract

The command accepts two required ISO-date options (`--from`, `--to`), both inclusive. It prints a flat list of matching entries to stdout -- one line per entry, format `YYYY-MM-DD  <headline>`, sorted by `occurredOn` descending with `loggedAt` descending as tie-breaker. If no entries match (including `from > to`), it prints `No entries in range.` to stdout and exits 0. If either date string fails to parse or a storage error occurs, it prints a human-readable error to stderr and exits 2.

#### Architectural approach

This slice mirrors the structure established by ticket 001's `create-entry` slice: Domain (unchanged) -> Use Case (new `summary` interactor) -> Adapters (new CLI controller + presenter, extended repository) -> Infrastructure (new Commander wiring, extended composition root). The dependency rule points inward; the interactor defines ports, adapters implement them.

The domain layer requires no changes -- the existing `Entry` entity already carries `occurredOn`, `headline`, and `loggedAt`, which is everything the summary needs.

The repository port gains a `findInRange` method. The JSON-file adapter implements it as a read-only operation (no file locking needed -- readers don't conflict with the rename-based atomic write used by the save path). Range filtering uses string comparison on ISO dates, which is lexicographically correct. Entries are reconstructed as `Entry` instances via `Entry.create`, not returned as raw rows.

The response DTO projects to only `occurredOn` and `headline` -- it does not leak `id` or `loggedAt` outward. Sorting happens in the interactor (application layer), not the repository (infrastructure), because sort order is a use-case concern.

The presenter handles the empty-list case as a presentation concern, not a domain or interactor concern: the interactor returns `ok([])`, the presenter renders the empty message. This preserves interactor purity and means a future JSON presenter could emit `[]` without touching application code.

#### Key decisions

1. **Flat output over grouped** -- the agent consumer doesn't need nested structure; grouping adds complexity on both ends (conversation: human agreed after agent pushback on the initial grouped mock).
2. **Human-readable over JSON** -- settled in conversation; the agent reformats anyway, and human readability aids debugging.
3. **Both `--from` and `--to` required** -- no implicit defaults; the caller always knows the dates (conversation: agreed immediately).
4. **Empty message over silent exit** -- human overrode the agent's recommendation of print-nothing; presenter prints `No entries in range.` (conversation: human chose explicit feedback).
5. **Duplicate the action-handler shell** -- conversation settled on rule-of-three; extraction deferred to ticket 003.
6. **No date-fns** -- ISO string comparison is sufficient; no library needed (conversation: human asked, agent demonstrated it was unnecessary).

### Execution Detail

#### Changes by area

**Application layer -- new use case (`src/application/use-cases/summary/`)**

- `summary.input-port.ts` -- `SummaryInputPort` interface with `execute(req: SummaryRequest): Promise<Result<SummaryResponse, SummaryFailure>>`.
- `summary.output-port.ts` -- `SummaryOutputPort<TView>` interface with `presentSuccess(response: SummaryResponse): TView` and `presentFailure(failure: SummaryFailure): TView`. `SummaryFailure = { kind: 'invalid-date'; raw: string } | LoadError`.
- `summary.interactor.ts` -- implements `SummaryInputPort`. Calls `repository.findInRange(from, to)`, sorts the returned entries by `occurredOn` descending then `loggedAt` descending, projects each to `{ occurredOn, headline }`, and returns `ok(SummaryResponse)`. Storage errors propagate as `err(LoadError)`.
- `dto/summary-request.ts` -- `{ from: CalendarDate; to: CalendarDate }`.
- `dto/summary-response.ts` -- `{ entries: Array<{ occurredOn: CalendarDate; headline: string }> }`. Only the fields the presenter needs; `id` and `loggedAt` are not exposed.

**Application layer -- repository port modification**

- `src/application/ports/entry-repository.ts` -- add `findInRange(from: CalendarDate, to: CalendarDate): Promise<Result<Entry[], LoadError>>`. Define `LoadError = { kind: 'storage-corrupt' | 'storage-io'; detail: string }` alongside the existing `SaveError`. Keep them as separate types so each method advertises only the failures it actually produces.

**Adapter layer -- new CLI files (`src/adapters/cli/`)**

- `summary.controller.ts` -- parses `from` and `to` strings via the injected `ParseDate` dependency (same `parseDate` function used by `create-entry.controller.ts`). If either parse fails, calls `presenter.presentFailure({ kind: 'invalid-date', raw })`. On success, builds the `SummaryRequest` DTO with typed `CalendarDate` values and calls the interactor, then passes the `Result` to the presenter.
- `summary.presenter.ts` -- `SummaryCliPresenter` implementing `SummaryOutputPort<SummaryCliViewModel>`. View model shape: `{ outcome: 'success' | 'error'; message: string; exitCode: 0 | 2 }` (mirroring `CreateEntryCliViewModel`). Empty list renders `No entries in range.` with exit 0. Non-empty list renders joined lines of `YYYY-MM-DD  headline` (two-space separator). Each failure kind maps to a human-readable message with exit 2.

**Infrastructure layer**

- `src/infrastructure/cli/commands/summary.command.ts` -- Commander wiring. Registers `summary` as a command with `--from <date>` and `--to <date>` as required options. Action handler calls `composeSummary`, writes the view model's message to stdout (success) or stderr (error) based on outcome, and exits with the view model's exit code. This duplicates the try/catch + write + exit shell from `entry.command.ts` (deliberate; see ticket 003).
- `src/infrastructure/cli/composition-root.ts` -- add `composeSummary(filePath: string)` returning `{ controller }`. Wires `JsonFileEntryRepository`, `SummaryInteractor`, `SummaryCliPresenter`, and the existing `parseDate` parser. No id-generator needed (read path only).
- `src/infrastructure/cli/bin/worklog.ts` -- register the new command via `.addCommand(summaryCommand())`.

**Adapter layer -- repository implementation**

- `src/adapters/persistence/json-file-entry.repository.ts` -- implement `findInRange`. Read the JSON file (no lock needed for reads), parse via existing `parsePersistedEntries`, filter rows where `occurredOn >= from && occurredOn <= to` (string comparison, ISO dates), reconstruct `Entry` instances via `Entry.create` for each row. Missing file returns `ok([])`.

**Tooling**

- `package.json` -- remove the `"build": "tsc --noEmit"` script. It duplicates `typecheck` and misleadingly implies a compiled build artefact. The CLI runs via `tsx`; there is no build step.

**Skill extension**

- `plugins/work-log/skills/worklog/SKILL.md` -- extend the existing skill (do not create a separate skill). Use the `/skill-creator:skill-creator` skill for guidance on description triggers, examples, and structure. Changes:
  - Broaden the description's trigger phrases to cover read intents ("what did I work on", "summarise yesterday", "review last week's log", "show me my entries for X").
  - Document both CLI signatures: `worklog entry -d <date> "<headline>"` and `worklog summary --from <date> --to <date>`.
  - Explain date resolution: agent resolves relative ranges to concrete ISO dates (single-day: both flags equal; "last week": seven-day window ending today; etc.). CLI takes only ISO dates.
  - Preserve the existing "use the user's words verbatim" guidance for the write path.
  - Add output rule for the read path: pass the CLI's stdout through to the user verbatim; do not re-summarise the lines unless the user asks for a narrative.

#### Reuse -- do not reimplement

- `parseDate` from `src/infrastructure/parsers/time.parsers.ts` -- returns `Result<CalendarDate, undefined>`; same `ParseDate` type alias used by `create-entry.controller.ts`.
- `parsePersistedEntries` from `src/infrastructure/parsers/persisted-entry.parsers.ts` -- same Zod parser used on the write path for round-tripping persisted data.
- `Result` / `ok` / `err` from `src/shared/result.ts`.
- `Entry.create` for reconstructing domain entities from persisted rows.
- `JsonFileEntryRepository` -- extend with `findInRange`, do not replace.

#### Testing strategy

All tests follow red-green TDD: write the failing test first, then implement until green.

**Unit tests:**

- `summary.interactor.test.ts` -- empty result returns `ok` with empty entries array; single-day result includes all matching entries; multi-day result is sorted by `occurredOn` descending; entries on the same day are tie-broken by `loggedAt` descending; storage error from repository propagates as `err(LoadError)`.
- `summary.controller.test.ts` -- mock input port and presenter; verify that a parse failure on `--from` routes through `presentFailure` with `{ kind: 'invalid-date', raw: <the bad string> }`; same for `--to`; success path forwards typed `CalendarDate` values unchanged to the interactor.
- `summary.presenter.test.ts` -- empty entries list renders `No entries in range.` with exit 0; single entry renders one line in `YYYY-MM-DD  headline` format; multiple entries render in the order received (presenter does not re-sort); each failure kind (`invalid-date`, `storage-corrupt`, `storage-io`) renders a human-readable message with exit 2.
- `json-file-entry.repository.test.ts` (extension) -- `findInRange`: missing file returns `ok([])`; file with entries across multiple dates filters correctly to the inclusive range; returned values are `Entry` instances (not raw rows); `storage-corrupt` error path (malformed JSON); `storage-io` error path (unreadable file).

Run all tests: `yarn test`.

**Type checking:** `yarn typecheck` (runs `tsc --noEmit`). There is no compiled build step.

#### Verification steps

After implementation, manually verify end-to-end:

```bash
# Seed a few entries across dates
WORKLOG_DATA_DIR=$(mktemp -d) && export WORKLOG_DATA_DIR
yarn worklog entry -d 2026-05-01 "Shipped auth token rotation"
yarn worklog entry -d 2026-05-01 "Reviewed PR #412"
yarn worklog entry -d 2026-05-03 "Refactored shipping gateway"
yarn worklog entry -d 2026-05-06 "Added summary command"

# Verify output: lines sorted descending, two-space separator, exit 0
yarn worklog summary --from 2026-05-01 --to 2026-05-06

# Verify empty range: message printed, exit 0
yarn worklog summary --from 2026-01-01 --to 2026-01-02

# Verify bad date: error to stderr, exit 2
yarn worklog summary --from not-a-date --to 2026-05-06
```
