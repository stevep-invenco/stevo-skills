---
name: application-event-table
description: Load Lynk's `application_event` table reference docs into context. Make sure to use this skill whenever the user mentions the application event table or any close variant — "app event", "app events", "app event table", "app-event table", "application event", "application events", "application event table", "application_event", "the app_event table", "appevent", "application_event row/rows", "event table", or asks about how rows land in it, the event payload shape, the actor/aggregate/command columns, `event_occurred_at` vs `created_at`, the PrismaWriteFinalizer write path, request_id correlation, or how a service writes domain events to its event table. Trigger even when the user does not name the skill explicitly — any reference to per-service event/audit rows, application_event JSONB payloads, or domain-event persistence in a Lynk service should pull this in.
---

# `application_event` Table Reference

This skill contains everything needed to answer questions about Lynk's per-service `application_event` table — the audit trail of domain events.

Answer the user's question directly. Cite the specific section that answers what they asked — don't dump the whole reference at them.

## Which services have this table

**Services with `application_event`:** sales, supply, products, automation, accounts, shipping, warehousing, analytics.

These all use the same schema, the same `PrismaWriteFinalizer` writer, and the same semantics. Sales is used as the example service throughout.

**Services without it:** inventory-service does NOT have an `application_event` table. It uses a different event architecture — `applyAfterHooks` dispatches domain events directly to EventGateway (EventBridge) after the Prisma transaction commits, with no persistent audit rows. If someone asks about application_event rows for inventory, tell them the table doesn't exist there and point them at `InventoryTransaction` records or service logs instead.

## Schema

```
application_event
├── id                    cuid (= ApplicationEvent entity id)
├── request_id            shared by every row from one HTTP/SQS request
├── command_name          e.g. CreateOrder, UpdateOrder
├── aggregate_id          the entity that emitted the event
├── aggregate_name        e.g. Order, Fulfillment, ShippingProfile
├── actor_id              who did it
├── actor_type            APP | USER | SYSTEM | ...
├── actor_access_context  SELLER | INVENCO_ADMIN | ...
├── event_name            OrderCreated, OrderUpdated, FulfillmentShipped, ...
├── event_payload         JSONB — aggregate DTO snapshot at commit time
├── event_occurred_at     when the DomainEvent was constructed (app-side)
└── created_at            when the row was INSERTed (db-side)

INDEX (aggregate_id, created_at)
```

---

## How rows land

The table is the audit trail of every domain event emitted while committing a write. One row per `DomainEvent` per aggregate, written in the same Prisma transaction as the aggregate change.

### Write path (CreateOrder example)

```
HTTP POST /orders (seller)
        │
        ▼
┌──────────────────────────┐
│ CreateOrderAsSeller      │   commandName = "CreateOrder"
│   Controller             │   actorId / type / accessContext
│                          │   requestId   ← from request
└──────────┬───────────────┘
           │ execute(input, CommandContext)
           ▼
┌──────────────────────────┐
│ CreateOrder UseCase      │
│   Order.create(...)      │
│   order.addDomainEvent(  │   ← OrderCreated{ order, dateTimeOccurred=now }
│     new OrderCreated(o)) │
│   repo.save(order)       │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│ BasePrismaRepo.writeAndFinalize (inside tx)  │
│  1. INSERT/UPDATE Order, OrderLine, ...      │
│  2. WriteFinalizer.finalize([order])         │
└──────────┬───────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│ PrismaWriteFinalizer.finalize                │
│   for each aggregate:                        │
│     for each domainEvent:                    │
│       ApplicationEvent.create(evt, ctx)      │
│       SalesApplicationEventMapper.toDTO(...) │
│         → eventPayload = OrderMapper.toDTO   │
│   tx.applicationEvent.createMany(rows)       │
└──────────────────────────────────────────────┘
           │
           ▼
   application_event row(s) committed
   atomically with the Order write
```

### Three things to remember

1. **Same transaction.** If the Order insert rolls back, the event row never lands. No event in the table = the write didn't happen.
2. **One row per DomainEvent.** A single use case can produce several rows (e.g. `OrderCreated` + `OrderProcessAutomationStarted` + `OrderProcessReservationInventoryStarted` for one create).
3. **Payload is mapped at write time.** What you see in `event_payload` is the aggregate as it existed at commit, snapshot via the service's `ApplicationEventMapper`.

### Key files

| Concern | File |
|---|---|
| Domain event base | `common/@invenco/ddd-core/src/domain/events/DomainEvent.ts` |
| Wrapper persisted as a row | `common/@invenco/ddd-core/src/domain/events/ApplicationEvent.ts` |
| The actual writer | `common/@invenco/aws-common-infra/src/prisma/PrismaWriteFinalizer.ts` |
| DTO → row shape | `common/@invenco/common-application/src/mappers/eventMapper/BaseApplicationEventMapper.ts` |
| Sales payload mappers | `services/sales-service/src/modules/sales/mappers/eventMapper/SalesApplicationEventMapper.ts` |
| Sales schema | `services/sales-service/prisma/schema.prisma` (`model ApplicationEvent`) |

### Missing rows

`PrismaWriteFinalizer.finalize` short-circuits and logs only when:

- **CommandContext not available** — no row written, warn log: *"CommandContext is not available, skip creating event log"*. The transaction is NOT rolled back (there's a code comment noting this should change in future).
- **No payload mapper registered** for a domain event → `eventPayload` is `null` and the row is filtered out before insert. Warn log: *"No payload mapper found for event: ..."*.
- **Event mapper throws** → row dropped, error logged: *"Failed to initialize ApplicationEventDTO"*.

None of these roll back the transaction today. So "the write succeeded but no row in `application_event`" is possible — check the service logs for those three warnings before assuming the use case didn't run.

---

## `event_occurred_at` vs `created_at`

Two timestamps, two different clocks, two different questions.

```
   request lifetime
   ──────────────────────────────────────────────────────────────▶ time

   t0                    t1                          t2
   │                     │                           │
   │ new OrderCreated()  │ tx.applicationEvent       │ COMMIT
   │ ──► dateTimeOccurred│   .createMany({...})      │
   │     captured here   │ ──► row written, DEFAULT  │
   │                     │     now() fires here      │
   ▼                     ▼                           ▼
 event_occurred_at  ≈  (in-flight work)        created_at
 "when the domain      "when the row hit
  decided this         the table"
  happened"
```

### `event_occurred_at` — when the domain says it happened

- Set in `DomainEvent`'s constructor: `this.dateTimeOccurred = new Date()`.
- Stamped the moment the use case calls `new OrderCreated(order)` — on the application server, before the Prisma transaction commits.
- This is the timestamp you trust for **business reasoning**: "the order was created at ...".

### `created_at` — when the row was inserted

- Stamped by Postgres / Prisma at INSERT time inside the transaction.
- Always >= `event_occurred_at`. The gap is time spent in the use case after the event was raised.
- This is the timestamp you trust for **observability**: "when did this become visible to readers / downstream services?".

### Which column to use

| Question | Use this column |
|-------------------------------------------------|----------------------|
| When did the customer's order get placed? | `event_occurred_at` |
| Why did the downstream consumer see it late? | `created_at` |
| Order rows in the order they actually occurred | `event_occurred_at` |
| Order rows in the order they became visible | `created_at` |
| Big gap between the two on one row? | Long-running tx — investigate use-case latency |
| Two rows with different `created_at` but same `request_id` | Same use case wrote them both — group by `request_id` |

If they're ever far apart, that's a signal, not a bug: something held the transaction open.

---

## `event_payload` — what is it?

A JSON snapshot of the aggregate at commit time, produced by the service's `ApplicationEventMapper`. Not the `DomainEvent` object. Not the request body. The aggregate's DTO.

### Pipeline

```
DomainEvent (in memory)            event_payload (JSONB)
┌──────────────────────────┐       ┌────────────────────────────┐
│ OrderCreated {           │       │ { id, name, status,        │
│   order: <Order entity>, │ ────▶ │   accountId, channel:{...},│
│   dateTimeOccurred       │       │   orderLines:[...],        │
│ }                        │       │   orderProcesses:[...],    │
│                          │       │   shippingAddress:{...},   │
└──────────────────────────┘       │   ... }                    │
            │                      └────────────────────────────┘
            ▼
SalesApplicationEventMapper:
   [EventName.OrderCreated]:
     (event) => OrderMapper.toDTO(event.order)
            │
            ▼
BaseApplicationEventMapper.toDTO:
   eventPayload: payloadMapper(domainEvent) ?? null
```

The payload's shape matches the public DTO of the aggregate (`OrderDTO`, `FulfillmentDTO`, `ShippingProfileDTO`, ...) — the same shape your APIs return. That's reused on purpose so consumers and dashboards can read both interchangeably.

### Key properties of the payload

- **Denormalised.** `channel`, addresses, lines — all in one blob. No joins needed.
- **Snapshot, not a diff.** `OrderUpdated` payloads contain the whole order after the update. Compare two consecutive rows for the same `aggregate_id` to see what changed.
- **Entity `createdAt` != event timestamps.** The `createdAt` inside `event_payload` is the Order's own `createdAt`. The row's `created_at` and `event_occurred_at` columns are separate.

### When payload is null / missing

- **No mapper registered for the event name** → payload is `null`, and `PrismaWriteFinalizer` filters the row out before insert. No mapper = no row at all, plus a warn log.
- **Mapper throws** → `Result.fail(...)`, row dropped, error log.
- Everything else → payload is the mapper's return value serialised to JSONB.

### Common queries

```sql
-- What did the order look like the moment it was created?
SELECT event_payload
FROM application_event
WHERE aggregate_id = '<id>'
  AND event_name = 'OrderCreated';

-- Reconstruct timeline of an aggregate
SELECT event_occurred_at, event_name, command_name, request_id
FROM application_event
WHERE aggregate_id = '<id>'
ORDER BY event_occurred_at;

-- Pull a single field out of the JSON
SELECT event_occurred_at,
       event_payload->>'status'           AS status,
       event_payload->>'fulfillmentStatus' AS f_status
FROM application_event
WHERE aggregate_id = '<id>'
ORDER BY event_occurred_at;

-- Find every row produced by the same HTTP request
SELECT event_occurred_at, aggregate_name, event_name
FROM application_event
WHERE request_id = '<request_id>'
ORDER BY event_occurred_at;
```

### Payload accuracy

The payload is only as good as the mapper. If a new field is added to the aggregate but the `*Mapper.toDTO` isn't updated, the payload silently misses it — no error, just absent. When troubleshooting and something looks "wrong" in the payload, check the mapper before suspecting the domain.
