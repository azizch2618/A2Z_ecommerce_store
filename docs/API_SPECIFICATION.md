# A2Z Tools — API Specification

**Django REST Framework · PostgreSQL · Version 1.0**

| Attribute | Value |
|-----------|-------|
| **Base URL** | `https://api.a2ztools.com.au/api/v1` |
| **Format** | JSON (`Content-Type: application/json`) |
| **Authentication** | JWT Bearer tokens |
| **Currency** | AUD (amounts in integer cents) |
| **Tax** | GST 10% |
| **Locale** | en-AU |
| **Document Version** | 1.0 |

---

## Table of Contents

1. [Global Conventions](#1-global-conventions)
2. [Authentication](#2-authentication)
3. [Products](#3-products)
4. [Categories](#4-categories)
5. [Brands](#5-brands)
6. [Inventory](#6-inventory)
7. [Cart](#7-cart)
8. [Wishlist](#8-wishlist)
9. [Orders](#9-orders)
10. [Payments](#10-payments)
11. [Shipping](#11-shipping)
12. [Reviews](#12-reviews)
13. [Analytics](#13-analytics)
14. [Appendix](#14-appendix)

---

## 1. Global Conventions

### 1.1 Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Conditional | `Bearer <access_token>` — required on protected endpoints |
| `Content-Type` | On writes | `application/json` |
| `Accept` | Recommended | `application/json` |
| `X-Session-Key` | Guest cart | UUID session key for anonymous cart operations |
| `X-Request-Id` | Optional | Client-generated UUID for tracing |
| `Accept-Language` | Optional | Default `en-AU` |

### 1.2 Identifiers

| Type | Format | Usage |
|------|--------|-------|
| Public ID | UUID v4 | All API path parameters and response references |
| Order number | String | Human-readable e.g. `A2Z-20250617-0042` |
| SKU | String | Product variant stock-keeping unit |

Internal integer primary keys are **never** exposed in public API responses.

### 1.3 Monetary Values

All amounts are **integer cents** in AUD unless noted.

| Field Pattern | Example | Meaning |
|---------------|---------|---------|
| `amount_cents` | `34900` | $349.00 |
| `gst_rate` | `0.1000` | 10% GST |
| `gst_cents` | `3490` | GST component |
| `amount_ex_gst_cents` | `34900` | Excluding GST |
| `amount_inc_gst_cents` | `38390` | Including GST |
| `currency_code` | `AUD` | Always AUD in Phase 1 |

### 1.4 Pagination

Cursor-based pagination on all list endpoints.

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cursor` | string | null | Opaque cursor from previous response |
| `limit` | integer | 20 | Page size (max 100) |

**Paginated response envelope:**

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Result items |
| `pagination.next_cursor` | string \| null | Cursor for next page |
| `pagination.has_more` | boolean | More results available |
| `pagination.limit` | integer | Applied page size |

### 1.5 Error Response

| Field | Type | Description |
|-------|------|-------------|
| `error.code` | string | Machine-readable code e.g. `VALIDATION_ERROR` |
| `error.message` | string | Human-readable summary |
| `error.details` | object \| array | Field-level errors or context |

**HTTP status codes:**

| Code | Usage |
|------|-------|
| 200 | Success (GET, PATCH) |
| 201 | Created (POST) |
| 204 | No content (DELETE) |
| 400 | Validation error |
| 401 | Unauthenticated |
| 403 | Forbidden / insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict (e.g. insufficient stock) |
| 422 | Business rule violation |
| 429 | Rate limit exceeded |
| 500 | Server error |

### 1.6 Common Object Schemas

#### Address

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `line1` | string | yes | Street address |
| `line2` | string | no | Unit, suite, level |
| `suburb` | string | yes | |
| `state` | string | yes | NSW, VIC, QLD, SA, WA, TAS, NT, ACT |
| `postcode` | string | yes | 4-digit AU postcode |
| `country` | string | no | Default `AU` |

#### Price Block

| Field | Type | Description |
|-------|------|-------------|
| `amount_ex_gst_cents` | integer | Unit price ex GST |
| `gst_cents` | integer | GST per unit |
| `amount_inc_gst_cents` | integer | Unit price inc GST |
| `gst_rate` | decimal | e.g. `0.1000` |
| `currency_code` | string | `AUD` |
| `compare_at_cents` | integer \| null | RRP / was price |
| `is_trade_price` | boolean | Trade pricing applied |

#### Stock Status

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `in_stock`, `low_stock`, `backorder`, `out_of_stock` |
| `quantity_available` | integer | Sellable quantity |
| `lead_time_days` | integer \| null | For backorder items |

#### Timestamps

All resources include:

| Field | Type | Description |
|-------|------|-------------|
| `created_at` | ISO 8601 datetime | UTC |
| `updated_at` | ISO 8601 datetime | UTC |

---

## 2. Authentication

### 2.1 Register

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/register/` |
| **Method** | `POST` |
| **Purpose** | Create a new customer account with email and password |
| **Authentication** | No |

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | yes | Valid email address |
| `password` | string | yes | Min 8 chars, complexity rules enforced |
| `password_confirm` | string | yes | Must match password |
| `first_name` | string | yes | |
| `last_name` | string | yes | |
| `phone` | string | no | Australian mobile format |
| `customer_type` | string | no | `retail` (default), `trade`, `contractor`, `business` |
| `marketing_opt_in` | boolean | no | Default `false` |

**Response `201 Created`:**

| Field | Type | Description |
|-------|------|-------------|
| `user.id` | uuid | Public user ID |
| `user.email` | string | |
| `user.first_name` | string | |
| `user.last_name` | string | |
| `user.email_verified` | boolean | Always `false` on register |
| `customer.id` | uuid | Customer profile ID |
| `customer.customer_type` | string | |
| `tokens.access` | string | JWT access token (15 min) |
| `tokens.refresh` | string | JWT refresh token (7 days) |
| `message` | string | Verification email sent notice |

---

### 2.2 Login

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/login/` |
| **Method** | `POST` |
| **Purpose** | Authenticate user and issue JWT tokens |
| **Authentication** | No |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `email` | string | yes |
| `password` | string | yes |

**Response `200 OK`:**

| Field | Type | Description |
|-------|------|-------------|
| `user.id` | uuid | |
| `user.email` | string | |
| `user.first_name` | string | |
| `user.last_name` | string | |
| `user.email_verified` | boolean | |
| `customer.id` | uuid | |
| `customer.customer_type` | string | |
| `customer.trade_account_status` | string \| null | `pending`, `approved`, `suspended`, `rejected` |
| `tokens.access` | string | JWT access token |
| `tokens.refresh` | string | JWT refresh token |

---

### 2.3 Refresh Token

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/refresh/` |
| **Method** | `POST` |
| **Purpose** | Exchange refresh token for new access token |
| **Authentication** | No (refresh token in body) |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `refresh` | string | yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `access` | string |
| `refresh` | string |

---

### 2.4 Logout

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/logout/` |
| **Method** | `POST` |
| **Purpose** | Revoke refresh token and invalidate session |
| **Authentication** | Yes |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `refresh` | string | yes |

**Response `204 No Content`**

---

### 2.5 Verify Email

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/verify-email/` |
| **Method** | `POST` |
| **Purpose** | Confirm email address via verification token |
| **Authentication** | No |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `token` | string | yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `message` | string |
| `email_verified` | boolean |

---

### 2.6 Resend Verification Email

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/resend-verification/` |
| **Method** | `POST` |
| **Purpose** | Resend email verification link |
| **Authentication** | Yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `message` | string |

---

### 2.7 Forgot Password

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/forgot-password/` |
| **Method** | `POST` |
| **Purpose** | Initiate password reset flow |
| **Authentication** | No |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `email` | string | yes |

**Response `200 OK`:** (always returns success to prevent email enumeration)

| Field | Type |
|-------|------|
| `message` | string |

---

### 2.8 Reset Password

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/reset-password/` |
| **Method** | `POST` |
| **Purpose** | Set new password using reset token |
| **Authentication** | No |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `token` | string | yes |
| `password` | string | yes |
| `password_confirm` | string | yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `message` | string |

---

### 2.9 Get Current User

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/me/` |
| **Method** | `GET` |
| **Purpose** | Retrieve authenticated user profile and customer details |
| **Authentication** | Yes |

**Response `200 OK`:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | uuid | User ID |
| `email` | string | |
| `first_name` | string | |
| `last_name` | string | |
| `phone` | string \| null | |
| `avatar_url` | string \| null | |
| `email_verified` | boolean | |
| `customer.id` | uuid | |
| `customer.customer_type` | string | |
| `customer.trade_account_status` | string \| null | |
| `customer.credit_limit_cents` | integer | |
| `customer.payment_terms_days` | integer \| null | |
| `organization` | object \| null | Embedded if B2B (see below) |
| `roles` | array[string] | Assigned role slugs |
| `created_at` | datetime | |
| `updated_at` | datetime | |

**Organization embed (if present):**

| Field | Type |
|-------|------|
| `id` | uuid |
| `legal_name` | string |
| `trading_name` | string \| null |
| `abn` | string \| null |
| `abn_verified` | boolean |

---

### 2.10 Update Profile

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/me/` |
| **Method** | `PATCH` |
| **Purpose** | Update user profile fields |
| **Authentication** | Yes |

**Request body (partial):**

| Field | Type |
|-------|------|
| `first_name` | string |
| `last_name` | string |
| `phone` | string |
| `preferences` | object |

**Response `200 OK`:** Same structure as Get Current User.

---

### 2.11 Change Password

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/change-password/` |
| **Method** | `POST` |
| **Purpose** | Change password for authenticated user |
| **Authentication** | Yes |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `current_password` | string | yes |
| `new_password` | string | yes |
| `new_password_confirm` | string | yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `message` | string |

---

### 2.12 List Addresses

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/addresses/` |
| **Method** | `GET` |
| **Purpose** | List saved customer addresses |
| **Authentication** | Yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `data` | array of Address objects |

**Address object:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `label` | string \| null |
| `line1` | string |
| `line2` | string \| null |
| `suburb` | string |
| `state` | string |
| `postcode` | string |
| `country` | string |
| `is_default_billing` | boolean |
| `is_default_shipping` | boolean |

---

### 2.13 Create Address

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/addresses/` |
| **Method** | `POST` |
| **Purpose** | Add a new saved address |
| **Authentication** | Yes |

**Request body:** Address fields + `label`, `is_default_billing`, `is_default_shipping`

**Response `201 Created`:** Address object.

---

### 2.14 Update Address

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/addresses/{address_id}/` |
| **Method** | `PATCH` |
| **Purpose** | Update an existing address |
| **Authentication** | Yes |

**Response `200 OK`:** Address object.

---

### 2.15 Delete Address

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/addresses/{address_id}/` |
| **Method** | `DELETE` |
| **Purpose** | Remove a saved address |
| **Authentication** | Yes |

**Response `204 No Content`**

---

### 2.16 Apply for Trade Account

| Property | Value |
|----------|-------|
| **Endpoint** | `/auth/trade-account/apply/` |
| **Method** | `POST` |
| **Purpose** | Submit trade account application with business details |
| **Authentication** | Yes |

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `legal_name` | string | yes | Registered business name |
| `trading_name` | string | no | |
| `abn` | string | yes | 11-digit ABN |
| `acn` | string | no | |
| `business_email` | string | yes | |
| `business_phone` | string | yes | |
| `business_address` | Address | yes | |
| `customer_segment` | string | yes | `trade`, `contractor`, `business` |
| `estimated_monthly_spend` | string | no | Range selection |
| `notes` | string | no | Application notes |

**Response `201 Created`:**

| Field | Type |
|-------|------|
| `organization.id` | uuid |
| `trade_account_status` | string |
| `message` | string |

---

## 3. Products

### 3.1 List Products

| Property | Value |
|----------|-------|
| **Endpoint** | `/products/` |
| **Method** | `GET` |
| **Purpose** | List and filter products with pagination |
| **Authentication** | No (trade pricing if authenticated) |

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cursor` | string | Pagination cursor |
| `limit` | integer | Page size (default 20, max 100) |
| `category` | uuid | Filter by category public ID |
| `brand` | uuid | Filter by brand public ID |
| `search` | string | Full-text search query |
| `min_price` | integer | Min price in cents (ex GST) |
| `max_price` | integer | Max price in cents (ex GST) |
| `in_stock` | boolean | Only in-stock products |
| `sort` | string | `relevance`, `price_asc`, `price_desc`, `newest`, `name` |

**Response `200 OK`:**

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | Product summary objects |
| `pagination` | object | Cursor pagination envelope |
| `facets` | object | Filter counts (brand, category, price ranges) |

**Product summary object:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `name` | string |
| `slug` | string |
| `short_description` | string \| null |
| `brand` | object `{ id, name, slug }` |
| `primary_image` | object `{ url, alt_text }` \| null |
| `default_variant` | object `{ id, sku, price, stock }` |
| `price` | Price Block |
| `stock` | Stock Status |
| `badges` | array[string] |
| `average_rating` | decimal \| null |
| `review_count` | integer |

---

### 3.2 Get Product by Slug

| Property | Value |
|----------|-------|
| **Endpoint** | `/products/{slug}/` |
| **Method** | `GET` |
| **Purpose** | Retrieve full product detail for PDP |
| **Authentication** | No (trade pricing if authenticated) |

**Response `200 OK`:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | uuid | |
| `name` | string | |
| `slug` | string | |
| `description` | string | HTML content |
| `short_description` | string \| null | |
| `product_type` | string | `simple`, `variable`, `bundle` |
| `visibility` | string | |
| `brand` | object | `{ id, name, slug, logo_url }` |
| `categories` | array | `{ id, name, slug, is_primary }` |
| `images` | array | `{ id, url, alt_text, sort_order, is_primary }` |
| `documents` | array | `{ id, title, document_type, url }` |
| `variants` | array | Variant detail objects |
| `attributes` | array | Grouped specification attributes |
| `related_products` | array | Product summary objects |
| `meta_title` | string \| null | |
| `meta_description` | string \| null | |
| `average_rating` | decimal | |
| `review_count` | integer | |

**Variant detail object:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `sku` | string |
| `barcode` | string \| null |
| `name` | string \| null |
| `price` | Price Block |
| `stock` | Stock Status |
| `weight_grams` | integer \| null |
| `dimensions` | object `{ length_mm, width_mm, height_mm }` |
| `attributes` | array `{ name, value, unit }` |
| `is_default` | boolean |

---

### 3.3 Get Product by ID

| Property | Value |
|----------|-------|
| **Endpoint** | `/products/id/{product_id}/` |
| **Method** | `GET` |
| **Purpose** | Retrieve product by UUID |
| **Authentication** | No |

**Response `200 OK`:** Same as §3.2.

---

### 3.4 Get Variant

| Property | Value |
|----------|-------|
| **Endpoint** | `/products/variants/{variant_id}/` |
| **Method** | `GET` |
| **Purpose** | Single variant with live price and stock |
| **Authentication** | No |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `product_id` | uuid |
| `product_name` | string |
| `product_slug` | string |
| `sku` | string |
| `price` | Price Block |
| `stock` | Stock Status |
| `primary_image` | object \| null |
| `is_active` | boolean |

---

### 3.5 Search Products (Autocomplete)

| Property | Value |
|----------|-------|
| **Endpoint** | `/products/search/` |
| **Method** | `GET` |
| **Purpose** | Typeahead search for header/search overlay |
| **Authentication** | No |

**Query parameters:** `q` (required, min 2 chars), `limit` (default 5, max 10)

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `query` | string |
| `products` | array `{ id, name, slug, sku, image_url, price }` |
| `categories` | array `{ id, name, slug }` |
| `brands` | array `{ id, name, slug }` |

---

### 3.6 Compare Products

| Property | Value |
|----------|-------|
| **Endpoint** | `/products/compare/` |
| **Method** | `POST` |
| **Purpose** | Side-by-side comparison for up to 4 products |
| **Authentication** | No |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `product_ids` | array[uuid] | yes (2–4 items) |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `products` | array |
| `comparison_attributes` | array |

---

## 4. Categories

### 4.1 List Categories

| Property | Value |
|----------|-------|
| **Endpoint** | `/categories/` |
| **Method** | `GET` |
| **Purpose** | Category tree for navigation |
| **Authentication** | No |

**Query parameters:** `parent` (uuid), `depth` (integer), `flat` (boolean)

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `data` | array of category nodes |

**Category node:** `id`, `name`, `slug`, `description`, `image_url`, `sort_order`, `product_count`, `children[]`, `meta_title`, `meta_description`

---

### 4.2 Get Category by Slug

| Property | Value |
|----------|-------|
| **Endpoint** | `/categories/{slug}/` |
| **Method** | `GET` |
| **Purpose** | Category landing page with breadcrumbs |
| **Authentication** | No |

**Response `200 OK`:** Category node + `breadcrumbs[]`, `featured_products[]`

---

### 4.3 List Category Products

| Property | Value |
|----------|-------|
| **Endpoint** | `/categories/{slug}/products/` |
| **Method** | `GET` |
| **Purpose** | Products within category and subcategories |
| **Authentication** | No |

**Query parameters:** Same as §3.1. **Response:** Paginated product list with facets.

---

## 5. Brands

### 5.1 List Brands

| Property | Value |
|----------|-------|
| **Endpoint** | `/brands/` |
| **Method** | `GET` |
| **Purpose** | List active brands |
| **Authentication** | No |

**Query parameters:** `cursor`, `limit`, `search`, `featured`

**Response `200 OK`:** Paginated `{ id, name, slug, logo_url, product_count }`

---

### 5.2 Get Brand by Slug

| Property | Value |
|----------|-------|
| **Endpoint** | `/brands/{slug}/` |
| **Method** | `GET` |
| **Purpose** | Brand landing page data |
| **Authentication** | No |

**Response `200 OK`:** Brand detail + `featured_products[]`, SEO metadata

---

### 5.3 List Brand Products

| Property | Value |
|----------|-------|
| **Endpoint** | `/brands/{slug}/products/` |
| **Method** | `GET` |
| **Purpose** | Products for a brand |
| **Authentication** | No |

**Response `200 OK`:** Paginated product list.

---

## 6. Inventory

### 6.1 Get Variant Stock

| Property | Value |
|----------|-------|
| **Endpoint** | `/inventory/variants/{variant_id}/` |
| **Method** | `GET` |
| **Purpose** | Public stock availability for a variant |
| **Authentication** | No |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `variant_id` | uuid |
| `sku` | string |
| `stock` | Stock Status |
| `warehouses` | array `{ code, name, quantity_available, allows_pickup }` |

---

### 6.2 Bulk Stock Check

| Property | Value |
|----------|-------|
| **Endpoint** | `/inventory/check/` |
| **Method** | `POST` |
| **Purpose** | Validate stock for multiple variants (cart/checkout) |
| **Authentication** | No |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `items` | array | yes |
| `items[].variant_id` | uuid | yes |
| `items[].quantity` | integer | yes |
| `postcode` | string | no |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `items` | array `{ variant_id, requested_quantity, available_quantity, stock, can_fulfill }` |
| `all_available` | boolean |

---

### 6.3 Back-in-Stock Alert

| Property | Value |
|----------|-------|
| **Endpoint** | `/inventory/back-in-stock/` |
| **Method** | `POST` |
| **Purpose** | Register email alert when variant restocked |
| **Authentication** | No |

**Request body:** `variant_id` (uuid), `email` (string, required if guest)

**Response `201 Created`:** `{ id, variant_id, message }`

---

### 6.4 List Warehouses

| Property | Value |
|----------|-------|
| **Endpoint** | `/inventory/warehouses/` |
| **Method** | `GET` |
| **Purpose** | Pickup locations for click & collect |
| **Authentication** | No |

**Response `200 OK`:** `{ data: [{ id, code, name, suburb, state, allows_pickup, opening_hours }] }`

---

### 6.5 Admin: List Inventory Levels

| Property | Value |
|----------|-------|
| **Endpoint** | `/inventory/admin/levels/` |
| **Method** | `GET` |
| **Purpose** | Staff stock levels across warehouses |
| **Authentication** | Yes (`inventory.view`) |

**Query parameters:** `warehouse`, `variant_id`, `sku`, `low_stock`, `cursor`, `limit`

**Response `200 OK`:** Paginated inventory records.

---

### 6.6 Admin: Adjust Stock

| Property | Value |
|----------|-------|
| **Endpoint** | `/inventory/admin/adjustments/` |
| **Method** | `POST` |
| **Purpose** | Manual stock adjustment with ledger entry |
| **Authentication** | Yes (`inventory.adjust`) |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `warehouse_id` | uuid | yes |
| `variant_id` | uuid | yes |
| `quantity_change` | integer | yes |
| `transaction_type` | string | yes |
| `notes` | string | no |

**Response `201 Created`:** `{ transaction_id, quantity_before, quantity_after, created_at }`

---

## 7. Cart

### 7.1 Get Cart

| Property | Value |
|----------|-------|
| **Endpoint** | `/cart/` |
| **Method** | `GET` |
| **Purpose** | Retrieve current cart (authenticated or guest session) |
| **Authentication** | Optional (guest via `X-Session-Key` header) |

**Response `200 OK`:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | uuid | Cart ID |
| `items` | array | Cart line items |
| `items[].id` | uuid | Line item ID |
| `items[].variant_id` | uuid | |
| `items[].sku` | string | |
| `items[].product_name` | string | |
| `items[].variant_name` | string \| null | |
| `items[].image_url` | string \| null | |
| `items[].quantity` | integer | |
| `items[].price` | Price Block | Per-unit pricing |
| `items[].line_total` | object | `{ amount_ex_gst_cents, gst_cents, amount_inc_gst_cents }` |
| `items[].stock` | Stock Status | |
| `item_count` | integer | Total line items |
| `totals.subtotal_ex_gst_cents` | integer | |
| `totals.gst_cents` | integer | |
| `totals.discount_cents` | integer | |
| `totals.total_inc_gst_cents` | integer | |
| `totals.currency_code` | string | `AUD` |
| `coupon` | object \| null | Applied coupon summary |
| `updated_at` | datetime | |

---

### 7.2 Add Item to Cart

| Property | Value |
|----------|-------|
| **Endpoint** | `/cart/items/` |
| **Method** | `POST` |
| **Purpose** | Add variant to cart or increment quantity |
| **Authentication** | Optional |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `variant_id` | uuid | yes |
| `quantity` | integer | yes (min 1) |

**Response `201 Created`:** Full cart object (§7.1).

**Errors:** `409` insufficient stock, `404` variant not found.

---

### 7.3 Update Cart Item

| Property | Value |
|----------|-------|
| **Endpoint** | `/cart/items/{item_id}/` |
| **Method** | `PATCH` |
| **Purpose** | Update quantity for a cart line item |
| **Authentication** | Optional |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `quantity` | integer | yes |

**Response `200 OK`:** Full cart object.

---

### 7.4 Remove Cart Item

| Property | Value |
|----------|-------|
| **Endpoint** | `/cart/items/{item_id}/` |
| **Method** | `DELETE` |
| **Purpose** | Remove line item from cart |
| **Authentication** | Optional |

**Response `200 OK`:** Full cart object.

---

### 7.5 Clear Cart

| Property | Value |
|----------|-------|
| **Endpoint** | `/cart/clear/` |
| **Method** | `POST` |
| **Purpose** | Remove all items from cart |
| **Authentication** | Optional |

**Response `200 OK`:** Empty cart object.

---

### 7.6 Apply Coupon

| Property | Value |
|----------|-------|
| **Endpoint** | `/cart/coupon/` |
| **Method** | `POST` |
| **Purpose** | Apply discount coupon code to cart |
| **Authentication** | Optional |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `code` | string | yes |

**Response `200 OK`:** Full cart object with `coupon` populated.

**Errors:** `422` invalid/expired coupon, minimum not met.

---

### 7.7 Remove Coupon

| Property | Value |
|----------|-------|
| **Endpoint** | `/cart/coupon/` |
| **Method** | `DELETE` |
| **Purpose** | Remove applied coupon from cart |
| **Authentication** | Optional |

**Response `200 OK`:** Full cart object.

---

### 7.8 Merge Guest Cart

| Property | Value |
|----------|-------|
| **Endpoint** | `/cart/merge/` |
| **Method** | `POST` |
| **Purpose** | Merge guest session cart into authenticated user cart on login |
| **Authentication** | Yes |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `session_key` | string | yes |

**Response `200 OK`:** Merged cart object.

---

## 8. Wishlist

### 8.1 List Wishlists

| Property | Value |
|----------|-------|
| **Endpoint** | `/wishlists/` |
| **Method** | `GET` |
| **Purpose** | List all wishlists for authenticated customer |
| **Authentication** | Yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `data` | array |
| `data[].id` | uuid |
| `data[].name` | string |
| `data[].is_default` | boolean |
| `data[].item_count` | integer |
| `data[].created_at` | datetime |

---

### 8.2 Get Wishlist

| Property | Value |
|----------|-------|
| **Endpoint** | `/wishlists/{wishlist_id}/` |
| **Method** | `GET` |
| **Purpose** | Retrieve wishlist with all items |
| **Authentication** | Yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `name` | string |
| `is_default` | boolean |
| `items` | array |
| `items[].id` | uuid |
| `items[].variant_id` | uuid |
| `items[].product_name` | string |
| `items[].sku` | string |
| `items[].image_url` | string \| null |
| `items[].price` | Price Block |
| `items[].stock` | Stock Status |
| `items[].desired_quantity` | integer |
| `items[].added_at` | datetime |

---

### 8.3 Create Wishlist

| Property | Value |
|----------|-------|
| **Endpoint** | `/wishlists/` |
| **Method** | `POST` |
| **Purpose** | Create a new named wishlist |
| **Authentication** | Yes |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `name` | string | yes |

**Response `201 Created`:** Wishlist summary object.

---

### 8.4 Add Item to Wishlist

| Property | Value |
|----------|-------|
| **Endpoint** | `/wishlists/{wishlist_id}/items/` |
| **Method** | `POST` |
| **Purpose** | Add variant to wishlist |
| **Authentication** | Yes |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `variant_id` | uuid | yes |
| `desired_quantity` | integer | no (default 1) |
| `notes` | string | no |

**Response `201 Created`:** Wishlist with items (§8.2).

---

### 8.5 Remove Wishlist Item

| Property | Value |
|----------|-------|
| **Endpoint** | `/wishlists/{wishlist_id}/items/{item_id}/` |
| **Method** | `DELETE` |
| **Purpose** | Remove item from wishlist |
| **Authentication** | Yes |

**Response `200 OK`:** Updated wishlist.

---

### 8.6 Move Wishlist Item to Cart

| Property | Value |
|----------|-------|
| **Endpoint** | `/wishlists/{wishlist_id}/items/{item_id}/move-to-cart/` |
| **Method** | `POST` |
| **Purpose** | Add wishlist item to cart (optionally remove from wishlist) |
| **Authentication** | Yes |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `quantity` | integer | no |
| `remove_from_wishlist` | boolean | no (default true) |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `cart` | Cart object (§7.1) |
| `wishlist` | Wishlist object (§8.2) |

---

### 8.7 Delete Wishlist

| Property | Value |
|----------|-------|
| **Endpoint** | `/wishlists/{wishlist_id}/` |
| **Method** | `DELETE` |
| **Purpose** | Delete a non-default wishlist |
| **Authentication** | Yes |

**Response `204 No Content`**

---

## 9. Orders

### 9.1 Create Order (Checkout)

| Property | Value |
|----------|-------|
| **Endpoint** | `/orders/` |
| **Method** | `POST` |
| **Purpose** | Place order from cart — creates pending order for payment |
| **Authentication** | Optional (guest checkout supported) |

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cart_id` | uuid | yes | Source cart |
| `email` | string | guest only | Guest contact email |
| `billing_address` | Address | yes | |
| `shipping_address` | Address | no | Defaults to billing |
| `shipping_method_id` | uuid | yes | Selected delivery method |
| `warehouse_id` | uuid | no | For click & collect |
| `payment_method` | string | yes | `card`, `paypal`, `bank_transfer`, `trade_credit` |
| `po_number` | string | no | B2B purchase order reference |
| `customer_notes` | string | no | Delivery instructions |
| `guest_checkout` | boolean | no | Default false |

**Response `201 Created`:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `order_number` | string |
| `status` | string |
| `payment_status` | string |
| `items` | array of order line items |
| `totals` | Order totals object |
| `billing_address` | Address |
| `shipping_address` | Address |
| `shipping_method` | object |
| `payment` | object `{ id, status, client_secret }` for Stripe |
| `placed_at` | datetime |

**Order totals object:**

| Field | Type |
|-------|------|
| `subtotal_ex_gst_cents` | integer |
| `gst_total_cents` | integer |
| `shipping_ex_gst_cents` | integer |
| `shipping_gst_cents` | integer |
| `discount_cents` | integer |
| `total_inc_gst_cents` | integer |
| `currency_code` | string |

**Order line item:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `sku` | string |
| `product_name` | string |
| `variant_name` | string \| null |
| `quantity` | integer |
| `unit_price_ex_gst_cents` | integer |
| `unit_gst_cents` | integer |
| `gst_rate` | decimal |
| `line_total_inc_gst_cents` | integer |

---

### 9.2 List Orders

| Property | Value |
|----------|-------|
| **Endpoint** | `/orders/` |
| **Method** | `GET` |
| **Purpose** | List orders for authenticated customer |
| **Authentication** | Yes |

**Query parameters:** `cursor`, `limit`, `status`, `from_date`, `to_date`

**Response `200 OK`:** Paginated order summary objects.

**Order summary:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `order_number` | string |
| `status` | string |
| `payment_status` | string |
| `fulfilment_status` | string |
| `item_count` | integer |
| `total_inc_gst_cents` | integer |
| `currency_code` | string |
| `placed_at` | datetime |

---

### 9.3 Get Order

| Property | Value |
|----------|-------|
| **Endpoint** | `/orders/{order_id}/` |
| **Method** | `GET` |
| **Purpose** | Full order detail with items, shipping, and payment status |
| **Authentication** | Yes (owner) or guest with `order_number` + `email` query |

**Query parameters (guest):** `email` (string)

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `order_number` | string |
| `status` | string |
| `payment_status` | string |
| `fulfilment_status` | string |
| `items` | array |
| `totals` | Order totals object |
| `billing_address` | Address |
| `shipping_address` | Address |
| `shipping_method` | object |
| `shipments` | array | Shipment summary objects |
| `payment` | object |
| `coupon` | object \| null |
| `po_number` | string \| null |
| `tax_invoice` | object \| null | `{ id, invoice_number, pdf_url, status }` |
| `status_history` | array `{ from_status, to_status, comment, created_at }` |
| `placed_at` | datetime |
| `created_at` | datetime |

---

### 9.4 Cancel Order

| Property | Value |
|----------|-------|
| **Endpoint** | `/orders/{order_id}/cancel/` |
| **Method** | `POST` |
| **Purpose** | Cancel order before shipment |
| **Authentication** | Yes |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `reason` | string | no |

**Response `200 OK`:** Updated order object.

**Errors:** `422` if already shipped.

---

### 9.5 Reorder

| Property | Value |
|----------|-------|
| **Endpoint** | `/orders/{order_id}/reorder/` |
| **Method** | `POST` |
| **Purpose** | Add all order items to current cart |
| **Authentication** | Yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `cart` | Cart object (§7.1) |
| `unavailable_items` | array | Items that could not be added |

---

### 9.6 Get Tax Invoice

| Property | Value |
|----------|-------|
| **Endpoint** | `/orders/{order_id}/invoice/` |
| **Method** | `GET` |
| **Purpose** | Retrieve GST tax invoice for order |
| **Authentication** | Yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `invoice_number` | string |
| `order_id` | uuid |
| `order_number` | string |
| `seller_abn` | string |
| `seller_name` | string |
| `seller_address` | Address |
| `buyer_abn` | string \| null |
| `buyer_name` | string |
| `buyer_address` | Address |
| `lines` | array |
| `lines[].line_number` | integer |
| `lines[].description` | string |
| `lines[].quantity` | integer |
| `lines[].unit_price_ex_gst_cents` | integer |
| `lines[].gst_rate` | decimal |
| `lines[].gst_amount_cents` | integer |
| `lines[].line_total_inc_gst_cents` | integer |
| `subtotal_ex_gst_cents` | integer |
| `gst_total_cents` | integer |
| `total_inc_gst_cents` | integer |
| `currency_code` | string |
| `invoice_date` | date |
| `due_date` | date \| null |
| `status` | string |
| `pdf_url` | string \| null |

---

### 9.7 Track Order (Guest)

| Property | Value |
|----------|-------|
| **Endpoint** | `/orders/track/` |
| **Method** | `POST` |
| **Purpose** | Look up order status without account |
| **Authentication** | No |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `order_number` | string | yes |
| `email` | string | yes |

**Response `200 OK`:** Order summary + `shipments[]` with tracking.

---

## 10. Payments

### 10.1 Create Payment Intent

| Property | Value |
|----------|-------|
| **Endpoint** | `/payments/intent/` |
| **Method** | `POST` |
| **Purpose** | Create Stripe PaymentIntent for order checkout |
| **Authentication** | Optional |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `order_id` | uuid | yes |

**Response `201 Created`:**

| Field | Type |
|-------|------|
| `payment_id` | uuid |
| `order_id` | uuid |
| `amount_cents` | integer |
| `currency_code` | string |
| `status` | string |
| `client_secret` | string |
| `gateway` | string |

---

### 10.2 Confirm Payment

| Property | Value |
|----------|-------|
| **Endpoint** | `/payments/{payment_id}/confirm/` |
| **Method** | `POST` |
| **Purpose** | Confirm payment completion after Stripe client-side flow |
| **Authentication** | Optional |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `payment_intent_id` | string | yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `payment_id` | uuid |
| `status` | string |
| `order_id` | uuid |
| `order_status` | string |
| `paid_at` | datetime |

---

### 10.3 Get Payment

| Property | Value |
|----------|-------|
| **Endpoint** | `/payments/{payment_id}/` |
| **Method** | `GET` |
| **Purpose** | Retrieve payment status and details |
| **Authentication** | Yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `order_id` | uuid |
| `payment_method` | string |
| `status` | string |
| `amount_cents` | integer |
| `currency_code` | string |
| `gateway` | string |
| `paid_at` | datetime \| null |
| `transactions` | array `{ type, status, amount_cents, created_at }` |

---

### 10.4 Stripe Webhook

| Property | Value |
|----------|-------|
| **Endpoint** | `/payments/webhooks/stripe/` |
| **Method** | `POST` |
| **Purpose** | Receive Stripe payment events (server-to-server) |
| **Authentication** | Stripe signature verification |

**Request body:** Raw Stripe event payload.

**Response `200 OK`:** `{ received: true }`

---

### 10.5 Request Refund

| Property | Value |
|----------|-------|
| **Endpoint** | `/payments/{payment_id}/refund/` |
| **Method** | `POST` |
| **Purpose** | Initiate full or partial refund |
| **Authentication** | Yes (customer request) or staff |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `amount_cents` | integer | no | Partial refund; omit for full |
| `reason` | string | no |

**Response `201 Created`:**

| Field | Type |
|-------|------|
| `refund_id` | uuid |
| `payment_id` | uuid |
| `amount_cents` | integer |
| `status` | string |
| `processed_at` | datetime \| null |

---

### 10.6 List Saved Payment Methods

| Property | Value |
|----------|-------|
| **Endpoint** | `/payments/methods/` |
| **Method** | `GET` |
| **Purpose** | List saved cards for authenticated customer |
| **Authentication** | Yes |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `data` | array |
| `data[].id` | string |
| `data[].brand` | string |
| `data[].last4` | string |
| `data[].exp_month` | integer |
| `data[].exp_year` | integer |
| `data[].is_default` | boolean |

---

## 11. Shipping

### 11.1 List Shipping Methods

| Property | Value |
|----------|-------|
| **Endpoint** | `/shipping/methods/` |
| **Method** | `GET` |
| **Purpose** | Available delivery methods |
| **Authentication** | No |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `data` | array |
| `data[].id` | uuid |
| `data[].code` | string |
| `data[].name` | string |
| `data[].carrier` | string |
| `data[].description` | string |
| `data[].estimated_days_min` | integer |
| `data[].estimated_days_max` | integer |

---

### 11.2 Calculate Shipping Rates

| Property | Value |
|----------|-------|
| **Endpoint** | `/shipping/rates/` |
| **Method** | `POST` |
| **Purpose** | Calculate shipping options and costs for cart/address |
| **Authentication** | Optional |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `cart_id` | uuid | yes |
| `shipping_address` | Address | yes |
| `warehouse_id` | uuid | no | For pickup option |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `rates` | array |
| `rates[].shipping_method_id` | uuid |
| `rates[].name` | string |
| `rates[].carrier` | string |
| `rates[].amount_ex_gst_cents` | integer |
| `rates[].gst_cents` | integer |
| `rates[].amount_inc_gst_cents` | integer |
| `rates[].is_free` | boolean |
| `rates[].estimated_delivery` | object `{ min_date, max_date }` |

---

### 11.3 Get Delivery Estimate

| Property | Value |
|----------|-------|
| **Endpoint** | `/shipping/estimate/` |
| **Method** | `GET` |
| **Purpose** | Quick delivery ETA for product page by postcode |
| **Authentication** | No |

**Query parameters:** `variant_id` (uuid), `postcode` (string), `quantity` (integer)

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `postcode` | string |
| `warehouse` | object `{ code, name, state }` |
| `estimated_days_min` | integer |
| `estimated_days_max` | integer |
| `estimated_delivery` | object `{ min_date, max_date }` |

---

### 11.4 Get Shipment

| Property | Value |
|----------|-------|
| **Endpoint** | `/shipping/shipments/{shipment_id}/` |
| **Method** | `GET` |
| **Purpose** | Shipment tracking detail |
| **Authentication** | Yes (order owner) |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `order_id` | uuid |
| `order_number` | string |
| `status` | string |
| `carrier` | string |
| `tracking_number` | string |
| `tracking_url` | string |
| `items` | array `{ sku, product_name, quantity }` |
| `ship_to_address` | Address |
| `shipped_at` | datetime \| null |
| `delivered_at` | datetime \| null |
| `events` | array `{ status, description, occurred_at, location }` |

---

### 11.5 Validate Postcode

| Property | Value |
|----------|-------|
| **Endpoint** | `/shipping/postcodes/{postcode}/validate/` |
| **Method** | `GET` |
| **Purpose** | Validate AU postcode and return state/suburb suggestions |
| **Authentication** | No |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `postcode` | string |
| `valid` | boolean |
| `state` | string \| null |
| `suburbs` | array[string] |
| `is_serviceable` | boolean |

---

## 12. Reviews

### 12.1 List Product Reviews

| Property | Value |
|----------|-------|
| **Endpoint** | `/products/{slug}/reviews/` |
| **Method** | `GET` |
| **Purpose** | Approved reviews for a product |
| **Authentication** | No |

**Query parameters:** `cursor`, `limit`, `sort` (`newest`, `highest`, `lowest`, `helpful`)

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `data` | array |
| `summary.average_rating` | decimal |
| `summary.review_count` | integer |
| `summary.rating_distribution` | object `{ 1: n, 2: n, 3: n, 4: n, 5: n }` |
| `pagination` | object |

**Review object:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `rating` | integer (1–5) |
| `title` | string \| null |
| `body` | string |
| `author_name` | string |
| `is_verified_purchase` | boolean |
| `helpful_count` | integer |
| `response` | object \| null `{ body, created_at }` |
| `published_at` | datetime |

---

### 12.2 Create Review

| Property | Value |
|----------|-------|
| **Endpoint** | `/products/{slug}/reviews/` |
| **Method** | `POST` |
| **Purpose** | Submit product review (verified purchase required) |
| **Authentication** | Yes |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `rating` | integer | yes (1–5) |
| `title` | string | no |
| `body` | string | yes |
| `order_id` | uuid | yes |

**Response `201 Created`:**

| Field | Type |
|-------|------|
| `id` | uuid |
| `status` | string |
| `message` | string |

---

### 12.3 Mark Review Helpful

| Property | Value |
|----------|-------|
| **Endpoint** | `/reviews/{review_id}/helpful/` |
| **Method** | `POST` |
| **Purpose** | Increment helpful vote on a review |
| **Authentication** | Optional |

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `helpful_count` | integer |

---

### 12.4 Admin: List Pending Reviews

| Property | Value |
|----------|-------|
| **Endpoint** | `/reviews/admin/pending/` |
| **Method** | `GET` |
| **Purpose** | Moderation queue for staff |
| **Authentication** | Yes (`reviews.moderate`) |

**Response `200 OK`:** Paginated reviews with `status: pending`.

---

### 12.5 Admin: Moderate Review

| Property | Value |
|----------|-------|
| **Endpoint** | `/reviews/admin/{review_id}/` |
| **Method** | `PATCH` |
| **Purpose** | Approve or reject a review |
| **Authentication** | Yes (`reviews.moderate`) |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `status` | string | yes | `approved`, `rejected` |
| `response` | string | no | Official store response |

**Response `200 OK`:** Updated review object.

---

## 13. Analytics

### 13.1 Track Event

| Property | Value |
|----------|-------|
| **Endpoint** | `/analytics/events/` |
| **Method** | `POST` |
| **Purpose** | Record client-side behavioural event |
| **Authentication** | Optional |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `event_type` | string | yes |
| `session_id` | string | yes |
| `properties` | object | no |
| `page_url` | string | no |
| `referrer` | string | no |

**Allowed event types:** `page_view`, `product_view`, `add_to_cart`, `remove_from_cart`, `begin_checkout`, `purchase`, `search`, `signup`, `login`

**Response `202 Accepted`:**

| Field | Type |
|-------|------|
| `event_id` | uuid |

---

### 13.2 Start Session

| Property | Value |
|----------|-------|
| **Endpoint** | `/analytics/sessions/` |
| **Method** | `POST` |
| **Purpose** | Initialise analytics session on site visit |
| **Authentication** | Optional |

**Request body:**

| Field | Type | Required |
|-------|------|----------|
| `session_id` | string | yes |
| `utm_source` | string | no |
| `utm_medium` | string | no |
| `utm_campaign` | string | no |
| `device_type` | string | no |
| `referrer` | string | no |

**Response `201 Created`:**

| Field | Type |
|-------|------|
| `session_id` | string |
| `started_at` | datetime |

---

### 13.3 End Session

| Property | Value |
|----------|-------|
| **Endpoint** | `/analytics/sessions/{session_id}/end/` |
| **Method** | `POST` |
| **Purpose** | Mark session ended (page unload beacon) |
| **Authentication** | No |

**Response `204 No Content`**

---

### 13.4 Admin: Dashboard Summary

| Property | Value |
|----------|-------|
| **Endpoint** | `/analytics/admin/summary/` |
| **Method** | `GET` |
| **Purpose** | KPI summary for admin dashboard |
| **Authentication** | Yes (`analytics.view`) |

**Query parameters:** `from_date`, `to_date`, `granularity` (`day`, `week`, `month`)

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `revenue_inc_gst_cents` | integer |
| `order_count` | integer |
| `average_order_value_cents` | integer |
| `conversion_rate` | decimal |
| `top_products` | array `{ variant_id, sku, name, quantity_sold, revenue_cents }` |
| `traffic` | object `{ sessions, page_views, unique_visitors }` |
| `revenue_by_day` | array `{ date, revenue_cents, order_count }` |

---

### 13.5 Admin: Search Analytics

| Property | Value |
|----------|-------|
| **Endpoint** | `/analytics/admin/search/` |
| **Method** | `GET` |
| **Purpose** | Zero-result and top search queries |
| **Authentication** | Yes (`analytics.view`) |

**Query parameters:** `from_date`, `to_date`, `limit`

**Response `200 OK`:**

| Field | Type |
|-------|------|
| `top_queries` | array `{ query, count }` |
| `zero_result_queries` | array `{ query, count }` |

---

## 14. Appendix

### 14.1 Endpoint Summary

| Module | Endpoints | Public | Authenticated | Admin |
|--------|-----------|--------|---------------|-------|
| Authentication | 16 | 6 | 10 | 0 |
| Products | 6 | 6 | 0 | 0 |
| Categories | 3 | 3 | 0 | 0 |
| Brands | 3 | 3 | 0 | 0 |
| Inventory | 6 | 4 | 0 | 2 |
| Cart | 8 | 0 | 8* | 0 |
| Wishlist | 7 | 0 | 7 | 0 |
| Orders | 7 | 2 | 5 | 0 |
| Payments | 6 | 1 | 4 | 1 |
| Shipping | 5 | 4 | 1 | 0 |
| Reviews | 5 | 2 | 1 | 2 |
| Analytics | 5 | 3 | 0 | 2 |
| **Total** | **77** | **34** | **36** | **7** |

*Cart endpoints support guest access via `X-Session-Key` header.

### 14.2 Health & Meta Endpoints

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/health/` | GET | Liveness check | No |
| `/ready/` | GET | Readiness (DB, Redis) | No |
| `/schema/` | GET | OpenAPI 3.0 schema | No |

### 14.3 Rate Limits

| Tier | Limit | Scope |
|------|-------|-------|
| Anonymous | 100 req/min | Per IP |
| Authenticated | 300 req/min | Per user |
| Auth endpoints | 10 req/min | Per IP (login, register) |
| Analytics events | 60 req/min | Per session |
| Admin | 600 req/min | Per staff user |

Rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### 14.4 Webhook Events (Outbound — Phase 2)

| Event | Payload | Subscriber |
|-------|---------|------------|
| `order.confirmed` | Order object | ERP, email service |
| `order.shipped` | Order + shipment | Notification service |
| `payment.succeeded` | Payment object | Accounting |
| `inventory.low_stock` | Variant + warehouse | Procurement |
| `trade_account.approved` | Organization object | CRM |

### 14.5 Document References

| Document | Location |
|----------|----------|
| Project Master Plan | `/docs/PROJECT_MASTER_PLAN.md` |
| Database Plan | `/docs/DATABASE_PLAN.md` |
| UI Design System | `/docs/UI_DESIGN_SYSTEM.md` |

---

*Document Version: 1.0*
*Last Updated: June 2025*
*Author: Senior Backend Architect*
*Status: Approved for Phase 1 Implementation*


