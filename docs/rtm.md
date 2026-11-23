# Requirement Traceability Matrix

Every requirement maps to at least one test case, and every test case maps to an automated test.
Generated from `build_test_cases.py` (same data as `test-cases.xlsx`).

| Req ID | Requirement | Test cases | Result | Defects |
|---|---|---|---|---|
| REQ-AUTH-01 | User can log in with valid username and password | TC-AUTH-001, TC-AUTH-007, TC-AUTH-008 | 3/3 pass ✅ | — |
| REQ-AUTH-02 | Invalid or empty credentials show a clear error and do not log in | TC-AUTH-002, TC-AUTH-003, TC-AUTH-004, TC-AUTH-005 | 4/4 pass ✅ | — |
| REQ-AUTH-03 | Locked accounts cannot log in | TC-AUTH-006 | 1/1 pass ✅ | — |
| REQ-AUTH-04 | Products, cart and checkout require login; logout ends the session | TC-AUTH-009, TC-AUTH-010 | 2/2 pass ✅ | — |
| REQ-PRD-01 | All products are listed with name and price | TC-PRD-001 | 1/1 pass ✅ | — |
| REQ-PRD-02 | Products can be sorted by name (A-Z, Z-A) and price (low-high, high-low) | TC-PRD-002, TC-PRD-003, TC-PRD-004, TC-PRD-005 | 3/4 pass ⚠️ | BUG-001 |
| REQ-PRD-03 | Out-of-stock products cannot be added to cart | TC-PRD-006 | 1/1 pass ✅ | — |
| REQ-CRT-01 | Adding items updates the cart and the cart badge count | TC-CRT-001, TC-CRT-002 | 2/2 pass ✅ | — |
| REQ-CRT-02 | Items can be removed; cart and badge update | TC-CRT-004, TC-CRT-005, TC-CRT-006 | 2/3 pass ⚠️ | BUG-003 |
| REQ-CRT-03 | Cart total equals sum of price x quantity | TC-CRT-003 | 1/1 pass ✅ | — |
| REQ-CRT-04 | Checkout is not reachable with an empty cart | TC-CRT-007 | 1/1 pass ✅ | — |
| REQ-CHK-01 | Full name, email and PIN code are mandatory | TC-CHK-002, TC-CHK-006 | 2/2 pass ✅ | — |
| REQ-CHK-02 | Email must be a valid format | TC-CHK-003 | 1/1 pass ✅ | — |
| REQ-CHK-03 | PIN code must be exactly 6 digits | TC-CHK-004, TC-CHK-005 | 1/2 pass ⚠️ | BUG-002 |
| REQ-CHK-04 | Successful order shows order ID and total and clears the cart | TC-CHK-001 | 1/1 pass ✅ | — |
| REQ-API-01 | POST /api/login returns a token for valid users and correct errors otherwise | TC-API-001, TC-API-002, TC-API-003 | 3/3 pass ✅ | — |
| REQ-API-02 | Product endpoints follow the documented schema and status codes | TC-API-004, TC-API-005, TC-API-006 | 1/3 pass ⚠️ | BUG-001, BUG-004 |
| REQ-API-03 | Cart endpoints require a valid Bearer token | TC-API-007 | 1/1 pass ✅ | — |
| REQ-API-04 | Cart endpoints validate product id, type and quantity (1..stock) | TC-API-008, TC-API-009, TC-API-010, TC-API-011, TC-API-012, TC-API-013 | 4/6 pass ⚠️ | BUG-005 |

**Totals:** 19 requirements · 42 test cases · 35 passed · 7 failed · requirement coverage 100%
