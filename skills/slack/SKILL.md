---
name: slack
description: >-
  Conventions and a cached directory of users + channels for working with the
  Invenco Slack workspace (`invencoteam.slack.com`) via the `claude_ai_Slack`
  MCP server — reading channels and threads, searching messages, and posting
  messages or drafts. Also covers posting via the Slack Web API directly (bot
  tokens, `chat.postMessage`/`chat.update`, Block Kit `rich_text` for correct
  list/code formatting). Consult this skill before the first
  `mcp__claude_ai_Slack__*` call in a turn so you can skip user/channel ID
  lookups and follow the posting conventions here, AND before any direct `curl`
  to `slack.com/api` — the formatting rules differ between the two paths and
  getting them wrong produces broken bullets/bold. Trigger whenever the user
  mentions Slack, asks you to read/search/post/DM/reply, refers to a teammate
  by first name (Dave, Joe, Nathan, Cody, Ashish, Gerd, Plus, Marc, Michael,
  Greg, James), or names a channel like `#development`, `#engineering`,
  `#datadog-errors`, or `#pr-fire-hose` — even if they don't explicitly ask for
  the skill. Also trigger on standup-related phrases like "post my standup",
  "send my standup", "standup update", "write my standup".
---

## Workspace

- Single workspace: `invencoteam.slack.com` (Invenco / Lynk).
- Current logged-in user: **Steven Prentice** (`U07KH4X8PR8`).

## Team directory

When the user refers to a teammate by first name, resolve to the user ID below and skip the `slack_search_users` round-trip. If a name is ambiguous (e.g. two Michaels), ask before guessing. If someone is named who is **not** in this list, fall back to `slack_search_users` and offer to add them to this skill afterwards.

| First name   | Full name      | Role                              | User ID        | Email                          | TZ                  |
| ------------ | -------------- | --------------------------------- | -------------- | ------------------------------ | ------------------- |
| Dave         | Dave Scott     | Founder / CEO                     | `U0GH8PJMU`    | dave.scott@invenco.net         | Australia/Canberra  |
| Joe          | Joe Swallow    | Head of Product                   | `U01946E5XHA`  | joe.swallow@invenco.net        | Australia/Canberra  |
| Nathan       | Nathan Harris  | Platform / Customer Support       | `U07T34L6DK3`  | nathan.harris@invenco.net      | Australia/Canberra  |
| Cody         | Cody Jenkins   | Head of Engineering               | `U052LHZA66A`  | cody.jenkins@invenco.net       | Australia/Canberra  |
| Ashish       | Ashish Tilara  | Principal Engineer                | `U03M4FAU5M3`  | ashish.tilara@invenco.net      | Australia/Canberra  |
| Gerd         | Gerd Wittchen  | Senior Engineer                   | `U0AHAR8EH25`  | gerd.wittchen@invenco.net      | Australia/Canberra  |
| Plus         | Plus Pingya    | Senior Engineer                   | `U028ER9QUBC`  | plus.pingya@invenco.net        | Asia/Bangkok        |
| Marc         | Marc Rubio     | Senior Engineer                   | `U0AM1RG2DC3`  | marc.rubio@invenco.net         | Australia/Brisbane  |
| Michael      | Michael Ebens  | Principal Frontend Engineer       | `U06NTLN8J6P`  | michael.ebens@invenco.net      | Australia/Hobart    |
| Greg         | Greg Boers     | Data Engineer                     | `U019S5XAYE6`  | greg.boers@invenco.net         | Australia/Canberra  |
| James        | James Arthur   | Engineer (GitHub: jjarthur-invenco) | `U09VBRJRPU3`  | james.arthur@invenco.net       | Australia/Canberra  |
| Steve / me   | Steven Prentice | (the user — current Slack login) | `U07KH4X8PR8`  | steve.prentice@invenco.net     | Australia/Canberra  |

### Mention syntax

Slack mentions are NOT `@firstname` — that renders as plain text and won't notify. Use `<@USER_ID>` in message bodies, e.g. `<@U019S5XAYE6>` to ping Greg. This applies to both `slack_send_message` and `slack_send_message_draft`.

## Channel directory

| Channel        | ID            | Type            | Purpose                                                                                                            |
| -------------- | ------------- | --------------- | ------------------------------------------------------------------------------------------------------------------ |
| `#development`     | `G286KAVGW`   | private         | The dev team's primary chat. Most-used channel — all dev team conversation happens here. High-signal for context. |
| `#engineering`     | `C08R9J2D69W` | public          | Where Platform / Customer Support interact with the engineering team. Used during the rotating support week.       |
| `#datadog-errors`  | `C07TN31R39B` | public          | Datadog log-monitor alert feed. **Each alert is a top-level message; discussion lives in the thread** — always `slack_read_thread` before assuming an alert is unhandled, someone may have triaged or silenced it. The datadog skill recommends starting here for "check datadog errors" / "see what's broken" / "triage alerts" requests. |
| `#pr-fire-hose`    | `C0APNUXN859` | public          | PR review request feed. Engineers post GitHub PR links here when they need reviews/approvals. High-volume broadcast — each PR is a top-level message. Convention: add a `:white_check_mark:` reaction to your own post once it's been reviewed/merged so others know to skip it. |

(Other channels TBA — when the user mentions a channel not listed here, use `slack_search_channels` and offer to add it.)

### Slackbot

Slack's built-in system user is `USLACKBOT`. It posts daily reminders (e.g. the standup prompt in `#development`) and reactji-driven workflows. Don't `<@USLACKBOT>`-mention it — the ping is meaningless. When you see a Slackbot message that looks like a teammate posted it, it's a scheduled reminder, not a person; reply in the thread underneath rather than re-prompting the channel.

### Standup updates

A daily standup reminder is posted by Slackbot in `#development` (`G286KAVGW`) at ~9:01 AM AEST with the text "Write-up what you did yesterday for stand-up." Each team member replies in that thread with their update.

When the user asks to post their standup:

1. **Find today's standup thread.** Search for the Slackbot reminder in `#development` using `slack_search_public_and_private` with query `from:<@USLACKBOT> in:<#G286KAVGW> "stand-up"` scoped to today. Extract the parent `message_ts`.
2. **Compose the update.** Flat format (no groups):
   ```
   <timeframe>
   - <bullet>
   - <bullet>
   ```
   Grouped format (bold subheadings, e.g. from the `standup` skill) — **put a blank line before every subheading**:
   ```
   <timeframe>
   **<Group>**
   - <bullet>

   **<Group>**
   - <bullet>
   ```
   - The timeframe line (e.g. "Yesterday", "Friday", "Last week") comes from the user's input or defaults to "Yesterday".
   - Bullets should be **meaningful at a glance** - never just a ticket ID or branch name. Describe what was actually done in plain language. `ENG-1234` on its own is useless; "finished the bill-holds retry logic (ENG-1234)" tells the reader something.
   - Keep it terse and informal - match the channel register.
   - **Blank line before each bold subheading is mandatory** when groups are present. Slack's markdown→rich-text conversion (in `slack_send_message`) keeps a bullet list "open" across a following `**bold**` line, so a heading placed directly after bullets gets sucked into the list's indentation and renders as an indented item instead of a flush-left heading. A blank line closes the list so the heading sits flush-left. The *first* group right under the timeframe line doesn't strictly need it (the timeframe isn't a list), but add it everywhere for consistency. This is a Slack-rendering fix the posting layer owns — don't ask the `standup` skill to change its surface-agnostic output.
3. **Show the composed text in this chat and wait for the user's OK.** Don't use `slack_send_message_draft` for standups — see the note below.
4. **On approval, send directly** with `slack_send_message`, `channel_id: G286KAVGW`, `thread_ts` set to the parent message ts.

If no standup thread is found for today, tell the user - don't post a top-level message.

> **Why direct-send, not a Slack draft, for standups.** When Claude sends via `slack_send_message`, Slack renders `-` bullets as real `•` and auto-appends a `*Sent using* <@U0AF947DA3E|Claude>` attribution stamp (the workspace's Claude app, bot `U0AF947DA3E`) — matching how teammates like Marc and Gerd post. A `slack_send_message_draft` that the user sends by hand goes out as a plain human post: no stamp, and the agent's markdown bullets are at the mercy of the composer. Steve wants the stamped, properly-bulleted format, so the review gate for standups is **in this chat** (show text → get OK → direct send), not a Slack-side draft. This is standup-specific; the general "prefer drafts" posture below still holds for everything else.

## When to read Slack

Reach for Slack reads when the user's request implies recent team conversation is the source of truth. Strong signals:

- "What's going on with X?" / "any updates on Y?" / "did anyone mention Z?"
- "What did `<person>` say about ...?"
- The user references a Slack-synced Linear ticket (see the linear skill — Slack threads sync back to Linear comments).
- A bug, deploy, or incident the user is investigating, where the team likely discussed it informally.
- Catch-up requests: "what did I miss in #development?" / "summarise this morning's chat".

Default to `#development` for engineering-internal context and `#engineering` for support-week issues. Don't read both unless the question genuinely spans them.

### Read tools — pick the right one

- `slack_read_channel` — pull recent messages from a channel by ID. Use when you need a chronological window.
- `slack_read_thread` — fetch a single thread when you have the parent `ts`. Threads carry the real detail; channel views often show only the parent.
- `slack_search_public` / `slack_search_public_and_private` — keyword search across messages. Use `from:<@USER_ID>` and `in:<#CHANNEL_ID>` filters to narrow. Prefer this when you don't know which channel a discussion happened in.
- `slack_search_users` / `slack_search_channels` — only when the directory above doesn't have what you need.

Fan out reads in parallel when independent (e.g. one `read_channel` per channel, or one `read_thread` per ticket) — don't fetch sequentially.

## When to post to Slack

**Default posture: don't post unless the user has asked you to.** Slack messages are visible to the team and can't be silently undone. Reading is free; posting is a side-effect.

The user may explicitly ask:

- "Post in #development that ..." — direct send is fine.
- "Reply in that thread saying ..." — direct send is fine, in thread.
- "Draft a message to Cody about ..." — use `slack_send_message_draft` so the user can review before it goes out.
- "Let Greg know ..." — ambiguous; default to a draft and confirm before sending.

When in doubt, prefer `slack_send_message_draft` over `slack_send_message` — a draft the user approves and sends manually is strictly safer than a message that needed to be deleted.

### Posting conventions

- **Reply in thread**, not in channel, whenever you're responding to an existing message. Pass `thread_ts` to `slack_send_message`. Breaking out of a thread fragments the conversation and pings everyone again.
- **Mention with `<@USER_ID>`** (see the directory above). Plain-text `@name` doesn't notify.
- **Tone**: terse, lowercase-ish, no signature, no "Hi team!" preamble. Match the channel's existing register — `#development` is informal, internal dev chat. Don't open with pleasantries the user didn't write themselves.
- **No emoji** unless the user used one or the surrounding thread is using them. Don't sprinkle ✅ / 🎉 / 🚀 by default.
- **No AI disclaimers** ("As an AI...") and don't *type* a "Generated with Claude" footer yourself. Note this is distinct from the `*Sent using* <@U0AF947DA3E|Claude>` stamp Slack auto-appends to any message sent via `slack_send_message` — that stamp is Slack-side, not text you write, and is fine to let through (Steve actively wants it on standups; see the Standup section).
- **Code and links**: use Slack's mrkdwn — `` `inline code` ``, triple-backtick blocks, `<https://example.com|label>` for labelled links. Plain URLs auto-link.
- **Long content** (more than ~5 lines, or anything with screenshots / tables) — confirm with the user first; consider whether a Linear comment, doc, or canvas (`slack_create_canvas`) is a better surface than a long Slack message.

### Posting via the Web API directly (bot tokens)

Some automations post with a bot token via `curl` instead of the MCP — e.g. the pr-firehose bot (`prfirehosebot` / "PR Fire Fighter", token at `~/dev/lynk/.config/slack-token`, scopes `chat:write` + `reactions:write`, channel-limited by membership). The formatting rules on this path are DIFFERENT from the MCP, and getting them wrong is the #1 mistake:

- The MCP's `slack_send_message` accepts **GitHub-style markdown** (`**bold**`, `- bullets`, `1.` lists, ` ```ts ` blocks) and converts it to Slack's native rich text. Looks perfect.
- The raw API `text` field is **mrkdwn**, not markdown: `**bold**` renders as literal asterisks, `- ` / `• ` bullets are plain characters (no hanging indent on wrap), `1.` lists are plain text, and ` ```ts ` ignores the language. Result: visibly degraded messages.

**Rule: for any direct-API message containing lists, headings-as-bold, or multi-paragraph structure, do NOT use `text` mrkdwn — send Block Kit `rich_text` blocks.** That is the same internal format Slack's own composer produces, so lists get real bullets/numbers with hanging indents. Plain `text` mrkdwn is acceptable only for short one-liners (`*bold*`, `_italic_`, `` `code` ``, a single ``` block).

Block cheat-sheet (all nested under one `{"type": "rich_text", "elements": [...]}` block):

| Element | Use for | Notes |
|---|---|---|
| `rich_text_section` | paragraphs / text runs | children: `{"type":"text","text":"...","style":{"bold":true\|"italic":true\|"code":true\|"strike":true}}`; mentions: `{"type":"user","user_id":"U..."}`; links: `{"type":"link","url":"...","text":"label"}`; emoji: `{"type":"emoji","name":"white_check_mark"}` |
| `rich_text_list` | bullet / numbered lists | `"style": "bullet"` or `"ordered"`; each element is a `rich_text_section` (one per list item); optional `"indent"` for nesting |
| `rich_text_preformatted` | code blocks | no language/syntax highlighting on this path (that needs a file-snippet upload — usually not worth `files:write`) |
| `rich_text_quote` | blockquotes | |

Worked example (post or update — `chat.update` takes the identical payload plus `ts`):

```json
{
  "channel": "C0APNUXN859",
  "thread_ts": "<parent_ts>",
  "text": "fallback for notifications",
  "blocks": [
    { "type": "rich_text", "elements": [
      { "type": "rich_text_section", "elements": [
        { "type": "text", "text": "Issues to consider:", "style": { "bold": true } }
      ]},
      { "type": "rich_text_list", "style": "bullet", "elements": [
        { "type": "rich_text_section", "elements": [
          { "type": "text", "text": "fixture seeds " },
          { "type": "text", "text": "billStatus", "style": { "code": true } },
          { "type": "text", "text": " implicitly" }
        ]}
      ]},
      { "type": "rich_text_preformatted", "elements": [
        { "type": "text", "text": "await retry(() => ...)" }
      ]}
    ]}
  ]
}
```

Gotchas:

- **Always include the top-level `text` field** as notification fallback even when sending `blocks`.
- **Newlines live inside `text` runs** (`"\n\n"`), not between blocks — separate blocks get no implicit blank line.
- **`chat.update` / `chat.delete` only work on the token's own messages.** A bot can't edit MCP-posted or human messages, and vice versa.
- **`reactions.add`/`remove`** are per-identity: a bot can't remove a reaction a human (or another token) added.
- **`chat:write` is membership-gated for bots** — invite the bot to a channel before posting (`/invite @bot-name`); that membership is also the only way to "scope" a bot to specific channels.
- Build the JSON in a temp file (`/tmp/*.json`) and `curl -d @file` — inline shell quoting of nested Block Kit JSON is error-prone.

### Cross-posting and DMs

- DMing yourself (Steve, `U07KH4X8PR8`) is the lowest-stakes destination — fine for "save this as a note to self" patterns. Pass the user ID as `channel_id`.
- DMing a teammate is higher-stakes than posting in `#development` — the recipient sees a personal ping, not a passive channel message. Always draft first for DMs unless the user explicitly says "send".
- Don't cross-post the same message to multiple channels without asking — channel hygiene matters.

## Slack ↔ Linear synced threads

Triage tickets raised from Slack are bidirectionally synced: Slack thread replies appear in Linear (tagged "via Slack"), and Linear comments don't always sync back. **When a thread is Slack-synced, reply in the Slack thread**, not via `mcp__linear-server__save_comment` — the Slack reply mirrors back into Linear automatically and pings the watchers correctly.

Detection and step-by-step is in the linear skill (`Slack-synced threads` section). Key reminder: parse the synthetic marker comment to get `channel_id` and `thread_ts`, then post via `slack_send_message`.

## Searching effectively

- `from:<@U019S5XAYE6>` — messages by Greg.
- `in:<#G286KAVGW>` — limited to `#development`.
- `before:2026-04-01` / `after:2026-04-01` — date bounds.
- Quote multi-word phrases: `"deploy failed"`.
- Combine: `from:<@U052LHZA66A> in:<#G286KAVGW> "rollback"` — Cody talking about rollback in #development.

`slack_search_public_and_private` covers private channels Steve is in (including `#development`); `slack_search_public` skips them. Default to public when the question is about cross-team chatter, public-and-private when it's likely internal to the dev team.

## Common pitfalls

- **`@firstname` doesn't notify.** Always `<@USER_ID>`.
- **Posting in channel instead of thread.** If you're responding to a message, you almost always want `thread_ts`.
- **Sending instead of drafting** when the user said "let X know" / "tell X" — those are ambiguous; default to a draft.
- **Reading the parent message and assuming you have the thread.** Channel views show parents only; call `slack_read_thread` for the replies.
- **Searching without channel scope.** A bare keyword search across the whole workspace is noisy; add `in:<#...>` whenever you have a hint.
- **Treating `slack_search_users` as the first step.** This skill's directory should cover ~all day-to-day mentions; only fall back to search for someone outside the dev/leadership group.
