# Sales Service — endpoints

Service prefix (dev/staging/prod): `/sales`. Local: no prefix.

Every endpoint takes `Authorization: Bearer <JWT>`. The required principal **context** is shown per endpoint.

Standard pagination query params used widely (described once here, referenced as "standard pagination" below):
- `cursor` (string, optional) — pagination cursor
- `take` (number, optional, -500..500) — page size
- `q` (string, optional) — free-text search

## SELLER context

### `GET /v1/orders`
List orders.

- Path params: none
- Query params:
  - standard pagination (`cursor`, `take`, `q`)
  - `status` (string, optional) — order status
  - `holds` (string, optional) — comma-separated hold types, or `ALL`
  - `names` (string, optional) — comma-separated order names
  - `channel_names` (string, optional) — comma-separated channel names
  - `sku_names` (string, optional) — comma-separated SKU names that should appear on order lines
  - `tag_names` (string, optional) — comma-separated tag names on the order
  - `external_ids` (string, optional) — comma-separated external ids
  - `includes` (string, optional) — comma-separated child elements: `order_lines`, `fulfillments`, `tags`
- Body: none
- Source: postman SELLER → Order, yaml SELLER

### `POST /v1/orders`
Create an order.

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "order": {
      "email": "{EMAIL}",
      "shipping_address": {
        "contact_name": "{CONTACT_NAME}",
        "address_1": "{ADDRESS_1}",
        "city": "{CITY}",
        "state": "{STATE}",
        "postcode": "{POSTCODE}",
        "country": "{COUNTRY}"
      }
    }
  }
  ```
  Required: `order.email`, `order.shipping_address`. Optional fields: `order.external_id`, `order.external_url`, `order.name`, `order.status` (`draft`|`pending`), `order.currency`, `order.channel_name`, `order.notes`, `order.delivery_instructions`, `order.packing_instructions`, `order.customer_order_number`, `order.reference`, `order.customer_name`, `order.phone`, `order.ordered_at` (ISO datetime), `order.subtotal_shipping`, `order.shipping_description`, `order.shipping_profile_name`, `order.allow_partial_fulfillments`, `order.ignore_address_correction`, `order.fulfillment_profile_name`, `order.billing_address`, `order.order_lines[]` (each line: required `sku_name`, `qty_ordered`, `unit_price`; optional `description`, `discount_amount`, `discount_rate`, `external_sku_code`, `external_sku_name`, `external_id`, `custom_attributes`, `managed_actions` [`EDIT`]), `order.tags[].name`, `order.commitment_priority_level` (-5..5), `order.custom_attributes`, `order.managed_actions[]` (`RELEASE`|`CANCEL`|`CLOSE`).
- Source: postman SELLER → Order, yaml SELLER `CreateOrderDTO`

### `GET /v1/orders/{order_id}`
Get an order.

- Path params: `order_id` (string, required)
- Query params: none
- Body: none
- Source: postman SELLER → Order, yaml SELLER

### `PATCH /v1/orders/{order_id}`
Update an order.

- Path params: `order_id` (string, required)
- Query params: none
- Body (snake_case JSON):
  ```json
  { "order": { } }
  ```
  All fields optional (any subset of): `external_id`, `external_url`, `name`, `status` (`draft`|`pending`), `currency`, `channel_name`, `notes`, `delivery_instructions`, `packing_instructions`, `customer_order_number`, `reference`, `customer_name`, `email`, `phone`, `ordered_at`, `subtotal_shipping`, `shipping_description`, `shipping_profile_id`, `shipping_profile_name`, `allow_partial_fulfillments`, `ignore_address_correction`, `fulfillment_profile_name`, `shipping_address`, `billing_address`, `order_lines[]`, `commitment_priority_level`, `custom_attributes`, `managed_actions` (replaces existing).
- Source: postman SELLER → Order, yaml SELLER `UpdateOrderDTO`

### `POST /v1/orders/{order_id}/revert_to_draft`
Revert order to draft.

- Path params: `order_id` (string, required)
- Query params: none
- Body: none required. Optional:
  ```json
  {
    "add_managed_actions": ["RELEASE"],
    "remove_managed_actions": ["CANCEL"]
  }
  ```
  Optional fields: `add_managed_actions[]`, `remove_managed_actions[]` (values: `RELEASE`, `CANCEL`, `CLOSE`).
- Source: postman SELLER → Order, yaml SELLER

### `POST /v1/orders/{order_id}/release`
Release a draft order.

- Path params: `order_id` (string, required)
- Query params: none
- Body: none
- Source: postman SELLER → Order, yaml SELLER

### `POST /v1/orders/{order_id}/cancel`
Cancel an order.

- Path params: `order_id` (string, required)
- Query params: none
- Body: none
- Source: postman SELLER → Order, yaml SELLER

### `POST /v1/orders/{order_id}/apply_manual_hold`
Apply a manual hold to an order.

- Path params: `order_id` (string, required)
- Query params: none
- Body: none
- Source: postman SELLER → Order, yaml SELLER

### `POST /v1/orders/{order_id}/release_manual_hold`
Release the manual hold on an order.

- Path params: `order_id` (string, required)
- Query params: none
- Body: none
- Source: postman SELLER → Order, yaml SELLER

### `POST /v1/orders/{order_id}/apply_managed_actions`
Add and/or remove managed actions on an order.

- Path params: `order_id` (string, required)
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "add_managed_actions": ["RELEASE"],
    "remove_managed_actions": ["CANCEL"]
  }
  ```
  Optional fields: `add_managed_actions[]`, `remove_managed_actions[]` (values: `RELEASE`, `CANCEL`, `CLOSE`). Duplicates across both arrays are treated as removes.
- Source: yaml SELLER (not in postman)

### `POST /v1/orders/{order_id}/close`
Close an order.

- Path params: `order_id` (string, required)
- Query params: none
- Body: none
- Source: postman SELLER → Order, yaml SELLER

### `POST /v1/orders/{order_id}/order_lines`
Create an order line on an existing order.

- Path params: `order_id` (string, required)
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "order_line": {
      "sku_name": "{SKU_NAME}",
      "qty_ordered": 1,
      "unit_price": 0
    }
  }
  ```
  Required: `order_line.sku_name`, `order_line.qty_ordered`, `order_line.unit_price`. Optional fields: `order_line.description`, `order_line.discount_amount`, `order_line.discount_rate`, `order_line.external_sku_code`, `order_line.external_sku_name`, `order_line.external_id`, `order_line.custom_attributes`, `order_line.managed_actions[]` (`EDIT`).
- Source: postman SELLER → Order, yaml SELLER `CreateOrderLineDTO`

### `PATCH /v1/orders/{order_id}/order_lines/{order_line_id}`
Update an order line.

- Path params: `order_id` (string, required), `order_line_id` (string, required)
- Query params: none
- Body (snake_case JSON):
  ```json
  { "order_line": { } }
  ```
  All fields optional: `sku_name`, `qty_ordered`, `unit_price`, `description`, `discount_amount`, `discount_rate`, `external_sku_code`, `external_id`, `custom_attributes`.
- Source: postman SELLER → Order, yaml SELLER

### `GET /v1/fulfillments`
List fulfillments.

- Path params: none
- Query params:
  - standard pagination (`cursor`, `take`)
  - `limit` (integer, optional) — number of fulfillments to return (legacy alt to `take`)
  - `status` (string, optional) — `OPEN`, `PROCESSING`, `CLOSED`
  - `order_id` (string, optional) — related order id
  - `ids` (string, optional) — comma-separated fulfillment ids
  - `includes` (string, optional) — comma-separated: `fulfillment_lines`, `order`, `order_lines`
- Body: none
- Source: postman SELLER → Fulfillment, yaml SELLER

### `GET /v1/fulfillments/{fulfillment_id}`
Get a fulfillment.

- Path params: `fulfillment_id` (string, required)
- Query params:
  - `collapse_bundles` (boolean, optional) — collapse bundle component lines into the parent
- Body: none
- Source: postman SELLER → Fulfillment, yaml SELLER

### `GET /v1/shipping_profiles`
List shipping profiles.

- Path params: none
- Query params: standard pagination (`cursor`, `take`, `q`)
- Body: none
- Source: postman SELLER → ShippingProfile, yaml SELLER

### `POST /v1/shipping_profiles`
Create a shipping profile.

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "shipping_profile": {
      "name": "{NAME}"
    }
  }
  ```
  Required: `shipping_profile.name`. Optional fields: `shipping_profile.channel_id`, `shipping_profile.shipping_descriptions[]`, `shipping_profile.carrier_services[]` (each: `id`, `name`, `code`), `shipping_profile.carrier_service` (single, nullable), `shipping_profile.fulfillment_service_type` (`ECONOMY`|`STANDARD`|`PRIORITY`, default `STANDARD`), `shipping_profile.signature_required` (default `false`), `shipping_profile.inco_terms` (`DDU`|`DDP`).
- Source: postman SELLER → ShippingProfile, yaml SELLER `CreateShippingProfileDTO`

### `GET /v1/shipping_profiles/{shipping_profile_id}`
Get a shipping profile.

- Path params: `shipping_profile_id` (string, required)
- Query params: none
- Body: none
- Source: postman SELLER → ShippingProfile, yaml SELLER

### `PATCH /v1/shipping_profiles/{shipping_profile_id}`
Update a shipping profile.

- Path params: `shipping_profile_id` (string, required)
- Query params: none
- Body (snake_case JSON):
  ```json
  { "shipping_profile": { } }
  ```
  All fields optional: `name`, `channel_id`, `shipping_descriptions[]`, `carrier_services[]`, `carrier_service`, `fulfillment_service_type`, `signature_required`, `inco_terms`.
- Source: postman SELLER → ShippingProfile, yaml SELLER `UpdateShippingProfileDTO`

### `DELETE /v1/shipping_profiles/{shipping_profile_id}`
Delete a shipping profile.

- Path params: `shipping_profile_id` (string, required)
- Query params: none
- Body: none
- Source: postman SELLER → ShippingProfile, yaml SELLER

### `GET /v1/channels`
List channels.

- Path params: none
- Query params: standard pagination (`cursor`, `take`, `q`)
- Body: none
- Source: postman SELLER → Channel, yaml SELLER

### `POST /v1/channels`
Create a channel.

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "channel": {
      "name": "{NAME}",
      "fulfillment_location_ids": ["{LOCATION_ID}"]
    }
  }
  ```
  Required: `channel.name`, `channel.fulfillment_location_ids`. Optional fields: `channel.category`, `channel.brand_name`, `channel.default_shipping_profile_id`.
- Source: postman SELLER → Channel, yaml SELLER `CreateChannelDTO`

### `GET /v1/channels/{channel_id}`
Get a channel.

- Path params: `channel_id` (string, required)
- Query params: none
- Body: none
- Source: postman SELLER → Channel, yaml SELLER

### `PATCH /v1/channels/{channel_id}`
Update a channel.

- Path params: `channel_id` (string, required)
- Query params: none
- Body (snake_case JSON):
  ```json
  { "channel": { } }
  ```
  All fields optional: `name`, `fulfillment_location_ids[]`, `category`, `brand_name`, `default_shipping_profile_id`.
- Source: postman SELLER → Channel, yaml SELLER `UpdateChannelDTO`

### `GET /v1/customers`
List/search customers.

- Path params: none
- Query params: standard pagination (`cursor`, `take`, `q`)
- Body: none
- Source: postman SELLER → Customer, yaml SELLER

### `POST /v1/listings`
Create a listing.

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "listing": {
      "name": "{NAME}",
      "channel_name": "{CHANNEL_NAME}"
    }
  }
  ```
  Required: `listing.name`, `listing.channel_name`. Optional fields: `listing.external_sku_name`, `listing.description`, `listing.external_id`, `listing.status` (`DRAFT`|`ACTIVE`|`ARCHIVED`), `listing.strategy` (`DYNAMIC_AVAILABLE`|`STATIC_RINGFENCE`|`SOLD_OUT`|`PRESELL`), `listing.collections[]`.
- Source: postman SELLER → Listing, yaml SELLER + `CreateListingDTO`

### `GET /v1/listings`
List listings.

- Path params: none
- Query params:
  - standard pagination (`cursor`, `take`, `q`)
  - `sku_ids` (string, optional) — comma-separated SKU ids
  - `channel_ids` (string, optional) — comma-separated channel ids
  - `channel_names` (string, optional) — comma-separated channel names
  - `statuses` (string, optional) — comma-separated statuses (`DRAFT`,`ACTIVE`,`ARCHIVED`)
  - `strategies` (string, optional) — comma-separated strategies (`DYNAMIC_AVAILABLE`,`STATIC_RINGFENCE`,`SOLD_OUT`,`PRESELL`)
  - `updated_at_after` (string, optional) — ISO datetime filter
  - `refreshed_at_after` (string, optional) — ISO datetime filter
  - `sort_by` (string, optional) — `created_at` (default) or `refreshed_at`
  - `sort_direction` (string, optional) — `asc` (default) or `desc`
- Body: none
- Source: postman SELLER → Listing, yaml SELLER

### `PATCH /v1/listings/{listing_id}`
Update a listing.

- Path params: `listing_id` (string, required)
- Query params: none
- Body (snake_case JSON):
  ```json
  { "listing": { } }
  ```
  All fields optional: `name`, `external_sku_name`, `description`, `external_id`, `channel_name`, `status` (`DRAFT`|`ACTIVE`|`ARCHIVED`), `strategy` (`DYNAMIC_AVAILABLE`|`SOLD_OUT`|`PRESELL`), `collections[]`.
- Source: postman SELLER → Listing, yaml SELLER

### `POST /v1/listings/{listing_id}/set_sku`
Bind a SKU to a listing.

- Path params: `listing_id` (string, required)
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "listing": { "name": "{SKU_NAME}" }
  }
  ```
  Required: `listing.name` (the SKU name to bind).
- Source: postman SELLER → Listing, yaml SELLER

### `POST /v1/listings/{listing_id}/refresh`
Refresh listing inventory snapshot.

- Path params: `listing_id` (string, required)
- Query params: none
- Body: none
- Source: postman SELLER → Listing, yaml SELLER

### `GET /v1/settings/account`
Get account settings.

- Path params: none
- Query params: none
- Body: none
- Source: postman SELLER → AccountSettings, yaml SELLER

### `PATCH /v1/settings/account`
Update or create account settings.

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "account_settings": {
      "default_shipping_profile_id": "{SHIPPING_PROFILE_ID}"
    }
  }
  ```
  Optional fields: `account_settings.default_shipping_profile_id` (nullable).
- Source: postman SELLER → AccountSettings, yaml SELLER

### `GET /v1/tags`
List tags.

- Path params: none
- Query params:
  - standard pagination (`cursor`, `take`, `q`)
  - `type` (string, optional) — tag type to filter by
- Body: none
- Source: postman SELLER → Tag, yaml SELLER

### `GET /v1/fulfillment_profiles`
List fulfillment profiles for the account.

- Path params: none
- Query params: standard pagination (`cursor`, `take`, `q`)
- Body: none
- Source: postman SELLER → FulfillmentProfile, yaml SELLER

### `POST /v1/fulfillment_profiles`
Create a fulfillment profile.

- Path params: none
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "fulfillment_profile": {
      "name": "{NAME}",
      "fulfillment_location_id": "{LOCATION_ID}"
    }
  }
  ```
  Required: `fulfillment_profile.name`, `fulfillment_profile.fulfillment_location_id`. Optional fields (per source TS DTO): `fulfillment_profile.fulfillment_location_ids[]`, `fulfillment_profile.stock_availability_strategies[]`, `fulfillment_profile.fallback_location_id`. (Postman example uses `fallback_location_id`, `fulfillment_location_ids`, `stock_availability_strategies`; yaml requires `fulfillment_location_id`.)
- Source: postman SELLER → FulfillmentProfile, yaml SELLER `CreateFulfillmentProfileDTO`

### `PATCH /v1/fulfillment_profiles/{fulfillment_profile_id}`
Update an existing fulfillment profile.

- Path params: `fulfillment_profile_id` (string, required)
- Query params: none
- Body (snake_case JSON):
  ```json
  { "fulfillment_profile": { } }
  ```
  All fields optional (any subset of the create fields): `name`, `fulfillment_location_id`, `fulfillment_location_ids[]`, `stock_availability_strategies[]`, `fallback_location_id`.
- Source: postman SELLER → FulfillmentProfile, yaml SELLER `UpdateFulfillmentProfileDTO`

## SYSTEM context

System endpoints accept an `account_id` query param (or body field on POSTs that need it) so the principal can scope operations to a specific tenant account.

### `PATCH /v1/orders/{order_id}`
Update an order (system principal).

- Path params: `order_id` (string, required)
- Query params: none
- Body (snake_case JSON): same shape as SELLER `PATCH /v1/orders/{order_id}`. All fields optional. See SELLER context for the full optional field list.
- Source: postman SYSTEM → Order, yaml SYSTEM

### `POST /v1/orders/{order_id}/release`
Release a draft order (system principal).

- Path params: `order_id` (string, required)
- Query params: none
- Body: none
- Source: postman SYSTEM → Order, yaml SYSTEM

### `POST /v1/orders/{order_id}/cancel`
Cancel an order (system principal).

- Path params: `order_id` (string, required)
- Query params: none
- Body: none
- Source: postman SYSTEM → Order, yaml SYSTEM

### `POST /v1/orders/{order_id}/revert_to_draft`
Revert order to draft (system principal). Used by automation flows.

- Path params: `order_id` (string, required)
- Query params: none
- Body: none required. Optional:
  ```json
  { "for_automation_last_started_at": "{ISO_DATETIME}" }
  ```
  Optional fields: `for_automation_last_started_at` (nullable string, used to no-op if a newer automation run has started).
- Source: postman SYSTEM → Order, yaml SYSTEM

### `POST /v1/orders/{order_id}/apply_manual_hold`
Apply a manual hold (system principal).

- Path params: `order_id` (string, required)
- Query params: none
- Body: none
- Source: postman SYSTEM → Order, yaml SYSTEM

### `PATCH /v1/orders/{order_id}/order_lines/{order_line_id}`
Update an order line (system principal).

- Path params: `order_id` (string, required), `order_line_id` (string, required)
- Query params: none
- Body (snake_case JSON):
  ```json
  { "order_line": { } }
  ```
  All fields optional: `external_sku_code`, `external_id`, `sku_name`, `qty_ordered`, `unit_price`, `description`, `discount_amount`, `discount_rate`, `custom_attributes`.
- Source: postman SYSTEM → Order, yaml SYSTEM

### `POST /v1/orders/{order_id}/order_lines`
Create an order line on an existing order (system principal).

- Path params: `order_id` (string, required)
- Query params: none
- Body (snake_case JSON):
  ```json
  {
    "order_line": {
      "sku_name": "{SKU_NAME}",
      "qty_ordered": 1,
      "unit_price": 0
    }
  }
  ```
  Required: `order_line.sku_name`, `order_line.qty_ordered`, `order_line.unit_price`. Optional fields: same as SELLER POST plus top-level `account_id` (nullable string, scopes to a specific account).
- Source: postman SYSTEM → Order, yaml SYSTEM

### `GET /v1/fulfillments`
List fulfillments (system principal).

- Path params: none
- Query params:
  - standard pagination (`cursor`, `take`)
  - `limit` (integer, optional)
  - `status` (string, optional) — `OPEN`, `PROCESSING`, `CLOSED`
  - `order_id` (string, optional)
  - `account_id` (string, optional) — scope to a specific account
  - `ids` (string, optional) — comma-separated fulfillment ids
  - `includes` (string, optional) — `fulfillment_lines`, `order`, `order_lines`
- Body: none
- Source: postman SYSTEM → Fulfillment, yaml SYSTEM

### `GET /v1/fulfillments/{fulfillment_id}`
Get a fulfillment (system principal).

- Path params: `fulfillment_id` (string, required)
- Query params:
  - `account_id` (string, optional) — scope to a specific account
  - `collapse_bundles` (boolean, optional)
- Body: none
- Source: postman SYSTEM → Fulfillment, yaml SYSTEM

### `POST /v1/fulfillments/{fulfillment_id}/close`
Manually close a fulfillment (system principal).

- Path params: `fulfillment_id` (string, required)
- Query params: none
- Body: none
- Source: postman SYSTEM → Fulfillment, yaml SYSTEM

### `POST /v1/fulfillments/{fulfillment_id}/cancel`
Manually cancel a fulfillment (system principal).

- Path params: `fulfillment_id` (string, required)
- Query params: none
- Body: none
- Source: postman SYSTEM → Fulfillment, yaml SYSTEM

### `GET /v1/customers`
List/search customers (system principal).

- Path params: none
- Query params:
  - standard pagination (`cursor`, `take`, `q`)
  - `account_id` (string, optional) — scope to a specific account
- Body: none
- Source: postman SYSTEM → Customer, yaml SYSTEM

## PLATFORM context

### `POST /v1/fulfillments/{fulfillment_id}/close`
Manually close a fulfillment (platform principal).

- Path params: `fulfillment_id` (string, required)
- Query params: none
- Body: none
- Source: postman PLATFORM → Fulfillment, yaml PLATFORM

### `POST /v1/fulfillments/{fulfillment_id}/reship`
Manually trigger the fulfillment-shipped event for a fulfillment (platform principal).

- Path params: `fulfillment_id` (string, required)
- Query params: none
- Body: none
- Source: postman PLATFORM → Fulfillment, yaml PLATFORM

### `POST /v1/fulfillments/{fulfillment_id}/recancel`
Manually trigger the fulfillment-cancelled event for a fulfillment (platform principal).

- Path params: `fulfillment_id` (string, required)
- Query params: none
- Body: none
- Source: yaml PLATFORM (not in postman)
