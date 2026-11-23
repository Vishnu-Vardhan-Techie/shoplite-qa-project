# Test Summary Report — ShopLite v1.0

| Item | Detail |
|---|---|
| Report ID | TSR-SHOPLITE-001 |
| Prepared by | Vishnu Vardhan (QA) |
| Test plan | [TP-SHOPLITE-001](test-plan.md) |
| Build | ShopLite 1.0 |

## 1. Summary
Testing covered authentication, product catalogue, cart, checkout and the REST API. **5 defects were found, including 1 Critical** (API accepts negative cart quantities, which can make the order total negative). **Recommendation: not ready for release** until BUG-005 is fixed and BUG-001 / BUG-002 are fixed or formally accepted.

## 2. Manual test execution

| Module | Planned | Executed | Passed | Failed |
|---|---|---|---|---|
| Authentication | 10 | 10 | 10 | 0 |
| Products | 6 | 6 | 5 | 1 |
| Cart | 7 | 7 | 6 | 1 |
| Checkout | 6 | 6 | 5 | 1 |
| API | 13 | 13 | 9 | 4 |
| **Total** | **42** | **42** | **35** | **7** |

Pass rate: **83%** · Execution: **100%** · Requirement coverage: **19 / 19 (100%)** — see [rtm.md](rtm.md).

## 3. Automated test execution

| Suite | Tests | Passed | Known-bug (xfail) | Failed |
|---|---|---|---|---|
| API (pytest + requests) | 37 | 32 | 5 | 0 |
| UI (Playwright, POM) | 40 | 37 | 3 | 0 |
| **Total** | **77** | **69** | **8** | **0** |

Full run time ≈ 25 s. Smoke subset: 6 tests. Parametrized data-driven tests expand the 42 manual cases into 77 automated checks.

## 4. Defects

| Severity | Open | IDs |
|---|---|---|
| Critical | 1 | BUG-005 |
| High | 1 | BUG-001 |
| Medium | 2 | BUG-002, BUG-004 |
| Low | 1 | BUG-003 |

Details, steps and evidence: [bug-reports.md](bug-reports.md).

## 5. Observations and recommendations
1. **Add server-side quantity validation** (1 ≤ qty ≤ stock) to the cart API — highest risk, affects money.
2. **Numeric sort for prices** — one-line fix; covered by an existing automated test that will turn the build red once fixed so it can be promoted to a normal regression test.
3. **Align API error handling** — `GET /products/{id}` should return 404 like other endpoints.
4. Suggest adding a requirement for maximum quantity per order and for rate-limiting login attempts (currently unlimited retries — noted during exploratory testing, not raised as a defect because no requirement exists).

## 6. Not tested
Payment gateway, performance under load, cross-browser beyond Chromium, full accessibility audit — out of scope per test plan.
