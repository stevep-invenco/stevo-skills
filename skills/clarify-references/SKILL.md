---
name: clarify-references
description: >-
  Clarify references in an assistant reply that require the reader to remember
  earlier messages, inspect code, or reconstruct source material. Use when the
  user invokes /clarify-references or $clarify-references, asks what an unclear
  phrase refers to, or when reviewing a draft reveals unexplained wording such
  as "the distinction", "that behaviour", "the thing", or a code concept whose
  role has not been explained. This is a focused clarity pass, not a general
  request to shorten, simplify, or restyle an answer.
---

# Clarify references

The reader may have forgotten earlier messages, skimmed a ticket, or never read
the code. Information available to the agent is not necessarily available in the
reader's working memory.

The controlling question: **Can the reader understand what this sentence refers
to, and why it matters, without scrolling back, opening code, or reconstructing
source material?**

## Select the reply

- A bare invocation rewrites the most recent substantive assistant answer.
- An invocation with a quoted phrase focuses the correction on that phrase and
  the surrounding explanation. Integrate the correction into the answer unless
  the user asks for only the excerpt.
- When applied while drafting or through review feedback, inspect the current
  draft or the response identified by that feedback.
- If the user asks a direct question about a phrase, answer that question
  directly. Reprint the whole answer when they request a rewrite or invoke the
  skill without another instruction.

## Review and repair

Read the reply as the reader will encounter it. Earlier chat and inspected code
can establish the facts, but do not count as an explanation in the reply.

Look for pointers such as "the thing", "the distinction", "this approach",
"that behaviour", and "the existing mechanism". Also check precise names and
technical shorthand: naming a class or function does not explain its role.
These are candidates for review, not forbidden words. Leave references alone
when their meaning is obvious from nearby prose or the user's immediate question.

Where context is missing, supply the smallest explanation that makes the claim
understandable:

- Name the actual behaviour, problem, component, or decision being discussed.
- For a comparison, state which alternatives are being compared and the relevant
  difference. Put an explanation of a table row beside that row, or identify the
  row explicitly.
- For code, explain the relevant purpose and behaviour before relying on an
  identifier. A source link supports the explanation; it does not replace it.
- Explain the component's role in the scenario as far as needed for the claim.
  For example, a test's database client may prepare records and verify results
  as well as support the operation being tested and cleanup.
- When changing topics, introduce the next subject and its relationship to the
  preceding material. Do not open with an unexplained "This matters because...".

Replace empty pointing language with the explanation. Do not merely exchange
"the thing" for an equally unexplained technical name, append a glossary, or
expand every noun into a tutorial. Preserve clear passages, factual meaning,
uncertainty, and the user's requested level of detail.

Use established evidence to recover the intended meaning. If the referent cannot
be established, say what is unclear rather than inventing an explanation. A
clarity pass does not authorize code changes, edits to external artifacts, or
an unrelated investigation.

## Examples

**Unclear:** "The distinction matters." beneath a table of test scenarios.

**Clear:** "For the rollback test, let the first write succeed and make the second
fail, then check that neither change remains. Making the transaction fail before
any write happens cannot show whether earlier writes are undone."

**Unclear:** "The fixture repositories need the same provider."

**Clear:** "The repositories that create shipment and carrier records before the
test runs should use the same database provider as the repository being tested."

**Unclear:** "The test proves the getter choice, not the routing guarantee."

**Clear:** "The test checks which function the code calls to obtain a database
client. In this implementation, both functions reach the same database, so that
check does not establish that reads get fresher data."

**Already clear:** "The database connection timed out." No expansion is needed
solely because the sentence contains "the".

## Return the correction

Return the corrected answer directly, without an apology, editing report, or a
separate explanation the reader must stitch into the original. Recheck the
revised passages for unexplained references before sending. If an automatic
review finds no missing context, leave the reply unchanged and do not announce
the check. This skill supplies review instructions; automatic invocation is
model-dependent and does not install a runtime hook.
