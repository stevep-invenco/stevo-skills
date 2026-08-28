# Analytics Service — endpoints

Service prefix (dev/staging/prod): `/analytics`. Local: no prefix.

Every endpoint takes `Authorization: Bearer <JWT>`. The required principal **context** is shown per endpoint.

This service is a Looker / Omni BI gateway — it has **no database**. The only resources are **insights** (dashboards and reports). There are no dedicated dashboards/reports/queries endpoints; everything is exposed through the `insights` collection.

The Postman collection lists `/v1/insights` and `/v1/insights/{insight_id}` under SELLER, WAREHOUSE, SYSTEM, and PLATFORM. The handler routing in `src/modules/analytics/infra/aws/handlers/insightHttp.ts` only registers the **SELLER** access context, so calls under WAREHOUSE / SYSTEM / PLATFORM JWTs will currently 403 / not match. Group-mapping logic in `GetInsightByIdController` does anticipate Seller / Platform / Warehouse / System contexts, so support for the others is partially scaffolded but not wired through the router.

Unauthenticated:

- `GET /v1/info` — health/build info, no authorizer (declared in `serverless.yml`, not in postman/openapi).

## SELLER context

### `GET /v1/insights`
List insights available to the authenticated seller user (drawn from the user's Looker/Omni folder).

- Path params: none
- Query params: none
- Body: none
- Source: postman SELLER → /v1/insights; yaml `reference/API_SELLER.v1.yaml` → `/insights` GET

### `GET /v1/insights/{insight_id}`
Retrieve a single insight plus a signed Omni embed URL for rendering it.

- Path params:
  - `insight_id` (string, required) — opaque insight identifier (e.g. `looker:dashboard:123` / Omni dashboard id)
- Query params:
  - `theme` (string, optional) — base64-encoded JSON object of Omni theme overrides; keys must match Omni `CustomThemeProperty` names, values are strings
  - `prefers_dark` (string enum `true`|`false`, optional) — whether the embed should prefer dark mode
  - `first_name` (string, optional) — present in postman as a disabled query param; not consumed by the handler (legacy / Looker SSO leftover)
  - `last_name` (string, optional) — present in postman as a disabled query param; not consumed by the handler (legacy / Looker SSO leftover)
  - `email` (string, optional) — present in postman as a disabled query param; not consumed by the handler (legacy / Looker SSO leftover)
- Body: none
- Source: postman SELLER → /v1/insights/{insight_id}; yaml `reference/API_SELLER.v1.yaml` → `/insights/{insight_id}` GET; handler `src/modules/analytics/useCases/insights/getInsightById/GetInsightByIdController.ts`

## PLATFORM context

Postman-only. The OpenAPI spec at `reference/API_PLATFORM.v1.yaml` declares no paths, and the lambda router does not register PLATFORM handlers, so these endpoints will not respond today. Documented for completeness because the postman collection lists them.

### `GET /v1/insights` (postman-only, not wired)
List insights for a platform user.

- Path params: none
- Query params: none
- Body: none
- Source: postman PLATFORM → /v1/insights

### `GET /v1/insights/{insight_id}` (postman-only, not wired)
Get a single insight plus signed embed URL for a platform user.

- Path params:
  - `insight_id` (string, required) — insight identifier
- Query params:
  - `theme` (string, optional) — base64-encoded JSON theme overrides (controller-level, applies if/when wired)
  - `prefers_dark` (string enum `true`|`false`, optional) — prefer dark mode
  - `first_name` (string, optional) — disabled in postman, not consumed
  - `last_name` (string, optional) — disabled in postman, not consumed
  - `email` (string, optional) — disabled in postman, not consumed
- Body: none
- Source: postman PLATFORM → /v1/insights/{insight_id}

## SYSTEM context

Postman-only. The OpenAPI spec at `reference/API_SYSTEM.v1.yaml` declares no paths, and the lambda router does not register SYSTEM handlers, so these endpoints will not respond today.

### `GET /v1/insights` (postman-only, not wired)
List insights for a system principal.

- Path params: none
- Query params: none
- Body: none
- Source: postman SYSTEM → /v1/insights

### `GET /v1/insights/{insight_id}` (postman-only, not wired)
Get a single insight plus signed embed URL for a system principal.

- Path params:
  - `insight_id` (string, required) — insight identifier
- Query params:
  - `theme` (string, optional) — base64-encoded JSON theme overrides (controller-level, applies if/when wired)
  - `prefers_dark` (string enum `true`|`false`, optional) — prefer dark mode
  - `first_name` (string, optional) — disabled in postman, not consumed
  - `last_name` (string, optional) — disabled in postman, not consumed
  - `email` (string, optional) — disabled in postman, not consumed
- Body: none
- Source: postman SYSTEM → /v1/insights/{insight_id}

## WAREHOUSE context

Postman-only. The OpenAPI spec at `reference/API_WAREHOUSE.v1.yaml` declares no paths, and the lambda router does not register WAREHOUSE handlers, so these endpoints will not respond today.

### `GET /v1/insights` (postman-only, not wired)
List insights for a warehouse user.

- Path params: none
- Query params: none
- Body: none
- Source: postman WAREHOUSE → /v1/insights

### `GET /v1/insights/{insight_id}` (postman-only, not wired)
Get a single insight plus signed embed URL for a warehouse user.

- Path params:
  - `insight_id` (string, required) — insight identifier
- Query params:
  - `theme` (string, optional) — base64-encoded JSON theme overrides (controller-level, applies if/when wired)
  - `prefers_dark` (string enum `true`|`false`, optional) — prefer dark mode
  - `first_name` (string, optional) — disabled in postman, not consumed
  - `last_name` (string, optional) — disabled in postman, not consumed
  - `email` (string, optional) — disabled in postman, not consumed
- Body: none
- Source: postman WAREHOUSE → /v1/insights/{insight_id}
