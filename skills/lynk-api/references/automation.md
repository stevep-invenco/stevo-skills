# Automation Service — endpoints

Service prefix (dev/staging/prod): `/automation`. Local: no prefix.

Every endpoint takes `Authorization: Bearer <JWT>` unless noted otherwise. The required principal **context** is shown per endpoint. The same workflow paths are dual-mounted: the JWT's access context (SELLER vs WAREHOUSE) determines which controller (and which DTO shape) is used. SELLER tokens scope workflows to an account; WAREHOUSE tokens scope them to a WMS instance.

## UNAUTHENTICATED

### `GET /v1/info`
Health/info probe. Returns `{ healthy, git_commit_hash, git_branch_name, build_number }`.

- Path params: none
- Query params: none
- Body: none
- Auth: none (no authorizer attached in `serverless.yml`)
- Source: serverless.yml → functions.infoHttp → /v1/info

## SELLER context

Workflows created/managed under a SELLER token are scoped to an account. The `scope_type` is typically `ACCOUNT` and `scope_id` is the account id (the gateway derives scope from the JWT, so callers usually omit those fields on create).

### `POST /v1/workflows`
Create a workflow (seller scope).

- Path params: none
- Query params: none
- Body (JSON, snake_case):
  ```json
  {
    "workflow": {
      "id": "{WORKFLOW_ID}",
      "scope_type": "ACCOUNT",
      "scope_id": "{ACCOUNT_ID}",
      "name": "{WORKFLOW_NAME}",
      "description": "{DESCRIPTION}",
      "status": "ACTIVE",
      "data_type": "ORDER",
      "trigger_type": "ORDER_RELEASED",
      "rules": [
        {
          "name": "{RULE_NAME}",
          "condition": {
            "child_condition_type": "ALL",
            "child_conditions": [
              {
                "property": "skuName",
                "operator": "CONTAINS",
                "value": "{SKU_NAME_FRAGMENT}"
              }
            ]
          },
          "actions": [
            {
              "type": "ENSURE_ORDER_LINE",
              "params": {
                "sku_name": "{SKU_NAME}",
                "qty_ordered": 1,
                "unit_price": 0,
                "description": "{LINE_DESCRIPTION}"
              }
            }
          ],
          "else_actions": []
        }
      ]
    }
  }
  ```
- Notes: `workflow.id` is optional on create; if omitted the service generates one. Allowed enum values include `data_type` ∈ {`ORDER`, `WAREHOUSE_SHIPMENT`}, `trigger_type` example `ORDER_RELEASED`, `status` ∈ {`ACTIVE`, `INACTIVE`}. Rule `condition.child_conditions` may be flat property/operator/value tuples or nested typed conditions like `{"type":"ORDER_VALUE_EQUAL_TO_OR_OVER","value":["AUD","100"]}`. Action `type` examples: `ENSURE_ORDER_LINE`.
- Source: postman SELLER → /v1/workflows (POST); reference/API_SELLER.v1.yaml → POST /workflows (CreateWorkflowAsSellerDTO)

### `GET /v1/workflows`
List workflows (seller scope), paginated.

- Path params: none
- Query params:
  - `cursor` (string, optional) — opaque pagination cursor (SharedComponents.CursorQueryStringDTO)
  - `take` (number, optional) — page size (SharedComponents.TakeQueryStringDTO)
  - `search` (string, optional) — free-text search (SharedComponents.SearchQueryStringDTO)
  - `status` (string, optional, enum `ACTIVE` | `INACTIVE`) — filter by workflow status
- Body: none
- Source: postman SELLER → /v1/workflows (GET); reference/API_SELLER.v1.yaml → GET /workflows

### `GET /v1/workflows/{workflow_id}`
Fetch a single workflow.

- Path params:
  - `workflow_id` (string, required) — workflow id
- Query params: none
- Body: none
- Source: postman SELLER → /v1/workflows/{workflow_id} (GET); reference/API_SELLER.v1.yaml → GET /workflows/{workflow_id}

### `PUT /v1/workflows/{workflow_id}`
Replace/update a workflow.

- Path params:
  - `workflow_id` (string, required) — workflow id
- Query params: none
- Body (JSON, snake_case): same shape as `POST /v1/workflows` body above (CreateWorkflowAsSellerDTO under `workflow`).
  ```json
  {
    "workflow": {
      "id": "{WORKFLOW_ID}",
      "scope_type": "ACCOUNT",
      "scope_id": "{ACCOUNT_ID}",
      "name": "{WORKFLOW_NAME}",
      "description": "{DESCRIPTION}",
      "status": "INACTIVE",
      "data_type": "ORDER",
      "trigger_type": "ORDER_RELEASED",
      "rules": [
        {
          "name": "{RULE_NAME}",
          "condition": {
            "child_condition_type": "ALL",
            "child_conditions": [
              {
                "property": "skuName",
                "operator": "CONTAINS",
                "value": "{SKU_NAME_FRAGMENT}"
              }
            ]
          },
          "actions": [
            {
              "type": "ENSURE_ORDER_LINE",
              "params": {
                "sku_name": "{SKU_NAME}",
                "qty_ordered": 1,
                "unit_price": 0,
                "description": "{LINE_DESCRIPTION}"
              }
            }
          ],
          "else_actions": []
        }
      ]
    }
  }
  ```
- Source: postman SELLER → /v1/workflows/{workflow_id} (PUT); reference/API_SELLER.v1.yaml → PUT /workflows/{workflow_id}

### `DELETE /v1/workflows/{workflow_id}`
Delete a workflow.

- Path params:
  - `workflow_id` (string, required) — workflow id
- Query params: none
- Body: none
- Source: postman SELLER → /v1/workflows/{workflow_id} (DELETE); reference/API_SELLER.v1.yaml → DELETE /workflows/{workflow_id}

## WAREHOUSE context

Workflows created/managed under a WAREHOUSE token are scoped to a WMS instance. `scope_type` is typically `WMS_INSTANCE` and `scope_id` is the WMS instance id. `data_type` is typically `WAREHOUSE_SHIPMENT` with triggers like `WAREHOUSE_SHIPMENT_EXPORT`.

### `POST /v1/workflows`
Create a workflow (warehouse scope).

- Path params: none
- Query params: none
- Body (JSON, snake_case):
  ```json
  {
    "workflow": {
      "scope_id": "{WMS_INSTANCE_ID}",
      "scope_type": "WMS_INSTANCE",
      "name": "{WORKFLOW_NAME}",
      "description": "{DESCRIPTION}",
      "data_type": "WAREHOUSE_SHIPMENT",
      "trigger_type": "WAREHOUSE_SHIPMENT_EXPORT",
      "status": "INACTIVE",
      "rules": [
        {
          "name": "{RULE_NAME}",
          "condition": {
            "child_condition_type": "ALL",
            "child_conditions": [
              {
                "property": "WAREHOUSE_SHIPMENT_TENANT_CODE",
                "operator": "IN",
                "value": ["{TENANT_CODE}"]
              }
            ]
          },
          "actions": [
            {
              "type": "SET_WAREHOUSE_OPERATION_OPTIONS",
              "params": {
                "work_stream_name": "{WORK_STREAM_NAME}"
              }
            }
          ],
          "else_actions": []
        }
      ]
    }
  }
  ```
- Notes: action `type` examples for warehouse workflows: `SET_WAREHOUSE_OPERATION_OPTIONS`. Conditions can match warehouse-shipment properties such as `WAREHOUSE_SHIPMENT_TENANT_CODE`.
- Source: postman WAREHOUSE → /v1/workflows (POST); reference/API_WAREHOUSE.v1.yaml → POST /workflows (CreateWorkflowAsWarehouseDTO)

### `GET /v1/workflows`
List workflows (warehouse scope), paginated.

- Path params: none
- Query params:
  - `cursor` (string, optional) — opaque pagination cursor
  - `take` (number, optional) — page size
  - `search` (string, optional) — free-text search
  - `status` (string, optional, enum `ACTIVE` | `INACTIVE`) — filter by workflow status
- Body: none
- Source: postman WAREHOUSE → /v1/workflows (GET); reference/API_WAREHOUSE.v1.yaml → GET /workflows

### `GET /v1/workflows/{workflow_id}`
Fetch a single workflow.

- Path params:
  - `workflow_id` (string, required) — workflow id
- Query params: none
- Body: none
- Source: postman WAREHOUSE → /v1/workflows/{workflow_id} (GET); reference/API_WAREHOUSE.v1.yaml → GET /workflows/{workflow_id}

### `PUT /v1/workflows/{workflow_id}`
Replace/update a workflow.

- Path params:
  - `workflow_id` (string, required) — workflow id
- Query params: none
- Body (JSON, snake_case): same shape as `POST /v1/workflows` body above (CreateWorkflowAsWarehouseDTO under `workflow`).
  ```json
  {
    "workflow": {
      "scope_id": "{WMS_INSTANCE_ID}",
      "scope_type": "WMS_INSTANCE",
      "name": "{WORKFLOW_NAME}",
      "description": "{DESCRIPTION}",
      "data_type": "WAREHOUSE_SHIPMENT",
      "trigger_type": "WAREHOUSE_SHIPMENT_EXPORT",
      "status": "INACTIVE",
      "rules": [
        {
          "name": "{RULE_NAME}",
          "condition": {
            "child_condition_type": "ALL",
            "child_conditions": [
              {
                "property": "WAREHOUSE_SHIPMENT_TENANT_CODE",
                "operator": "IN",
                "value": ["{TENANT_CODE}"]
              }
            ]
          },
          "actions": [
            {
              "type": "SET_WAREHOUSE_OPERATION_OPTIONS",
              "params": {
                "work_stream_name": "{WORK_STREAM_NAME}"
              }
            }
          ],
          "else_actions": []
        }
      ]
    }
  }
  ```
- Source: postman WAREHOUSE → /v1/workflows/{workflow_id} (PUT); reference/API_WAREHOUSE.v1.yaml → PUT /workflows/{workflow_id}

### `DELETE /v1/workflows/{workflow_id}`
Delete a workflow.

- Path params:
  - `workflow_id` (string, required) — workflow id
- Query params: none
- Body: none
- Source: postman WAREHOUSE → /v1/workflows/{workflow_id} (DELETE); reference/API_WAREHOUSE.v1.yaml → DELETE /workflows/{workflow_id}
