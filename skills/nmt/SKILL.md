---
name: nmt
description: Re-aim and compress the reply you're about to give - lead with the high-level answer and keep it to roughly X lines, so the user gets the headline first and drills into detail only if they want it. Invoked manually as `/nmt [X] [optional question]` (e.g. `/nmt 5`, `/nmt 1 should I bump the timeout or add a retry?`). X is a soft brevity dial - lower is terser and more zoomed-out, higher leaves more room - not a hard line count. Use this skill ONLY when the user explicitly types /nmt; it is never triggered automatically. Do not invoke it on your own because a reply looks long, or because the user asked for brevity or a summary in other words - only the literal /nmt invocation counts.
---

# nmt - No More Than

You've been working at high detail and the user fired `/nmt`. Remember they're a human, not an agent: they have far less of the zoomed-in context you've built up, so when you open at the most specific point, they get lost. `/nmt` is their dial to pull you back up to altitude. Give them the headline; let them drill in if they want more.

## Reading the invocation

The argument is `[X] [optional question]`:

- A leading integer is **X**, the brevity dial. (`/nmt 3` -> X is 3.)
- Anything after the integer is a **question to answer** at that level. (`/nmt 3 should I cache this?` -> answer it, X=3.)
- **Bare `/nmt X`** with no question -> **compress your most recent substantive reply** to the X level. The user read it, found it too much, and wants the same content re-aimed higher.
- **No integer** (just `/nmt`) -> treat X as a moderate dial (~5) and compress the last reply.
- If there's nothing yet to compress (bare `/nmt` early in a chat), just answer whatever's on the table at the X level.

## What X means

X is a *vibe knob for how much detail*, not a counter to satisfy exactly. Aim for about X lines - the spirit matters more than the precise number:

- **1** -> one line. The single most useful thing: the answer, the recommendation, the verdict.
- **3-5** -> the headline plus the couple of points that actually bear on the decision.
- **10-15** -> room for a short structured view: a few bullets, the main tradeoffs.

A bigger number is *permission for more*, not a quota to fill - don't pad to reach it. And don't game a small number by cramming five clauses into one run-on line; that defeats the purpose.

## How to respond

The shift the user wants is **altitude**, not just fewer characters:

- **Lead with the conclusion** - the recommendation, the answer, the bottom line comes first, not the reasoning that produced it.
- **Cut the derivation.** They can ask "why?" or "show me" if they care. Trust them to drill in.
- **No preamble.** Skip "Great question", "Here's a summary", and restating what they asked. Every line is scarce - spend it on signal.
- **Match format to the budget.** Tiny X -> a sentence or two of plain prose. Larger X -> a few short bullets are fine. Headings are usually overkill at this size.
- **Keep the load-bearing specifics.** A path, a command, a number, a name - include it if it *is* the answer. Brevity means dropping the explanation, not the substance.

This applies to **this one response only**. Next turn, return to your normal level unless they fire `/nmt` again.

## Examples

**`/nmt 1`** (after you've laid out three migration strategies)

> Go with expand-contract - it's the only one of the three that avoids downtime here.

**`/nmt 5 should I bump the timeout or add a retry?`**

> Add the retry; don't bump the timeout.
> The failures are transient network blips, not slow responses - a longer timeout just makes each failure hang longer before failing anyway.
> A retry with backoff recovers without the user noticing.
> Cap it at 2-3 attempts so a real outage still fails fast.

**`/nmt 10 walk me through the tradeoffs`** (on choosing a queue)

> - **SQS standard**: cheapest, simplest, already in our stack - but no ordering guarantee.
> - **SQS FIFO**: ordering, lower throughput ceiling, slightly more setup.
> - **Kafka**: ordering + replay, but ops overhead we don't currently carry.
> - **For ~100/s where order doesn't matter**: SQS standard. Revisit only if you later need replay.
