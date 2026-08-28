---
name: lynk-api
description: Generate ready-to-run cURL commands for any Lynk REST endpoint. Use whenever the user wants to call, hit, test, or debug a Lynk API — phrases like "curl for lynk", "give me the request to ...", "hit the products endpoint", "call sales API", "how do I create an X via API", "what's the endpoint for Y", or any time the user names a Lynk service (accounts/sales/products/inventory/shipping/warehousing/supply/automation/analytics) together with an HTTP-shaped intent. The skill knows every endpoint's method, path, query params, body shape, required auth context (SELLER/PLATFORM/SYSTEM/WAREHOUSE/EXTERNAL), and per-environment base URL. Trigger even if the user does not say "curl" explicitly — anything that resolves to "I want to talk to Lynk over HTTP" qualifies.
---

# Lynk API — cURL generator

This skill emits ready-to-run cURL commands for Lynk REST endpoints. The user supplies the auth token and the request-specific values (IDs, body fields, filters); this skill supplies everything else.

## How to use this skill

1. Identify the **service** and **endpoint** the user wants. If ambiguous, ask one short clarifying question.
2. Open the matching `references/<service>.md` file to look up the endpoint's method, path, query params, body shape, and required auth context.
3. Pick the **base URL** from the env table below (default `staging` if the user does not specify).
4. Emit a cURL with placeholders. Above the cURL, give a **one-line preamble** stating: which auth context is required, and what the user must fill in.
5. Stop. Do not execute the cURL — the user runs it themselves.

If a service-specific reference says something different (e.g. a custom header, a non-standard base path), the reference wins.

## Environments and base URLs

| Env       | Base URL                                       | Notes                                                  |
|-----------|------------------------------------------------|--------------------------------------------------------|
| `local`   | `http://localhost:3000`                        | Single service per port — **no service prefix**        |
| `dev`     | `https://api.dev-lynksupplychain.com`          | API Gateway routes by service prefix                   |
| `staging` | `https://api.stage-lynksupplychain.com`        | API Gateway routes by service prefix                   |
| `prod`    | `https://api.lynksupplychain.com`              | API Gateway routes by service prefix                   |

**Service prefix:** for `dev`/`staging`/`prod`, every URL is `{base}/{service}/{path}` where `{service}` is one of: `accounts`, `sales`, `products`, `inventory`, `shipping`, `warehousing`, `supply`, `automation`, `analytics`. For `local`, drop the `{service}` segment — there is no API Gateway in front, the developer runs one service at a time on `:3000`.

If the user does not name an env, default to **staging** and mention you defaulted.

## Auth contexts

Every Lynk endpoint requires a JWT in `Authorization: Bearer <TOKEN>`. The same header carries every context — what differs is the *kind of principal* the JWT must represent. Each per-service reference tags every endpoint with its context. The contexts are:

| Context     | Who the principal is                                                      | Where it shows up                                |
|-------------|---------------------------------------------------------------------------|--------------------------------------------------|
| `SELLER`    | An end-user logged into the seller (merchant) workspace                   | Seller-facing UI flows (orders, SKUs, listings)  |
| `PLATFORM`  | An internal Lynk operator / platform admin                                | Cross-tenant admin actions, support tooling      |
| `SYSTEM`    | A backend service or job (machine-to-machine, no human)                   | Service-to-service calls, scheduled work         |
| `WAREHOUSE` | A user in the WMS / warehouse-operator workspace                          | Receiving, picking, packing, putaway flows       |
| `EXTERNAL`  | A third-party integrator using a public/partner key                       | Webhook-shaped or partner integration endpoints  |

When you emit a cURL, **state the required context explicitly** in the preamble so the user knows which token to grab. If an endpoint exists under multiple contexts (same path, different access), surface that — the user can then pick.

## Output format

Default template:

```
This endpoint requires a {CONTEXT} JWT. You'll need to fill in: {placeholders}.

curl -X {METHOD} '{base}/{service}{path}?{query}' \
  -H "Authorization: Bearer $LYNK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    ...body shape with placeholders...
  }'
```

Rules of thumb:
- Use `$LYNK_TOKEN` (a shell var the user exports) rather than inlining the token.
- Use `{ALL_CAPS_PLACEHOLDERS}` for IDs and values the user must substitute (e.g. `{ORDER_ID}`).
- Drop `-H "Content-Type: application/json"` and `-d` for GET/DELETE with no body.
- For optional query params, include them commented out or list them under the cURL with a one-line "supported query params: ..." note. Do not silently omit them — the whole point of this skill is the user knowing what's available.
- Keep request bodies *minimal but complete*: include all required fields with placeholder values; list optional fields beneath the cURL rather than stuffing them into the body.
- If the path has variable segments (`/v1/orders/{order_id}`), keep the `{order_id}` style — easy to find-and-replace.

## Per-service references

Open the matching file for endpoint details. Each reference covers every endpoint the service exposes, grouped by auth context.

| Service     | Reference                       | Endpoints | Contexts present                | What lives here                                                          |
|-------------|---------------------------------|-----------|---------------------------------|--------------------------------------------------------------------------|
| accounts    | `references/accounts.md`        | ~41       | SELLER, PLATFORM, SYSTEM, WAREHOUSE | Users, memberships, locations, list views, bills, bill holds, service agreements |
| sales       | `references/sales.md`           | ~52       | SELLER, SYSTEM, PLATFORM        | Orders, fulfillments, listings, channels, shipping/fulfillment profiles  |
| products    | `references/products.md`        | ~22       | SELLER, SYSTEM, PLATFORM        | SKUs, units, assemblies, component groups, import/export                 |
| inventory   | `references/inventory.md`       | ~7        | SELLER, SYSTEM, WAREHOUSE       | Stock levels, adjustments, reservations                                  |
| shipping    | `references/shipping.md`        | ~47       | SELLER, PLATFORM, SYSTEM, WAREHOUSE | Shipments, carriers, carrier services, shipping methods, prices, accounts |
| warehousing | `references/warehousing.md`     | ~21       | WAREHOUSE, PLATFORM, EXTERNAL   | WMS integration: warehouses, tenants, wms_instances, EXTERNAL `/v1/messages` webhook |
| supply      | `references/supply.md`          | ~13       | SELLER, SYSTEM, WAREHOUSE       | ASNs, ASN lines (no vendors/POs — out of scope)                          |
| automation  | `references/automation.md`      | ~10       | SELLER, WAREHOUSE               | Workflow definitions (triggers and actions live inside the workflow body)|
| analytics   | `references/analytics.md`       | ~2        | SELLER (other contexts scaffolded but not wired) | Insights (dashboards/reports surfaced as `insights`)         |

## Common pitfalls

- **`local` does not include a service prefix.** `http://localhost:3000/v1/orders` is right; `http://localhost:3000/sales/v1/orders` is wrong.
- **Bodies are snake_case.** Lynk APIs accept and return snake_case JSON. If a reference shows camelCase keys for a field, that is almost certainly a typo — prefer snake_case. **Exception:** the warehousing-service `POST /v1/messages` webhook accepts CamelCase payloads from WMS providers (`InstanceCode`, `TenantCode`, `PackSlipNumber`, etc.) — that's documented in `references/warehousing.md`.
- **`v1` lives in the path, not the host.** Every endpoint starts with `/v1/...` after the service prefix.
- **Tenancy is in the JWT.** There is no `X-Tenant-Id` header — the token's claims identify the seller/warehouse account. If a user asks "how do I switch tenants in the cURL", the answer is "use a different token".
- **If the user says `local`, ask which service is running on `:3000`** unless context makes it obvious — `local` only works for the one service the developer has booted.
- **Every service exposes `GET /v1/info` unauthenticated** as a health/version probe. Drop the `Authorization` header for these — it's not required and may cause unexpected behavior. They live under the `UNAUTHENTICATED` (or equivalent) section in each reference.
- **The same path can be context-overloaded.** Several routes (e.g. sales `PATCH /v1/orders/{id}`, supply `PATCH /v1/asns/{asn_id}`, inventory `POST /v1/adjustments`) share a method+path across multiple contexts but accept *different bodies*. The reference documents each context separately — read the right one based on the user's token.
- **Postman vs OpenAPI vs handler — prefer the handler.** Each reference uses a `Source:` breadcrumb. If a `Source: yaml-only` note appears, the endpoint is in the spec but you may want to confirm it's actually wired before relying on it. If a `Source: postman-only` note appears, expect the spec to lag the implementation — the wire format from postman is usually right.
