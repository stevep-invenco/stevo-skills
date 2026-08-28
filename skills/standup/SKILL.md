---
name: standup
description: >-
  Compose a tight, glanceable stand-up recap of work already completed, from
  whatever raw material you're handed - a verbose work-log dump, scattered notes,
  a list of tickets/PRs, or a messy account of "what I did". Turns that into a
  compact, subheaded, bullets-only summary. Historic only: it recaps the past
  (Yesterday, or named past days), never plans for today. Use this skill whenever
  the user wants to write / compose / format / condense / tidy a stand-up or daily
  update, turn yesterday's work into a stand-up post, shrink a long work log into a
  scannable recap, or hands over raw activity and asks for "a stand-up" - including
  the formatting step in a worklog -> standup -> post pipeline, and even when they
  just say "standup" alongside some work material. It emits plain GitHub-flavored
  markdown (bold subheadings, dash bullets, backtick code) that posting tools render
  correctly. This skill only composes the text - it does not post anywhere and is
  not responsible for sourcing the raw material or delivering the result.
---

# Stand-up composer

Your job is to turn whatever account of recent work you're given into a stand-up
recap that a busy teammate can read in five seconds. The hard part is not writing
more - it's writing less. Raw work logs and notes are verbose, repetitive, and
full of process narration ("fanned out agents over CI history, then folded the
findings back in..."). Almost none of that survives. What survives is the outcome,
grouped sensibly, one short line each.

The reader is another engineer skimming a channel during their own morning. They
want to know *what landed* and *what's stuck*, grouped so the shape of the day is
obvious at a glance. If they need detail, they'll ask - so it is always better to
be too terse than too complete.

## The one principle

**Glanceable beats complete.** Every decision below serves this. When you're unsure
whether to keep a clause, a second sentence, or a fifth bullet, cut it. Losing
detail is expected and fine; burying the signal is the only real failure.

## Output shape

Emit exactly this structure as plain markdown, nothing before or after it (no
preamble like "Here's your standup:", no sign-off):

```
<Timeframe>
**<Group>**
- <bullet>
- <bullet>
**<Group>**
- <bullet>
```

- **Timeframe line** is the first line, plain text (not bold). Default `Yesterday`.
  Use what the material implies instead when it's clearly a different day
  (`Friday`, `Last week`). See multi-day below.
- **Groups** are bold (`**...**`) subheadings.
- **Everything else is a dash bullet.** No paragraphs, no prose, no nested
  sub-bullets unless a parent genuinely needs 2-3 tight children. Bullets only is
  the whole point - it's what makes the post scannable.

Use `**double asterisks**` for bold, not single. Posting tools read this as
GitHub-flavored markdown and convert `**x**` to real bold; a single `*x*` would
come out italic. Wrap package names, paths, and identifiers in `` `backticks` ``
(e.g. `` `@invenco/inventory-*` ``, `` `nmt` ``).

## Grouping

Group by what makes the day legible, usually a hybrid of initiative and activity:

- **Project / initiative groups** carry the substance - the named piece of work
  the bullets belong to (e.g. `**Backend NX Migration**`). These are where most
  bullets live.
- **Cross-cutting groups** collect activity that spans projects - most commonly
  `**Meetings**`, and things like `**AI Tooling**`, `**Ops**`, `**On-call**`.

Pick the 2-4 groups that best fit the actual material; don't force a fixed
taxonomy onto a day that doesn't have it. A sensible default order is Meetings
first (quick "who I synced with" context), then the day's main initiative(s),
then lighter buckets like tooling - but optimize for "the reader finds the
important stuff fast," not a rigid sequence. If everything fits under one obvious
heading, one group is fine. Don't invent groups to look busy.

## Writing the bullets

- **One line each.** Aim for under ~12 words. If a bullet wraps in a chat client,
  it's too long - tighten it.
- **Lead with the outcome, drop the process.** "Reviewed migration follow-ups for
  Inventory and Analytics" - not "fanned out agents over code/git/CI history and
  the inventory & analytics notes for gap analysis, then folded findings back in."
  The reader wants what happened, not how the sausage was made.
- **Merge duplicates.** Work logs often record the same task three times as it
  progressed. Collapse to one bullet.
- **Split dense multi-ticket sentences.** If one paragraph in the source covers
  several tickets, break it into one bullet per ticket - that's far more scannable
  than a comma-spliced run-on. (See the example: one verbose self-review sentence
  becomes the `ENG-5484` and `ENG-5487` bullets.)
- **Be meaningful at a glance.** A bare ticket ID or branch name tells the reader
  nothing. Always say what was actually done.

## Tickets and references

Two kinds of reference show up in work logs, and the test for keeping one is the
same in both cases: **can the reader act on it?**

**Ticket IDs (e.g. `ENG-5481`)** pass that test - the team recognises them, searches
on them, and can pull them up in Linear. Keep them. For ticket-scoped work, lead with
the ID so a column of related tickets lines up and scans easily:
`ENG-5481 - Generate code for Sales migration`. Where the ID is incidental to the
bullet, append it instead: `Repointed the sales jest mock to the inventory-gateway
mocks subpath (ENG-5484)`.

**PR / commit numbers (e.g. `#242`, `#660`)** only pass that test as a real,
clickable link. A bare `#242` is a magic number - nobody reconstructs a URL from it in
their head, so on its own it just sits between the reader and the message as noise. But
the fix is to *get the link*, not to drop the work. Resolve each reference in order:

1. **URL already in the source** - use it directly:
   `Shipped a CI unblocker for the deploy-tag step ([#242](https://github.com/invenco/inventory/pull/242))`.
   The link survives the posting layer - it becomes a clickable `#242` in Slack.
2. **Bare number, no URL - ground it on GitHub. Don't guess the URL from the repo
   name** - a guessed URL is frequently the wrong repo (a `#825` that reads like
   inventory work can actually live in `sales`), and a link to the wrong PR is worse
   than no link. Instead look it up. Infer the repo from the context around the
   reference (the service or repo named in the same bullet; the org is `invenco`) and
   resolve the canonical URL with `gh`:
   `gh pr view 825 --repo invenco/sales-service --json url,title`
   `gh` follows repo renames (e.g. `inventory-service` resolves to `invenco/inventory`),
   so the `url` it returns is the real one. Check the returned `title` plausibly matches
   the work you're describing - that's what stops you linking a same-numbered PR in the
   wrong repo. If the first candidate repo errors or the title doesn't fit, try the
   other obvious candidate. Link the URL `gh` hands back - never one you typed yourself.
3. **Can't ground it** - no repo context to go on, every candidate errors, the title
   doesn't match, or there's no `gh`/network - then drop the number. A dropped
   reference is honest; a fabricated or wrong link sends someone to the wrong place.

Keep grounding cheap: ask `gh` for just `url,title`, and don't chase more than the one
or two repos the context actually suggests. Never emit a bare `#number` that isn't a
link, and never emit a link you didn't get from the source or from `gh`.

## Internal notes and bookkeeping

Work logs are full of personal bookkeeping artifacts - a follow-up id like `FU-1`, a
`TDRI` entry, a private backlog number, the filename of a notes page. These mean
something to *you*; to a teammate skimming the channel they're a riddle. "Raised FU-1
to consolidate shared NX config" gives the reader a label they can't look up and a
verb (`raised`) that describes filing paperwork, not doing work.

The work itself is still worth reporting - investigating, researching, scoping, or
writing something up is real activity. Just drop the artifact and lead with the verb
that says what you actually did:

- `Raised FU-1 to consolidate shared NX config to repo root` -> `Investigated consolidating shared NX config to the repo root`
- `Raised a TDRI to roll out the import/no-duplicates eslint rule` -> `Researched an eslint rule to auto-fix duplicate imports`

It's the same instinct as the PR-number rule: a reference the reader can't act on is
noise, so keep the substance and cut the bookkeeping. Public, recognisable names are
*not* bookkeeping - a package like `` `@invenco/common-*` `` or a real eslint rule
like `` `import/no-duplicates` `` is meaningful to the reader, so keep those.

## Blockers

Stand-ups exist partly to surface what's stuck, so never silently drop a blocker.
Flag it **inline on the bullet it relates to**, made visually prominent so it still
catches a skimming eye - there is no separate Blockers section. Two ways:

- Append to the related work bullet:
  `- ENG-5487 cutover done - **blocked** on review for #660`
- Or as its own bullet under the relevant group when it isn't tied to a single
  task: `- **Blocked:** waiting on Gerd to approve the workspace config change`

Bold the `blocked` / `Blocked:` marker so it reads at a glance. "Waiting on a
review/approval" counts - surface it the same way. If there are no blockers, write
nothing about blockers; an empty "no blockers" line is just noise.

## Timeframe and multi-day

This is a backward-looking recap. **Never include a "Today" / "Next" / plans
section** - if the source material mentions future intentions ("self-review +
chasing approvals today"), drop them; they aren't part of the recap.

Usually it's a single day -> single `Yesterday` block. When the material spans
several days (e.g. a Monday update covering weekend overtime), give each day its
own dated block, each with its own subheadings:

```
Friday
**<Group>**
- ...

Saturday
**<Group>**
- ...
```

Only break out days the material actually distinguishes; don't manufacture day
splits that aren't there.

## Sourcing the material (lightweight enrichment)

The raw account is normally already in front of you (handed in the prompt or sitting
in the conversation). Work from that. You're not responsible for fetching the
day's activity from scratch - just for shaping what you're given.

Reach for external tools (Linear, Notion, Slack, files on disk, URLs) **only when**
it directly serves a better bullet, and keep it cheap:

- The input names a pointer - a ticket ID with no description, a file path, a
  project note, a PR link, a Slack permalink - and you need its contents to write a
  meaningful bullet. Follow it.
- A bullet would otherwise be meaningless (e.g. a bare `ENG-5484` with no context).
  A quick Linear lookup to get the human title is worth it.
- A bullet references a PR by bare number and you want it to read as a usable link -
  ground the real URL with one `gh pr view <num> --repo invenco/<repo> --json url,title`
  call rather than guessing (see "Tickets and references"). This one is worth doing by
  default: links are a core part of a good recap, and the lookup is cheap.

Otherwise don't go fishing - resolving every ID, fetching full PR bodies, or scanning
channels for extra color costs time and rarely improves a five-second read. When in
doubt, prefer shipping the recap over enriching it.

## Guardrails

- **Never invent work.** Everything in the recap must trace to the source material
  (or something you looked up from it). If the input is too thin to form an honest
  bullet and you can't enrich it, leave it out or ask - don't pad.
- **Don't post or deliver.** You compose the text and stop. Where it goes is
  someone else's job.
- **No meta.** Don't explain what you did, don't caveat, don't add a footer. Just
  the recap.

## Worked example

This is the canonical transformation - verbose source in, glanceable recap out.

**Input** (raw, as a work log might hand it over):

```
- Self-reviewed the @invenco/common-* -> @invenco/inventory-* switchover across
  consumer services; found 2 gaps and generated the code for both - sales jest mock
  needs repointing to the inventory-gateway /mocks subpath (ENG-5484), and
  warehousing still needed the whole switchover (ENG-5487, PR #660). Self-review +
  chasing team approvals today
- Kicked off the sales & accounts NX migrations (ENG-5481 / ENG-5482): fanned out
  agents over code/git/CI history + the inventory & analytics migration notes for
  gap analysis, then folded the findings back into the migration prompting to cut
  post-codegen rework
- Met with Gerd/Cody/Marc on the PNPM package-age risk - inv & analytics migrations
  were safe, but we added minimumReleaseAge workspace config so installs fail when
  package age can't be determined; reviewed + approved Gerd's fixes (inventory #243,
  analytics #70)
- AI sync with Gerd (filesystem layouts, skills, symlinks); also built a new nmt
  skill to rein in long Claude responses and shared it with the team
  (https://github.com/invenco/standards/pull/88)
- Raised FU-3 in my NX backlog to dedupe the jest configs across repos - low
  priority, after the migrations land
```

**Output:**

```
Yesterday
**Meetings**
- Sync with Cody, Marc, Gerd on PNPM security gates
- Sync with Gerd on AI tooling
**Backend NX Migration**
- Reviewed & approved Gerd's pnpm-cooldown fixes for Inventory ([#243](https://github.com/invenco/inventory/pull/243)) and Analytics ([#70](https://github.com/invenco/analytics/pull/70))
- PR reviews of services cutting deps from `@invenco/common-*` to `@invenco/inventory-*`
- ENG-5481 - Generate code for Sales migration
- ENG-5482 - Generate code for Accounts migration
- ENG-5484 - Generate code to import mocks from `@invenco/inventory-gateway` in Sales
- ENG-5487 - Generate code for Warehousing deps cutover `@invenco/common-*` to `@invenco/inventory-*`
**AI Tooling**
- Created `nmt` skill ([#88](https://github.com/invenco/standards/pull/88)) - formats chat output for easy reading
**Tech Debt**
- Investigated deduping jest configs across repos
```

Note what happened: the "chasing approvals today" future-work was dropped; the dense
self-review sentence was split into two ticket bullets; process narration ("fanned
out agents...") disappeared entirely. Every reference became a real link: the `nmt`
PR already had a URL in the log, so `#88` went straight in; the bare `inventory #243`
and `analytics #70` had no URL, so they were grounded with
`gh pr view 243 --repo invenco/inventory --json url,title` (the titles came back as
Gerd's pnpm-cooldown fixes, confirming the right PRs) and linked to the canonical URLs
`gh` returned. And the internal `FU-3` backlog id was cut - the work behind it survived,
rewritten from "raised FU-3..." into "Investigated deduping jest configs". Same day, a
quarter of the words, every link real, and you can read it at a glance.
