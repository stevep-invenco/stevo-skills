# GraphQL through Prism

Pass `graphql query --help` to the wrapper to confirm installed syntax.
Use `PRISM_AGENT_CLI` as defined in SKILL.md.
The command reuses the selected profile's credentials.

```sh
bash "$PRISM_AGENT_CLI" graphql query 'query { customers { nodes { id name } } }' --profile <profile> --agent --format json
bash "$PRISM_AGENT_CLI" graphql query query.graphql --file --variables @variables.json --profile <profile> --agent --format json
```

Single-quote inline GraphQL so the shell does not expand GraphQL variables
such as `$id`. Keep query and variables files inside the authorized workspace,
and do not put credentials in them. Use the
[API schema](https://prismatic.io/docs/api/schema/) to check fields and filters.
GraphQL connections need explicit pagination with `pageInfo` and cursors;
the CLI list command's `--all` does not apply to arbitrary GraphQL queries.

Inspect the entire document, including fragments and files, before sending
it. Send query operations only. The wrapper keeps read-only mode enabled.
Inspect both transport errors and GraphQL errors before reporting success.
Do not assume a successful process exit means every requested field resolved.

If the CLI rejects the document in read-only mode, report the limitation.
Do not drop the guard to make a diagnostic query work. Prepare requested
GraphQL mutations for the user to run rather than executing them.
