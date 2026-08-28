# Warehousing Service — endpoints

Service prefix (dev/staging/prod): `/warehousing`. Local: no prefix.

Every endpoint takes `Authorization: Bearer <JWT>` unless noted otherwise. The required principal **context** is shown per endpoint.

This service is the WMS integration layer — it manages warehouses, WMS instances, tenants, warehouse-scoped SKUs, and warehouse carrier services, plus an EXTERNAL inbound webhook (`/v1/messages`) used by WMS providers to push shipment confirmations, status updates, item updates, inventory adjustments and warehouse receipts. There are **no** REST endpoints for picks/packs/bins/locations/containers/putaway — those are WMS-side concerns and only flow in via the `/v1/messages` passthrough. The `serverless.yml` confirms the full HTTP surface is what is documented below.

---

## WAREHOUSE context

### `GET /v1/warehouse_carrier_services`
List warehouse carrier services for the caller's warehouse.

- Path params: none
- Query params:
  - `cursor` (string, optional) — opaque cursor for pagination
  - `take` (number, optional) — page size
  - `search` (string, optional) — free-text search
- Body: none
- Source: postman WAREHOUSE → `/v1/warehouse_carrier_services` + `reference/API_WAREHOUSE.v1.yaml`

### `POST /v1/warehouse_carrier_services`
Create a warehouse carrier service mapping (Lynk carrier service → WMS carrier code).

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "warehouse_carrier_service": {
      "codes": [{ "code": "{WMS_CARRIER_CODE}", "is_primary": true }],
      "carrier_code": "{CARRIER_CODE}",
      "carrier_service_code": "{CARRIER_SERVICE_CODE}",
      "signature_required": false,
      "inco_terms": "DDP",
      "shipping_method_id": "{SHIPPING_METHOD_ID}",
      "wms_instance_id": "{WMS_INSTANCE_ID}"
    }
  }
  ```
  Required: `codes`, `carrier_code`, `carrier_service_code`, `signature_required`, `inco_terms` (`DDU` | `DDP`), `wms_instance_id`.
- Source: postman WAREHOUSE → `/v1/warehouse_carrier_services` + `reference/API_WAREHOUSE.v1.yaml`

### `GET /v1/warehouse_carrier_services/{warehouse_carrier_service_id}`
Get a single warehouse carrier service.

- Path params:
  - `warehouse_carrier_service_id` (string, required)
- Query params: none
- Body: none
- Source: postman WAREHOUSE → `/v1/warehouse_carrier_service/{warehouse_carrier_service_id}` + `reference/API_WAREHOUSE.v1.yaml`

### `PATCH /v1/warehouse_carrier_services/{warehouse_carrier_service_id}`
Update a warehouse carrier service.

- Path params:
  - `warehouse_carrier_service_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "warehouse_carrier_service": {
      "codes": [
        { "code": "{WMS_CARRIER_CODE_PRIMARY}", "is_primary": true },
        { "code": "{WMS_CARRIER_CODE_ALT}", "is_primary": false }
      ],
      "carrier_code": "{CARRIER_CODE}",
      "carrier_service_code": "{CARRIER_SERVICE_CODE}",
      "signature_required": false,
      "inco_terms": "DDP",
      "shipping_method_id": "{SHIPPING_METHOD_ID}",
      "wms_instance_id": "{WMS_INSTANCE_ID}"
    }
  }
  ```
- Source: postman WAREHOUSE → `/v1/warehouse_carrier_services/{warehouse_carrier_service_id}` + `reference/API_WAREHOUSE.v1.yaml`

### `GET /v1/warehouse_tenants`
List warehouse tenants visible to the caller's warehouse.

- Path params: none
- Query params:
  - `cursor` (string, optional)
  - `take` (number, optional)
  - `search` (string, optional)
  - `includes` (string, optional) — comma-separated child elements (`tenant`, `warehouse`)
- Body: none
- Source: postman WAREHOUSE → `/v1/warehouse_tenants` + `reference/API_WAREHOUSE.v1.yaml`

### `GET /v1/warehouse_tenants/{warehouse_tenant_id}`
Get a single warehouse tenant.

- Path params:
  - `warehouse_tenant_id` (string, required)
- Query params: none
- Body: none
- Source: postman WAREHOUSE → `/v1/warehouse_tenants/{warehouse_tenant_id} Copy` + `reference/API_WAREHOUSE.v1.yaml`

### `PATCH /v1/warehouse_tenants/{warehouse_tenant_id}`
Update warehouse-tenant operational options.

- Path params:
  - `warehouse_tenant_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "warehouse_tenant": {
      "warehouse_tenant_options": {
        "pack_method": "{PACK_METHOD}",
        "tariff_code": "{TARIFF_CODE}",
        "work_stream_name": "{WORK_STREAM_NAME}",
        "allowable_pick_strategies": ["{PICK_STRATEGY}"]
      }
    }
  }
  ```
  Required: `warehouse_tenant_options`.
- Source: postman WAREHOUSE → `/v1/warehouse_tenants/{warehouse_tenant_id}` + `reference/API_WAREHOUSE.v1.yaml`

### `GET /v1/warehouse_skus`
List warehouse-scoped SKUs (the WMS view of a SKU).

- Path params: none
- Query params:
  - `cursor` (string, optional)
  - `take` (number, optional)
  - `sku_names` (string, optional) — comma-separated SKU names to filter on
- Body: none
- Source: postman WAREHOUSE → `/v1/warehouse_skus` + `reference/API_WAREHOUSE.v1.yaml`

### `GET /v1/warehouse_skus/{warehouse_sku_id}`
Get a single warehouse SKU.

- Path params:
  - `warehouse_sku_id` (string, required)
- Query params: none
- Body: none
- Source: postman WAREHOUSE → `/v1/warehouse_skus/{warehouse_sku_id}` + `reference/API_WAREHOUSE.v1.yaml`

### `PATCH /v1/warehouse_skus/{warehouse_sku_id}`
Update warehouse-sku flags (batch / expiry / serial / autopack).

- Path params:
  - `warehouse_sku_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "warehouse_sku": {
      "batch_managed": true,
      "expiry_managed": true,
      "serial_managed": true,
      "autopack": true
    }
  }
  ```
- Source: postman WAREHOUSE → `/v1/warehouse_skus/{warehouse_sku_id}` + `reference/API_WAREHOUSE.v1.yaml`

### `GET /v1/wms_instances`
List WMS integration instances.

- Path params: none
- Query params:
  - `includes` (string, optional) — e.g. `warehouses` to include child warehouses
- Body: none
- Source: postman WAREHOUSE → `/v1/wms_instances` + `reference/API_WAREHOUSE.v1.yaml` (handler confirms WAREHOUSE context: `src/modules/warehousing/infra/aws/handlers/wmsInstanceHttp.ts`)

---

## PLATFORM context

### `GET /v1/warehouses`
List all warehouses across the platform.

- Path params: none
- Query params:
  - `cursor` (string, optional)
  - `take` (number, optional)
- Body: none
- Source: postman PLATFORM → `/v1/warehouses` + `reference/API_PLATFORM.v1.yaml`

### `POST /v1/warehouses`
Create a new warehouse and bind it to a WMS instance.

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "warehouse": {
      "name": "{WAREHOUSE_NAME}",
      "code": "{WAREHOUSE_CODE}",
      "account_id": "{ACCOUNT_ID}",
      "location_id": "{LOCATION_ID}",
      "wms_name": "DOTWMS",
      "wms_instance_code": "{WMS_INSTANCE_CODE}",
      "address": {
        "address_1": "{ADDRESS_LINE_1}",
        "address_2": "{ADDRESS_LINE_2}",
        "city": "{CITY}",
        "state": "{STATE}",
        "postcode": "{POSTCODE}",
        "country": "{COUNTRY}"
      }
    }
  }
  ```
  Required: `name`, `code`, `account_id`, `wms_name` (`DOTWMS` | `EXTENSIV` | `ORDERFLOW` | `BIZZYBEE`), `wms_instance_code`, `location_id`, `address`.
- Source: postman PLATFORM → `/v1/warehouses` + `reference/API_PLATFORM.v1.yaml`

### `POST /v1/warehouses/{warehouse_id}/warehouse_tenants`
Provision a tenant inside a warehouse.

- Path params:
  - `warehouse_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "warehouse_tenant": {
      "tenant_account_id": "{ACCOUNT_ID}",
      "tenant_name": "{TENANT_NAME}",
      "tenant_code": "{TENANT_CODE}",
      "warehouse_tenant_options": {
        "pack_method": "{PACK_METHOD}",
        "tariff_code": "{TARIFF_CODE}",
        "work_stream_name": "{WORK_STREAM_NAME}",
        "allowable_pick_strategies": ["{PICK_STRATEGY}"]
      }
    }
  }
  ```
  Required: `tenant_account_id`, `tenant_name`, `tenant_code`.
- Source: postman PLATFORM → `/v1/warehouses/{warehouse_id}/warehouse_tenants` + `reference/API_PLATFORM.v1.yaml`

### `POST /v1/integration_tasks/{integration_task_id}/replay`
Replay a failed integration task.

- Path params:
  - `integration_task_id` (string, required)
- Query params: none
- Body: none
- Source: postman PLATFORM → `/v1/integration_tasks/{integration_task_id}/replay` + `reference/API_PLATFORM.v1.yaml`

### `POST /v1/wms_instances`
Create a new WMS integration instance and access key.

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "wms_instance": {
      "code": "{WMS_INSTANCE_CODE}",
      "wms_name": "DOTWMS"
    }
  }
  ```
  Required: `code`, `wms_name` (`DOTWMS` | `EXTENSIV` | `BIZZYBEE` | `ORDERFLOW`).
- Source: postman PLATFORM → `/v1/wms_instances` + `reference/API_PLATFORM.v1.yaml`

### `GET /v1/tenants`
List warehousing-side tenants (one per account/warehouse).

- Path params: none
- Query params:
  - `cursor` (string, optional)
  - `take` (number, optional)
  - `account_id` (string, optional) — filter to a single account
- Body: none
- Source: postman PLATFORM → `/v1/tenants` + `reference/API_PLATFORM.v1.yaml`

### `GET /v1/tenants/{tenant_id}`
Get a single tenant.

- Path params:
  - `tenant_id` (string, required)
- Query params: none
- Body: none
- Source: postman PLATFORM → `/v1/tenants/{tenant_id}` + `reference/API_PLATFORM.v1.yaml`

### `PATCH /v1/tenants/{tenant_id}`
Update tenant mode (toggle between MIGRATION and LIVE). [yaml-only — not in postman]

- Path params:
  - `tenant_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "tenant": {
      "mode": "LIVE"
    }
  }
  ```
  Required: `tenant.mode` (`MIGRATION` | `LIVE`).
- Source: `reference/API_PLATFORM.v1.yaml` + `serverless.yml` + `src/modules/warehousing/infra/aws/handlers/tenantsHttp.ts`

---

## EXTERNAL context

This single endpoint is the WMS-to-Lynk inbound webhook. It is unauthenticated by JWT (no `warehousingAuth` authorizer in `serverless.yml`); WMS callers identify themselves with a bearer access key issued via `POST /v1/wms_instances` and routed by the `InstanceCode` / `TenantCode` fields in the payload. The body is intentionally a passthrough envelope and uses **CamelCase** WMS field names inside `data` (this is the on-the-wire format from the WMS providers — not Lynk snake_case).

### `POST /v1/messages`
Inbound webhook for WMS messages. The `message.type` field selects the message variant; `data` is shaped per type.

- Path params: none
- Query params: none
- Body envelope:
  ```json
  {
    "message": {
      "reference": "WMS",
      "type": "{MESSAGE_TYPE}",
      "data": { }
    }
  }
  ```
  Required: `message.type`, `message.data`. Also accepts `application/xml` and `text/xml` bodies (string passthrough).

  Known `message.type` values (from postman EXTERNAL examples):

  - `SHIPMENT_CONFIRMATION` — packjob shipment confirmation (sales fulfillment shipped). `data` includes `InstanceCode`, `TenantCode`, `WarehouseCode`, `JobType`, `PickMethod`, `PackMethod`, `SalesOrderNumber`, `PackSlipNumber`, `ParentCustomerCode`, `CustomerCode`, `OrderNumber`, `OrderDate`, plus per-line and per-package detail.
  - `SHIPMENT_STATUS_UPDATE` — packjob status updates. `data` includes `MessageCreationTimestamp`, `InstanceCode`, `TenantCode`, `WarehouseCode`, `SalesOrderNumber`, `PackSlipNumber`, `Additional01..NN`.
  - `CONNOTE_UPDATE` — package connote/dimension update. `data` includes `PackSlipNumber`, `ItemBarcode`, `VerifiedWeight`, `VerifiedWidth`, `VerifiedHeight`, `VerifiedDepth`.
  - `ITEM_UPDATE` — WMS-side SKU master update. `data` includes `TenantCode`, `ItemCode`, `ItemName`, `ItemGroup`, plus `IsBatchNumbered`, `IsSerialNumbered`, expiry/best-before flags, and capture-on-receipt flags.
  - `INVENTORY_ADJUSTMENT` — inventory deltas. `data` is an **array** of `{ Uldlid, ItemCode, Timestamp, ExpiryDate, TenantCode, BatchNumber, WarehouseCode, AdditionalInfo, TransactionType, ChangeByUnitQuantity }`.
  - `WAREHOUSE_RECEIPT_CONFIRMATION` — ASN/PO receipt. `data` includes a `Line` array of `{ ItemCode, ExpiryDate, SellByDate, BatchNumber, SerialNumber, PackagingDate, TradeItemType, NestBeforeDate, ProductionDate, TradeUnitQuantity, ReceivedBaseQuantity }` plus pack/header fields.

  Substitute `{PLACEHOLDERS}` for real WMS values when generating cURL.
- Source: postman EXTERNAL → `/v1/messages` (and 7 typed copies) + `reference/API_EXTERNAL.v1.yaml`

---

## UNAUTHENTICATED

These have no `Authorization` header requirement (no authorizer attached in `serverless.yml`).

### `GET /v1/info`
Service info / health probe. [serverless-only — not in postman or yaml]

- Path params: none
- Query params: none
- Body: none
- Source: `serverless.yml` → `infoHttp` (handler `src/modules/warehousing/infra/aws/handlers/infoHttp.handler`, no authorizer)
