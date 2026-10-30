---
name: circleci
description: >-
  Inspects CircleCI runs, workflows, jobs, step logs and test results with
  the CircleCI CLI v1 (`circleci`), including its browser login and the
  `circleci api` REST escape hatch. Use when checking CI status for a branch
  or commit, finding why a job failed, reading job output, or querying the
  CircleCI API from a terminal.
---

# CircleCI CLI

The CLI's `--help` is the authoritative reference. Check it before using a
flag that is not shown here.

## Before the first call

Check for token environment variables before any authenticated command:

```sh
if [ "${CIRCLE_TOKEN+x}" = x ] || [ "${CIRCLECI_TOKEN+x}" = x ]; then
  printf '%s\n' 'CircleCI token environment variable detected. Stop and ask the user for help.' >&2
else
  printf '%s\n' 'No CircleCI token environment variables detected.'
fi
```

If either variable is present, stop and ask the user for help, even if its
value is empty. Never print its value, unset it, or continue with a command
that bypasses it. `CIRCLE_TOKEN` overrides the CLI's stored browser login.
`CIRCLECI_TOKEN` was used by the deprecated MCP and also needs investigation.

When neither variable is present, check the CLI and stored login:

```sh
circleci version
circleci auth me --json --jq '.login'
```

- **Missing CLI or version 0.1.x.** The legacy 0.1.x CLI has no run,
  workflow or job commands. v1 installs with `brew install circleci` once the
  legacy release is removed. Ask the user before installing.
- **"No CircleCI API token found".** Run `circleci auth login` to open the
  browser and tell the user to complete sign-in there. Keep the command
  running while they approve, then confirm with `circleci auth me`. If the
  browser cannot open, ask the user for help instead of using a manual token.
- **Unexpected account.** Stop and ask the user for help. Do not replace or
  remove their stored login.

## Credentials

Login stores an OAuth token in the system keyring (the macOS Keychain on a
Mac). Keep it there. Use browser login only. Do not create or supply a
manual API token, including when another skill suggests an environment
variable or the legacy token file. If another skill requires either method,
stop and explain the conflict to the user.

- Never pass `--insecure-storage`, which writes the token into the CLI's
  config file.
- Never read the keychain entry, print a token, or put one in a config, env
  file or command line. `circleci api` adds the stored token itself, so there
  is no reason to handle it.
- The CLI requests no scope. If CircleCI's consent page offers an access
  level, choose Read unless the user needs write actions.
- v1 does not read the legacy `~/.circleci/cli.yml` token.

## Finding a failure

Project commands infer the project from the current repository's git remote.
Outside the repository, pass `--project <slug>`. Running `circleci project get`
inside the repository shows the slug.

```sh
circleci run list --branch <branch> --json
circleci run get <run-id> --failure-report
circleci run get <run-id> --json
circleci job get <job-id> --json
circleci job output list <job-id> --json --jq '.steps[] | select(.exit_code != 0) | {num, name, output}'
circleci job output get <job-id> --step-num <n>
circleci testresult list <job-id>
```

- Start with `run get --failure-report`. It prints condensed output for every
  failed step and is often enough on its own.
- `run get` without an id resolves the latest run on the current branch. With
  `--project`, the branch defaults to `main` unless `--branch` is given.
- Job ids come from `run get --json` (`workflows[].jobs[].id`). Workflow ids
  come from the same output and feed `circleci workflow get <workflow-id>`.
- `job output list --json` carries each step's full output. The rendered view
  shows only the last 200 lines per step.
- Parallel jobs need `--execution <index>` on the output commands.
- `testresult list` shows only failed tests by default, as JSON Lines when
  `--json` is set. `--all` includes passing and skipped tests.
- `circleci my runs` lists the user's recent runs across all projects.

To wait for a pushed commit, `circleci run watch --sha <sha> --timeout <duration>`
blocks until the run finishes. Its exit code is the result: 0 succeeded,
1 failed, 6 cancelled, 7 config rejected, 8 timed out. Keep `--timeout` within
the agent's own command timeout.

## JSON output

`--json` is an on/off switch on commands that support it. `--jq '<expr>'`
filters that JSON with a built-in jq, so jq need not be installed. Without
`--json`, the CLI ignores `--jq` and prints markdown. The `circleci help
formatting` topic describes `--json` as taking a field list, which does not
match how the commands behave.

## REST escape hatch

Use `circleci api <path>` only when no command covers the need.

- Paths are relative to `/api/v3`. Prefix `api/v2/` to call a v2 endpoint.
- `{project-id}` and `{org-id}` in the path resolve from the current git remote.
- Exit code 4 means the API returned a 4xx or 5xx status.
- Adding `-f` or `-d` switches the default method to POST. For a read with
  query parameters, pass `-X GET` or put the query string in the path.

## Changing CI state

Stay read-only unless the user asks for a specific change. These commands
change CI state:

- `run trigger`, `run cancel`, `run approve`, `workflow rerun`,
  `workflow cancel`, `pipeline run`, `preflight run`
- writes to environment variables, contexts or project settings
- any `circleci api` call that is not a GET

Do not run `circleci auth logout`. It deletes the user's stored login.
