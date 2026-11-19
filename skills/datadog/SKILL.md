---
name: datadog
description: Conventions and guidance for working with Datadog via the configured Datadog MCP server - log search, log analysis, metrics, traces, spans, RUM events, monitors, dashboards, incidents, and notebooks. Make sure to use this skill whenever the user mentions Datadog, "dd", observability data, logs/metrics/traces/spans/RUM, dashboards, monitors, incidents, or notebooks, AND whenever you are about to call any Datadog MCP tool - even if the user does not explicitly ask for the skill. Consult this skill before the first Datadog MCP call in a turn so the call is shaped by the conventions here.
---

## Log Explorer

- **Filter by environment.** Logs are faceted by `env`. Always scope queries to one of `env:prod`, `env:stage`, or `env:dev` unless cross-env comparison is the point - otherwise prod noise drowns the signal. **Default to `env:prod` when the prompt does not specify an environment.**
- **Filter by service.** Logs are faceted by `service`, which maps to a single Lynk microservice (e.g. `service:sales-service`, `service:inventory-service`, `service:shipping-service`). Add a `service:` filter whenever the question is scoped to a known service - it cuts the volume dramatically and avoids cross-service name collisions.
- **Trace a request across services.** Lynk runs on Lambda microservices, and the same `requestId` flows through every service that handles a request. To pull every log for one request - regardless of which attribute carries the id in each service - search with the wildcard-attribute form `*:<requestId>` rather than guessing `@requestId`, `@request_id`, `@http.request_id`, etc.

## `#datadog-errors` Slack channel

Datadog log monitors post alerts into the `#datadog-errors` Slack channel. When the user asks you to "check datadog errors", "see what's broken", "triage alerts", or anything similar, start there - the channel is the human-curated feed of what actually fired, which is faster than open-ended log queries.

- **Read the channel** with the Slack `slack_read_channel` tool. The channel id is `C07TN31R39B` - use it directly, no lookup needed.
- **Each alert is a top-level message; discussion lives in the thread.** Use the Slack `slack_read_thread` tool to pull replies before assuming an alert is unhandled - someone may have already triaged or silenced it.
- **Pivot from alert → logs.** Alert messages typically include the monitor name, env, service, and a link back to Datadog. Use those fields to build a follow-up Datadog log query (apply the `env:` / `service:` filters from the Log Explorer section above) rather than re-querying the whole index.
- **Don't post into the channel** unless the user explicitly asks. It's an alert feed, not a discussion channel - replies notify on-call.

## Lynk Overview dashboard

The `Lynk Overview` dashboard (id `mrs-tgy-na7`, https://us3.datadoghq.com/dashboard/mrs-tgy-na7) is the operational overview of every Lynk service: traffic, latency, errors, saturation, queue health (SQS) and recent deploys. Filter it with the `env` (default `prod`) and `service` template variables. When the user shares a link to it, fetch it with `get_datadog_dashboard` to see the exact widget queries rather than guessing metric names.

The queue widgets have two blind spots. Keep them in mind before answering "are the DLQs ok?" from the dashboard alone:

- **The "DLQ messages (current)" table only matches queues named `*_dlq.fifo`.** Some dead-letter queues are named `*_dead_letter.fifo` (the SQS queue-age monitors exclude both patterns), and they never appear in that table.
- **The same table shows the last value over the past hour.** A DLQ that filled during an incident and was then redriven or purged reads as 0.

To check DLQs properly, query the metric directly over the whole incident window, covering both naming patterns, and look at the peak rather than the last value:

```
max:aws.sqs.approximate_number_of_messages_visible{env:prod AND (queuename:*dlq* OR queuename:*dead_letter*)} by {queuename}
```

Don't use `aws.sqs.number_of_messages_sent` on a DLQ as evidence. SQS doesn't count messages moved there by a redrive policy, so it stays at 0 even when messages are dead-lettered. Also check that the queue you care about has a DLQ at all: list the service's queues with `max:aws.sqs.approximate_number_of_messages_visible{env:prod,service:<service>} by {queuename}` and look for a matching `_dlq` or `_dead_letter` sibling.
