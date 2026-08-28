---
name: ticket-writing
description: Write structured tickets from conversations, investigations, and plans. Use this skill whenever the user wants to create a ticket, write up work, capture a task, document a spike, or turn a conversation into trackable work — even if they don't say "ticket" explicitly. Trigger on phrases like "let's turn this into a ticket", "write this up", "create a ticket for this", "let's track this work", "write up what we found", or any intent to formalize a conversation or investigation into a work item.
argument-hint: "<context or instructions for the ticket>"
allowed-tools: Read, Grep, Glob, Write, Edit, Agent
disable-model-invocation: true
---

# Ticket Writing

The ticket you produce is the single source of truth for a piece of work. PR descriptions don't duplicate it — they link to it. Code reviewers read it to understand why things were done a certain way. Engineers picking up someone else's work start here. If a reader finishes your ticket and still has fundamental questions about the why, the scope, or the how, the ticket has failed.

**The ticket must stand alone.** A reader should never need to open a separate plan document, re-read a Slack thread, or trace back to the conversation that produced the ticket. If a detailed plan exists (from Plan Mode or elsewhere), extract its substance into the ticket — don't summarize and point elsewhere. If a conversation drove key decisions, narrate the decisions inline — don't say "as discussed" or "as settled in conversation." The ticket is the only artifact that survives.

## Workflow

### 1. Gather material

Before writing, assemble everything you can from the current conversation and workspace:

- **Conversation history** — What was investigated? What was found? What decisions did the human and agent make? What options were considered and rejected?
- **Code exploration** — Files read, patterns discovered, bugs found, architectural observations
- **Plans** — If a plan was created (e.g. Plan Mode), read the full plan. Its content gets extracted into the ticket body — the plan document itself is not an attachment.
- **External references** — Slack threads, meeting notes, existing tickets, documentation, PRs, dashboards
- **User arguments** — $ARGUMENTS may supply additional context, constraints, or destination instructions

If you're missing material for a section, ask. A thin ticket is worse than a delayed one.

### 2. Draft the ticket

Write the full ticket using the structure below. Present it in conversation for the user to review before saving anywhere.

### 3. Publish

Publish directly — no confirmation step needed. The user will read the ticket at the destination and request changes there if needed.

**Decide the destination from context, don't ask:**

- **Linear** — If the conversation involves Linear context (ENG- ticket references, linear skills loaded, linear MCP tools used, discussion of sprints/cycles/teams), write directly to Linear via the linear MCP server. This is the most common destination.
- **Other project destinations** — If the context points to a specific project or tool (e.g., work-log), write there directly.
- **Filesystem fallback** — Only save to claude temp `tickets/` dir as `<slugified-title>.md` when no destination can be inferred from context.

Never ask "where would you like to publish?" — infer it. If the inference is wrong, the user will redirect you.

---

## Formatting Principles

Tickets are read in tools like Linear whose markdown rendering makes dense prose hard to scan. Every formatting choice should optimize for readability at a quick glance.

### Structure over prose

- **Subheadings over bullet points for distinct concepts.** When describing two or more separate things (use cases, approaches, components), give each its own `###` subheading instead of cramming them into a single bullet list. Subheadings create visual anchors that let a reader jump to what they care about.
- **Short paragraphs.** If a paragraph exceeds 3-4 sentences, break it up — either with a subheading or a structural element like a list or table.
- **Bullet and numbered lists** for sequences, checklists, or sets of related items. When you have a set of items to enumerate (field names, getters, files changed), always use a vertical list — never inline them as a comma-separated run of backticked terms.
- **Tables** for comparisons, field mappings, type changes, or any data with consistent columns.
- **Code blocks** (` ``` `) for multi-line content: type signatures, queries, CLI commands, error messages, file paths.
- **Horizontal dividers** (`---`) between major sections to create visual breathing room.

### Inline monospace — less is more

Backtick every identifier in a sentence and the sentence becomes unreadable. Use inline monospace (`backticks`) only when the exact spelling matters — a type name the reader needs to search for, an API field name, a CLI flag. For concepts being discussed in prose, plain text is fine.

**Bad** — every term backticked:
> `warehouseLocationId: string` and `warehouseLocationName: string` getters return `props.warehouseLocation*` typed `string | null` → TS2322 under strict mode.

**Good** — backticks only where they earn their keep:
> The warehouseLocationId and warehouseLocationName getters declare `string` returns but their backing props are `string | null`, producing TS2322 under strict mode.

Rule of thumb: if a sentence has more than 2-3 backticked terms, rewrite it. Move dense type details into a table or code block instead.

### File paths — references, not inline

Never put file paths in parentheses inline. They break reading flow and add visual noise. Instead, collect file paths as numbered references at the end of the section or ticket, and use short reference markers in the prose.

**Bad:**
> `LocationInventory.create()` — only ever called from `PrismaLocationInventoryRepo.createLocationInventories` (`src/modules/inventory/repos/impl/PrismaLocationInventoryRepo.ts:295-309`).

**Good:**
> `LocationInventory.create()` is only ever called from `PrismaLocationInventoryRepo.createLocationInventories` [1].
>
> **References**
> [1] `src/modules/inventory/repos/impl/PrismaLocationInventoryRepo.ts:295-309`

If there are only 1-2 file paths in the entire ticket, a references section is overkill — just use a code block or omit the path if the class/method name is sufficient to locate it.

### Lists — vertical, not inline

When enumerating items (field names, getters audited, files changed, affected modules), use a vertical bullet list. Never flatten them into a comma-separated run on one line.

**Bad:**
> Audited getters: `accountId`, `accountName`, `skuId`, `skuName`, `skuDescription`, `externalSkuName`, `locationId`, `locationName`, `warehouseLocationId`, `warehouseLocationName`, `subInventories`, `reconciledAt`, `createdAt`, `updatedAt`.

**Good:**
> Audited getters:
> - accountId
> - accountName
> - skuId
> - skuName
> - ...

### Example: before and after

**Bad** — wall of text in a bullet list:
```
Adjustments are created through two use cases, both extending BaseCreateAdjustment:

- CreateAdjustmentAsWarehouse (seller/warehouse context) — takes lines without skuId, resolves SKUs via enrichSkuDataByName against the products service, then calls BaseCreateAdjustment.createAdjustment(). externalSkuName is enriched from input.externalSkuName || sku.externalSkuName (both nullable).

- CreateAdjustmentAsSystem (system context) — takes full CreateAdjustmentLineProps[] directly from the HTTP body (lines already include skuId), creates AdjustmentLine entities directly, then calls BaseCreateAdjustment.createAdjustment(). No SKU enrichment occurs — externalSkuName comes from whatever the API caller provides.
```

**Good** — subheadings with short focused blocks:
```
Both use cases extend `BaseCreateAdjustment`.

### CreateAdjustmentAsWarehouse

Seller/warehouse context. Takes lines **without** `skuId` — resolves SKUs via `enrichSkuDataByName` against the products service, then calls `BaseCreateAdjustment.createAdjustment()`.

`externalSkuName` is enriched from `input.externalSkuName || sku.externalSkuName` (both nullable).

### CreateAdjustmentAsSystem

System context. Takes full `CreateAdjustmentLineProps[]` directly from the HTTP body — lines already include `skuId`.

Creates `AdjustmentLine` entities directly, then calls `BaseCreateAdjustment.createAdjustment()`. No SKU enrichment — `externalSkuName` comes from whatever the API caller provides.
```

---

## Ticket Structure

### Title

A short phrase describing what this work accomplishes. It should make complete sense to someone who has never heard of this work before.

**Good**: "Make FulfillmentLine.skuId non-nullable"
**Bad**: "Fix skuId type issue" — which skuId? which issue?
**Bad**: "ENG-4801 follow-up" — meaningless without looking up another ticket

---

### Tracking Table

The very first thing in the ticket body. A document lifecycle log — when was this ticket created, and when was it materially changed. One row per document event.

This is **not** a place to summarize the investigation or repeat context. The Context section does that. The tracking table answers one question: "what happened to this document?"

Format: `Date | Event (one short phrase)`

**Good:**
```
| Date | Event |
|------|-------|
| 2026-05-06 | Wrote the ticket |
| 2026-05-07 | Updated scope — added AdjustmentLineDTO after tracing producers |
```

**Bad** — re-explaining the investigation in the tracking table:
```
| Date | Event |
|------|-------|
| 2026-05-06 | Spike opened — strict-mode compile errors on LocationInventory getters traced to producer/declared-type mismatches |
| 2026-05-06 | Producer-driven audit completed across all 14 non-qty getters; recommendations split into strict-mode unblock, internal cleanup, and debt follow-ups |
```
That's two rows for the same event ("wrote the ticket") with the investigation narrative stuffed in. Should be one row: `Wrote the ticket`.

A second row only appears when the document itself changes — e.g., "Updated scope due to new finding X" or "Revised execution plan after code review feedback."

---

### Context

This is the most important section. A reader with zero prior knowledge should finish it understanding exactly why this ticket exists and why it's worth doing now.

#### Lead with a situation setup

Open with a 2-3 sentence paragraph that orients a cold reader — what system, what problem, why now. This paragraph is the "elevator pitch" for the entire ticket. A reader who only reads this paragraph should walk away with a rough understanding of the work.

**Example:**
> We're enabling TypeScript strict mode across inventory-service. One of the blocking compile errors is in LocationReferenceInventory.referencesFromAdjustment(), which maps an AdjustmentDTO into a list of LocationReferenceInventoryIdentifier values. Under strict mode, four fields on the DTO don't type-check against the Identifier due to mismatched nullability.

#### Summarize linked content inline

Links to spike tickets, Slack threads, and related work are valuable — but the reader should never need to click a link to understand the ticket. Every link must be accompanied by a summary of what was found or concluded. The link is evidence; the summary is the content.

**Bad:** "See ENG-5056 for investigation results."
**Good:** "Spike ENG-5056 traced the producers for four fields across both creation paths. It found that the TS types on `AdjustmentDTO` and `AdjustmentLineDTO` disagree with the runtime invariants their producers actually enforce. (ENG-5056)"

#### What to include

- **The trigger** — What kicked this off? A bug report, a planning session, a discovery during other work, a conversation with Claude Code, a meeting decision?
- **Investigation trail** — What was explored, what was found? Reference specific evidence: production queries, code paths traced, test results, error logs. The reader should be able to follow your reasoning and verify it independently.
- **Decisions and rationale** — What approaches were considered? Why was this one chosen? If meetings or discussions informed the decision, mention them and summarize the relevant outcome.
- **Links** — Slack threads, related tickets, documentation, PRs, dashboards. Always with inline summaries.

#### Decision Trail

Track the timeline of how the solution was reached. This enables retrospective analysis — when someone asks "why did we do it this way?", the answer is here.

Include:
- What was tried first, and what happened
- What alternatives were considered and why they were rejected
- When the approach changed direction and what new information caused the shift
- Where the human disagreed with the agent's suggestion, and what they chose instead
- Where the human added constraints the agent hadn't considered
- What was deferred and why

This can be woven into the narrative or broken out as a subsection — whichever reads better for the specific ticket. The point is that the reasoning chain is preserved: the pushbacks, the redirections, the judgment calls — not just the conclusions.

---

### Scope

Always include this section with explicit headers, even if items were already mentioned in Context. Code reviewers scan this section directly during PR review — they shouldn't have to parse narrative prose to find scope boundaries.

#### In Scope

Discrete deliverables — what will be different when this ticket is done. Each item should be concrete enough that a code reviewer can verify it in the PR.

#### Out of Scope

What was deliberately excluded and why. This section exists primarily for code reviewers: when they see seemingly obvious missing functionality in a PR, they check here before asking "why didn't you also do X?"

If the work was split across multiple tickets, say so and reference the sibling tickets. Only list things that a reasonable reviewer would actually wonder about — if nobody would ask, don't clutter this section.

#### Related Work

Links to prerequisite, sibling, or follow-up tickets. Omit this subsection entirely if there are none.

---

### Execution Plan

How the work gets built. This section is split into two levels to serve different readers at different times.

#### Overview

The conceptual shape of the work — what you'd sketch on a whiteboard. This is the section a code reviewer reads to understand what the PR should look like before opening the diff.

**What to include:**

- **Behavioral contract** — What the feature does at its boundaries. Output formats, exit codes, error behavior, sort order, edge cases (empty input, invalid input, boundary values). This is what a reviewer checks a PR against.
- **Architectural approach** — The high-level strategy. Why this approach over alternatives? What existing patterns does it follow? What was deliberately deferred and why?
- **Key decisions** — Choices that shaped the implementation and aren't obvious from the architecture alone. Reference back to the Context decision trail where the decision was made.

#### Execution Detail

This section is optional. Include it when the conversation produced a detailed execution plan — from Plan Mode, a structured brainstorm, or iterative refinement during the session. If no detailed plan was produced, omit this section entirely; the Overview is sufficient.

When it exists, dump the full execution plan here without distilling or restructuring it. This is a free-form section — preserve the plan's original structure, detail level, and organization. The value is in having the complete tactical plan live inside the ticket rather than in a separate document that gets lost. File lists, type signatures, test cases, shell commands, reuse notes — whatever the plan contains, it goes here verbatim.

The only transformation to apply: if the plan references conversation context that a cold reader wouldn't have (e.g. "as we discussed above"), expand those references inline so the section stands alone.

---

## Writing Quality

**Direct and precise** — Declarative sentences, active voice. "FulfillmentLine.skuId is typed as `string | null`" beats "the type is incorrect." Cut filler phrases.

**Domain language** — Use the project's own terms consistently. Don't invent synonyms for concepts the codebase already names.

**Evidence over assertion** — "Production query returns 0 rows where skuId IS NULL" is stronger than "skuId is never null in practice." Show your work — tickets with evidence hold up over time.

**Reader-first** — Write for someone who is technically capable but has zero context on this specific problem. Every acronym, every reference to "the existing behavior" — make sure the reader can follow without having been in the room.
