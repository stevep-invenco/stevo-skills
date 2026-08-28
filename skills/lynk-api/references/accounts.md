# Accounts Service — endpoints

Service prefix (dev/staging/prod): `/accounts`. Local: no prefix.

Every endpoint takes `Authorization: Bearer <JWT>`. The required principal **context** is shown per endpoint.

## SELLER context

### `GET /v1/users/me`
Get the currently authenticated user.

- Path params: none
- Query params: none
- Body: none
- Source: postman SELLER → User → /v1/users/me; openapi `API_SELLER.v1.yaml` GET /v1/users/me

### `PATCH /v1/users/me`
Update the currently authenticated user (e.g. switch active membership).

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "user": {
      "active_membership_id": "{MEMBERSHIP_ID}"
    }
  }
  ```
  Required: `user.active_membership_id`.
- Source: postman SELLER → User → /v1/users/me (PATCH); openapi `API_SELLER.v1.yaml` PATCH /v1/users/me

### `POST /v1/accounts/{account_id}/memberships`
Invite/add a membership to an account (seller-issued; defaults to SELLER context, may also issue WAREHOUSE memberships scoped to specific locations).

- Path params:
  - `account_id` (string, required) — Account to add the membership to.
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "membership": {
      "user_email": "{USER_EMAIL}",
      "access_context": "SELLER",
      "location_ids": ["{LOCATION_ID}"]
    }
  }
  ```
  Required: `membership.user_email`. Optional: `membership.access_context` (`SELLER`|`WAREHOUSE`, default `SELLER`), `membership.location_ids`.
- Source: postman SELLER → Account → /v1/accounts/{account_id}/memberships; openapi `API_SELLER.v1.yaml` POST /v1/accounts/{account_id}/memberships

### `GET /v1/locations`
List locations (scoped to the seller's account).

- Path params: none
- Query params:
  - `take` (number, optional) — page size.
  - `cursor` (string, optional) — pagination cursor.
  - `q` (string, optional) — free-text search (postman shows it as enabled query in some collections; safe to pass).
  - `account_id` (string, optional) — filter by account id.
  - `name` (string, optional) — filter by location name.
  - `sort_by` (string, optional) — `created_at` | `name` (default `name`).
  - `sort_direction` (string, optional) — `asc` | `desc` (default `asc`).
  - `status` (string, optional) — filter by location status (e.g. `ACTIVE`, `ARCHIVED`).
- Body: none
- Source: postman SELLER → Location → /v1/locations (GET); openapi `API_SELLER.v1.yaml` GET /v1/locations

### `POST /v1/locations`
Create a location.

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "location": {
      "name": "{LOCATION_NAME}",
      "type": "STANDARD",
      "address": {
        "address_1": "{ADDRESS_1}",
        "address_2": "{ADDRESS_2}",
        "city": "{CITY}",
        "state": "{STATE}",
        "postcode": "{POSTCODE}",
        "country": "{COUNTRY_CODE}"
      }
    }
  }
  ```
  Required: `location.name`, `location.type` (`STANDARD`|`WAREHOUSE`|`MANAGED`), `location.address` (with `address_1` and `country` required), `location.account_id` (per OpenAPI; usually inferred from caller's active membership in seller context — pass it if the caller is a platform user).
  Optional fields: `location.status`, `location.address.company_name`, `location.address.address_2`, `location.address.city`, `location.address.state`, `location.address.postcode`, `location.address.type`.
- Source: postman SELLER → Location → /v1/locations (POST); openapi `API_SELLER.v1.yaml` POST /v1/locations

### `GET /v1/bills/{bill_id}`
Get a bill by id.

- Path params:
  - `bill_id` (string, required) — Bill id.
- Query params: none
- Body: none
- Source: postman SELLER → Bill → /v1/bills/{bill_id} (note: postman raw URL incorrectly says `/v1/orders/{bill_id}` — the wired path is `/v1/bills/{bill_id}` per `serverless.yml` and openapi `API_SELLER.v1.yaml`).

### `GET /v1/list_views`
List the caller's list views.

- Path params: none
- Query params:
  - `take` (number, optional) — page size.
  - `cursor` (string, optional) — pagination cursor.
  - `list_id` (string, optional) — filter to views for a specific list.
- Body: none
- Source: postman SELLER → ListView → /v1/list_views (GET); openapi `API_SELLER.v1.yaml` GET /v1/list_views

### `POST /v1/list_views`
Create a list view.

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "list_view": {
      "name": "{VIEW_NAME}",
      "list_id": "{LIST_ID}",
      "filters": { "{FILTER_KEY}": "{FILTER_VALUE}" }
    }
  }
  ```
  Required: `list_view.name`, `list_view.list_id`, `list_view.filters` (object; may be empty `{}`).
- Source: postman SELLER → ListView → /v1/list_views (POST); openapi `API_SELLER.v1.yaml` POST /v1/list_views

### `PATCH /v1/list_views/{list_view_id}`
Update a list view's name and/or filters.

- Path params:
  - `list_view_id` (string, required) — List view id.
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "list_view": {
      "name": "{VIEW_NAME}",
      "filters": { "{FILTER_KEY}": "{FILTER_VALUE}" }
    }
  }
  ```
  All fields optional under `list_view`. Provide whichever you want to change.
- Source: postman SELLER → ListView → /v1/list_views/{list_view_id} (PATCH); openapi `API_SELLER.v1.yaml` PATCH /v1/list_views/{list_view_id}

### `DELETE /v1/list_views/{list_view_id}`
Delete a list view.

- Path params:
  - `list_view_id` (string, required) — List view id.
- Query params: none
- Body: none
- Source: postman SELLER → ListView → /v1/list_views/{list_view_id} (DELETE); openapi `API_SELLER.v1.yaml` DELETE /v1/list_views/{list_view_id}

## PLATFORM context

### `GET /v1/accounts`
List accounts.

- Path params: none
- Query params:
  - `take` (number, optional) — page size.
  - `cursor` (string, optional) — pagination cursor.
  - `q` (string, optional) — free-text search.
  - `sort_by` (string, optional) — `created_at` | `name` (default `name`).
  - `sort_direction` (string, optional) — `asc` | `desc` (default `asc`).
- Body: none
- Source: postman PLATFORM → Account → /v1/accounts (GET); openapi `API_PLATFORM.v1.yaml` GET /v1/accounts

### `POST /v1/accounts`
Create an account (also creates the primary user and adds them as a member).

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "account": {
      "name": "{ACCOUNT_NAME}",
      "code": "{ACCOUNT_CODE}",
      "primary_name": "{PRIMARY_USER_NAME}",
      "primary_email": "{PRIMARY_USER_EMAIL}",
      "primary_phone": "{PRIMARY_USER_PHONE}"
    }
  }
  ```
  Required: `account.name`, `account.code`, `account.primary_name`, `account.primary_email`, `account.primary_phone`.
  Optional fields: `account.external_id`.
- Source: postman PLATFORM → Account → /v1/accounts (POST); openapi `API_PLATFORM.v1.yaml` POST /v1/accounts

### `GET /v1/accounts/{account_id}`
Get an account by id.

- Path params:
  - `account_id` (string, required) — Account id.
- Query params: none
- Body: none
- Source: postman PLATFORM → Account → /v1/accounts/{account_id} (GET); openapi `API_PLATFORM.v1.yaml` GET /v1/accounts/{account_id}

### `PATCH /v1/accounts/{account_id}`
Update account details.

- Path params:
  - `account_id` (string, required) — Account id.
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "account": {
      "name": "{ACCOUNT_NAME}",
      "primary_name": "{PRIMARY_NAME}",
      "primary_email": "{PRIMARY_EMAIL}",
      "primary_phone": "{PRIMARY_PHONE}"
    }
  }
  ```
  All `account.*` fields are optional — pass only what you want to change.
  Optional fields: `account.external_id`, `account.name`, `account.primary_name`, `account.primary_email`, `account.primary_phone`.
  Note: postman example uses camelCase keys (`externalId`, `primaryEmail`, etc.) but the OpenAPI schema and the rest of the API use snake_case — prefer snake_case.
- Source: postman PLATFORM → Account → /v1/accounts/{{account_id}} (PATCH); openapi `API_PLATFORM.v1.yaml` PATCH /v1/accounts/{account_id}

### `POST /v1/accounts/{account_id}/enable_bill_holds`
Enable bill holds for the account so newly created bills are automatically held. Existing bills are not affected. Responds `409` if bill holds are already enabled (the existing reason is not overwritten); `400` if the reason is missing/empty.

- Path params:
  - `account_id` (string, required) — Account id.
- Query params: none
- Body (JSON):
  ```json
  {
    "reason": "{REASON}"
  }
  ```
  Required: `reason` (non-empty string) — the reason for enabling bill holds.
- Source: postman PLATFORM → Account → /v1/accounts/{account_id}/enable_bill_holds; openapi `API_PLATFORM.v1.yaml` POST /v1/accounts/{account_id}/enable_bill_holds

### `POST /v1/accounts/{account_id}/disable_bill_holds`
Disable bill holds for the account and clear the reason. Newly created bills will no longer be held automatically. Existing bill holds are not affected. Responds `409` if bill holds are already disabled.

- Path params:
  - `account_id` (string, required) — Account id.
- Query params: none
- Body: none
- Source: postman PLATFORM → Account → /v1/accounts/{account_id}/disable_bill_holds; openapi `API_PLATFORM.v1.yaml` POST /v1/accounts/{account_id}/disable_bill_holds

### `POST /v1/accounts/{account_id}/memberships`
Add a membership to an account (platform context — can target any access context).

- Path params:
  - `account_id` (string, required) — Account id.
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "membership": {
      "user_email": "{USER_EMAIL}",
      "access_context": "SELLER",
      "location_id": "{LOCATION_ID}"
    }
  }
  ```
  Required: `membership.user_email`. Optional: `membership.access_context` (`SELLER`|`WAREHOUSE`, default `SELLER`), `membership.location_id`.
- Source: postman PLATFORM → Account → /v1/accounts/{account_id}/memberships; openapi `API_PLATFORM.v1.yaml` POST /v1/accounts/{account_id}/memberships

### `DELETE /v1/accounts/{account_id}/memberships/{membership_id}`
Remove a membership from an account.

- Path params:
  - `account_id` (string, required) — Account id.
  - `membership_id` (string, required) — Membership id.
- Query params: none
- Body: none
- Source: postman PLATFORM → Account → /v1/accounts/{account_id}/memberships/{membership_id} (DELETE); openapi `API_PLATFORM.v1.yaml` DELETE /v1/accounts/{account_id}/memberships/{membership_id}

### `GET /v1/users/me`
Get the currently authenticated user.

- Path params: none
- Query params: none
- Body: none
- Source: postman PLATFORM → User → /v1/users/me (GET); openapi `API_PLATFORM.v1.yaml` GET /v1/users/me

### `PATCH /v1/users/me`
Update the currently authenticated user.

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "user": {
      "active_membership_id": "{MEMBERSHIP_ID}"
    }
  }
  ```
  Required: `user.active_membership_id`.
- Source: postman PLATFORM → User → /v1/users/me (PATCH); openapi `API_PLATFORM.v1.yaml` PATCH /v1/users/me

### `GET /v1/users/{user_id}`
Get a user by id.

- Path params:
  - `user_id` (string, required) — User id.
- Query params: none
- Body: none
- Source: postman PLATFORM → User → /v1/users/{user_id} (GET); openapi `API_PLATFORM.v1.yaml` GET /v1/users/{user_id}

### `PATCH /v1/users/{user_id}`
Update a user (e.g. set active membership).

- Path params:
  - `user_id` (string, required) — User id.
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "user": {
      "active_membership_id": "{MEMBERSHIP_ID}"
    }
  }
  ```
  Required: `user.active_membership_id`.
- Source: postman PLATFORM → User → /v1/users/{user_id} (PATCH); openapi `API_PLATFORM.v1.yaml` PATCH /v1/users/{user_id}

### `POST /v1/users`
Create a platform-managed user (sends invite).

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "user": {
      "name": "{USER_NAME}",
      "email": "{USER_EMAIL}",
      "phone": "{USER_PHONE}"
    }
  }
  ```
  Required: `user.name`, `user.email`. Optional: `user.phone`, `user.external_id`.
- Source: postman PLATFORM → User → /v1/users (POST); openapi `API_PLATFORM.v1.yaml` POST /v1/users

### `POST /v1/users/{user_id}/resend_invite`
Resend the invite email for a user.

- Path params:
  - `user_id` (string, required) — User id.
- Query params: none
- Body: none
- Source: postman PLATFORM → User → /v1/users/{user_id}/resend_invite; openapi `API_PLATFORM.v1.yaml` POST /v1/users/{user_id}/resend_invite

### `GET /v1/locations`
List locations across accounts.

- Path params: none
- Query params:
  - `take` (number, optional) — page size.
  - `cursor` (string, optional) — pagination cursor.
  - `q` (string, optional) — free-text search.
  - `account_id` (string, optional) — filter by account id.
  - `name` (string, optional) — filter by location name.
  - `location_ids` (string, optional) — comma-separated list of location ids.
  - `sort_by` (string, optional) — `created_at` | `name` (default `name`).
  - `sort_direction` (string, optional) — `asc` | `desc` (default `asc`).
- Body: none
- Source: postman PLATFORM → Location → /v1/locations (GET); openapi `API_PLATFORM.v1.yaml` GET /v1/locations

### `GET /v1/locations/{location_id}`
Get a location by id.

- Path params:
  - `location_id` (string, required) — Location id.
- Query params: none
- Body: none
- Source: postman PLATFORM → Location → /v1/locations/{location_id} (GET); openapi `API_PLATFORM.v1.yaml` GET /v1/locations/{location_id}

### `POST /v1/locations`
Create a location for a specific account.

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "location": {
      "name": "{LOCATION_NAME}",
      "account_id": "{ACCOUNT_ID}",
      "type": "STANDARD",
      "address": {
        "address_1": "{ADDRESS_1}",
        "address_2": "{ADDRESS_2}",
        "city": "{CITY}",
        "state": "{STATE}",
        "postcode": "{POSTCODE}",
        "country": "{COUNTRY_CODE}"
      }
    }
  }
  ```
  Required: `location.name`, `location.type` (`STANDARD`|`WAREHOUSE`|`MANAGED`), `location.account_id`, `location.address` (with `address_1` and `country` required).
  Optional fields: `location.status` (`ACTIVE`|`ARCHIVED`), `location.address.company_name`, `location.address.address_2`, `location.address.city`, `location.address.state`, `location.address.postcode`, `location.address.type`.
- Source: postman PLATFORM → Location → /v1/locations (POST); openapi `API_PLATFORM.v1.yaml` POST /v1/locations

### `GET /v1/bills`
List bills.

- Path params: none
- Query params:
  - `take` (number, optional) — page size.
  - `cursor` (string, optional) — pagination cursor.
  - `q` (string, optional) — free-text search.
  - `account_id` (string, optional) — filter by account id.
  - `period_includes_date` (string, optional, `YYYY-MM-DD`) — only bills whose period includes this date.
  - `status` (string, optional) — `OPEN` | `PENDING` | `CLOSED`.
  - `sort_by` (string, optional) — `created_at` | `period_start` (default `created_at`).
  - `sort_direction` (string, optional) — `asc` | `desc` (default `asc`).
- Body: none
- Source: postman PLATFORM → Bill → /v1/bills (GET); openapi `API_PLATFORM.v1.yaml` GET /v1/bills

### `GET /v1/bills/{bill_id}`
Get a bill by id.

- Path params:
  - `bill_id` (string, required) — Bill id.
- Query params: none
- Body: none
- Source: postman PLATFORM → Bill → /v1/bills/{bill_id} (GET); openapi `API_PLATFORM.v1.yaml` GET /v1/bills/{bill_id}

### `POST /v1/bills/{bill_id}/recalculate`
Recalculate a single bill's totals.

- Path params:
  - `bill_id` (string, required) — Bill id.
- Query params: none
- Body: none
- Source: postman PLATFORM → Bill → /v1/bills/{bill_id}/recalculate; openapi `API_PLATFORM.v1.yaml` POST /v1/bills/{bill_id}/recalculate

### `POST /v1/bills/{bill_id}/close`
Close a bill. A bill with one or more active holds cannot be closed (responds `409`) until every hold is released.

- Path params:
  - `bill_id` (string, required) — Bill id.
- Query params: none
- Body: none
- Source: postman PLATFORM → Bill → /v1/bills/{bill_id}/close; openapi `API_PLATFORM.v1.yaml` POST /v1/bills/{bill_id}/close

### `POST /v1/bills/{bill_id}/holds`
Add a hold to a bill. Responds `409` if a hold with the same reason already exists on the bill or the bill is closed; `400` if the reason is empty/missing.

- Path params:
  - `bill_id` (string, required) — Bill id.
- Query params: none
- Body: `{ "reason": string }` (required, non-empty) — the reason for the hold.
- Source: postman PLATFORM → Bill → /v1/bills/{bill_id}/holds; openapi `API_PLATFORM.v1.yaml` POST /v1/bills/{bill_id}/holds

### `DELETE /v1/bills/{bill_id}/holds/{hold_id}`
Release (delete) a hold from a bill.

- Path params:
  - `bill_id` (string, required) — Bill id.
  - `hold_id` (string, required) — Hold id.
- Query params: none
- Body: none
- Source: postman PLATFORM → Bill → /v1/bills/{bill_id}/holds/{hold_id}; openapi `API_PLATFORM.v1.yaml` DELETE /v1/bills/{bill_id}/holds/{hold_id}

### `POST /v1/bills/recalculate`
Recalculate all open bills (bulk).

- Path params: none
- Query params: none
- Body: none (postman shows empty body)
- Source: postman PLATFORM → Bill → /v1/bills/recalculate; openapi `API_PLATFORM.v1.yaml` POST /v1/bills/recalculate

### `POST /v1/service_agreements`
Create a service agreement (also creates the first bill).

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "service_agreement": {
      "account_id": "{ACCOUNT_ID}",
      "location_id": "{LOCATION_ID}",
      "commencement_date": "{YYYY-MM-DD}"
    }
  }
  ```
  Required: `service_agreement.account_id`, `service_agreement.location_id`, `service_agreement.commencement_date`.
- Source: postman PLATFORM → ServiceAgreement → /v1/service_agreements (POST); openapi `API_PLATFORM.v1.yaml` POST /v1/service_agreements

### `GET /v1/service_agreements`
List service agreements.

- Path params: none
- Query params:
  - `account_id` (string, optional) — filter by account id.
- Body: none
- Source: postman PLATFORM → ServiceAgreement → /v1/service_agreements (GET); openapi `API_PLATFORM.v1.yaml` GET /v1/service_agreements

### `GET /v1/service_agreements/{service_agreement_id}`
Get a service agreement by id.

- Path params:
  - `service_agreement_id` (string, required) — Service agreement id.
- Query params: none
- Body: none
- Source: postman PLATFORM → ServiceAgreement → /v1/service_agreements/{service_agreement_id} (GET); openapi `API_PLATFORM.v1.yaml` GET /v1/service_agreements/{service_agreement_id}

### `PATCH /v1/service_agreements/{service_agreement_id}`
Update a service agreement (commencement date).

- Path params:
  - `service_agreement_id` (string, required) — Service agreement id.
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "service_agreement": {
      "commencement_date": "{YYYY-MM-DD}"
    }
  }
  ```
  Required: `service_agreement.commencement_date`.
- Source: postman PLATFORM → ServiceAgreement → /v1/service_agreements/{service_agreement_id} (PATCH); openapi `API_PLATFORM.v1.yaml` PATCH /v1/service_agreements/{service_agreement_id}

### `POST /v1/service_agreements/{service_agreement_id}/terminate`
Terminate a service agreement.

- Path params:
  - `service_agreement_id` (string, required) — Service agreement id.
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "service_agreement": {
      "termination_date": "{YYYY-MM-DD}"
    }
  }
  ```
  Required: `service_agreement.termination_date`.
- Source: postman PLATFORM → ServiceAgreement → /v1/service_agreements/{service_agreement_id}/terminate; openapi `API_PLATFORM.v1.yaml` POST /v1/service_agreements/{service_agreement_id}/terminate

## SYSTEM context

### `GET /v1/accounts/{account_id}`
Get an account by id (system caller — typically used by other services).

- Path params:
  - `account_id` (string, required) — Account id.
- Query params: none
- Body: none
- Source: postman SYSTEM → Account → /v1/accounts/{account_id}; openapi `API_SYSTEM.v1.yaml` GET /v1/accounts/{account_id}

### `GET /v1/locations`
List locations (system caller — can filter by warehouse location ids in addition to seller filters).

- Path params: none
- Query params:
  - `take` (number, optional) — page size.
  - `cursor` (string, optional) — pagination cursor.
  - `q` (string, optional) — free-text search.
  - `account_id` (string, optional) — filter by account id.
  - `name` (string, optional) — filter by location name.
  - `location_ids` (string, optional) — comma-separated location ids.
  - `warehouse_location_ids` (string, optional) — comma-separated warehouse location ids (system-only filter).
  - `sort_by` (string, optional) — `created_at` | `name` (default `name`).
  - `sort_direction` (string, optional) — `asc` | `desc` (default `asc`).
- Body: none
- Source: postman SYSTEM → Location → /v1/locations (GET); openapi `API_SYSTEM.v1.yaml` GET /v1/locations

### `GET /v1/locations/{location_id}`
Get a location by id.

- Path params:
  - `location_id` (string, required) — Location id.
- Query params: none
- Body: none
- Source: postman SYSTEM → Location → /v1/locations/{location_id}; openapi `API_SYSTEM.v1.yaml` GET /v1/locations/{location_id}

### `GET /v1/users/{user_id}`
Get a user by id (system caller).

- Path params:
  - `user_id` (string, required) — User id.
- Query params: none
- Body: none
- Source: openapi `API_SYSTEM.v1.yaml` GET /v1/users/{user_id} (not present in postman SYSTEM folder).

## WAREHOUSE context

### `GET /v1/users/me`
Get the currently authenticated warehouse user.

- Path params: none
- Query params: none
- Body: none
- Source: postman WAREHOUSE → User → /v1/users/me (GET); openapi `API_WAREHOUSE.v1.yaml` GET /v1/users/me

### `PATCH /v1/users/me`
Update the currently authenticated warehouse user.

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "user": {
      "active_membership_id": "{MEMBERSHIP_ID}"
    }
  }
  ```
  Required: `user.active_membership_id`.
- Source: postman WAREHOUSE → User → /v1/users/me (PATCH); openapi `API_WAREHOUSE.v1.yaml` PATCH /v1/users/me
