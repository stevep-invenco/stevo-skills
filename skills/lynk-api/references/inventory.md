# Inventory Service — endpoints

Service prefix (dev/staging/prod): `/inventory`. Local: no prefix.

Every endpoint takes `Authorization: Bearer <JWT>`. The required principal **context** is shown per endpoint.

## SELLER context

### `GET /v1/inventories`
List inventory levels by location and status (paginated).

- Path params: none
- Query params:
  - `cursor` (string, optional) — pagination cursor
  - `take` (integer, optional) — page size
  - `sort_direction` (string, optional) — `asc` or `desc`
  - `search` (string, optional) — free-text search
  - `location_ids` (string, optional) — comma-separated location IDs
  - `sku_ids` (string, optional) — comma-separated SKU IDs
  - `sku_name` (string, optional) — filter by SKU name
  - `updated_at_after` (string date-time, optional) — only inventories updated after this timestamp
  - `sort_by` (string, optional) — `created_at` (default) or `updated_at`
  - `includes` (string, optional) — optional child elements (`sub_inventories`)
- Body: none
- Source: yaml SELLER → `/inventories` GET; postman SELLER → /v1/inventories

### `GET /v1/adjustments`
List inventory adjustments (paginated).

- Path params: none
- Query params:
  - `cursor` (string, optional) — pagination cursor
  - `take` (integer, optional) — page size
  - `sort_direction` (string, optional) — `asc` or `desc`
  - `created_at_after` (string date-time, optional) — only adjustments created after this timestamp
  - `sort_by` (string, optional) — `created_at` (default)
  - `includes` (string, optional) — optional child elements (`adjustment_lines`)
- Body: none
- Source: yaml SELLER → `/adjustments` GET; postman SELLER → /v1/adjustments

### `GET /v1/adjustments/{adjustment_id}`
Retrieve a single adjustment by id.

- Path params:
  - `adjustment_id` (string, required) — the adjustment id
- Query params: none
- Body: none
- Source: yaml SELLER → `/adjustments/{adjustment_id}` GET; postman SELLER → /v1/adjustments/{adjustment_id}

## SYSTEM context

### `GET /v1/inventories`
List inventory levels by location and status (paginated). System variant supports `account_id` filter for cross-account queries.

- Path params: none
- Query params:
  - `cursor` (string, optional) — pagination cursor
  - `take` (integer, optional) — page size
  - `sort_direction` (string, optional) — `asc` or `desc`
  - `search` (string, optional) — free-text search
  - `location_ids` (string, optional) — comma-separated location IDs
  - `sku_ids` (string, optional) — comma-separated SKU IDs
  - `sku_name` (string, optional) — filter by SKU name
  - `updated_at_after` (string date-time, optional) — only inventories updated after this timestamp
  - `account_id` (string, optional) — filter by account id
  - `sort_by` (string, optional) — `created_at` (default) or `updated_at`
  - `includes` (string, optional) — optional child elements (`sub_inventories`)
- Body: none
- Source: yaml SYSTEM → `/inventories` GET; postman SYSTEM → /v1/inventories

### `POST /v1/inventories/reserve`
Reserve (or rebalance) inventory against a document such as an order or ASN.

- Path params: none
- Query params: none
- Body:

```json
{
  "document_id": "{DOCUMENT_ID}",
  "account_id": "{ACCOUNT_ID}",
  "reason": "reserve",
  "apply_at": "{ISO_8601_TIMESTAMP}",
  "reservations": [
    {
      "reference_type": "order_line",
      "reference_id": "{ORDER_LINE_ID}",
      "sku_id": "{SKU_ID}",
      "location_id": "{LOCATION_ID}",
      "target_qty_reserved": 0,
      "target_qty_committed": 0
    }
  ]
}
```

  Required: `document_id`, `account_id`, `reason`, `apply_at`, `reservations`. Each reservation requires `reference_type` (`asn_line` | `order_line` | `fulfillment_line` | `ADJUSTMENT_LINE`), `reference_id`, `sku_id`, `location_id`, `target_qty_reserved` (integer ≥ 0), `target_qty_committed` (integer ≥ 0). `reason` is `reserve` or `REBALANCE`.
- Source: yaml SYSTEM → `/inventories/reserve` POST; postman SYSTEM → /v1/inventories/reserve

### `POST /v1/adjustments`
Create an inventory adjustment. SYSTEM variant requires `location_id` on the adjustment and `sku_id` on each line.

- Path params: none
- Query params: none
- Body:

```json
{
  "adjustment": {
    "location_id": "{LOCATION_ID}",
    "location_name": "{LOCATION_NAME}",
    "external_id": "{EXTERNAL_ID}",
    "adjustment_lines": [
      {
        "sku_id": "{SKU_ID}",
        "sku_name": "{SKU_NAME}",
        "qty_adjustment": 0,
        "external_id": "{EXTERNAL_LINE_ID}",
        "external_sku_name": "{EXTERNAL_SKU_NAME}",
        "batch": "{BATCH}",
        "expiry": "{YYYY-MM-DD}",
        "reason_code": "BIN_COUNT"
      }
    ]
  }
}
```

  Required on adjustment: `location_id`, `adjustment_lines`. Required on each line: `sku_id`, `qty_adjustment`. `reason_code` enum: `BIN_COUNT` | `FIX_EXPIRY_BATCH` | `EXTRA_STOCK` | `MISSING_STOCK` | `ADJUSTED_FUTILE` | `BARCODE_ISSUE` | `RECEIPT_ERROR` | `SHORT_SHIPPED` | `PICK_ERROR` | `REPLEN_TRANSFER_ERROR` | `DAMAGED_QUARANTINE` | `RECONCILIATION` | `OTHER`.
- Source: yaml SYSTEM → `/adjustments` POST; postman SYSTEM → /v1/adjustments

## WAREHOUSE context

### `POST /v1/adjustments`
Create an inventory adjustment. WAREHOUSE variant requires `location_name` on the adjustment and `sku_name` on each line (warehouses identify by name, not id).

- Path params: none
- Query params: none
- Body:

```json
{
  "adjustment": {
    "account_id": "{ACCOUNT_ID}",
    "location_name": "{LOCATION_NAME}",
    "external_id": "{EXTERNAL_ID}",
    "adjustment_lines": [
      {
        "sku_name": "{SKU_NAME}",
        "qty_adjustment": 0,
        "external_id": "{EXTERNAL_LINE_ID}",
        "external_sku_name": "{EXTERNAL_SKU_NAME}",
        "batch": "{BATCH}",
        "expiry": "{YYYY-MM-DD}",
        "reason_code": "BIN_COUNT"
      }
    ]
  }
}
```

  Required on adjustment: `location_name`, `adjustment_lines`. Required on each line: `sku_name`, `qty_adjustment`. `reason_code` enum: see SYSTEM `POST /v1/adjustments` above. The postman example also includes `account_id` so the warehouse principal can target an account it manages.
- Source: yaml WAREHOUSE → `/adjustments` POST; postman WAREHOUSE → /v1/adjustments

## UNCATEGORIZED

### `GET /v1/info`
Service info / health endpoint. Defined in `serverless.yml` with no authorizer, so it is unauthenticated (no Bearer token required) and has no SELLER/PLATFORM/SYSTEM/WAREHOUSE/EXTERNAL gating. Not present in any postman collection or OpenAPI spec.

- Path params: none
- Query params: none
- Body: none
- Source: serverless.yml `infoHttp` function; handler `src/modules/inventory/infra/aws/handlers/infoHttp.ts` (yaml-only? — neither, serverless-only)
