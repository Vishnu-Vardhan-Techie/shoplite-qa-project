# Test Plan — ShopLite v1.0

| Item | Detail |
|---|---|
| Document ID | TP-SHOPLITE-001 |
| Author | Vishnu Vardhan (QA) |
| Application | ShopLite web store + REST API |
| Version under test | 1.0 |
| Status | Executed — see [test-summary-report.md](test-summary-report.md) |

## 1. Objective
Verify that a customer can sign in, browse products, manage a cart and place an order correctly, and that the REST API behaves according to its contract. Find and report defects before release.

## 2. Scope

**In scope**

| Module | Features |
|---|---|
| Authentication | Login, logout, locked account, session protection |
| Product catalogue | Listing, sorting (name / price), out-of-stock handling |
| Cart | Add, remove, quantity, totals, cart badge |
| Checkout | Form validation (name, email, PIN code), order confirmation |
| REST API | `/api/login`, `/api/products`, `/api/cart` — status codes, schema, auth, negative cases |

**Out of scope:** payment gateway, performance/load testing, mobile apps, accessibility audit (spot checks only), security penetration testing.

## 3. Test approach

| Level / type | How | Tooling |
|---|---|---|
| Functional — manual | Scripted test cases from requirements; exploratory sessions on cart and checkout | [test-cases.xlsx](test-cases.xlsx) |
| Functional — UI automation | Page Object Model; stable `data-test` locators; no hard waits | Playwright + pytest |
| API testing | Status codes, response schema, auth headers, negative and boundary inputs | pytest + requests, Postman |
| Regression | Full automated suite on every push | GitHub Actions |
| Smoke | `-m smoke` subset: login, product list, add to cart, end-to-end purchase | pytest markers |

**Test design techniques used**
- **Equivalence partitioning** — valid / invalid / empty / wrong-case credentials.
- **Boundary value analysis** — PIN code length 5 / 6 / 7; cart quantity 0, -1, stock, stock+1.
- **Error guessing** — missing auth header, malformed JSON, wrong data types, non-existent IDs.
- **State transition** — logged out → logged in → logged out; cart empty → items → empty.

## 4. Entry and exit criteria

**Entry:** build deployed to test environment; requirements frozen; test data available.

**Exit:**
- 100% of planned test cases executed.
- No open **Critical** defects; any open **High** defects accepted by product owner.
- Smoke suite passing.

## 5. Environment
- OS: Ubuntu 22.04 / Windows 11
- Browser: Chrome (latest), Chromium via Playwright
- Python 3.11+, Flask test server on localhost
- Test accounts: `standard_user` / `secret123`, `locked_user` / `secret123`

## 6. Defect management
Each defect gets an ID (BUG-NNN), severity, priority, steps to reproduce, expected vs actual result, and evidence. Every defect found by automation has a matching test marked `known_bug` that will **fail the build as soon as the bug is fixed** (strict xfail), so the test is then converted into a normal regression test.

| Severity | Meaning |
|---|---|
| Critical | Blocks a core flow or causes data/money loss, no workaround |
| High | Major function wrong, workaround hard |
| Medium | Function wrong but a workaround exists |
| Low | Cosmetic / minor UX |

## 7. Risks
| Risk | Mitigation |
|---|---|
| Money calculations wrong (cart total, quantity) | Dedicated API + UI checks on totals; boundary tests on quantity |
| Flaky UI tests | Auto-waiting Playwright assertions, isolated browser context per test, API state reset per test |
| Requirement gaps (e.g. PIN format) | Clarified with product: Indian PIN = exactly 6 digits |

## 8. Deliverables
Test plan · test cases · requirement traceability matrix · bug reports · automated test suites · HTML test report · test summary report.
