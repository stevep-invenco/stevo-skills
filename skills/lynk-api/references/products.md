# Products Service — endpoints

Service prefix (dev/staging/prod): `/products`. Local: no prefix.

Base URLs:
- Production: `https://api.lynksupplychain.com/products`
- Staging: `https://api.stage-lynksupplychain.com/products`
- Dev: `https://api.dev-lynksupplychain.com/products`

Every endpoint takes `Authorization: Bearer <JWT>` (except `GET /v1/info`, which is unauthenticated). The required principal **context** is shown per endpoint. Context dispatch happens in `src/modules/products/infra/aws/handlers/skuHttp.ts` via `LambdaHttpAccessContextRouter`.

Notes / anomalies:
- `POST /v1/skus/{sku_id}/component_groups` and `PATCH .../component_groups/{component_group_id}` use body key `component_group` per the OpenAPI spec, but the postman collection uses `sku_component_group`. The OpenAPI spec is authoritative — use `component_group`.
- `PUT /v1/skus` (create-or-update SKU) is **deprecated** but still routed in `serverless.yml`.
- `POST /v1/skus/{sku_id}/convert_to_assembly` is **deprecated** in favour of `POST /v1/skus/{sku_id}/convert`.
- `POST /v1/skus/{sku_id}/archive` and `/unarchive` exist in `serverless.yml` + `API_SELLER.v1.yaml` but are **missing from the postman collection**.
- `PUT /v1/skus/{sku_id}/units` is SYSTEM only (no SELLER variant).
- `POST /v1/skus/{sku_id}/refresh` is PLATFORM only.
- `GET /v1/info` is open and not in the postman collection.

## UNAUTHENTICATED context

### `GET /v1/info`
Health/info probe — returns `healthy`, git commit hash, branch, build number.

- Path params: none
- Query params: none
- Body: none
- Source: serverless.yml `infoHttp` → `src/modules/products/infra/aws/handlers/infoHttp.ts`

## SELLER context

### `GET /v1/skus`
List SKUs (paginated, cursor-based).

- Path params: none
- Query params:
  - `q` (string, optional) — search query
  - `cursor` (string, optional) — pagination cursor
  - `take` (int, optional) — page size
  - `names` (string, optional) — comma-separated SKU names
  - `ids` (string, optional) — comma-separated SKU ids
  - `type` (string, optional) — `STANDARD` | `BUNDLE` | `MYSTERY` | `ALIAS`
  - `includes` (string, optional) — `components`
  - `exclude_sku_ids` (string, optional) — comma-separated SKU ids to exclude
  - `updated_at_after` (string, optional) — ISO date filter
  - `archived` (boolean, optional) — `true`/`false`/omit for both
- Body: none
- Source: yaml API_SELLER → `/v1/skus` GET; postman SELLER → /v1/skus

### `POST /v1/skus`
Create a SKU.

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "sku": {
      "name": "{NAME}",
      "description": "{DESCRIPTION}",
      "external_id": "{EXTERNAL_ID}",
      "external_sku_name": "{EXTERNAL_SKU_NAME}",
      "barcode": "{BARCODE}",
      "type": "STANDARD",
      "fulfillment_strategy": "STOCK",
      "purchase_price": 0,
      "sell_price": 0,
      "unit_type": "BASE",
      "unit_of_measure": "EACH",
      "base_quantity": 1,
      "measurement": {
        "dimension_unit": "CM",
        "length": 0,
        "height": 0,
        "width": 0,
        "weight_unit": "KG",
        "weight": 0
      },
      "hs_code": "{HS_CODE}",
      "country_of_origin": "{COUNTRY_CODE}",
      "custom_attributes": [{ "name": "{ATTR_NAME}", "value": "{ATTR_VALUE}" }],
      "manufacturer_identification_code": "{MIC}",
      "custom_description": "{CUSTOM_DESCRIPTION}",
      "per_country_hs_codes": [{ "country_code": "{COUNTRY_CODE}", "hs_code": "{HS_CODE}" }]
    }
  }
  ```
  Required: `sku.name`, `sku.description`.
- Source: yaml API_SELLER → `/v1/skus` POST; postman SELLER → /v1/skus

### `PUT /v1/skus`
Create or update a SKU. **Deprecated** — prefer `POST` + `PATCH`.

- Path params: none
- Query params: none
- Body: same shape as `POST /v1/skus` (uses `CreateSkuDTO`).
- Source: yaml API_SELLER → `/v1/skus` PUT; postman SELLER → /v1/skus (PUT)

### `POST /v1/skus/import`
Import a SKU (less strict than `POST` — only `name` is required).

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "sku": {
      "name": "{NAME}",
      "description": "{DESCRIPTION}",
      "external_id": "{EXTERNAL_ID}",
      "external_sku_name": "{EXTERNAL_SKU_NAME}",
      "barcode": "{BARCODE}",
      "type": "STANDARD",
      "fulfillment_strategy": "STOCK",
      "purchase_price": 0,
      "sell_price": 0,
      "unit_type": "BASE",
      "unit_of_measure": "EACH",
      "base_quantity": 1,
      "measurement": {
        "dimension_unit": "CM",
        "length": 0,
        "height": 0,
        "width": 0,
        "weight_unit": "KG",
        "weight": 0
      },
      "hs_code": "{HS_CODE}",
      "country_of_origin": "{COUNTRY_CODE}",
      "custom_attributes": [{ "name": "{ATTR_NAME}", "value": "{ATTR_VALUE}" }],
      "manufacturer_identification_code": "{MIC}",
      "custom_description": "{CUSTOM_DESCRIPTION}",
      "per_country_hs_codes": [{ "country_code": "{COUNTRY_CODE}", "hs_code": "{HS_CODE}" }]
    }
  }
  ```
  Required: `sku.name`.
- Source: yaml API_SELLER → `/v1/skus/import` POST; postman SELLER → /v1/skus/import

### `GET /v1/skus/export`
Export all SKUs as CSV (`text/csv` response).

- Path params: none
- Query params: none
- Body: none
- Source: yaml API_SELLER → `/v1/skus/export` GET; postman SELLER → /v1/skus/export

### `POST /v1/skus/get_many`
List SKUs with filter criteria via POST body (avoids URL length limits).

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "q": "{SEARCH}",
    "cursor": "{CURSOR}",
    "take": 100,
    "names": "{COMMA_SEPARATED_NAMES}",
    "ids": "{COMMA_SEPARATED_IDS}",
    "type": "STANDARD",
    "includes": "components",
    "exclude_sku_ids": "{COMMA_SEPARATED_IDS}",
    "archived": false
  }
  ```
  All fields optional.
- Source: yaml API_SELLER → `/v1/skus/get_many` POST; postman SELLER → /v1/skus/get_many

### `GET /v1/skus/{sku_id}`
Retrieve a SKU and related entities.

- Path params:
  - `sku_id` (string, required)
- Query params:
  - `includes` (string, optional) — comma-separated; supported value: `assemblies`
- Body: none
- Source: yaml API_SELLER → `/v1/skus/{sku_id}` GET; postman SELLER → /v1/skus/{sku_id}

### `PATCH /v1/skus/{sku_id}`
Update an existing SKU.

- Path params:
  - `sku_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "sku": {
      "external_id": "{EXTERNAL_ID}",
      "external_sku_name": "{EXTERNAL_SKU_NAME}",
      "description": "{DESCRIPTION}",
      "barcode": "{BARCODE}",
      "type": "STANDARD",
      "fulfillment_strategy": "STOCK",
      "purchase_price": 0,
      "sell_price": 0,
      "unit_type": "BASE",
      "unit_of_measure": "EACH",
      "base_quantity": 1,
      "measurement": {
        "dimension_unit": "CM",
        "length": 0,
        "height": 0,
        "width": 0,
        "weight_unit": "KG",
        "weight": 0
      },
      "hs_code": "{HS_CODE}",
      "country_of_origin": "{COUNTRY_CODE}",
      "custom_attributes": [{ "name": "{ATTR_NAME}", "value": "{ATTR_VALUE}" }],
      "custom_description": "{CUSTOM_DESCRIPTION}",
      "per_country_hs_codes": [{ "country_code": "{COUNTRY_CODE}", "hs_code": "{HS_CODE}" }],
      "manufacturer_identification_code": "{MIC}"
    }
  }
  ```
  Note: `name` is intentionally not patchable as a SELLER.
- Source: yaml API_SELLER → `/v1/skus/{sku_id}` PATCH; postman SELLER → /v1/skus/{sku_id} (PATCH)

### `POST /v1/skus/{sku_id}/units`
Create a unit on a SKU.

- Path params:
  - `sku_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "unit": {
      "name": "{UNIT_NAME}",
      "description": "{DESCRIPTION}",
      "barcode": "{BARCODE}",
      "unit_type": "TRADE",
      "unit_of_measure": "PALLET",
      "base_quantity": 1,
      "hs_code": "{HS_CODE}",
      "country_of_origin": "{COUNTRY_CODE}",
      "custom_attributes": [{ "name": "{ATTR_NAME}", "value": "{ATTR_VALUE}" }],
      "manufacturer_identification_code": "{MIC}"
    }
  }
  ```
  `unit_type` ∈ `TRADE` | `LOGISTICS`. `unit_of_measure` ∈ `EACH` | `CARTON` | `PALLET`.
- Source: yaml API_SELLER → `/v1/skus/{sku_id}/units` POST; postman SELLER → /v1/skus/{sku_id}/units

### `POST /v1/skus/{sku_id}/convert_to_assembly`
**Deprecated** — change SKU type to assembly with given `fulfillment_strategy`.

- Path params:
  - `sku_id` (string, required)
- Query params: none
- Body:
  ```json
  { "fulfillment_strategy": "BUNDLE" }
  ```
  `fulfillment_strategy` ∈ `BUNDLE` | `STOCK` (default `BUNDLE`).
- Source: yaml API_SELLER → `/v1/skus/{sku_id}/convert_to_assembly` POST; postman SELLER → /v1/skus/{sku_id}/convert_to_assembly

### `POST /v1/skus/{sku_id}/convert`
Convert SKU to a new type (`STANDARD` | `BUNDLE` | `MYSTERY` | `ALIAS`) and fulfillment strategy.

- Path params:
  - `sku_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "type": "BUNDLE",
    "fulfillment_strategy": "BUNDLE"
  }
  ```
  `type` ∈ `STANDARD` | `BUNDLE` | `MYSTERY` | `ALIAS` (default `STANDARD`). `fulfillment_strategy` ∈ `BUNDLE` | `STOCK` (default `STOCK`).
- Source: yaml API_SELLER → `/v1/skus/{sku_id}/convert` POST; postman SELLER → /v1/skus/{sku_id}/convert

### `POST /v1/skus/{sku_id}/archive`
Archive a SKU.

- Path params:
  - `sku_id` (string, required)
- Query params: none
- Body: none
- Source: yaml API_SELLER → `/v1/skus/{sku_id}/archive` POST; serverless.yml (yaml-only — not in postman collection)

### `POST /v1/skus/{sku_id}/unarchive`
Unarchive a SKU.

- Path params:
  - `sku_id` (string, required)
- Query params: none
- Body: none
- Source: yaml API_SELLER → `/v1/skus/{sku_id}/unarchive` POST; serverless.yml (yaml-only — not in postman collection)

### `PUT /v1/skus/{sku_id}/assembly_components`
Replace the full set of assembly components (edits + deletes via diff).

- Path params:
  - `sku_id` (string, required) — assembly SKU id
- Query params: none
- Body:
  ```json
  {
    "components": [
      {
        "component_sku_id": "{COMPONENT_SKU_ID}",
        "quantity": 1,
        "component_group_id": "{COMPONENT_GROUP_ID}",
        "priority": 1
      }
    ]
  }
  ```
  Each item requires `component_sku_id` and `quantity`. `component_group_id` and `priority` are optional (priority used for `ALIAS` SKUs — lower = higher priority).
- Source: yaml API_SELLER → `/v1/skus/{sku_id}/assembly_components` PUT; postman SELLER → /v1/skus/{sku_id}/assembly_components

### `POST /v1/skus/{sku_id}/assembly_components`
Add a single assembly component.

- Path params:
  - `sku_id` (string, required) — assembly SKU id
- Query params: none
- Body:
  ```json
  {
    "component": {
      "component_sku_id": "{COMPONENT_SKU_ID}",
      "quantity": 1,
      "component_group_id": "{COMPONENT_GROUP_ID}",
      "priority": 1
    }
  }
  ```
  Required: `component.component_sku_id`, `component.quantity`.
- Source: yaml API_SELLER → `/v1/skus/{sku_id}/assembly_components` POST; postman SELLER → /v1/skus/{kit_sku_id}/assembly_components

### `DELETE /v1/skus/{assembly_sku_id}/assembly_components/{component_sku_id}`
Delete an assembly component (the assembly→component relationship).

- Path params:
  - `assembly_sku_id` (string, required)
  - `component_sku_id` (string, required)
- Query params: none
- Body: none
- Source: yaml API_SELLER → `/v1/skus/{assembly_sku_id}/assembly_components/{component_sku_id}` DELETE; postman SELLER

### `POST /v1/skus/{sku_id}/component_groups`
Create a component group on an assembly SKU.

- Path params:
  - `sku_id` (string, required) — assembly SKU id
- Query params: none
- Body:
  ```json
  {
    "component_group": {
      "name": "{GROUP_NAME}",
      "quantity": 1,
      "selection_methods": ["MOST_AVAILABLE"]
    }
  }
  ```
  Required: `component_group.name`, `component_group.quantity`. `selection_methods` items ∈ `MOST_UNIQUE_TO_ORDER` | `MOST_AVAILABLE` | `LEAST_AVAILABLE` | `RANDOM` | `PRIORITY`.
  Note: postman collection uses `sku_component_group` instead of `component_group` — the spec key is `component_group`.
- Source: yaml API_SELLER → `/v1/skus/{sku_id}/component_groups` POST; postman SELLER → /v1/skus/{sku_id}/component_groups

### `PATCH /v1/skus/{sku_id}/component_groups/{component_group_id}`
Update a component group.

- Path params:
  - `sku_id` (string, required)
  - `component_group_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "component_group": {
      "name": "{GROUP_NAME}",
      "quantity": 1,
      "selection_methods": ["MOST_AVAILABLE"]
    }
  }
  ```
  All fields optional. Same naming caveat as the POST above.
- Source: yaml API_SELLER → `/v1/skus/{sku_id}/component_groups/{component_group_id}` PATCH; postman SELLER

### `DELETE /v1/skus/{sku_id}/component_groups/{component_group_id}`
Delete a component group and its associated components.

- Path params:
  - `sku_id` (string, required)
  - `component_group_id` (string, required)
- Query params: none
- Body: none
- Source: yaml API_SELLER → `/v1/skus/{sku_id}/component_groups/{component_group_id}` DELETE; postman SELLER

## SYSTEM context

### `GET /v1/skus`
List SKUs across accounts (M2M).

- Path params: none
- Query params:
  - `q` (string, optional) — search query
  - `cursor` (string, optional)
  - `take` (int, optional)
  - `names` (string, optional) — comma-separated
  - `ids` (string, optional) — comma-separated
  - `account_id` (string, optional) — restrict to one account (SYSTEM-only)
  - `type` (string, optional) — `STANDARD` | `BUNDLE` | `MYSTERY` | `ALIAS`
  - `includes` (string, optional) — `components`
  - `exclude_sku_ids` (string, optional)
  - `updated_at_after` (string, optional) — ISO date
  - `archived` (boolean, optional)
- Body: none
- Source: yaml API_SYSTEM → `/v1/skus` GET; postman SYSTEM → /v1/skus

### `PATCH /v1/skus/{sku_id}`
Update SKU as system (e.g., `verified_measurement` after warehouse measurement).

- Path params:
  - `sku_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "sku": {
      "account_id": "{ACCOUNT_ID}",
      "barcode": "{BARCODE}",
      "verified_measurement": {
        "dimension_unit": "CM",
        "length": 0,
        "height": 0,
        "width": 0,
        "weight_unit": "KG",
        "weight": 0
      }
    }
  }
  ```
  Required: `sku.account_id`, `sku.barcode`, `sku.verified_measurement`.
- Source: yaml API_SYSTEM → `/v1/skus/{sku_id}` PATCH; postman SYSTEM → /v1/skus/{sku_id}

### `PUT /v1/skus/{sku_id}/units`
Replace the entire set of units on a SKU as system.

- Path params:
  - `sku_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "account_id": "{ACCOUNT_ID}",
    "units": [
      {
        "name": "{UNIT_NAME}",
        "barcode": "{BARCODE}",
        "unit_of_measure": "PALLET",
        "base_quantity": 1,
        "verified_measurement": {
          "dimension_unit": "CM",
          "width": 0,
          "height": 0,
          "length": 0,
          "weight_unit": "KG",
          "weight": 0
        }
      }
    ]
  }
  ```
  Required: `account_id`. Each unit requires `base_quantity` and `unit_of_measure`. `unit_of_measure` ∈ `EACH` | `CARTON` | `PALLET`.
- Source: yaml API_SYSTEM → `/v1/skus/{sku_id}/units` PUT; postman SYSTEM → /v1/skus/{sku_id}/units

### `POST /v1/skus/get_many`
SYSTEM variant of get_many (same body as SELLER).

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "q": "{SEARCH}",
    "cursor": "{CURSOR}",
    "take": 100,
    "names": "{COMMA_SEPARATED_NAMES}",
    "ids": "{COMMA_SEPARATED_IDS}",
    "type": "STANDARD",
    "includes": "components",
    "exclude_sku_ids": "{COMMA_SEPARATED_IDS}",
    "archived": false
  }
  ```
  All fields optional.
- Source: yaml API_SYSTEM → `/v1/skus/get_many` POST; postman SYSTEM → /v1/skus/get_many

### `GET /v1/skus/{sku_id}`
Retrieve a SKU as system. Routed in `skuHttp.ts` (yaml-only — no postman entry).

- Path params:
  - `sku_id` (string, required)
- Query params:
  - `includes` (string, optional) — `assemblies`
- Body: none
- Source: handler `skuHttp.ts` route `GET /v1/skus/{sku_id}` (SYSTEM); not in API_SYSTEM.v1.yaml or postman

## PLATFORM context

### `POST /v1/skus/{sku_id}/refresh`
Trigger a SKU Updated event to fan out to other Lynk services.

- Path params:
  - `sku_id` (string, required)
- Query params: none
- Body: none
- Source: yaml API_PLATFORM → `/v1/skus/{sku_id}/refresh` POST; postman PLATFORM → /v1/skus/{sku_id}/refresh
