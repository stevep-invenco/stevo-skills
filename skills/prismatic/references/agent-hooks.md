# Blocking raw Prism commands

The shared [hook definition](../hooks/hooks.json) works with both agents.
It runs [block-raw-prism.py](../hooks/block-raw-prism.py) before shell tool
calls and returns a denial for `prism` in common executable positions.
It catches direct commands, absolute paths ending in `/prism`, chained
commands, explicit shell `-c` commands, and package runner invocations.
Passing `--read-only` directly
does not exempt a raw command. Mentioning the wrapper elsewhere in the same
command does not exempt it either.

The hook uses Python 3's standard library. It does not execute inspected
input, modify commands, print command text, or approve unrelated commands.
Allowed calls produce no output, preserving the agent's normal permission
flow. Ordinary arguments, prose, search terms, and heredoc bodies are data,
so mentions of `prism` or Prismatic there do not trigger the hook. Syntax
that cannot be inspected also leaves the normal permission flow intact.

## Registration

Publish the skill before registering the hook, so the script exists at
`~/.agents/skills/prismatic/hooks/block-raw-prism.py`. Merge the `PreToolUse`
entry from `hooks/hooks.json` into existing hook configuration, preserving
all other settings and avoiding duplicate entries:

- Claude Code uses `~/.claude/settings.json` for all local projects.
- Codex uses `~/.codex/hooks.json` for all local projects.

Register in agent settings rather than skill frontmatter so a raw command
is checked even when the agent has not loaded the skill. Publishing with
`pnpm upskill` copies the hook files but does not register them.

After registration, start fresh sessions and inspect `/hooks` in both agents.
Codex skips untrusted hooks until the user reviews and trusts their exact
definition. Do not bypass the trust check or mark the hook trusted on the
user's behalf. Check that hooks are enabled and the entry is active.

For a live check, ask each agent to run `prism --version`. The hook should
deny the call with a message directing it to the wrapper. The wrapper's
`--version` command should still work. Do not test with a remote mutation.

## Limits

The hook deliberately favors avoiding false positives over exhaustive shell
analysis. Clipboard heredocs and worklog headlines can contain command
examples, punctuation, and apostrophes without being treated as CLI calls.

The hook does not inspect arbitrary scripts, interpreter code, aliases,
shell expansions, heredoc execution by an interpreter, or renamed binaries.
It cannot protect against an
agent editing or disabling its own hook. Calls sent through a different
MCP or terminal tool may not match `Bash`. Codex does not rerun `PreToolUse`
for input sent through `write_stdin` to an existing session.

The wrapper still enforces read-only mode on its child process. A Prismatic
account with server-enforced read-only permissions remains necessary if
writes must be impossible through every execution path.

- [Claude Code hooks](https://code.claude.com/docs/en/hooks)
- [Codex hooks and trust](https://learn.chatgpt.com/docs/hooks)
