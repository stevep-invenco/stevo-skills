---
name: ticket-writing
description: Write structured tickets from conversations, investigations, and plans. Use this skill whenever the user wants to create a ticket, write up work, capture a task, document a spike, or turn a conversation into trackable work — even if they don't say "ticket" explicitly. Trigger on phrases like "let's turn this into a ticket", "write this up", "create a ticket for this", "let's track this work", "write up what we found", or any intent to formalize a conversation or investigation into a work item.
argument-hint: "<context or instructions for the ticket>"
allowed-tools: Read, Grep, Glob, Write, Edit, Agent
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

### 3. Save and publish

After the user approves (or you incorporate their edits):

1. Save the ticket to claude temp `tickets/` dir as `<slugified-title>.md`
2. Ask the user where they'd like to publish it — they'll guide you to the destination

---

## Ticket Structure

### Title

A short phrase describing what this work accomplishes. It should make complete sense to someone who has never heard of this work before.

**Good**: "Make FulfillmentLine.skuId non-nullable"
**Bad**: "Fix skuId type issue" — which skuId? which issue?
**Bad**: "ENG-4801 follow-up" — meaningless without looking up another ticket

### Context

This is the most important section. A reader with zero prior knowledge should finish it understanding exactly why this ticket exists and why it's worth doing now.

**What to include:**

- **The trigger** — What kicked this off? A bug report, a planning session, a discovery during other work, a conversation with Claude Code, a meeting decision?
- **Investigation trail** — What was explored, what was found? Reference specific evidence: production queries, code paths traced, test results, error logs. The reader should be able to follow your reasoning and verify it independently.
- **Decisions and rationale** — What approaches were considered? Why was this one chosen? If meetings or discussions informed the decision, mention them and summarize the relevant outcome.
- **Links** — Slack threads, related tickets, documentation, PRs, dashboards. Links are evidence and entry points for readers who want to go deeper.
- **Conversation trail** (when the ticket originates from a conversation or Claude Code session) — Don't just state what was decided. Walk through how the decisions were reached. Where did the human disagree with the agent's suggestion, and what did they choose instead? Where did the human add constraints the agent hadn't considered? Where did the human defer a decision, and what was deferred? A reader should understand the reasoning chain — the pushbacks, the redirections, the judgment calls — not just the conclusions. This matters because the decisions often only make sense in light of the alternatives that were rejected.

The Context section reads as a short narrative — it tells the story of how you got here. Don't reduce it to terse bullet points. Think of ENG-5030 as a reference: trigger → investigation → evidence → recommendation, each flowing into the next.

### Scope

Always include this section with explicit headers, even if items were already mentioned in Context. Code reviewers scan this section directly during PR review — they shouldn't have to parse narrative prose to find scope boundaries.

#### In Scope

Discrete deliverables — what will be different when this ticket is done. Each item should be concrete enough that a code reviewer can verify it in the PR.

#### Out of Scope

What was deliberately excluded and why. This section exists primarily for code reviewers: when they see seemingly obvious missing functionality in a PR, they check here before asking "why didn't you also do X?"

If the work was split across multiple tickets, say so and reference the sibling tickets. Only list things that a reasonable reviewer would actually wonder about — if nobody would ask, don't clutter this section.

#### Related Work

Links to prerequisite, sibling, or follow-up tickets. Omit this subsection entirely if there are none.

### Execution Plan

How the work gets built. This section is split into two levels to serve different readers at different times.

#### Overview

The conceptual shape of the work — what you'd sketch on a whiteboard. This is the section a code reviewer reads to understand what the PR should look like before opening the diff.

**What to include:**

- **Behavioral contract** — What the feature does at its boundaries. Output formats, exit codes, error behavior, sort order, edge cases (empty input, invalid input, boundary values). This is what a reviewer checks a PR against.
- **Architectural approach** — The high-level strategy. Why this approach over alternatives? What existing patterns does it follow? What was deliberately deferred and why?
- **Key decisions** — Choices that shaped the implementation and aren't obvious from the architecture alone. Reference back to the Context conversation trail where the decision was made.

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
