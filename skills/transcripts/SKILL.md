---
name: transcripts
description: >-
  Retrieves raw meeting transcripts from Zoom My Notes (Zoom plugin) and
  Granola (MCP `granola`) for Zoom meetings, Slack huddles, and ad hoc calls,
  and explains how they are archived under `rituals/`. Use when fetching or
  pulling a meeting transcript, checking exactly what someone said in a
  meeting, archiving a recurring meeting (retro, tech huddle, TDRI, standup,
  manager catch-up), or when a broader task needs the original meeting
  dialogue. Also use before the first Zoom or Granola tool call in a turn.
---

## Sources

Two sources hold raw meeting transcripts. Prefer Zoom; use Granola when Zoom
has no note for the meeting (Slack huddles, ad hoc calls).

| Source  | Tool source   | Covers                                  | Speaker names | Timestamps |
| ------- | ------------- | --------------------------------------- | ------------- | ---------- |
| Zoom    | Zoom plugin   | Zoom meetings Steve attended (My Notes) | Yes           | Yes        |
| Granola | MCP `granola` | Huddles and ad hoc calls (desktop app)  | No            | No         |

Never try either via the browser. If the tool is missing or errors, stop and
raise rather than working around it.

## Zoom

Transcripts come from Zoom My Notes (the AI Companion attendee-side note
taker), not from host cloud recordings. A `zoom_meeting` search result with
`has_transcript: false` does not establish that a My Notes transcript is
absent; check My Notes regardless.

1. Find the note: `search` with datasource `zoom_my_notes`, `query` set to the
   meeting name. Titles are the meeting name plus local start time, e.g.
   `Sprint Retro 2026-09-22 10:31(GMT+10:00)`. Each result carries a
   `file_id`, which is the note id.
2. Fetch the transcript with `my_notes_get_note_content`, `noteId` set to that
   `file_id` and `include=transcript`. Segments are
   `.transcript.items[]` with `start_time`, `end_time`, `speaker_id`, `text`.
   Resolve names through `.transcript.speakers[]` (`speaker_id` to
   `display_name`).
3. `get_meeting_assets` (meeting UUID) also returns the note, shaped
   differently: `.my_notes.transcript.transcript_items[]` with `start`, `end`,
   `text`, where `text` is already prefixed with `Speaker: `.
4. Times are offsets from transcript start. Archived transcripts use local
   wall-clock times, so add each offset to the meeting start time from the note
   title.
5. If the client persists a large response to a file instead of returning it
   inline, extract with `jq` against whichever shape applies, e.g.
   `jq -r '.my_notes.transcript.transcript_items[] | "\(.start) --> \(.end)\n\(.text)\n"'`.

## Granola

1. `list_meetings` with a `custom` range spanning several days around the
   meeting. A single-day range can return nothing for a meeting that exists.
2. `get_meeting_transcript` with the meeting id. The `transcript` field is one
   string, no timestamps. Labels are audio sources, not speakers:
   `Microphone` is the recording device (Steve's when he captured the note),
   `System audio` is everyone on the call and may cover several people.

## Output format

When exporting or archiving a transcript, keep it raw: preserve source text,
labels and timestamps as returned, do not summarise, clean up, reorder, or
invent timestamps or names. This does not apply to a summary or answer the
user asked for; derive those from the transcript freely.

Timestamped sources (Zoom), one block per segment, blank line between blocks:

```text
HH:MM:SS --> HH:MM:SS
Speaker Name: what they said
```

Untimed sources (Granola), one block per segment, blank line between blocks:

```text
Label: what they said
```

## Where transcripts land

Recurring team meetings are archived under
`~/dev/lynk/rituals/<ritual>/<YYYY-MM-DD>/transcript.md` (with an optional
`notes.md` beside it). Rituals: `tech-huddle`, `tdri`, `retro`,
`manager-catchup`, `standup`. Read `rituals/AGENTS.md` before writing there; it
is an archive, so the only permitted write is adding a dated directory or
filling in a missing `notes.md`. Anything derived from a transcript (summaries,
action items, work log entries) goes in a scratchpad, the work log, Linear, or
Notion, citing the transcript by path.
