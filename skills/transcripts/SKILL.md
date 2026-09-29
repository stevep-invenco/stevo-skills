---
name: transcripts
description: How to fetch a raw meeting transcript given Steve's workspace setup - Zoom My Notes via the Zoom plugin for Zoom meetings, Granola via the `granola` MCP for Slack huddles and ad hoc calls - and the raw output format they get written in. Use whenever the user mentions a meeting transcript, transcripts, "what was said in", "pull the transcript", "grab the recording/notes from the meeting", Zoom notes, My Notes, Granola, huddle notes, or asks to archive a ritual (retro, tech huddle, TDRI review, manager catch-up, standup) into `rituals/`, AND before the first Zoom or Granola tool call in a turn so the call hits the right source.
---

## Sources

Two sources hold raw meeting transcripts. Prefer Zoom; use Granola when Zoom has
no note for the meeting (Slack huddles, ad hoc calls).

| Source  | Tool source     | Covers                                 | Speaker names | Timestamps |
| ------- | --------------- | -------------------------------------- | ------------- | ---------- |
| Zoom    | Zoom plugin     | Zoom meetings Steve attended (My Notes) | Yes           | Yes        |
| Granola | MCP `granola`   | Huddles and ad hoc calls (desktop app) | No            | No         |

Never try either via the browser. If the tool is missing or errors, stop and
raise rather than working around it.

## Zoom

Transcripts come from Zoom My Notes (the AI Companion attendee-side note
taker), not from host cloud recordings. Meeting search results report
`has_transcript: false` even when a My Notes transcript exists, so ignore that
flag.

1. Find the meeting: `search` with datasource `zoom_my_notes`, filtering by
   title and date. Note titles are the meeting name plus start time, e.g.
   `Sprint Retro 2026-09-22 10:31(GMT+10:00)`.
2. Fetch the transcript: `get_meeting_assets` with the meeting UUID, or
   `my_notes_get_note_content` with the note file id and `include=transcript`.
3. Read `.my_notes.transcript.transcript_items[]`. Each item has `start`, `end`
   and `text`; `text` is already prefixed with the speaker name. Timestamps are
   offsets from meeting start.
4. Results are large and get persisted to a file. Extract with `jq`, e.g.
   `jq -r '.my_notes.transcript.transcript_items[] | "\(.start) --> \(.end)\n\(.text)\n"'`.

## Granola

1. `list_meetings` (widen the date range; usage is intermittent).
2. `get_meeting_transcript` with the meeting id. Speakers are labelled
   `Microphone` (Steve) and `System audio` (everyone else).

## Output format

Keep transcripts raw. Do not summarise, clean up, or reorder. Write one block
per segment, blank line between blocks:

```text
HH:MM:SS --> HH:MM:SS
Speaker Name: what they said
```

## Where transcripts land

Recurring team meetings are archived under `~/dev/lynk/rituals/<ritual>/<YYYY-MM-DD>/transcript.md`
(with an optional `notes.md` beside it). Rituals: `tech-huddle`, `tdri`, `retro`,
`manager-catchup`, `standup`. Read `rituals/AGENTS.md` before writing there; it is
an archive, so the only permitted write is adding a dated directory or filling in a
missing `notes.md`. Anything derived from a transcript (summaries, action items,
work log entries) goes in a scratchpad, the work log, Linear, or Notion, citing the
transcript by path.
