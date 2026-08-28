---
name: pr-firehose-review
description: Performs one sweep of the Invenco `#pr-fire-hose` Slack channel (`C0APNUXN859`). For each new PR post it threads a single combined context-and-status reply, kept current via edits. All channel writes go through the `PR Fire Fighter` bot identity via the Slack Web API; the Slack MCP is used for reading only. Designed to be invoked manually as `/pr-firehose-review since:<YYYY-MM-DD>` - either as a one-shot or wrapped in `/loop` for continuous operation. Each iteration is fully self-contained so the loop never accumulates context across runs. Use this skill only when the user explicitly invokes it; it is not auto-triggering.
---

## What this skill does (one iteration)

Each iteration runs **two passes** over the channel:

**Pass A - State refresh (cheap, no content work).** For messages where the bot already has a combined reply in the thread, re-check each PR's GitHub state, `chat.update` the reply with fresh per-PR statuses, and sync the parent reactions. A message is **terminal** only when **every PR in it** is merged or closed; once terminal, the message is left alone.

**Pass B - Context + status for new messages.** For messages with no bot reply in the thread and no terminal reactions, spawn one subagent that gathers context on all PRs in the message, then post a single combined thread reply with the backstory and per-PR status lines. One reply per parent, always.

End of iteration: one-line summary to stdout (e.g. "Pass A: 5 refreshed (2 state changes); Pass B: 3 context posts").

## Identities and write paths

- **Reads** (channel, threads): Slack MCP (`slack_read_channel`, `slack_read_thread`).
- **All channel writes** (thread replies, reactions): the **`PR Fire Fighter` bot** (`prfirehosebot`, user `U0B8MPY903V`) via the Slack Web API. Token: `xoxb-` at `~/dev/lynk/.config/slack-token`, scopes `chat:write` + `reactions:write`, channel-limited by membership to `#pr-fire-hose`.
- **DMs to Steve** (failure escalations): Slack MCP `slack_send_message` with `channel_id: U07KH4X8PR8`. The bot token has no `im:write`, so it cannot DM - don't try.
- **Message formatting**: the combined reply uses **plain `text` mrkdwn** (not Block Kit). The format is short lines with emoji shortcodes and `<url|text>` links - no bullet lists, no bold headlines that need `rich_text`. Plain mrkdwn renders this correctly and is trivial to `chat.update`.
- **Legacy reactions (pre-bot era)**: messages handled before June 2026 carry managed reactions under **Steve's** name (old `xoxp-` token). The bot cannot remove another identity's reactions - `reactions.remove` only ever removes the bot's own. Treat any managed-set reaction as readable state regardless of who set it, never attempt to "fix" Steve-era ones, and accept that old messages may show stale leftovers. No migration - this was an explicit decision.

## Slack prose style (applies to every word the skill posts)

Channel readers skim. Walls of text make people angry and deliver nothing. Rules, non-negotiable:

- NEVER use em-dashes. Hyphens or sentence splits only.
- No semicolon-chained lists. Use bullets or separate lines.
- No parenthetical asides. If it matters, give it its own short sentence. If it doesn't, cut it.
- Short bites. One idea per line. Chunk with line breaks freely.
- Context replies target 6-10 short lines total. If you're over, cut the least useful line, repeat.
- Don't pad. No "I hope this helps", no restating the PR title in prose, no throat-clearing.

### Reaction state machine

| Reaction                  | Source                                | Meaning                                            |
|---------------------------|---------------------------------------|----------------------------------------------------|
| `:loading:`               | This skill, transient                 | "The bot has claimed this message and is working." Added before Pass B work starts, removed when it completes (success or failure). |
| `:git-merged:`            | This skill, mirrored from GitHub      | All PRs in the message are terminal, at least 1 merged. **Terminal marker** - only applied when every PR is terminal; the message is ignored from here on |
| `:pr-closed:`             | This skill, mirrored from GitHub      | Closed-without-merging counterpart. Same all-terminal rule |
| `:hourglass_flowing_sand:`| This skill, combined-state marker     | At least 1 PR is still awaiting review. Pending dominates - shown whenever any PR has no decision yet. Not terminal |
| `:git-approved:`          | This skill, combined-state marker     | EVERY live PR is approved (non-live siblings merged). The whole post is approved. Not terminal - keep polling until all merge |
| `:git-changes-requested:` | This skill, combined-state marker     | No PR awaiting, and at least 1 PR has `reviewDecision: CHANGES_REQUESTED` |
| `:github-discussion:`     | This skill, combined-state marker     | No PR awaiting or changes-requested, and at least 1 PR has a review/comment from a non-author, non-bot human |
| `:white_check_mark:`      | Humans (channel convention)           | Human "approved/done" signal. Treated like `:git-approved:` - not terminal; never removed by the skill |

Managed set (the only reactions the skill adds/removes): `loading`, `git-merged`, `pr-closed`, `git-approved`, `git-changes-requested`, `github-discussion`, `hourglass_flowing_sand`. `:white_check_mark:` is a human signal - read it, never write it.

Aggregation rule: each PR maps to **one** state (highest-priority wins). The parent then gets **one** combined state reaction = the **least-advanced** state across ALL PRs in the post (the post is only as done as its least-done PR). A single approved PR does NOT make the post approved. Precedence for a live post (first match wins, inspect every PR): any awaiting review -> `hourglass_flowing_sand`; else any changes-requested -> `git-changes-requested`; else any in discussion -> `github-discussion`; else (every live PR approved) -> `git-approved`. `git-approved` requires ALL live PRs approved; `git-merged`/`pr-closed` only when ALL PRs are terminal (see below). Terminal posts may carry both `git-merged` and `pr-closed` when outcomes are mixed; otherwise the live parent carries exactly one state reaction.

### Per-PR state model (multi-PR messages)

State is intrinsically **per-PR**, but reactions are **per-message**. The rules that reconcile the two:

1. **A message is terminal only when every PR in it is terminal** (merged or closed). Terminal reactions (`:git-merged:`, `:pr-closed:`) go on the parent only at that point - never while any sibling PR is still live.
2. **While any PR is live**, the parent carries a single combined state reaction = the least-advanced state across ALL PRs (see the Aggregation rule above). An approved or merged sibling does NOT pull the parent up to approved/merged while another PR is still awaiting, in discussion, or changes-requested - the laggard wins. Each PR's individual outcome stays visible in the combined reply's status lines. This keeps "has terminal reaction -> safe to ignore" true for routing.
3. **Multi-PR messages get a single bot-maintained combined reply** in the thread - backstory up top, one status line per PR, kept current via `chat.update` until the message goes terminal.

Single-PR messages degenerate cleanly: the PR's state maps straight onto the parent reactions, the combined reply has one status line.

### Per-message routing

For each non-terminal parent message, read its thread (`slack_read_thread`) and check for a bot reply (`U0B8MPY903V`):

1. **Has `:git-merged:` or `:pr-closed:`** -> fully terminal. Skip entirely - no context, no refresh, no thread read.

2. **Bot reply exists in thread** -> Pass A (state refresh). `chat.update` the existing reply with fresh statuses, sync parent reactions.

3. **No bot reply** -> Pass B posts the combined reply. This includes messages that already have `:git-approved:`, `:github-discussion:`, or other reactions - the combined reply is the per-PR breakdown, and parent-level reactions alone don't tell you which PR they refer to.

## Loop vs skill boundary

This skill is **one full sweep**. To run continuously, the user wraps it externally:

```
/loop /pr-firehose-review since:2026-05-15
```

Do not put `/loop` inside the skill. The skill should always be safe to invoke as a one-shot. The loop is a separate concern (cadence, stop conditions) that the user controls from the outer prompt.

## Why one subagent per message

Pass B pulls a diff + ticket into context. If that landed in the orchestrator's context, a long-running loop would balloon and degrade fast. So each message's work happens in a fresh foreground subagent, and only a small structured payload returns. The orchestrator stays lean across many messages and many iterations.

One subagent handles ALL PRs in a message. For homogeneous batches (same ticket, mechanical bumps) the subagent naturally deduplicates the backstory. For heterogeneous multi-PR posts it writes per-PR "what" descriptions. Either way, one subagent call per message - not one per PR.

Run subagents **sequentially** (default `Agent` behavior - just await each call before launching the next).

## Prerequisites and preflight checks

Before doing anything, verify:

1. **`gh` CLI authenticated.** Run `gh auth status`. If not authenticated, DM Steve (`U07KH4X8PR8`, via MCP) and exit.

2. **Bot token valid.** Check `~/dev/lynk/.config/slack-token` exists and is readable - this is the `xoxb-` bot token for `prfirehosebot`. Verify with:
   ```bash
   curl -sS -X POST https://slack.com/api/auth.test \
     -H "Authorization: Bearer $(cat ~/dev/lynk/.config/slack-token)"
   ```
   Expect `"ok": true` and `"user_id": "U0B8MPY903V"`. If the file is missing, `invalid_auth`, or a different identity, DM Steve (via MCP) with what's wrong and exit.

3. **`since:` arg present.** If the user invoked the skill without `since:<date>`, ask them once for it and exit. Don't guess a default - the loop iterations should be reproducible.

## Step 1: Pull and bucket messages

Use `mcp__claude_ai_Slack__slack_read_channel` on `C0APNUXN859` with a window covering the `since:` date through now. Read only top-level messages (not threads).

Bucket each message per **Per-message routing**:

- **Ignore bucket** - terminal (has `:git-merged:` or `:pr-closed:`). Do nothing.
- **Non-terminal** - read the thread (`slack_read_thread`). If a bot reply (`U0B8MPY903V`) exists -> **Refresh bucket (Pass A)**, Step 3a. Otherwise -> **Context bucket (Pass B)**, Step 2 + Step 3b.

Terminal reactions count for routing **no matter who set them** - the bot's, Steve's legacy ones, and humans' all read the same.

## Step 2: Extract PR URLs

GitHub PR URLs match `https://github.com/<org>/<repo>/pull/<number>`. A single message may contain multiple. Extract all of them. If a message has no PR URLs, skip it - it's not a PR post, just noise in the channel.

## Step 3a: Pass A - state refresh

For each message in the Refresh bucket, extract the PR URLs and fetch each PR's current GitHub state directly - no checkout, no subagent:

```bash
gh pr view <num> -R <org>/<repo> --json state,reviewDecision,author,reviews,comments
```

From the responses, compute each PR's state:
- `state == "MERGED"` -> terminal: merged
- `state == "CLOSED"` (closed without merging) -> terminal: closed
- `reviewDecision == "APPROVED"` -> approved
- `reviewDecision == "CHANGES_REQUESTED"` -> changes-requested
- Has at least 1 review or comment that counts as "real discussion" -> discussion. A comment counts when ALL of these are true:
  - Author is NOT the PR author
  - Author is NOT in the noise-bot list: any login matching `*[bot]`, the well-known noise list (`dependabot`, `renovate`, `codecov-commenter`, `github-actions`), or `linear` (the Linear-GitHub integration posts linkback templates and synced thread mirrors)

Examples:
- Comment by `marc-invenco` saying "looks good to me" -> counts.
- Comment by `linear` (linkback OR synced engineer comment) -> doesn't count.
- Comment by `dependabot[bot]` -> doesn't count.
- Comment by the PR author themselves -> doesn't count.

Then compute the **desired parent reaction** per the Aggregation rule (single combined state):
- **All PRs terminal** -> `git-merged` (if any merged) and/or `pr-closed` (if any closed), nothing else state-wise.
- **Any PR live** -> exactly one combined state reaction, the least-advanced across ALL PRs (first match: any awaiting -> `hourglass_flowing_sand`; else any changes-requested -> `git-changes-requested`; else any in discussion -> `github-discussion`; else every live PR approved -> `git-approved`), and NO terminal reactions. A finished sibling's outcome lives in the combined reply, not the parent.

Then sync: compare desired vs current. Add missing via `reactions.add`; remove no-longer-applicable bot reactions via `reactions.remove`. Removal only ever affects the bot's own - Steve-era and human reactions are untouchable; `no_reaction` on remove is benign (usually means the stale reaction belongs to someone else - leave it).

**Important:** only touch the managed set. Never `white_check_mark`, never anything else a human put on.

**Combined reply maintenance:** the bot's combined reply was already found during bucketing (Step 1's thread read). If there are multiple bot replies (legacy format from pre-redesign), use the one whose text contains PR status lines (lines starting with a state emoji like `:hourglass_flowing_sand:`, `:git-approved:`, `:git-merged:`, etc.). If no combined-format reply exists among the bot's replies (old format with per-PR context messages), skip message editing - just maintain parent reactions.

To update the combined reply:
1. Split the existing text into backstory (everything above the first PR status line) and status section (the PR status lines).
2. Rebuild the status section from the fresh GitHub state using the status line format (see Step 4).
3. Preserve the backstory verbatim.
4. `chat.update` with backstory + rebuilt status section.

If this refresh takes the message terminal, do one final update, then apply terminal reactions.

**Stale `:loading:` cleanup:** if Pass A finds `:loading:` on a message with an existing bot reply, remove it - leftover from a crashed iteration.

No content reply on Pass A - the `chat.update` and reactions speak for themselves.

## Step 3b: Pass B - context + status (for new messages)

This pass gives channel readers the story behind the PR(s) in one glance. **No code review. No checkout.**

For each message in the Context bucket:

**Add `:loading:`** to the parent (treat `already_reacted` as benign). Spawn one foreground subagent (`subagent_type: general-purpose`) with the context prompt below. After it returns: post the combined reply (Step 4), apply reactions (Step 5), **remove `:loading:`** (treat `no_reaction` as benign, do it even on failure paths).

### Prompt template for the per-message context subagent

```
Build a context summary for a PR post in #pr-fire-hose. You are writing for engineers skimming a busy Slack channel. No code review - your job is orientation, not critique.

The parent message contains these PR URLs:
<LIST_ALL_PR_URLS>

Gather per PR:
1. gh pr view <num> -R <org>/<repo> --json title,body,headRefName,baseRefName,additions,deletions,changedFiles,state,reviewDecision,author,reviews,comments
2. gh pr diff <num> -R <org>/<repo> | head -200   (enough to see the shape; don't read more)

Then find the shared context:
3. Look for a Linear ticket: check PR titles, branch names, and bodies for an ENG-XXXX identifier.
   - If found: load the Linear MCP tool via ToolSearch ("select:mcp__linear-server__get_issue"), then fetch the issue. Read its title, description, and project name.
   - If the issue belongs to a project and the ticket alone doesn't explain WHY, you may also fetch the project (mcp__linear-server__get_project) for one line of backstory.
   - If no ticket is found, say so in the backstory field ("no linked ticket") and work from the PR bodies alone.
4. If the WHY is still thin, check Notion for the bigger picture. Load tools via ToolSearch ("select:mcp__notion-server__notion-search,mcp__notion-server__notion-fetch"). Pick the database by the work's shape:
   - Feature/project work -> Project pages: notion data source 1c132119cf028099a31bf0bde1537dda, then Pitches: 19832119cf028080957fce45e82f96de
   - Tech-debt / reliability / improvement work -> TDRI database: notion data source 26f32119cf0280fab862e3a98a3394a5. Signals that a PR is TDRI-shaped: refactor/cleanup/hardening/migration language, strict-mode or type-safety passes, flaky-test fixes, observability or alerting tweaks, no feature ticket or a ticket with no project.
   Search by the Linear project name, the PR's feature name, or the tech-debt subject. Skim the matched page's opening section only - you want ONE line of backstory, not a document summary. Hard budget: at most one search + one page fetch per database, max two databases. If nothing matches quickly, move on.

Synthesize - WRITING RULES, non-negotiable:
- NEVER use em-dashes. Hyphens or sentence splits only.
- No semicolon-chained lists. No parenthetical asides.
- Short bites. One idea per line. Concrete: name files, endpoints, tables.

Determine if the batch is HOMOGENEOUS (all PRs serve the same ticket with the same mechanical change) or HETEROGENEOUS (PRs do different things or serve different aspects of the ticket).

Return JSON ONLY (no prose), shape:
{
  "ticket": "ENG-XXXX" | null,
  "ticket_url": "https://linear.app/invenco/issue/ENG-XXXX" | null,
  "backstory": "<1-3 short lines: the ticket/project story. What problem, whose problem. For homogeneous batches, include what the PRs do here since they all do the same thing.>",
  "homogeneous": true | false,
  "prs": [
    {
      "pr_url": "<URL>",
      "repo_short": "<repo name without org, e.g. accounts-service>",
      "number": 260,
      "what": "<for heterogeneous: 1 short fragment describing what THIS PR does. for homogeneous: null>",
      "size": "<e.g. +7/-7, 4 files>",
      "gh_state": {
        "state": "OPEN" | "MERGED" | "CLOSED",
        "review_decision": "APPROVED" | "CHANGES_REQUESTED" | "REVIEW_REQUIRED" | null,
        "author_login": "<github username>",
        "non_author_human_comment": true | false
      }
    }
  ]
}

Or on failure:
{ "error": "<short reason>" }
```

## Step 4: Post the combined reply

The combined reply is posted by the **bot** via `chat.postMessage` with `thread_ts` set to the parent. Uses **plain `text` mrkdwn** - no Block Kit needed since the format is short lines with emoji and links, no bullet lists.

### Format

**Backstory section** (top):
- Line 1: ticket link (bold, if present) + opening backstory line
- Lines 2-3: remaining backstory (keep to 1-3 lines total)

**Blank line separator**

**PR status lines** (bottom, one per PR):

For **homogeneous** batches (all PRs do the same thing):
```
:emoji: <pr_url|repo_short#number> - <status_label>
```

For **heterogeneous** batches (PRs do different things):
```
:emoji: <pr_url|repo_short#number> - <what> - <status_label>
```

State -> emoji/label mapping (pick the single highest-priority state per PR):

| PR state (priority order) | Emoji | Label |
|---|---|---|
| merged | `:git-merged:` | merged |
| closed without merge | `:pr-closed:` | closed |
| approved | `:git-approved:` | approved |
| changes requested | `:git-changes-requested:` | changes requested |
| human discussion, no decision | `:github-discussion:` | in discussion |
| open, no engagement | `:hourglass_flowing_sand:` | awaiting review |

### Example: homogeneous (9 PRs, same ticket, same change)

```
*<https://linear.app/invenco/issue/ENG-5367|ENG-5367>*  ddd-core 5.4.0 - StaleRepoError now includes entity type and version.
Services pinned on 5.3.2. This sweeps them current.
Mechanical bump - only code change is test assertion wording.

:hourglass_flowing_sand: <https://github.com/invenco/accounts-service/pull/260|accounts-service#260> - awaiting review
:hourglass_flowing_sand: <https://github.com/invenco/sales-service/pull/824|sales-service#824> - awaiting review
:git-approved: <https://github.com/invenco/warehousing/pull/643|warehousing#643> - approved
:hourglass_flowing_sand: <https://github.com/invenco/supply/pull/227|supply#227> - awaiting review
```

### Example: heterogeneous (3 PRs, one ticket, different repos doing different things)

```
*<https://linear.app/invenco/issue/ENG-5365|ENG-5365>*  e2e circle-back - failing e2e runs invisible to caller pipelines.

:github-discussion: <https://github.com/invenco/common/pull/688|common#688> - shared CI trigger/check scripts - in discussion
:hourglass_flowing_sand: <https://github.com/invenco/e2e/pull/114|e2e#114> - approve_caller job on completion - awaiting review
:git-approved: <https://github.com/invenco/accounts-service/pull/259|accounts-service#259> - reference adopter, wires the gate - approved
```

### Example: single PR

```
*<https://linear.app/invenco/issue/ENG-5300|ENG-5300>*  Strict-mode cleanup in the fulfillment aggregate.
Removes 12 ts-expect-error suppressions around nullable order fields.

:hourglass_flowing_sand: <https://github.com/invenco/warehousing/pull/640|warehousing#640> - awaiting review
```

### Always post

The combined reply is posted for every message Pass B processes, regardless of PR state. Even if every PR is already merged, the per-PR breakdown is useful context for anyone opening the thread later. The bot reply's presence in the thread is the routing signal (bot reply = handled), so skipping would leave the message stuck in Pass B's orbit forever or require a separate marker. Always post, no exceptions.

### Posting via the Web API

```bash
curl -sS -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $(cat ~/dev/lynk/.config/slack-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d @/tmp/pr-firehose-reply.json
```

Where the JSON file contains:
```json
{
  "channel": "C0APNUXN859",
  "thread_ts": "<parent_ts>",
  "text": "<the full mrkdwn text>"
}
```

For updates:
```bash
curl -sS -X POST https://slack.com/api/chat.update \
  -H "Authorization: Bearer $(cat ~/dev/lynk/.config/slack-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d @/tmp/pr-firehose-update.json
```

Where the JSON file contains:
```json
{
  "channel": "C0APNUXN859",
  "ts": "<bot_reply_ts>",
  "text": "<the full updated mrkdwn text>"
}
```

### Handling subagent errors

- Subagent returns `{ "error": "..." }` -> thread one-liner `_Skipped: <short reason>_` (retries next iteration since no bot reply exists to gate it into Pass A).
- Subagent returns a payload but some PRs have errors -> post the combined reply with whatever succeeded. For errored PRs, include them in the status lines as `:hourglass_flowing_sand: <link> - context pending`.

## Step 5: Apply reactions

The Slack MCP exposes no `reactions.add`/`remove` tool, so the skill calls Slack's REST API directly with the **bot token**. Reactions appear under `PR Fire Fighter`.

```bash
# Add
curl -sS -X POST https://slack.com/api/reactions.add \
  -H "Authorization: Bearer $(cat ~/dev/lynk/.config/slack-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"channel":"C0APNUXN859","timestamp":"<parent_ts>","name":"<emoji-name>"}'

# Remove (same shape, different endpoint)
curl -sS -X POST https://slack.com/api/reactions.remove ...
```

Expected response: `{"ok":true}`. Common failure modes:
- `already_reacted` (on add) - benign, treat as success.
- `no_reaction` (on remove) - benign. Also what you get when the stale reaction belongs to Steve (legacy) or a human - not the bot's to remove; leave it.
- `invalid_auth` / `token_expired` - DM Steve (via MCP) with regen instructions and exit the iteration.
- `ratelimited` - honour `Retry-After`; if still failing, log and continue.

### Computing desired reactions from `gh_state`

Map each PR to its **single highest-priority state** (first match wins, same priority order as the status line table):
1. `state == "MERGED"` -> merged (terminal)
2. `state == "CLOSED"` -> closed (terminal)
3. `review_decision == "APPROVED"` -> approved
4. `review_decision == "CHANGES_REQUESTED"` -> changes-requested
5. `non_author_human_comment == true` -> discussion ("human" excludes the PR author and all bot/integration accounts)
6. Otherwise -> awaiting review

Then combine to a **single message-level reaction** = the least-advanced state across ALL PRs:
- **All PRs terminal** -> `git-merged` (any merged) and/or `pr-closed` (any closed). No live-state reactions.
- **Any PR live** (first match wins, scan every PR):
  1. Any PR `awaiting review` -> `hourglass_flowing_sand`
  2. Else any PR `changes-requested` -> `git-changes-requested`
  3. Else any PR `discussion` -> `github-discussion`
  4. Else (every live PR `approved`, rest merged) -> `git-approved`
  No terminal reactions on a parent with any live PR.

### When to apply

**Pass B (context):**
- Combined reply posted successfully -> apply the computed set.
- Subagent errored entirely -> do NOT apply any reactions; next iteration retries.

**Pass A (refresh):**
- Sync to current state. Add anything missing from the managed set, remove any bot-owned reaction no longer applicable. Legacy (Steve-era) managed reactions are immovable - accept them.

## Step 6: Iteration summary

One line to stdout:

```
Iteration complete: Pass A refreshed <N> (<X> state changes); Pass B posted context on <M> (<K> skipped: <reasons>).
```

Don't recap individual PRs - they're already in Slack.

## Things to avoid

- **Don't post multiple thread replies per parent.** One combined reply, always. Updates via `chat.update`.
- **Don't post outside the thread.** All Slack output is threaded replies to the parent message.
- **Don't ping people.** Use `<pr_title>` not `<@author>`; the people watching the channel can see the parent already.
- **Don't send structured bodies as Block Kit.** The combined reply is plain `text` mrkdwn. No `rich_text` blocks.
- **Don't violate the prose style section.** Em-dashes, semicolon chains, parenthetical asides, and walls of text are all defects.
- **Don't put terminal reactions on a parent while any of its PRs is still live.** That ejects a live PR from tracking forever.
- **Don't try to remove reactions the bot didn't add.** Steve's legacy reactions and human reactions are out of reach by design.
- **Don't spawn one subagent per PR.** One subagent per message. It handles all PRs in that message.

## Why this design holds up under `/loop`

- **No accumulated context**: each iteration is self-contained; per-message work is in subagents; the orchestrator sees only small JSON payloads.
- **Stateless tracking**: the combined reply is re-found every iteration by author (`U0B8MPY903V`) in the thread. Its presence IS the routing signal - no separate marker reaction needed. Status lines are parsed and rebuilt from fresh GitHub state. Durable channel state, not skill memory.
- **Idempotent**: bot reply presence gates re-posting context, `reactions.add` is idempotent, `chat.update` with the same content is a visual no-op.
- **Safe to interrupt**: messages without a bot reply get retried; an interrupted Pass B that never posted the reply leaves the message in the Context bucket.
- **Cheap steady state**: no checkout, no review toolkit, no worktree. The whole iteration is `gh pr view` calls + Slack API calls.
- **Single write identity**: every Slack artifact the skill manages is owned by the bot token.
- **One message per parent**: no N+1 reply explosion for multi-PR posts.
