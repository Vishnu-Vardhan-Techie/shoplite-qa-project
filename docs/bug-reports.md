# Bug Reports — ShopLite v1.0

| ID | Title | Module | Severity | Priority | Status | Automated test |
|---|---|---|---|---|---|---|
| BUG-005 | API cart accepts zero, negative and over-stock quantities | Cart API | **Critical** | P1 | Open | `test_cart_api.py::test_add_non_positive_quantity_is_rejected`, `test_add_more_than_stock_is_rejected` |
| BUG-001 | "Price (high to low)" sort returns wrong order | Products | High | P2 | Open | `test_products.py::test_sort_by_price_high_to_low`, `test_products_api.py::test_sort_by_price_descending` |
| BUG-002 | Checkout accepts a 5-digit PIN code | Checkout | Medium | P2 | Open | `test_cart_checkout.py::test_five_digit_pincode_is_rejected` |
| BUG-004 | `GET /api/products/{id}` returns 200 `{}` for unknown id | Products API | Medium | P3 | Open | `test_products_api.py::test_unknown_product_returns_404` |
| BUG-003 | Cart badge count does not decrease after removing an item | Cart UI | Low | P3 | Open | `test_cart_checkout.py::test_badge_decreases_after_remove` |

---

## BUG-005 — API cart accepts zero, negative and over-stock quantities

| Field | Value |
|---|---|
| Severity / Priority | Critical / P1 |
| Environment | ShopLite 1.0, API, localhost |
| Found by | Boundary value analysis on `quantity` |

**Steps to reproduce**
1. `POST /api/login` with `{"username":"standard_user","password":"secret123"}` and copy the token.
2. `POST /api/cart` with header `Authorization: Bearer <token>` and body `{"product_id": 1, "quantity": -1}`.

**Expected:** `400 Bad Request` — quantity must be between 1 and available stock.
**Actual:** `201 Created`. The cart now contains Canvas Backpack × -1 and the **total is ₹-49.99**. Same with `quantity: 0` (line with qty 0) and `{"product_id": 4, "quantity": 6}` when stock is 5.

**Impact:** a customer could reduce their order total with negative lines, or order stock that doesn't exist. Money and inventory risk.

**Evidence**
```http
POST /api/cart  {"product_id": 1, "quantity": -1}
HTTP/1.1 201 CREATED
{"items":[{"id":1,"line_total":-49.99,"name":"Canvas Backpack","price":49.99,"qty":-1,"stock":12}],"total":-49.99}
```

---

## BUG-001 — "Price (high to low)" sort returns wrong order

| Field | Value |
|---|---|
| Severity / Priority | High / P2 |
| Environment | Chrome 13x, ShopLite 1.0 (UI and `GET /api/products?sort=price_desc`) |

**Steps to reproduce**
1. Log in as `standard_user`.
2. On the Products page choose **Price (high to low)** in the sort dropdown.

**Expected:** ₹129.00, ₹49.99, ₹24.50, ₹15.99, ₹9.99
**Actual:** ₹9.99, ₹49.99, ₹24.50, ₹15.99, ₹129.00 — the most expensive item appears last and the cheapest first.

**Root-cause hint:** the order matches a text (alphabetical) sort of the prices — "9.99" > "49.99" > "24.5" > "15.99" > "129.0". Prices are likely compared as strings. **Price (low to high)** works correctly.

---

## BUG-002 — Checkout accepts a 5-digit PIN code

| Field | Value |
|---|---|
| Severity / Priority | Medium / P2 |
| Requirement | REQ-CHK-03: PIN code must be exactly 6 digits |

**Steps to reproduce**
1. Log in, add any in-stock product, go to Checkout.
2. Enter name `Priya Sharma`, email `priya@example.com`, PIN code `60000`.
3. Click **Place order**.

**Expected:** validation error "Enter a valid 6-digit PIN code"; order not placed.
**Actual:** order is placed and confirmation page is shown.

**Notes:** boundary testing — 4 digits ✅ rejected, **5 digits ❌ accepted**, 6 digits ✅ accepted, 7 digits ✅ rejected. Error message itself already says "6-digit", so only the validation rule is wrong. Impact: orders shipped to invalid addresses.

---

## BUG-004 — `GET /api/products/{id}` returns 200 `{}` for unknown id

| Field | Value |
|---|---|
| Severity / Priority | Medium / P3 |

**Steps to reproduce:** `GET /api/products/999`

**Expected:** `404 Not Found` with `{"error": "Product not found"}` (consistent with `POST /api/cart`, which already returns 404 for an unknown product).
**Actual:** `200 OK` with body `{}`.

**Impact:** API clients can't tell "missing" from "found"; a front end would render an empty product page instead of a not-found message.

---

## BUG-003 — Cart badge count does not decrease after removing an item

| Field | Value |
|---|---|
| Severity / Priority | Low / P3 |

**Steps to reproduce**
1. Log in, add Canvas Backpack once and Steel Water Bottle twice. Badge shows **3**.
2. Open the cart and click **Remove** on Canvas Backpack.

**Expected:** badge shows **2** (matches the cart).
**Actual:** badge still shows **3**. It stays wrong until an order is placed or the user logs out. Cart contents and total are correct, so this is a display issue only.
