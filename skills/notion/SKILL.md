---
name: notion
description: Conventions and cached structure for working with the Invenco Notion workspace via the configured Notion MCP server — projects, project notes, cycles, pitches, and page content. Consult this skill before the first Notion MCP tool call in a turn so the call is shaped by the conventions here. Trigger whenever the user mentions Notion, asks to create/read/update a project, add a note, check a pitch, look up a cycle, or refers to any Notion page — even if they don't explicitly say "Notion". Also trigger on phrases like "add a note to project X", "what's in the project notes", "check the pitch for X", "create a project for cycle N", or when the user pastes a notion.so URL.
---

## Authentication

The Notion MCP requires OAuth each session. If a Notion MCP call fails or the tools aren't available yet, run the Notion `authenticate` tool and ask the user to open the auth URL. If the redirect page shows a connection error, ask the user to paste the full URL from the address bar and call the Notion `complete_authentication` tool with it.

## Workspace structure

The Invenco Notion workspace organises engineering work around **Projects**, **Cycles**, **Pitches**, and **Project Notes**. These are all databases linked by relations.

### Projects database

The central hub for cycle work.

- **Database URL**: `https://www.notion.so/1c132119cf028099a31bf0bde1537dda`
- **Data source**: `collection://1c132119-cf02-80ab-bbbf-000b378d1e05`
- **Default view** (table, grouped by Cycle): `view://1c132119-cf02-80a9-a199-000c0d11cfac`
- **Default template**: `1c132119-cf02-8045-9dbd-ff55227cf561` ("New Project")

| Property | Type | Notes |
|---|---|---|
| Name | title | Project name |
| Project Lead | person (limit 1) | |
| Project Team | person (multi) | |
| Project Duration | date (range) | Start/end dates for the project |
| Cycle | relation (limit 1) | Links to Cycles DB |
| Pitch | relation (limit 1) | Links to Pitches DB |
| Linear Project | url | Link to the Linear project |
| Miro | text | Miro board link |
| Slack | text | Slack channel link |

### Cycles database

Build cycles are ~5 week periods grouped into fiscal years (FY).

- **Database URL**: `https://www.notion.so/1c132119cf0280cf8ce4d7596977cd2e`
- **Data source**: `collection://1c132119-cf02-80f6-a118-000be6c0b9b1`
- **Table view** (sorted by KEY asc): `view://1c132119-cf02-80aa-a0f5-000c785806ae`

| Property | Type | Notes |
|---|---|---|
| Name | title | e.g. "Cycle 8 - FY26" |
| KEY | auto_increment_id | Sequential cycle number |
| Type | select | `Build` or `Cooldown` |
| Period | date (range) | Cycle start/end dates |

To find a cycle by name, query the table view and match by `Name`. Pass the cycle page URL as a JSON array string in the `Cycle` relation property when creating/updating a project (e.g. `"[\"https://www.notion.so/<page-id>\"]"`).

### Project Notes database

An inline database embedded in each project page under the "Project Notes" tab. Each project has its own filtered view showing only notes related to that project.

- **Data source**: `collection://1c832119-cf02-80c3-a105-000bc724edfb`

| Property | Type | Notes |
|---|---|---|
| Name | title | Note title |
| Type | select | e.g. `Meeting`, and others TBD |
| Created | date | Auto-set creation timestamp |
| Project | relation | Back-link to the Projects DB |
| Related Links | text | |
| Text | text | |

The Project Notes tab is not visible via `notion-fetch` on the project page — the MCP only returns the "Project Details" tab content. To find notes for a project, search for the project name with `notion-search` scoped to the project page, or search the data source directly.

### Pitches database

Pitches are the ideation/scoping documents that precede a project. Projects link to their originating pitch via the `Pitch` relation.

- **Data source**: `collection://19832119-cf02-8005-8f9c-000bf9085ca1`

When the user asks to "check the pitch" for a project, fetch the project first, extract the Pitch relation URL from properties, then fetch that page.

## Common operations

### Creating a project

1. Query the Cycles table view to find the target cycle page URL
2. Create the page using `notion-create-pages` with:
   - `parent`: `{"type": "data_source_id", "data_source_id": "1c132119-cf02-80ab-bbbf-000b378d1e05"}`
   - `template_id`: `"1c132119-cf02-8045-9dbd-ff55227cf561"` (applies the "New Project" template which sets up the tabbed layout and Project Notes inline DB)
   - Properties: `Name`, `Cycle` (as JSON array of page URL), `Linear Project` (if known)
3. If a Linear project also needs creating, do that first so the URL can be set on the Notion page

### Adding a note to a project

1. Find the project — search by name or fetch directly if you have the URL
2. Create a page in the Project Notes data source with `notion-create-pages`:
   - `parent`: `{"type": "data_source_id", "data_source_id": "1c832119-cf02-80c3-a105-000bc724edfb"}`
   - Properties: `Name` (note title), `Type` (e.g. "Meeting"), `Project` (JSON array with the project page URL)
   - `content`: the note body in Notion markdown
3. The note will appear under the project's "Project Notes" tab because of the relation

### Reading project notes

1. Fetch the project page to get its URL
2. Use `notion-search` with `page_url` set to the project page ID to find child pages
3. Or search the Project Notes data source directly: `notion-search` with `data_source_url: "collection://1c832119-cf02-80c3-a105-000bc724edfb"` and a query matching the project name
4. Fetch individual note pages for their full content

### Updating page content

1. Always fetch the page first to get current content — `notion-update-page` with `update_content` command requires exact `old_str` matches
2. Use `update_content` with search-and-replace operations for surgical edits
3. Use `replace_content` only when rewriting the entire page body — it will fail if child pages or databases would be deleted unless you preserve them with `<page url="...">` tags

### Querying a database view

Use `notion-query-database-view` with the view URL to get filtered/sorted results matching the view's configuration. This is the fastest way to list projects, cycles, etc.

## Notion MCP quirks

- **Tabbed pages**: Project pages use a tabbed layout ("Project Details" / "Project Notes"). The `notion-fetch` tool only returns the content of the first tab. Inline databases in other tabs are invisible to fetch — use search to find their contents.
- **Relations are page URLs**: Relation properties are JSON arrays of Notion page URLs, not IDs. Always pass them as `"[\"https://www.notion.so/<page-id>\"]"`.
- **Date properties use expanded format**: Split into `date:<prop>:start`, `date:<prop>:end`, and `date:<prop>:is_datetime` (0 for date, 1 for datetime).
- **Data source vs database**: The MCP distinguishes between databases (which can have multiple data sources/views) and data sources (collections). Use `data_source_id` as the parent type when creating pages, not `database_id`, especially for multi-source databases.
- **Templates matter**: Always use the "New Project" template when creating projects — it sets up the tabbed layout and the inline Project Notes database. Without it, the project page is just a blank page.
- **Fetch before update**: The `update_content` command requires exact string matching on `old_str`. Always fetch the page first and use the exact content strings from the response.
