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

How the work gets built. This section serves two audiences: the implementer (a roadmap) and future readers (understanding the architectural decisions behind the code).

Include the following in priority order. Every ticket should cover at least the first two; include the rest based on what the work demands:

1. **Behavioral contract** — What the feature does at its boundaries. Output formats, exit codes, error behavior, sort order, edge cases (empty input, invalid input, boundary values). This is what a code reviewer checks a PR against — if it's not in the ticket, the reviewer can't verify correctness.

2. **Approach and architectural decisions** — The high-level strategy. Why this approach over alternatives? What existing patterns or conventions does it follow? What was deliberately deferred and why?

3. **Testing strategy** — How correctness is verified. What gets unit tested, what needs integration tests, what requires manual verification? Include concrete commands where applicable. A reviewer should be able to compare the PR's actual test coverage against what was planned here.

4. **Implementation areas** — Which modules, layers, or domains get touched. Organized by architectural concern, not as an exhaustive file manifest. The architecture and conventions should dictate where files go — the plan explains what changes, not where every file lives.

If a detailed plan exists (from Plan Mode or any other source), extract its substance here. The behavioral contract, architectural reasoning, and testing strategy from the plan should all appear in the ticket. File-by-file implementation details from the plan can be trimmed — the implementer will follow the architecture's conventions for file placement.

---

## Writing Quality

**Direct and precise** — Declarative sentences, active voice. "FulfillmentLine.skuId is typed as `string | null`" beats "the type is incorrect." Cut filler phrases.

**Domain language** — Use the project's own terms consistently. Don't invent synonyms for concepts the codebase already names.

**Evidence over assertion** — "Production query returns 0 rows where skuId IS NULL" is stronger than "skuId is never null in practice." Show your work — tickets with evidence hold up over time.

**Reader-first** — Write for someone who is technically capable but has zero context on this specific problem. Every acronym, every reference to "the existing behavior" — make sure the reader can follow without having been in the room.
