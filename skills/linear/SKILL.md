---
name: linear
description: Conventions and guidance for working with Linear via the configured Linear MCP server — issues, comments, triage, status transitions, and Slack-synced threads. Make sure to use this skill whenever the user mentions Linear, "tickets", "ENG-XXXX" identifiers, triage, or asks you to read/write/close/comment on issues, AND whenever you are about to call any Linear MCP tool — even if the user does not explicitly ask for the skill. Consult this skill before the first Linear MCP call in a turn so the call is shaped by the conventions here.
---

## Identifiers and teams

- Issues are identified by `<TEAM_PREFIX>-<NUMBER>` (e.g. `ENG-4914`). Pass this directly as the `id` / `issueId` / `parentId` parameter — no separate UUID lookup needed.
- The primary team is `Engineering`. When a user says "the engineering team" or just refers to a ticket without a team, default to `team: "Engineering"`.
- Status names are not always standard. Engineering uses: `Triage`, `Backlog`, `Todo`, `Ready`, `In Progress`, `In Review`, `Ready to Deploy`, `Acceptance Testing`, `Done`, `Canceled`, `Duplicate`. To **close as fixed**, set `state: "Done"`. To close as won't-do/duplicate, use `Canceled` or `Duplicate`. If unsure, call `list_issue_statuses` first.

## Listing and triage

- Use `list_issues` with `state: "triage"` (the status type, lowercase) to pull the triage queue. `team: "Engineering"` scopes to the right backlog.
- Comment threads carry the real status of a triage ticket — the workflow state is often stale. Always pull `list_comments` on each triage issue before summarising; derive status from the conversation (e.g. "fix deployed", "blocked on vendor", "fixed but never moved out of triage").
- Comments come back in `updatedAt` order (default desc). The newest comment is usually the most informative — read top-down.
- Fan out the comment fetches in parallel — one `list_comments` call per issue in a single tool-call batch. Don't fetch sequentially.

### Triage summary output format

When the user asks for a "triage summary" (or similar — "what's in triage", "summarise triage", "tldr triage"), default to a compact markdown table. Order rows by **actionability**: closeable / awaiting-confirm first, blocked or parked next, untouched last — so the eye lands on what needs doing.

| Ticket                                                | Title       | Status                                        |
| ----------------------------------------------------- | ----------- | --------------------------------------------- |
| [ENG-XXXX](https://linear.app/invenco/issue/ENG-XXXX) | short title | emoji + one-line status derived from comments |

**Status emoji legend** (use these consistently so the table scans fast):

- ✅ **Fixed / fix deployed** — closeable, or awaiting reporter confirmation
- ⏸ **Blocked** — on a vendor, another team, or a business decision; note who/what
- 🔍 **Diagnosed** — root cause known, no fix shipped yet
- 🚧 **In flight** — someone is actively working on it
- 🆕 **Untouched** — filed recently, no investigation yet

Keep the status cell to one line. If the ticket needs more context than fits, append a short bullet list under the table for those rows only — don't bloat every row.

## Slack-synced threads

Triage tickets raised from Slack are bidirectionally synced: Slack thread replies appear in Linear (tagged "via Slack"), and replies posted into the Slack thread appear back as Linear comments. The Linear MCP **does not** expose the "Post to Slack" toggle — `save_comment` only creates a Linear-native comment, which will **not** mirror back into the Slack thread or notify the people watching it.

When the conversation is happening in Slack, reply in the Slack thread instead. The reply will sync back into Linear automatically, so you get the Linear comment + Slack ping + correct mention behaviour in one shot.

### How to detect a synced thread

Linear injects a synthetic marker comment into the issue's comment list whenever a Slack thread is synced. It looks like:

> _"This comment thread is synced to a corresponding [thread in Slack](https://invencoteam.slack.com/archives/C08R9J2D69W/p1776095524617999?thread_ts=1776095524.617999&cid=C08R9J2D69W). All replies are displayed in both locations."_

There can be multiple markers per issue (one per Linear comment thread that got synced). Pick the most recent, or match by surrounding comment context.

### Step-by-step: post a comment into a Slack-synced ticket

1. **Pull comments** — `list_comments` with the issue identifier (e.g. `ENG-4909`).
2. **Find the marker** — grep the comment bodies for `synced to a corresponding [thread in Slack]`. Take the Slack URL from inside the link.
3. **Parse the URL** — format is `https://<workspace>.slack.com/archives/<CHANNEL_ID>/p<TS_DIGITS>` with optional `?thread_ts=<TS>&cid=<CHANNEL_ID>`. Extract:
   - `channel_id` → the path segment after `archives/` (e.g. `C08R9J2D69W`).
   - `thread_ts` → either the `thread_ts` query param verbatim, **or** reconstruct from the `p<digits>` segment by inserting a `.` before the last 6 digits (e.g. `p1776095524617999` → `1776095524.617999`).
4. **Post the reply** — `slack_send_message` with `channel_id` set to the channel and `thread_ts` set to the parent message ts. Body in standard markdown.
5. **Mention with Slack syntax** — `@greg.boers` won't notify; use `<@U019S5XAYE6>` (look up the user id with `slack_search_users` if you don't have it). Linear-style mentions are fine in Linear-native comments but break in Slack.
6. **Verify** — the returned `message_link` confirms it landed in the thread (`?thread_ts=` will be present). It should appear back in Linear within seconds as a "via Slack" comment.

### When to use Linear-native comments anyway

- The ticket has **no** Slack marker (i.e. wasn't raised from Slack).
- You want to leave a record on the ticket without notifying the Slack thread participants (e.g. internal note, status reasoning before closing).
- You're closing the ticket and the Slack thread is already resolved.

In those cases, `save_comment` is the right tool.

## Mentions in Linear-native comments

- Linear's `@username` (e.g. `@greg.boers`) renders correctly and notifies the user. Use this in `save_comment` bodies.
- Don't use `<user id="...">` HTML form unless you're echoing existing markup — it works but is uglier.
