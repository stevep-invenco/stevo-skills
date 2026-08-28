# Shipping Service — endpoints

Service prefix (dev/staging/prod): `/shipping`. Local: no prefix.

Every endpoint takes `Authorization: Bearer <JWT>` (except `/v1/info`). The required principal **context** is shown per endpoint. Several endpoints accept multiple contexts and are repeated under each section so callers can find them by role.

Conventional pagination/search query params (provided by `@invenco/common-interface`):
- `cursor` (string, optional) — opaque pagination cursor
- `take` (number, optional) — page size
- `q` (string, optional) — free-text search
- `sort_direction` (string, optional, `ASC|DESC`)

---

## SELLER context

### `GET /v1/shipments`
List shipments for the seller account.

- Path params: none
- Query params:
  - `names` (string, optional) — comma-separated shipment names
  - `shippable_ids` (string, optional) — comma-separated source document IDs (e.g. fulfillment IDs)
  - `channel_ids` (string, optional) — comma-separated channel IDs
  - `channel_names` (string, optional) — comma-separated channel names
  - `shipped_at_after` (string, optional) — ISO date-time lower bound
  - `statuses` (string, optional) — comma-separated shipment statuses
  - `sort_by` (string, optional, `created_at|shipped_at`, default `created_at`)
  - `includes` (string, optional) — `packages,shipment_lines,trackers,shipment_tracking_update`
  - `cursor`, `take`, `sort_direction`, `q` (standard)
- Body: none
- Source: postman SELLER → Shipment → /v1/shipments; yaml API_SELLER `/v1/shipments` GET

### `GET /v1/shipments/{shipment_id}`
Get a single shipment with nested entities.

- Path params: `shipment_id` (string, required)
- Query params: none
- Body: none
- Source: postman SELLER → Shipment → /v1/shipments/{shipment_id}; yaml API_SELLER `/v1/shipments/{shipment_id}` GET

### `GET /v1/carriers`
List carriers visible to the seller.

- Path params: none
- Query params:
  - `codes` (string, optional) — comma-separated carrier codes
  - `includes` (string, optional) — e.g. `carrier_services`
  - `q` (string, optional)
  - `cursor`, `take` (standard)
- Body: none
- Source: postman SELLER → Carrier → /v1/carriers; yaml API_SELLER `/v1/carriers` GET

### `GET /v1/carrier_services`
List carrier services.

- Path params: none
- Query params:
  - `codes` (string, optional) — comma-separated carrier service codes
  - `q` (string, optional)
  - `cursor`, `take` (standard)
- Body: none
- Source: postman SELLER → CarrierService → /v1/carrier_services; yaml API_SELLER `/v1/carrier_services` GET

### `GET /v1/carrier_services/available`
List the carrier services available to the seller account, derived from active shipping methods.

- Path params: none
- Query params:
  - `location_ids` (string, optional) — comma-separated location IDs
- Body: none
- Source: postman SELLER → CarrierService → /v1/carrier_services/available; yaml API_SELLER `/v1/carrier_services/available` GET

---

## PLATFORM context

### `GET /v1/shipments`
Platform-wide shipment listing (cross-account).

- Path params: none
- Query params: same as the SELLER `GET /v1/shipments` (`names`, `shippable_ids`, `channel_ids`, `channel_names`, `shipped_at_after`, `statuses`, `sort_by`, `includes`, `cursor`, `take`, `sort_direction`, `q`)
- Body: none
- Source: postman PLATFORM → Shipment → /v1/shipments; yaml API_PLATFORM `/v1/shipments` GET

### `POST /v1/shipments/quote`
Get a shipping quote for an in-flight shipment payload (no shipment must exist).

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "shipment": {
      "shippable_id": "{FULFILLMENT_ID}",
      "shippable_type": "FULFILLMENT",
      "account_id": "{ACCOUNT_ID}",
      "shipment_date": "{ISO_DATETIME}",
      "from": { "location_id": "{LOCATION_ID}" },
      "to": {
        "address_type": "RESIDENTIAL",
        "address_1": "{STREET}",
        "address_2": "{STREET_2}",
        "city": "{CITY}",
        "state": "{STATE}",
        "postcode": "{POSTCODE}",
        "country": "{COUNTRY_CODE}"
      },
      "packages": [
        {
          "name": "{PACKAGE_NAME}",
          "weight": { "value": 0.5, "unit": "KG" },
          "dimensions": { "length": 10, "height": 10, "width": 10, "unit": "CM" }
        }
      ]
    },
    "parameters": {
      "rating_method": "CHEAPEST",
      "carrier_service_ids": ["{CARRIER_SERVICE_ID}"]
    }
  }
  ```
- Source: yaml API_PLATFORM `/v1/shipments/quote` POST (postman has placeholder, no request body)

### `POST /v1/quotes`
Get a quote against a quotable document (e.g. fulfillment).

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "quotable_id": "{FULFILLMENT_ID}",
    "quotable_type": "FULFILLMENT",
    "account_id": "{ACCOUNT_ID}",
    "shipment_date": "{ISO_DATETIME}",
    "inco_terms": "DDU",
    "signature_required": false,
    "from": { "location_id": "{LOCATION_ID}" },
    "to": {
      "company_name": null,
      "contact_name": "{NAME}",
      "contact_number": "{PHONE}",
      "contact_email": "{EMAIL}",
      "address_1": "{STREET}",
      "city": "{CITY}",
      "state": "{STATE}",
      "postcode": "{POSTCODE}",
      "country": "{COUNTRY_CODE}",
      "address_type": "RESIDENTIAL"
    },
    "items": [
      {
        "sku_name": "{SKU}",
        "description": "{DESC}",
        "quantity": 1,
        "unit_weight": { "value": 0.8, "unit": "KG" },
        "unit_dimensions": { "length": 60, "width": 30, "height": 30, "unit": "CM" }
      }
    ],
    "parameters": {
      "rating_method": "CHEAPEST",
      "carrier_service_ids": ["{CARRIER_SERVICE_ID}"]
    }
  }
  ```
- Source: yaml API_PLATFORM `/v1/quotes` POST; handler quoteHttp routes PLATFORM/SYSTEM

### `POST /v1/shipments/{shipment_id}/recalculate_costs`
Recalculate carrier and shipping prices on an existing shipment.

- Path params: `shipment_id` (string, required)
- Query params: none
- Body: none (or `{}`)
- Source: postman PLATFORM → Shipment → /v1/shipments/{shipment_id}/recalculate_costs; yaml API_PLATFORM `/v1/shipments/{shipment_id}/recalculate_costs` POST

### `POST /v1/shipments/{shipment_id}/set_cost`
Manually set the shipment cost.

- Path params: `shipment_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "shipment_cost": {
      "cost": 99.99,
      "currency": "AUD"
    }
  }
  ```
- Source: postman PLATFORM → Shipment → /v1/shipments/{shipment_id}/set_cost; yaml API_PLATFORM `/v1/shipments/{shipment_id}/set_cost` POST

### `POST /v1/shipments/{shipment_id}/reship`
Trigger a reship of a previously shipped shipment.

- Path params: `shipment_id` (string, required)
- Query params: none
- Body: none (request body is empty in postman example)
- Source: postman PLATFORM → Shipment → /v1/shipments/{shipment_id}/reship; yaml API_PLATFORM `/v1/shipments/{shipment_id}/reship` POST

### `GET /v1/shipping_methods`
List shipping methods.

- Path params: none
- Query params:
  - `account_id` (string, optional)
  - `location_id` (string, optional)
  - `carrier_service_id` (string, optional)
  - `warehouse_shipping_method_id` (string, optional)
  - `carrier_account_id` (string, optional)
  - `type` (string, optional, `WAREHOUSE|MANAGED|LOCATION|GLOBAL`)
  - `status` (string, optional, `ACTIVE|INACTIVE|ARCHIVED`)
  - `cursor`, `take`, `q` (standard)
- Body: none
- Source: postman PLATFORM → ShippingMethod → /v1/shipping_methods; yaml API_PLATFORM `/v1/shipping_methods` GET

### `POST /v1/shipping_methods`
Create a shipping method (WAREHOUSE or MANAGED type, distinguished by body fields).

- Path params: none
- Query params: none
- Body (WAREHOUSE type):
  ```json
  {
    "shipping_method": {
      "name": "{NAME}",
      "account_id": "{ACCOUNT_ID}",
      "location_id": "{LOCATION_ID}",
      "rates_carrier_account_id": "{CARRIER_ACCOUNT_ID}",
      "booking_carrier_account_id": "{CARRIER_ACCOUNT_ID}",
      "carrier_service_id": "{CARRIER_SERVICE_ID}",
      "rate_match_method": "STATE_STATE",
      "rate_calculation_method": "PER_CONSIGNMENT",
      "status": "ACTIVE",
      "auto_invite": "MANAGED_LOCATIONS",
      "dynamically_priced": true
    }
  }
  ```
- Body (MANAGED type):
  ```json
  {
    "shipping_method": {
      "name": "{NAME}",
      "account_id": "{ACCOUNT_ID}",
      "location_id": "{LOCATION_ID}",
      "warehouse_shipping_method_id": "{WAREHOUSE_SHIPPING_METHOD_ID}",
      "carrier_service_id": "{CARRIER_SERVICE_ID}"
    }
  }
  ```
- Source: postman PLATFORM → ShippingMethod → /v1/shipping_methods (WAREHOUSE) / (MANAGED); yaml API_PLATFORM `/v1/shipping_methods` POST

### `GET /v1/shipping_methods/{shipping_method_id}`
Get a single shipping method.

- Path params: `shipping_method_id` (string, required)
- Query params: none
- Body: none
- Source: postman PLATFORM → ShippingMethod → /v1/shipping_methods/{shipping_method_id}; yaml API_PLATFORM `/v1/shipping_methods/{shipping_method_id}` GET

### `PATCH /v1/shipping_methods/{shipping_method_id}`
Update a shipping method.

- Path params: `shipping_method_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "shipping_method": {
      "rates_carrier_account_id": "{CARRIER_ACCOUNT_ID}",
      "booking_carrier_account_id": "{CARRIER_ACCOUNT_ID}",
      "rate_match_method": "ALL",
      "rate_match_calculation": "PER_PACKAGE",
      "status": "ACTIVE",
      "auto_invite": "MANAGED_LOCATIONS",
      "dynamic_price": true
    }
  }
  ```
- Source: postman PLATFORM → ShippingMethod → /v1/shipping_methods/{shipping_method_id}; yaml API_PLATFORM PATCH

### `POST /v1/shipping_methods/{shipping_method_id}/shipping_rates`
Add a shipping rate to a shipping method.

- Path params: `shipping_method_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "shipping_rate": {
      "from_location_id": "{LOCATION_ID}",
      "to_address_type": "RESIDENTIAL",
      "to_country_code": "AU",
      "to_state": "NSW",
      "to_city": "{CITY}",
      "to_postcode": "{POSTCODE}",
      "weight_min": 0,
      "weight_max": 999,
      "weight_unit": "KG",
      "packages_min": 1,
      "packages_max": 999,
      "total_cost": 100,
      "currency": "AUD",
      "delivery_days": 1,
      "valid_from": "{ISO_DATETIME}",
      "valid_to": "{ISO_DATETIME}"
    }
  }
  ```
- Source: postman PLATFORM → ShippingMethod → /v1/shipping_methods/{shipping_method_id}/shipping_rates; yaml API_PLATFORM POST

### `GET /v1/carriers`
List carriers (platform view).

- Path params: none
- Query params: same as SELLER `GET /v1/carriers` (`codes`, `includes`, `cursor`, `take`, `q`)
- Body: none
- Source: postman PLATFORM → Carrier → /v1/carriers; yaml API_PLATFORM `/v1/carriers` GET

### `POST /v1/carriers`
Create a carrier.

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "carrier": {
      "name": "{CARRIER_NAME}",
      "code": "{CARRIER_CODE}",
      "base_tracking_url": "{TRACKING_URL_TEMPLATE}"
    }
  }
  ```
- Source: postman PLATFORM → Carrier → /v1/carriers; yaml API_PLATFORM POST

### `POST /v1/carriers/{carrier_id}/carrier_services`
Add a carrier service under a carrier.

- Path params: `carrier_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "carrier_service": {
      "name": "{NAME}",
      "code": "{CODE}",
      "external_codes": ["{EXTERNAL_CODE}"],
      "category": "EXPRESS",
      "allowable_address_types": ["RESIDENTIAL", "BUSINESS", "POSTAL"],
      "allowable_inco_terms": ["DDU"],
      "rate_match_method": "STATE_STATE"
    }
  }
  ```
- Source: postman PLATFORM → Carrier → /v1/carriers/{carrier_id}/carrier_services; yaml API_PLATFORM POST

### `GET /v1/carrier_services`
List carrier services (platform view).

- Path params: none
- Query params: same as SELLER `GET /v1/carrier_services` (`codes`, `cursor`, `take`, `q`)
- Body: none
- Source: postman PLATFORM → CarrierService → /v1/carrier_services; yaml API_PLATFORM GET

### `PATCH /v1/carrier_services/{carrier_service_id}`
Update a carrier service.

- Path params: `carrier_service_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "carrier_service": {
      "code": "{CODE}",
      "external_codes": ["{EXT1}", "{EXT2}"],
      "category": "PICK_UP",
      "name": "{NAME}",
      "rate_match_method": "STATE_STATE",
      "allowable_address_types": ["BUSINESS", "POSTAL"],
      "allowable_inco_terms": ["DDU"]
    }
  }
  ```
- Source: postman PLATFORM → CarrierService → /v1/carrier_services/{carrier_service_id}; yaml API_PLATFORM PATCH

### `POST /v1/carrier_services/{carrier_service_id}/carrier_rates`
Add a carrier rate to a carrier service.

- Path params: `carrier_service_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "carrier_rate": {
      "carrier_account_id": "{CARRIER_ACCOUNT_ID}",
      "from_address": {
        "address_1": "{STREET}",
        "city": "{CITY}",
        "state": "{STATE}",
        "postcode": "{POSTCODE}",
        "country": "{COUNTRY_CODE}"
      },
      "to_country_code": "AU",
      "to_state": "NSW",
      "to_postcode": "{POSTCODE}",
      "weight": 5.1,
      "weight_unit": "KG",
      "total_cost": 18.88,
      "base_cost": 20,
      "currency": "AUD",
      "delivery_days": 1,
      "valid_from": "{ISO_DATETIME}",
      "allowable_address_types": ["RESIDENTIAL", "POSTAL"],
      "packages_min": 5,
      "packages_max": 10
    }
  }
  ```
- Source: postman PLATFORM → CarrierService → /v1/carrier_services/{carrier_service_id}/carrier_rates; yaml API_PLATFORM POST

### `GET /v1/carrier_services/{carrier_service_id}/carrier_rates`
List carrier rates for a carrier service.

- Path params: `carrier_service_id` (string, required)
- Query params:
  - `cursor`, `take` (standard)
- Body: none
- Source: postman PLATFORM → CarrierService → /v1/carrier_services/{carrier_service_id}/carrier_rates; yaml API_PLATFORM GET

### `PATCH /v1/carrier_services/{carrier_service_id}/carrier_rates/{carrier_rate_id}`
Update a carrier rate.

- Path params: `carrier_service_id` (string, required), `carrier_rate_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "carrier_rate": {
      "carrier_account_id": "{CARRIER_ACCOUNT_ID}",
      "from_address": {
        "address_1": "{STREET}",
        "city": "{CITY}",
        "state": "{STATE}",
        "postcode": "{POSTCODE}",
        "country": "{COUNTRY_CODE}"
      },
      "to_country_code": "AU",
      "to_state": "NSW",
      "to_city": "{CITY}",
      "to_postcode": "{POSTCODE}",
      "weight": 10.2,
      "weight_unit": "KG",
      "total_cost": 22.66,
      "currency": "USD",
      "delivery_days": 2,
      "valid_from": "{ISO_DATETIME}",
      "valid_to": "{ISO_DATETIME}",
      "allowable_address_types": ["RESIDENTIAL", "BUSINESS"],
      "packages_min": 1,
      "packages_max": 5
    }
  }
  ```
- Source: postman PLATFORM → CarrierService → /v1/carrier_services/{carrier_service_id}/carrier_rates/{carrier_rate_id}; yaml API_PLATFORM PATCH

### `GET /v1/carrier_rates/{carrier_rate_id}`
Get a single carrier rate.

- Path params: `carrier_rate_id` (string, required)
- Query params: none
- Body: none
- Source: postman PLATFORM → CarrierRate → /v1/carrier_rates/{carrier_rate_id}; yaml API_PLATFORM GET

### `POST /v1/shipping_prices`
Create a shipping price.

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "shipping_price": {
      "account_id": "{ACCOUNT_ID}",
      "name": "{NAME}",
      "location_id": "{LOCATION_ID}",
      "valid_from": "{ISO_DATETIME}",
      "valid_to": "{ISO_DATETIME}",
      "price_bands": [
        { "markup": 0.35, "max_cost": 7.5 },
        { "markup": 0.30, "max_cost": 12.5 },
        { "markup": 0.20 }
      ],
      "carrier_prices": [
        {
          "carrier_id": "{CARRIER_ID}",
          "price_bands": [
            { "markup": 2.10, "max_cost": 30.5 },
            { "markup": 2.30 }
          ]
        }
      ]
    }
  }
  ```
- Source: postman PLATFORM → ShippingPrice → /v1/shipping_prices; yaml API_PLATFORM POST

### `GET /v1/shipping_prices`
List shipping prices.

- Path params: none
- Query params:
  - `account_id` (string, optional)
  - `cursor`, `take`, `q` (standard)
- Body: none
- Source: postman PLATFORM → ShippingPrice → /v1/shipping_prices; yaml API_PLATFORM GET

### `GET /v1/shipping_prices/{shipping_price_id}`
Get a shipping price.

- Path params: `shipping_price_id` (string, required)
- Query params: none
- Body: none
- Source: postman PLATFORM → ShippingPrice → /v1/shipping_prices/{shipping_price_id}; yaml API_PLATFORM GET

### `PATCH /v1/shipping_prices/{shipping_price_id}`
Update a shipping price.

- Path params: `shipping_price_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "shipping_price": {
      "name": "{NAME}",
      "location_id": "{LOCATION_ID}",
      "valid_from": "{ISO_DATETIME}",
      "valid_to": "{ISO_DATETIME}",
      "price_bands": [
        { "markup": 0.35, "max_cost": 17.5 },
        { "markup": 0.30 }
      ],
      "carrier_prices": [
        {
          "carrier_id": "{CARRIER_ID}",
          "price_bands": [
            { "markup": 2.10, "max_cost": 30.5 },
            { "markup": 2.30 }
          ]
        }
      ]
    }
  }
  ```
- Source: postman PLATFORM → ShippingPrice → /v1/shipping_prices/{shipping_price_id}; yaml API_PLATFORM PATCH

### `POST /v1/carrier_accounts`
Create a carrier account.

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "carrier_account": {
      "name": "{NAME}",
      "code": "{CODE}",
      "carrier_id": "{CARRIER_ID}",
      "account_id": "{ACCOUNT_ID}",
      "authorization": {
        "token": "{CREDENTIAL}"
      }
    }
  }
  ```
  Required: `name`, `code`, `carrier_id`, `account_id`, `authorization`.
- Source: postman PLATFORM → CarrierAccount → /v1/carrier_accounts; yaml API_PLATFORM POST

### `GET /v1/carrier_accounts`
List carrier accounts (platform view).

- Path params: none
- Query params:
  - `carrier_ids` (string, optional) — comma-separated
  - `account_id` (string, optional)
  - `cursor`, `take` (standard)
- Body: none
- Source: postman PLATFORM → CarrierAccount → /v1/carrier_accounts; yaml API_PLATFORM GET

### `PATCH /v1/carrier_accounts/{carrier_account_id}`
Update a carrier account.

- Path params: `carrier_account_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "carrier_account": {
      "name": "{NAME}",
      "code": "{CODE}",
      "carrier_id": "{CARRIER_ID}",
      "account_id": "{ACCOUNT_ID}",
      "authorization": {
        "foo": "bar"
      }
    }
  }
  ```
- Source: postman PLATFORM → CarrierAccount → /v1/carrier_accounts/{carrier_account_id}; yaml API_PLATFORM PATCH

---

## SYSTEM context

### `POST /v1/shipments`
Create a shipment with shipment lines and packages.

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "shipment": {
      "status": "DRAFT",
      "from_location_id": "{LOCATION_ID}",
      "account_id": "{ACCOUNT_ID}",
      "shippable_id": "{FULFILLMENT_ID}",
      "shippable_type": "FULFILLMENT",
      "channel_name": "{CHANNEL_NAME}",
      "from_address": {
        "company_name": "{COMPANY}",
        "contact_name": "{NAME}",
        "contact_number": "{PHONE}",
        "contact_email": "{EMAIL}",
        "address_1": "{STREET}",
        "address_2": "{STREET_2}",
        "city": "{CITY}",
        "state": "{STATE}",
        "postcode": "{POSTCODE}",
        "country": "{COUNTRY_CODE}"
      },
      "to_address": {
        "company_name": "{COMPANY}",
        "contact_name": "{NAME}",
        "contact_number": "{PHONE}",
        "contact_email": "{EMAIL}",
        "address_1": "{STREET}",
        "address_2": "{STREET_2}",
        "city": "{CITY}",
        "state": "{STATE}",
        "postcode": "{POSTCODE}",
        "country": "{COUNTRY_CODE}"
      },
      "packages": [
        { "name": "{PACKAGE_NAME}", "height": 0, "length": 0, "width": 0, "weight": 0 }
      ],
      "shipment_lines": [
        { "sku": "{SKU}", "description": "{DESC}", "qty_shipped": 0, "unit_value": 0, "unit_weight": 0 }
      ]
    }
  }
  ```
- Source: postman SYSTEM → Shipment → /v1/shipments POST; yaml API_SYSTEM `/v1/shipments` POST

### `GET /v1/shipments/{shipment_id}`
Get a shipment by id (system caller).

- Path params: `shipment_id` (string, required)
- Query params: none
- Body: none
- Source: postman SYSTEM → Shipment → /v1/shipments/{shipment_id}; yaml API_SYSTEM `/v1/shipments/{shipment_id}` GET

### `PATCH /v1/shipments/{shipment_id}`
Update shipment status.

- Path params: `shipment_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "shipment": {
      "status": "WAITING"
    }
  }
  ```
  `status` enum: `WAITING|PROCESSING`.
- Source: postman SYSTEM → Shipment → /v1/shipments/{shipment_id} PATCH; yaml API_SYSTEM PATCH

### `POST /v1/shipments/{shipment_id}/verify`
Submit verified package barcodes/dimensions/weights.

- Path params: `shipment_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "packages": [
      {
        "barcode": "{PACKAGE_BARCODE}",
        "verified_dimensions": {
          "width": 125.0,
          "height": 200.0,
          "length": 150.15,
          "unit": "MM"
        },
        "verified_weight": {
          "value": 1.66,
          "unit": "KG"
        }
      }
    ]
  }
  ```
  Required: `packages[].barcode`, `verified_dimensions`, `verified_weight`.
- Source: postman SYSTEM → Shipment → /v1/shipments/{shipment_id}/verify; yaml API_SYSTEM POST

### `POST /v1/shipments/{shipment_id}/ship`
Mark a shipment as shipped, providing carrier/service/tracking and updated package + line data.

- Path params: `shipment_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "shipment": {
      "external_id": "{EXTERNAL_ID}",
      "to_address": {
        "company_name": "{COMPANY}",
        "contact_name": "{NAME}",
        "contact_number": "{PHONE}",
        "contact_email": "{EMAIL}",
        "address_1": "{STREET}",
        "address_2": "{STREET_2}",
        "city": "{CITY}",
        "state": "{STATE}",
        "postcode": "{POSTCODE}",
        "country": "{COUNTRY_CODE}"
      },
      "carrier_code": "{CARRIER_CODE}",
      "carrier_service_id": "{CARRIER_SERVICE_ID}",
      "carrier_service_code": "{CARRIER_SERVICE_CODE}",
      "shipping_method_id": "{SHIPPING_METHOD_ID}",
      "signature_required": true,
      "inco_terms": "DDU",
      "tracking_number": "{TRACKING_NUMBER}",
      "tracking_status": "PENDING",
      "packages": [
        {
          "name": "{PACKAGE_NAME}",
          "measurement": {
            "dimension_unit": "CM",
            "length": 10,
            "width": 10,
            "height": 10,
            "weight_unit": "KG",
            "weight": 10
          },
          "packaging_barcode": "{PACKAGING_BARCODE}",
          "barcode": "{BARCODE}"
        }
      ],
      "shipment_lines": [
        {
          "sku": "{SKU}",
          "description": "{DESC}",
          "qty_shipped": 1,
          "unit_value": 10,
          "unit_weight": 10,
          "package_name": "{PACKAGE_NAME}"
        }
      ]
    }
  }
  ```
- Source: postman SYSTEM → Shipment → /v1/shipments/{shipment_id}/ship; yaml API_SYSTEM POST

### `POST /v1/shipments/{shipment_id}/cancel`
Cancel a shipment.

- Path params: `shipment_id` (string, required)
- Query params: none
- Body: none
- Source: postman SYSTEM → Shipment → /v1/shipments/{shipment_id}/cancel; yaml API_SYSTEM POST

### `POST /v1/addresses/validate`
Validate (and normalize) a postal address.

- Path params: none
- Query params: none
- Body:
  ```json
  {
    "address": {
      "address_1": "{STREET}",
      "address_2": "{STREET_2}",
      "city": "{CITY}",
      "state": "{STATE}",
      "postcode": "{POSTCODE}",
      "country": "{COUNTRY_CODE}",
      "company_name": "{COMPANY}"
    },
    "account_id": "{ACCOUNT_ID}",
    "reference": {
      "type": "order",
      "id": "{ORDER_ID}"
    }
  }
  ```
  Required: `address` (with at least `country`).
- Source: postman SYSTEM → Address → /v1/addresses/validate; yaml API_SYSTEM POST

### `POST /v1/quotes`
Get a quote against a quotable document. Body identical to PLATFORM `POST /v1/quotes` (see above).
- Source: postman SYSTEM → Quote → /v1/quotes; yaml API_SYSTEM POST

### `POST /v1/shipments/quote`
Quote an in-flight shipment payload. Body identical to PLATFORM `POST /v1/shipments/quote` (see above).
- Source: yaml API_SYSTEM `/v1/shipments/quote` POST (yaml-only — postman SYSTEM lists this entry but with no body)

### `GET /v1/carriers`
List carriers (system view).

- Path params: none
- Query params: same as SELLER `GET /v1/carriers` (`codes`, `includes`, `cursor`, `take`, `q`)
- Body: none
- Source: postman SYSTEM → Carrier → /v1/carriers; yaml API_SYSTEM GET

### `GET /v1/carrier_services`
List carrier services (system view).

- Path params: none
- Query params: same as SELLER `GET /v1/carrier_services` (`codes`, `cursor`, `take`, `q`)
- Body: none
- Source: postman SYSTEM → CarrierService → /v1/carrier_services; yaml API_SYSTEM GET

### `GET /v1/shipping_methods`
List shipping methods (system view).

- Path params: none
- Query params: same as PLATFORM `GET /v1/shipping_methods` (`account_id`, `location_id`, `carrier_service_id`, `warehouse_shipping_method_id`, `carrier_account_id`, `type`, `status`, `cursor`, `take`, `q`)
- Body: none
- Source: postman SYSTEM → ShippingMethod → /v1/shipping_methods; yaml API_SYSTEM GET

### `GET /v1/shipping_methods/{shipping_method_id}`
Get a single shipping method (system view).

- Path params: `shipping_method_id` (string, required)
- Query params: none
- Body: none
- Source: postman SYSTEM → ShippingMethod → /v1/shipping_methods/{shipping_method_id}; yaml API_SYSTEM GET

---

## WAREHOUSE context

### `POST /v1/shipments/{shipment_id}/label`
Generate a shipping label (and any required customs documents) for a shipment.

- Path params: `shipment_id` (string, required)
- Query params: none
- Body:
  ```json
  {
    "paper_size": "4x8",
    "from_address": {
      "contact_name": "{NAME}",
      "address_1": "{STREET}",
      "address_2": "{STREET_2}",
      "city": "{CITY}",
      "state": "{STATE}",
      "postcode": "{POSTCODE}",
      "country": "{COUNTRY_CODE}"
    },
    "to_address": {
      "contact_name": "{NAME}",
      "contact_number": "{PHONE}",
      "address_1": "{STREET}",
      "city": "{CITY}",
      "state": "{STATE}",
      "postcode": "{POSTCODE}",
      "country": "{COUNTRY_CODE}"
    },
    "packages": [
      {
        "name": "{PACKAGE_NAME}",
        "width": 100,
        "height": 150,
        "length": 120,
        "dimension_unit": "cm",
        "weight": 1.56,
        "weight_unit": "kg",
        "box_type": "custom",
        "items": [
          {
            "description": "{DESC}",
            "quantity": 10,
            "sku_id": "{SKU_ID}",
            "sku_name": "{SKU}",
            "price": 99.50,
            "currency": "AUD",
            "country_of_origin": "AUS",
            "hs_code": "{HS_CODE}",
            "weight": 0.156,
            "weight_unit": "kg"
          }
        ]
      }
    ],
    "purpose": "merchandise"
  }
  ```
  Required: `from_address`, `to_address`, `packages` (each package requires `items` with `description`, `quantity`, `price`).
- Source: postman WAREHOUSE → Shipment → /v1/shipments/{shipment_id}/label; yaml API_WAREHOUSE POST

### `GET /v1/carrier_accounts`
List carrier accounts (warehouse view).

- Path params: none
- Query params: same as PLATFORM `GET /v1/carrier_accounts` (`carrier_ids`, `account_id`, `cursor`, `take`)
- Body: none
- Source: yaml API_WAREHOUSE `/v1/carrier_accounts` GET (yaml-only — not in postman)

### `GET /v1/carriers`
List carriers (warehouse view).

- Path params: none
- Query params: same as SELLER `GET /v1/carriers` (`codes`, `includes`, `cursor`, `take`, `q`)
- Body: none
- Source: yaml API_WAREHOUSE `/v1/carriers` GET (yaml-only — not in postman)

### `GET /v1/carrier_services`
List carrier services (warehouse view).

- Path params: none
- Query params: same as SELLER `GET /v1/carrier_services` (`codes`, `cursor`, `take`, `q`)
- Body: none
- Source: yaml API_WAREHOUSE `/v1/carrier_services` GET (yaml-only — not in postman)

### `GET /v1/shipping_methods`
List shipping methods (warehouse view).

- Path params: none
- Query params: same as PLATFORM `GET /v1/shipping_methods`
- Body: none
- Source: yaml API_WAREHOUSE `/v1/shipping_methods` GET (yaml-only — not in postman)

---

## UNCATEGORIZED

### `GET /v1/info`
Service health/build-info probe. No `Authorization` required.

- Path params: none
- Query params: none
- Body: none
- Returns `{ healthy, git_commit_hash, git_branch_name, build_number }`.
- Source: serverless.yml → infoHttp.handler; src/modules/shipping/infra/aws/handlers/infoHttp.ts (no auth context — public health check; not in postman or any API_*.yaml)
