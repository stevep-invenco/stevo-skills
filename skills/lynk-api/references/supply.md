# Supply Service — endpoints

Service prefix (dev/staging/prod): `/supply`. Local: no prefix.

Every endpoint takes `Authorization: Bearer <JWT>`. The required principal **context** is shown per endpoint.

The supply service exposes a single domain — ASNs (Advanced Shipment Notices) and ASN lines. There are no vendor or purchase order endpoints. Context routing happens inside the lambda (`asnHttp.handler`), so the same path+method may map to different controllers depending on the auth context. See `src/modules/supply/infra/aws/handlers/asnHttp.ts`.

## Public (no auth) context

### `GET /v1/info`
Service info / health check (no authorizer attached in `serverless.yml`).

- Path params: none
- Query params: none
- Body: none
- Source: serverless.yml functions.infoHttp

## SELLER context

### `GET /v1/asns`
List ASNs (paginated, summary level — no nested asn lines unless `includes=asn_lines`).

- Path params: none
- Query params:
  - `cursor` (string, optional) — pagination cursor
  - `take` (integer, optional) — page size
  - `q` (string, optional) — free-text search
  - `sort_direction` (string, optional) — `asc` or `desc`
  - `status` (string, optional, deprecated) — single Asn status (use `statuses` instead)
  - `external_ids` (string, optional) — comma-separated Asn external ids
  - `statuses` (string, optional) — comma-separated Asn statuses (e.g. `DRAFT,PENDING`)
  - `locations` (string, optional) — comma-separated location ids
  - `presell` (string `true`|`false`, optional) — Asn presell flag
  - `updated_at_after` (string date-time, optional) — ISO timestamp
  - `closed_at_after` (string date-time, optional) — ISO timestamp
  - `includes` (string, optional) — `asn_lines` to embed lines
  - `sort_by` (string, optional) — `created_at` (default) or `closed_at`
- Body: none
- Source: yaml SELLER → `/v1/asns` GET; postman SELLER → /v1/asns GET

### `POST /v1/asns`
Create a new ASN to capture expected inbound inventory.

- Path params: none
- Query params: none
- Body:

```json
{
  "asn": {
    "name": "{ASN_NAME}",
    "reference": "{REFERENCE}",
    "external_id": "{EXTERNAL_ID}",
    "expected_at": "{ISO_TIMESTAMP}",
    "location_name": "{LOCATION_NAME}",
    "asn_lines": [
      {
        "sku_name": "{SKU_NAME}",
        "description": "{DESCRIPTION}",
        "qty_expected": 10,
        "manufacturer_identification_code": "{MIC}"
      }
    ],
    "status": "DRAFT",
    "carrier": "{CARRIER}",
    "tracking_number": "{TRACKING_NUMBER}",
    "note": "{NOTE}",
    "from_address": {
      "company_name": "{COMPANY_NAME}",
      "contact_name": "{CONTACT_NAME}",
      "contact_number": "{CONTACT_NUMBER}",
      "contact_email": "{CONTACT_EMAIL}",
      "address_1": "{ADDRESS_1}",
      "address_2": "{ADDRESS_2}",
      "city": "{CITY}",
      "state": "{STATE}",
      "postcode": "{POSTCODE}",
      "country": "{COUNTRY}"
    },
    "presell": true,
    "currency": "AUD"
  }
}
```

- Source: yaml SELLER → `/v1/asns` POST; postman SELLER → /v1/asns POST

### `GET /v1/asns/{asn_id}`
Retrieve a single ASN with nested data (asn_lines).

- Path params:
  - `asn_id` (string, required) — the ASN id
- Query params: none
- Body: none
- Source: yaml SELLER → `/v1/asns/{asn_id}` GET; postman SELLER → /v1/asns/{asn_id} GET

### `PATCH /v1/asns/{asn_id}`
Update an existing ASN (typically while in DRAFT). Seller may update from_address, expected_at, note, presell, location_name, currency, custom_attributes.

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body:

```json
{
  "asn": {
    "from_address": {
      "company_name": "{COMPANY_NAME}",
      "contact_name": "{CONTACT_NAME}",
      "contact_number": "{CONTACT_NUMBER}",
      "contact_email": "{CONTACT_EMAIL}",
      "address_1": "{ADDRESS_1}",
      "address_2": "{ADDRESS_2}",
      "city": "{CITY}",
      "state": "{STATE}",
      "postcode": "{POSTCODE}",
      "country": "{COUNTRY}"
    },
    "expected_at": "{ISO_TIMESTAMP}",
    "note": "{NOTE}",
    "presell": false,
    "location_name": "{LOCATION_NAME}",
    "currency": "AUD",
    "custom_attributes": {}
  }
}
```

- Source: yaml SELLER → `/v1/asns/{asn_id}` PATCH; postman SELLER → /v1/asns/{asn_id} PATCH

### `POST /v1/asns/{asn_id}/book`
Transition an ASN from DRAFT to OPEN.

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body: none
- Source: yaml SELLER → `/v1/asns/{asn_id}/book` POST; postman SELLER → /v1/asns/{asn_id}/book POST

### `POST /v1/asns/{asn_id}/cancel`
Cancel an ASN.

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body: none
- Source: yaml SELLER → `/v1/asns/{asn_id}/cancel` POST; postman SELLER → /v1/asns/{asn_id}/cancel POST

### `POST /v1/asns/{asn_id}/asn_lines`
Add a new line to an ASN.

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body:

```json
{
  "asn_line": {
    "sku_name": "{SKU_NAME}",
    "description": "{DESCRIPTION}",
    "qty_expected": 20,
    "manufacturer_identification_code": "{MIC}",
    "unit_purchase_cost": 0,
    "unit_cost_total": 0,
    "custom_attributes": {}
  }
}
```

- Source: yaml SELLER → `/v1/asns/{asn_id}/asn_lines` POST; postman SELLER → /v1/asns/{asn_id}/asn_lines POST

### `PATCH /v1/asns/{asn_id}/asn_lines/{asn_line_id}`
Update an ASN line (typically in DRAFT). `qty_expected` is required by the schema.

- Path params:
  - `asn_id` (string, required)
  - `asn_line_id` (string, required)
- Query params: none
- Body:

```json
{
  "asn_line": {
    "qty_expected": 120,
    "description": "{DESCRIPTION}",
    "manufacturer_identification_code": "{MIC}",
    "unit_purchase_cost": 0,
    "unit_cost_total": 0,
    "custom_attributes": {}
  }
}
```

- Source: yaml SELLER → `/v1/asns/{asn_id}/asn_lines/{asn_line_id}` PATCH; postman SELLER → /v1/asns/{asn_id}/asn_lines/{asn_line_id} PATCH

### `DELETE /v1/asns/{asn_id}/asn_lines/{asn_line_id}`
Delete an ASN line.

- Path params:
  - `asn_id` (string, required)
  - `asn_line_id` (string, required)
- Query params: none
- Body: none (postman shows a body but the yaml defines DELETE without a request body; ignore the postman body)
- Source: yaml SELLER → `/v1/asns/{asn_id}/asn_lines/{asn_line_id}` DELETE; postman SELLER → /v1/asns/{asn_id}/asn_lines/{asn_line_id} DELETE

### `POST /v1/asns/{asn_id}/recost`
Recost ASN lines (apply new unit purchase costs).

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body:

```json
{
  "recost_lines": [
    {
      "id": "{ASN_LINE_ID}",
      "unit_purchase_cost": 10,
      "unit_cost_total": 0
    }
  ]
}
```

- Source: yaml SELLER → `/v1/asns/{asn_id}/recost` POST; postman SELLER → /v1/asns/{{asn_id}}/recost POST

### `POST /v1/asns/{asn_id}/rollover`
Roll an ASN over (creates a successor ASN for the unreceived remainder). yaml-only.

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body: none
- Source: yaml SELLER → `/v1/asns/{asn_id}/rollover` POST; serverless.yml asnHttp; handler `RolloverAsnAsSellerController` (tag: yaml-only)

## SYSTEM context

### `GET /v1/asns`
List ASNs across accounts. SYSTEM variant accepts an `account_id` filter.

- Path params: none
- Query params:
  - `cursor` (string, optional)
  - `take` (integer, optional)
  - `q` (string, optional)
  - `sort_direction` (string, optional) — `asc` or `desc`
  - `account_id` (string, optional) — Lynk account id
  - `external_ids` (string, optional) — comma-separated
  - `statuses` (string, optional) — comma-separated (e.g. `DRAFT,PENDING`)
  - `locations` (string, optional) — comma-separated
  - `presell` (string `true`|`false`, optional)
  - `updated_at_after` (string date-time, optional)
  - `closed_at_after` (string date-time, optional)
  - `includes` (string, optional) — `asn_lines`
  - `sort_by` (string, optional) — `created_at` (default) or `closed_at`
- Body: none
- Source: yaml SYSTEM → `/v1/asns` GET; postman SYSTEM → /v1/asns GET

### `POST /v1/asns`
Create an ASN as the SYSTEM (must specify `account_id`).

- Path params: none
- Query params: none
- Body:

```json
{
  "asn": {
    "account_id": "{ACCOUNT_ID}",
    "reference": "{REFERENCE}",
    "external_id": "{EXTERNAL_ID}",
    "expected_at": "{ISO_TIMESTAMP}",
    "location_name": "{LOCATION_NAME}",
    "asn_lines": [
      {
        "sku_name": "{SKU_NAME}",
        "description": "{DESCRIPTION}",
        "qty_expected": 123
      }
    ],
    "status": "DRAFT",
    "carrier": "{CARRIER}",
    "tracking_number": "{TRACKING_NUMBER}",
    "note": "{NOTE}",
    "from_address": {
      "company_name": "{COMPANY_NAME}",
      "contact_name": "{CONTACT_NAME}",
      "contact_number": "{CONTACT_NUMBER}",
      "contact_email": "{CONTACT_EMAIL}",
      "address_1": "{ADDRESS_1}",
      "address_2": "{ADDRESS_2}",
      "city": "{CITY}",
      "state": "{STATE}",
      "postcode": "{POSTCODE}",
      "country": "{COUNTRY}"
    }
  }
}
```

- Source: yaml SYSTEM → `/v1/asns` POST; postman SYSTEM → /v1/asns POST

### `GET /v1/asns/{asn_id}`
Retrieve an ASN by id (SYSTEM scope).

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body: none
- Source: yaml SYSTEM → `/v1/asns/{asn_id}` GET; postman SYSTEM → /v1/asns/{asn_id} GET

### `PATCH /v1/asns/{asn_id}`
Update an ASN's `receipt_status` as SYSTEM. Requires a `location_id` alongside the ASN payload.

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body:

```json
{
  "asn": {
    "receipt_status": "WAITING",
    "custom_attributes": {}
  },
  "location_id": "{LOCATION_ID}"
}
```

`receipt_status` enum: `WAITING`, `PROCESSING`. `asn` and `location_id` are required.

- Source: yaml SYSTEM → `/v1/asns/{asn_id}` PATCH; postman SYSTEM → /v1/asns/{asn_id} PATCH

### `POST /v1/asns/{asn_id}/close`
Close an ASN, recording the actual received quantities per SKU.

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body:

```json
{
  "received_skus": [
    {
      "sku_name": "{SKU_NAME}",
      "qty_received": 123
    }
  ]
}
```

- Source: yaml SYSTEM → `/v1/asns/{asn_id}/close` POST; postman SYSTEM → /v1/asns/{asn_id}/close POST

### `POST /v1/asns/{asn_id}/cancel`
Cancel an ASN as SYSTEM.

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body: none
- Source: yaml SYSTEM → `/v1/asns/{asn_id}/cancel` POST; postman SYSTEM → /v1/asns/{asn_id}/cancel POST

## WAREHOUSE context

### `PATCH /v1/asns/{asn_id}`
Update an ASN's `receipt_status` as the receiving warehouse. The auth context's location is implicit (no `location_id` in body, unlike SYSTEM).

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body:

```json
{
  "asn": {
    "receipt_status": "WAITING",
    "custom_attributes": {}
  }
}
```

`receipt_status` enum: `WAITING`, `PROCESSING`. `asn` is required.

- Source: yaml WAREHOUSE → `/v1/asns/{asn_id}` PATCH; postman WAREHOUSE → /v1/asns/{asn_id} PATCH

### `POST /v1/asns/{asn_id}/close`
Close an ASN as the receiving warehouse, recording received quantities.

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body:

```json
{
  "received_skus": [
    {
      "sku_name": "{SKU_NAME}",
      "qty_received": 123
    }
  ]
}
```

- Source: yaml WAREHOUSE → `/v1/asns/{asn_id}/close` POST; postman WAREHOUSE → /v1/asns/{asn_id}/close POST

### `POST /v1/asns/{asn_id}/cancel`
Cancel an ASN as the receiving warehouse.

- Path params:
  - `asn_id` (string, required)
- Query params: none
- Body: none
- Source: yaml WAREHOUSE → `/v1/asns/{asn_id}/cancel` POST; postman WAREHOUSE → /v1/asns/{asn_id}/cancel POST
