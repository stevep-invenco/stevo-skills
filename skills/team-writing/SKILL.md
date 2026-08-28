---
name: team-writing
description: >-
  Voice and structure for any written artifact shared with the team - explainers,
  decision logs, proposals, investigation write-ups, announcements, onboarding
  primers, whatever the destination. Use whenever the user wants something
  "written up for the team", "made readable for everyone", "turned into a doc",
  "presented to the team", or wants research, findings, an architecture, an
  incident, or a plan documented for an audience broader than the author - even
  if they never name a document type. Also use when updating such a document
  (flipping a decision status, adding a section). If the reader is a mixed group
  of teammates rather than the user themself, this skill applies.
---

# Writing for the team

## The voice

Write as a senior engineer walking into a meeting room to present. You have done the
research and understand the system conceptually, without having gone deep into every
implementation detail. The room is mixed: backend, frontend, a product owner - different
strengths, thought processes and experience levels. The job is alignment: everyone leaves
with a high-altitude understanding and enough context to ask questions or challenge
assumptions. You are not writing to prove how much you found; you are writing so the
room can think alongside you.

The controlling test for every sentence: **this page will be up on a projector.** A room
of people cannot read fine print on a screen. If a detail only matters to the person
implementing it, it does not belong in the main flow - it belongs in a collapsed section
at the bottom. The main flow should survive being read aloud, top to bottom, in a few
minutes.

## The universal skeleton

Every team-facing artifact makes the same move: ramp the room up, deliver the payload,
hide the fine print. In order:

1. **Scope callout** (optional, top of page). One callout saying what the doc is NOT
   about, when the title invites a wrong assumption. Preserve any callout the user has
   already placed.

2. **Intro paragraph.** Two or three sentences: the problem, what this doc gives the
   reader, and any legend they need to read it (e.g. decision statuses).

3. **Context ramp** - before the payload appears. Assume the room is green to the
   subject and catch them up without condescension. Say out loud that not knowing is
   fine ("only two people have worked on it since - this section is the catch-up").
   The ramp usually has these beats:
   - *What the thing actually is.* People may only know the surface (the spec files,
     the UI, the acronym); tell them what is really behind it, in a paragraph.
   - *The one fact that drives everything below*, stated in bold on its own. Then
     explain the constraint or force it creates by starting from what the room already
     knows and showing what changes (e.g. "on a normal EC2 box the host is ours...
     Fargate takes the host away"). End with the trade-off stated plainly and whether
     it is accepted - never leave a trade-off hanging.
   - *Readiness.* If prerequisites are already solved, say so as an "if": "**if** we
     pick an approach that uses X, the blocker is gone." Keeps prerequisites distinct
     from the payload itself.

4. **The payload** - the decision, explanation, findings or proposal. See the shaping
   notes below for how each type carries itself.

5. **What happens next** (when there is action). Numbered tickets or steps with a
   one-line scope each, linked. End with "Done looks like:" - one concrete, observable
   outcome anyone in the room can picture ("pick any request, find its log, jump to its
   trace").

6. **Not this work.** One line listing what is out of scope.

7. **Fine print.** Everything detailed - config keys, comparison tables, quoted
   documentation evidence, raw data - goes into collapsed toggles at the bottom. Never
   delete the evidence; hide it. The person challenging an assumption expands the
   toggle; the projector never shows it.

Not every artifact needs every part - a short explainer may be only ramp and payload.
Drop parts deliberately, never reorder them.

## Language rules

- Short paragraphs, complete sentences, one idea per paragraph. Prose carries the
  reasoning; bullets carry only enumerable facts.
- Bold the one sentence in each section that the room must not miss.
- Define jargon inline exactly where it first appears, one plain line per term ("Two
  names worth knowing: ..."). No glossary section.
- Judgments in plain words ("supported is not a reason to choose it"), not hedged
  analysis-speak.
- One simple diagram where flow or shape matters: ASCII in a code fence, showing the
  shape, not every config key.
- Hyphens, never em-dashes.
- No internal-workspace references: scratchpads, local file paths, agent or chat
  artifacts, superseded working docs. The page must read as if written directly for the
  team.
- Naming people and their in-flight work is fine ("Steve is reading further into
  dd-trace") - it tells the room who unblocks what. Flag it to the user if it feels
  sensitive.

## Shaping the payload by artifact type

The skeleton holds; the payload section flexes.

- **Decision log.** Legend in the intro: **Decided**, **Parked** (explored, not taken),
  **Pending**. One section per decision, status in the heading as emoji + word
  (✅ / 🅿️ / ❌ / ⏳). Lead with the option the official docs recommend. Options set
  aside get one paragraph each with the reason - not a full section. Pending decisions
  name the candidates, the current lean and why, and who or what unblocks them. It is a
  living log: statuses flip in place by editing the section, never by appending a new
  document, and parked options stay on the page with their reasons.
- **Explainer / primer.** Organize around the questions the room would actually ask, in
  the order they would ask them. Each section earns its place by changing what the
  reader can do or challenge.
- **Investigation / incident write-up.** Lead with the finding, then how you know
  (evidence summarized, raw material in toggles), then what to do about it.
- **Proposal.** Lead with the recommendation, then the forces that shaped it, then the
  alternatives as one-paragraph set-asides with reasons.

This skill is about voice and structure only. Platform mechanics (Notion syntax, where
to file a page) belong to the destination's own skill - consult it alongside this one.
