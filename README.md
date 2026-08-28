# stevo-skills

Personal (non-company) agent skills, managed the same way `invenco-skills`
manages the shared library: skills live here as plain SKILL.md directories and
Vercel's [`skills`](https://www.npmjs.com/package/skills) CLI publishes them to
every coding agent on the machine.

## Layout

```text
stevo-skills/
├── skills/<name>/SKILL.md   # one directory per skill - the publish set
├── eval/                    # skill-development artifacts; never published
└── package.json             # pins the skills CLI via pnpm
```

## Publishing

```sh
nvm use && pnpm install   # first time
pnpm upskill              # publish/republish everything
```

`upskill` installs canonical copies into `~/.agents/skills/` (read natively by
Codex and most agents) and symlinks them into `~/.claude/skills/` for Claude
Code. Start a new agent session afterwards to pick up changes.

Edits to `skills/` are not live - republish after every change.

## Adding / removing a skill

```sh
pnpm exec skills init skills/<name>    # scaffold, then fill in SKILL.md
pnpm upskill

pnpm exec skills remove --global       # interactive removal from agents
```

To retire a skill fully: remove it from agents (above), then delete its
directory here.

## Sanity check

```sh
pnpm exec skills add . --list
```

Lists every skill the CLI can see. If one is missing, its frontmatter is
probably not strict YAML (unquoted `: ` in the description is the usual cause).
