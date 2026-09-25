# stevo-skills

Steve's personal agent skills - the non-company counterpart to the
`invenco-skills` repo. One directory per skill under `skills/`, published to
every agent through Vercel's `skills` CLI (pinned as a pnpm devDependency).

## How publishing works

`pnpm upskill` copies each skill into the canonical store `~/.agents/skills/`
(Codex and other agents read it natively) and symlinks it into
`~/.claude/skills/` for Claude Code.

`pnpm downskill <name>...` reverses that for the named skills. It refuses any
name without a `skills/<name>/SKILL.md` in this repo and never touches source.

## Rules

1. Edits here are NOT live. After changing anything under `skills/`, run
   `pnpm upskill`.
2. The canonical store `~/.agents/skills/` is shared with company skills from
   `invenco-skills`. Never reuse a name from that repo's skill catalog.
3. Only `skills/` publishes. `eval/` holds skill-development artifacts
   (benchmarks, grading runs) and is never installed anywhere.
4. Frontmatter must be strict YAML: quote or block-scalar any `description`
   containing `: `. A SKILL.md that fails to parse is skipped at publish with
   only a warning, so check the publish output names every skill.
