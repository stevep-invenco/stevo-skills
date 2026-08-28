---
name: tdri
description: >
  Context and operations for the TDRI (Tech Debt, Reliability, and Innovation) Notion database —
  where the Lynk team tracks tech debt, reliability work, and platform improvements between project cycles.
  Use this skill whenever the user mentions "TDRI", asks about tech debt items, wants to check what improvement
  work is queued up, or wants to create/update/query TDRI entries. Also trigger when the user asks things like
  "what's next to pick up", "any tech debt for shipping service", "add a TDRI for X", or "link this Linear ticket
  to the TDRI".
---

# TDRI: Tech Debt, Reliability, and Innovation

TDRI is the Lynk engineering team's backlog for non-project work — tech debt paydown, reliability improvements, developer experience upgrades, and platform hardening. These items are groomed and picked up between project cycles.

## Prerequisites

This skill requires the `notion-server` MCP server. If it is not available, tell the user that TDRI operations need the Notion MCP connection and stop — do not attempt to work around it.

## Notion Database

- **Database URL:** `https://www.notion.so/invenco/26f32119cf0280fab862e3a98a3394a5?v=26f32119cf02808cbdd2000ce473208b`
- **Database ID:** `26f32119cf0280fab862e3a98a3394a5`
- **Data Source:** `collection://26f32119-cf02-80db-a39a-000bb0d76f6c`
- **Default View:** `view://26f32119-cf02-808c-bdd2-000ce473208b` (table, grouped by Status, sorted by Priority descending)

Use the `notion-server` MCP tools to interact with this database. Fetch the database or query the view to get current state.

## Schema

| Property | Type | Details |
|----------|------|---------|
| Summary | title | The ticket name/description |
| Status | status | See status workflow below |
| Impact | select | 1–5 scale (set during grooming only) |
| Effort | select | 1–5 scale (set during grooming only) |
| Urgency | select | 1–3 scale (set during grooming only) |
| Priority | formula | Computed from Impact, Effort, Urgency |
| Assigned To | person | Team member(s) working the item |
| Linear | url | Link to associated Linear issue or project |
| AI Solutions | url | Legacy/unused column — ignore |

## Status Workflow

| Status | Notion group | Meaning |
|--------|--------------|---------|
| Backlog | to_do | Unprioritized pool; where new entries land |
| Groom Next | to_do | Flagged for the upcoming grooming session. Human process: each team member picks 1 from Backlog they think is important. Never set this programmatically |
| Ready | to_do | Groomed and scored, available to schedule |
| Next | in_progress | Next to be picked up (queued, not yet started - despite the Notion group) |
| Now | in_progress | Actively being worked on |
| Done | complete | Finished |
| Cancelled | complete | Won't do |

## Scoring Rules

**Impact** (1–5), **Effort** (1–5), and **Urgency** (1–3) are set exclusively by the team during grooming meetings. Never modify these values programmatically — they reflect human judgment about relative importance. **Priority** is a formula that combines them automatically.

When creating new TDRI entries, leave Impact, Effort, and Urgency blank. Set Status to "Backlog" - promotion to "Groom Next" is a human decision, never made by an agent.

## Creating New Entries

The database has a default page template, "Problem + Solution Statements" (`26f32119-cf02-8030-bba1-e351ebdce9b9`). When creating a new TDRI page, either pass it as `template_id` to `notion-create-pages`, or write the page body explicitly using the structure below (they are identical).

Set these properties:
- **Summary**: concise title describing the issue
- **Status**: `Backlog`
- Leave Impact, Effort, Urgency blank (scored during grooming)
- Set **Linear** if a Linear issue already exists
- Leave **AI Solutions** empty

### Page Body Template

Use this exact structure for the page content:

```markdown
## Problem statement

### What problem or job are we going after?

**As a** [user]
**When** [describe the user context]
**I want to** [describe user motivation]
**So I can** [expected outcome]
**But** [problem or limitations blocking achievement of the outcome]

## Solutions

### What are possible solution?

### What's the initial scope?
```

Always fill in the problem statement fields (As a / When / I want to / So I can / But) using whatever context is available from the user's request and your knowledge of the Lynk codebase. Write concrete, specific statements — not placeholders. The team can refine the wording during grooming, but a well-formed first draft is far more useful than empty brackets. If a field genuinely can't be inferred, write your best guess and note the uncertainty inline.

## Common Operations

### Query the board
Fetch the default view to get a prioritized overview:
```
notion-fetch: https://www.notion.so/invenco/26f32119cf0280fab862e3a98a3394a5?v=26f32119cf02808cbdd2000ce473208b
```
Or query the data source for filtered results:
```
notion-query-data-sources: data source URL above
```

### Check what's active or next
Query the view and filter results by Status = "Now" or "Next".

### Find related TDRIs
Use `notion-search` with relevant keywords scoped to the database's data source URL to find existing entries before creating duplicates.

### Link a Linear ticket
Update the TDRI page's **Linear** property with the Linear issue or project URL.
