"""Generates docs/test-cases.xlsx (Test Cases, Requirements, RTM) and docs/rtm.md.

Run:  python docs/build_test_cases.py
"""
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

HERE = Path(__file__).parent

REQUIREMENTS = [
    ("REQ-AUTH-01", "Authentication", "User can log in with valid username and password"),
    ("REQ-AUTH-02", "Authentication", "Invalid or empty credentials show a clear error and do not log in"),
    ("REQ-AUTH-03", "Authentication", "Locked accounts cannot log in"),
    ("REQ-AUTH-04", "Authentication", "Products, cart and checkout require login; logout ends the session"),
    ("REQ-PRD-01", "Products", "All products are listed with name and price"),
    ("REQ-PRD-02", "Products", "Products can be sorted by name (A-Z, Z-A) and price (low-high, high-low)"),
    ("REQ-PRD-03", "Products", "Out-of-stock products cannot be added to cart"),
    ("REQ-CRT-01", "Cart", "Adding items updates the cart and the cart badge count"),
    ("REQ-CRT-02", "Cart", "Items can be removed; cart and badge update"),
    ("REQ-CRT-03", "Cart", "Cart total equals sum of price x quantity"),
    ("REQ-CRT-04", "Cart", "Checkout is not reachable with an empty cart"),
    ("REQ-CHK-01", "Checkout", "Full name, email and PIN code are mandatory"),
    ("REQ-CHK-02", "Checkout", "Email must be a valid format"),
    ("REQ-CHK-03", "Checkout", "PIN code must be exactly 6 digits"),
    ("REQ-CHK-04", "Checkout", "Successful order shows order ID and total and clears the cart"),
    ("REQ-API-01", "API", "POST /api/login returns a token for valid users and correct errors otherwise"),
    ("REQ-API-02", "API", "Product endpoints follow the documented schema and status codes"),
    ("REQ-API-03", "API", "Cart endpoints require a valid Bearer token"),
    ("REQ-API-04", "API", "Cart endpoints validate product id, type and quantity (1..stock)"),
]

U = "Logged in as standard_user"
P = "Logged in; on Products page"
C = "Logged in; cart has Canvas Backpack x1, Steel Water Bottle x2"
K = "Cart has items; on Checkout page"
A = "Valid API token"

# id, req, title, pre, steps, data, expected, priority, type, automated test, bug, status, actual
CASES = [
    ("TC-AUTH-001", "REQ-AUTH-01", "Login with valid credentials", "On login page",
     "1. Enter username\n2. Enter password\n3. Click Login", "standard_user / secret123",
     "Redirected to Products page", "High", "Positive", "test_login.py::test_valid_login_lands_on_products", "", "Pass", "As expected"),
    ("TC-AUTH-002", "REQ-AUTH-02", "Login with wrong password", "On login page",
     "1. Enter valid username\n2. Enter wrong password\n3. Click Login", "standard_user / wrong",
     "Error 'Invalid username or password'; stays on login", "High", "Negative", "test_login.py::test_invalid_login_shows_error", "", "Pass", "As expected"),
    ("TC-AUTH-003", "REQ-AUTH-02", "Login with unknown username", "On login page",
     "1. Enter unknown username\n2. Enter password\n3. Click Login", "unknown_user / secret123",
     "Error 'Invalid username or password'", "Medium", "Negative", "test_login.py::test_invalid_login_shows_error", "", "Pass", "As expected"),
    ("TC-AUTH-004", "REQ-AUTH-02", "Username is case-sensitive", "On login page",
     "1. Enter username in upper case\n2. Enter password\n3. Click Login", "STANDARD_USER / secret123",
     "Error 'Invalid username or password'", "Low", "Negative", "test_login.py::test_invalid_login_shows_error", "", "Pass", "As expected"),
    ("TC-AUTH-005", "REQ-AUTH-02", "Login with empty fields", "On login page",
     "1. Leave username/password empty (each combination)\n2. Click Login", "'' / secret123, standard_user / '', '' / ''",
     "Error 'Username and password are required'", "Medium", "Negative", "test_login.py::test_invalid_login_shows_error", "", "Pass", "As expected"),
    ("TC-AUTH-006", "REQ-AUTH-03", "Locked user cannot log in", "On login page",
     "1. Enter locked user credentials\n2. Click Login", "locked_user / secret123",
     "Error 'This account has been locked'", "High", "Negative", "test_login.py::test_locked_user_cannot_login", "", "Pass", "As expected"),
    ("TC-AUTH-007", "REQ-AUTH-01", "Password field is masked", "On login page",
     "1. Type in password field", "any", "Characters are masked (type=password)", "Low", "UI", "test_login.py::test_password_field_is_masked", "", "Pass", "As expected"),
    ("TC-AUTH-008", "REQ-AUTH-01", "Login using Enter key", "On login page",
     "1. Enter credentials\n2. Press Enter in password field", "standard_user / secret123",
     "Logged in, Products page shown", "Low", "Usability", "test_login.py::test_login_with_enter_key", "", "Pass", "As expected"),
    ("TC-AUTH-009", "REQ-AUTH-04", "Protected pages redirect to login", "Not logged in",
     "1. Open /products, /cart, /checkout directly", "URLs", "Each redirects to login page", "High", "Security", "test_login.py::test_protected_pages_redirect_to_login", "", "Pass", "As expected"),
    ("TC-AUTH-010", "REQ-AUTH-04", "Logout ends session", U,
     "1. Click Logout\n2. Open /products directly", "", "Login page shown both times", "High", "Security", "test_login.py::test_logout_ends_session", "", "Pass", "As expected"),

    ("TC-PRD-001", "REQ-PRD-01", "All products listed", U, "1. Open Products page", "", "5 product cards with name and price", "High", "Positive", "test_products.py::test_all_products_are_listed", "", "Pass", "As expected"),
    ("TC-PRD-002", "REQ-PRD-02", "Default sort is Name A-Z", P, "1. Observe order of product names", "", "Names in alphabetical order", "Medium", "Positive", "test_products.py::test_default_sort_is_name_a_to_z", "", "Pass", "As expected"),
    ("TC-PRD-003", "REQ-PRD-02", "Sort by Name Z-A", P, "1. Select 'Name (Z to A)'", "", "Names in reverse alphabetical order", "Medium", "Positive", "test_products.py::test_sort_by_name_z_to_a", "", "Pass", "As expected"),
    ("TC-PRD-004", "REQ-PRD-02", "Sort by Price low-high", P, "1. Select 'Price (low to high)'", "", "9.99, 15.99, 24.50, 49.99, 129.00", "High", "Positive", "test_products.py::test_sort_by_price_low_to_high", "", "Pass", "As expected"),
    ("TC-PRD-005", "REQ-PRD-02", "Sort by Price high-low", P, "1. Select 'Price (high to low)'", "", "129.00, 49.99, 24.50, 15.99, 9.99", "High", "Positive", "test_products.py::test_sort_by_price_high_to_low", "BUG-001", "Fail", "9.99, 49.99, 24.50, 15.99, 129.00"),
    ("TC-PRD-006", "REQ-PRD-03", "Out-of-stock item cannot be added", P, "1. Find Desk Lamp\n2. Check Add button", "Desk Lamp (stock 0)", "Button disabled, label 'Out of stock'", "High", "Negative", "test_products.py::test_out_of_stock_product_cannot_be_added", "", "Pass", "As expected"),

    ("TC-CRT-001", "REQ-CRT-01", "Add to cart updates badge", P, "1. Add Canvas Backpack\n2. Add Steel Water Bottle", "", "Badge shows 1 then 2", "High", "Positive", "test_products.py::test_add_to_cart_updates_badge", "", "Pass", "As expected"),
    ("TC-CRT-002", "REQ-CRT-01", "Cart lists items and quantities", C, "1. Open Cart", "", "2 rows; Backpack qty 1, Bottle qty 2", "High", "Positive", "test_cart_checkout.py::test_cart_shows_items_and_quantities", "", "Pass", "As expected"),
    ("TC-CRT-003", "REQ-CRT-03", "Cart total is correct", C, "1. Open Cart\n2. Check total", "49.99 + 2 x 9.99", "Total = 69.97", "High", "Positive", "test_cart_checkout.py::test_cart_total_is_calculated_correctly", "", "Pass", "As expected"),
    ("TC-CRT-004", "REQ-CRT-02", "Remove item updates cart and total", C, "1. Remove Canvas Backpack", "", "1 row left; total 19.98", "High", "Positive", "test_cart_checkout.py::test_remove_item_updates_cart", "", "Pass", "As expected"),
    ("TC-CRT-005", "REQ-CRT-02", "Badge decreases after remove", C, "1. Note badge (3)\n2. Remove Canvas Backpack", "", "Badge shows 2", "Low", "UI", "test_cart_checkout.py::test_badge_decreases_after_remove", "BUG-003", "Fail", "Badge still shows 3"),
    ("TC-CRT-006", "REQ-CRT-02", "Removing all items shows empty cart", C, "1. Remove every item", "", "Message 'Your cart is empty.'", "Medium", "Positive", "test_cart_checkout.py::test_removing_all_items_shows_empty_cart", "", "Pass", "As expected"),
    ("TC-CRT-007", "REQ-CRT-04", "Empty cart cannot reach checkout", "Logged in; cart empty", "1. Open /checkout directly", "", "Redirected to Cart page", "Medium", "Negative", "test_cart_checkout.py::test_empty_cart_cannot_reach_checkout", "", "Pass", "As expected"),

    ("TC-CHK-001", "REQ-CHK-04", "End-to-end purchase", C,
     "1. Click Checkout\n2. Fill valid details\n3. Click Place order", "Priya Sharma, priya@example.com, 600001",
     "Thank-you page; order ID ORD-XXXXXX; total 69.97; badge 0", "High", "E2E", "test_cart_checkout.py::test_end_to_end_purchase", "", "Pass", "As expected"),
    ("TC-CHK-002", "REQ-CHK-01", "All checkout fields mandatory", K, "1. Leave all fields empty\n2. Place order", "", "Error shown under each of the 3 fields", "High", "Negative", "test_cart_checkout.py::test_all_fields_required", "", "Pass", "As expected"),
    ("TC-CHK-003", "REQ-CHK-02", "Invalid email formats rejected", K, "1. Enter each invalid email\n2. Place order", "priya, priya@, @example.com, priya@example, 'pri ya@example.com'", "Email error shown; no order", "High", "Negative", "test_cart_checkout.py::test_invalid_email_is_rejected", "", "Pass", "As expected"),
    ("TC-CHK-004", "REQ-CHK-03", "PIN code boundary: 7 digits / letters / blank", K, "1. Enter each value\n2. Place order", "6000011, 60A001, '', '  '", "PIN error shown; no order", "High", "Boundary", "test_cart_checkout.py::test_invalid_pincode_is_rejected", "", "Pass", "As expected"),
    ("TC-CHK-005", "REQ-CHK-03", "PIN code boundary: 5 digits", K, "1. Enter 5-digit PIN\n2. Place order", "60000", "PIN error shown; no order", "High", "Boundary", "test_cart_checkout.py::test_five_digit_pincode_is_rejected", "BUG-002", "Fail", "Order placed successfully"),
    ("TC-CHK-006", "REQ-CHK-01", "Entered values kept after validation error", K, "1. Fill name & PIN, bad email\n2. Place order", "bad-email", "Name and PIN still filled in", "Low", "Usability", "test_cart_checkout.py::test_form_keeps_values_after_validation_error", "", "Pass", "As expected"),

    ("TC-API-001", "REQ-API-01", "POST /api/login valid -> 200 + token", "API running", "POST /api/login", '{"username":"standard_user","password":"secret123"}', "200; 32-char token; new token each call", "High", "API", "test_auth_api.py::test_login_with_valid_credentials_returns_token", "", "Pass", "As expected"),
    ("TC-API-002", "REQ-API-01", "POST /api/login invalid -> 400/401", "API running", "POST /api/login with each invalid pair", "see test data", "401 (wrong) / 400 (missing); error message; no token", "High", "API", "test_auth_api.py::test_login_with_invalid_credentials_is_rejected", "", "Pass", "As expected"),
    ("TC-API-003", "REQ-API-01", "Locked user -> 403", "API running", "POST /api/login", "locked_user", "403 'This account has been locked'", "Medium", "API", "test_auth_api.py::test_locked_user_gets_403", "", "Pass", "As expected"),
    ("TC-API-004", "REQ-API-02", "GET /api/products schema", "API running", "GET /api/products", "", "200; JSON array of 5; fields id,name,price,stock with right types; unique ids", "High", "API", "test_products_api.py::test_every_product_matches_schema", "", "Pass", "As expected"),
    ("TC-API-005", "REQ-API-02", "GET /api/products?sort=price_desc", "API running", "GET with sort param", "price_desc", "Prices in descending order", "High", "API", "test_products_api.py::test_sort_by_price_descending", "BUG-001", "Fail", "Text-sorted order"),
    ("TC-API-006", "REQ-API-02", "GET /api/products/999 -> 404", "API running", "GET unknown id", "999", "404 + error message", "Medium", "API", "test_products_api.py::test_unknown_product_returns_404", "BUG-004", "Fail", "200 {}"),
    ("TC-API-007", "REQ-API-03", "Cart without / with bad token -> 401", "API running", "GET /api/cart with missing, invalid, wrong-scheme token", "", "401 Unauthorized each time", "High", "Security", "test_auth_api.py::test_cart_requires_valid_bearer_token", "", "Pass", "As expected"),
    ("TC-API-008", "REQ-API-04", "Add to cart -> 201 + correct total", A, "POST /api/cart", '{"product_id":1,"quantity":2}', "201; qty 2; total 99.98", "High", "API", "test_cart_api.py::test_add_item_to_cart", "", "Pass", "As expected"),
    ("TC-API-009", "REQ-API-04", "Wrong data types -> 400", A, "POST /api/cart with string / null / float values", '"1", "2", null, 1.5', "400", "Medium", "API", "test_cart_api.py::test_add_with_wrong_types_returns_400", "", "Pass", "As expected"),
    ("TC-API-010", "REQ-API-04", "Out-of-stock -> 409, unknown -> 404", A, "POST /api/cart", "product 5, product 999", "409 / 404; cart unchanged", "Medium", "API", "test_cart_api.py::test_add_out_of_stock_item_returns_409", "", "Pass", "As expected"),
    ("TC-API-011", "REQ-API-04", "Quantity 0 / negative rejected", A, "POST /api/cart", "quantity 0, -1", "400", "High", "Boundary", "test_cart_api.py::test_add_non_positive_quantity_is_rejected", "BUG-005", "Fail", "201; total becomes negative"),
    ("TC-API-012", "REQ-API-04", "Quantity above stock rejected", A, "POST /api/cart", "product 4 (stock 5), quantity 6", "400 or 409", "High", "Boundary", "test_cart_api.py::test_add_more_than_stock_is_rejected", "BUG-005", "Fail", "201 accepted"),
    ("TC-API-013", "REQ-API-04", "DELETE /api/cart/{id}", A, "Add item, DELETE it, DELETE again", "product 1", "204 then 404", "Medium", "API", "test_cart_api.py::test_remove_item_from_cart", "", "Pass", "As expected"),
]

HEADERS = ["TC ID", "Requirement", "Title", "Preconditions", "Steps", "Test Data", "Expected Result",
           "Priority", "Type", "Automated Test", "Bug ID", "Status", "Actual Result"]
WIDTHS = [12, 13, 34, 26, 38, 30, 38, 9, 11, 46, 9, 8, 28]

HEAD_FILL = PatternFill("solid", fgColor="1D2330")
PASS_FILL = PatternFill("solid", fgColor="DDF3E4")
FAIL_FILL = PatternFill("solid", fgColor="FBE0DE")
THIN = Side(style="thin", color="D0D4DB")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def style_header(ws, widths):
    for i, w in enumerate(widths, 1):
        c = ws.cell(row=1, column=i)
        c.font, c.fill = Font(bold=True, color="FFFFFF"), HEAD_FILL
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[c.column_letter].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions


def build():
    wb = Workbook()
    ws = wb.active
    ws.title = "Test Cases"
    ws.append(HEADERS)
    for case in CASES:
        ws.append(list(case))
    style_header(ws, WIDTHS)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(vertical="top", wrap_text=True)
            c.border = BORDER
        row[11].fill = PASS_FILL if row[11].value == "Pass" else FAIL_FILL
    dv = DataValidation(type="list", formula1='"Pass,Fail,Blocked,Not Run"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"L2:L{ws.max_row}")

    rq = wb.create_sheet("Requirements")
    rq.append(["Req ID", "Module", "Requirement"])
    for r in REQUIREMENTS:
        rq.append(list(r))
    style_header(rq, [14, 16, 80])

    by_req = defaultdict(list)
    for case in CASES:
        by_req[case[1]].append(case)

    rtm = wb.create_sheet("RTM")
    rtm.append(["Req ID", "Requirement", "Test Cases", "# Cases", "Passed", "Failed", "Defects", "Coverage"])
    n = len(REQUIREMENTS) + 1
    for i, (rid, _, text) in enumerate(REQUIREMENTS, start=2):
        cases = by_req[rid]
        bugs = sorted({c[10] for c in cases if c[10]})
        rtm.append([rid, text, ", ".join(c[0] for c in cases),
                    f"=COUNTIF('Test Cases'!B:B,A{i})",
                    f"=COUNTIFS('Test Cases'!B:B,A{i},'Test Cases'!L:L,\"Pass\")",
                    f"=COUNTIFS('Test Cases'!B:B,A{i},'Test Cases'!L:L,\"Fail\")",
                    ", ".join(bugs) or "-",
                    f'=IF(D{i}>0,"Covered","GAP")'])
    rtm.append([])
    rtm.append(["TOTAL", "", "", f"=SUM(D2:D{n})", f"=SUM(E2:E{n})", f"=SUM(F2:F{n})", "",
                f'=TEXT(E{n + 2}/D{n + 2},"0%")&" pass rate"'])
    style_header(rtm, [14, 60, 40, 9, 8, 8, 18, 16])
    for row in rtm.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(vertical="top", wrap_text=True)
    for c in rtm[n + 2]:
        c.font = Font(bold=True)

    wb.save(HERE / "test-cases.xlsx")

    # Markdown RTM for GitHub readers
    lines = ["# Requirement Traceability Matrix", "",
             "Every requirement maps to at least one test case, and every test case maps to an automated test.",
             "Generated from `build_test_cases.py` (same data as `test-cases.xlsx`).", "",
             "| Req ID | Requirement | Test cases | Result | Defects |", "|---|---|---|---|---|"]
    for rid, _, text in REQUIREMENTS:
        cases = by_req[rid]
        passed = sum(c[11] == "Pass" for c in cases)
        bugs = ", ".join(sorted({c[10] for c in cases if c[10]})) or "—"
        result = f"{passed}/{len(cases)} pass" + (" ⚠️" if passed < len(cases) else " ✅")
        lines.append(f"| {rid} | {text} | {', '.join(c[0] for c in cases)} | {result} | {bugs} |")
    total, passed = len(CASES), sum(c[11] == "Pass" for c in CASES)
    lines += ["", f"**Totals:** {len(REQUIREMENTS)} requirements · {total} test cases · "
              f"{passed} passed · {total - passed} failed · requirement coverage 100%"]
    (HERE / "rtm.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{total} test cases, {passed} pass, {total - passed} fail")


if __name__ == "__main__":
    build()
