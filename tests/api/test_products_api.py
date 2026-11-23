import pytest

from tests.data.test_data import MISSING_ID, PRODUCT_COUNT

pytestmark = pytest.mark.api

PRODUCT_SCHEMA = {"id": int, "name": str, "price": (int, float), "stock": int}


@pytest.mark.smoke
def test_list_products_returns_all_products(api):
    r = api.products()
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/json")
    assert len(r.json()) == PRODUCT_COUNT


def test_every_product_matches_schema(api):
    for product in api.products().json():
        assert set(product) == set(PRODUCT_SCHEMA), f"unexpected fields in {product}"
        for field, typ in PRODUCT_SCHEMA.items():
            assert isinstance(product[field], typ), f"{field} has wrong type in {product}"
        assert product["price"] > 0
        assert product["stock"] >= 0


def test_product_ids_are_unique(api):
    ids = [p["id"] for p in api.products().json()]
    assert len(ids) == len(set(ids))


def test_get_single_product(api):
    r = api.product(1)
    assert r.status_code == 200
    assert r.json()["name"] == "Canvas Backpack"


def test_sort_by_price_ascending(api):
    prices = [p["price"] for p in api.products(sort="price_asc").json()]
    assert prices == sorted(prices)


@pytest.mark.known_bug
@pytest.mark.xfail(reason="BUG-001: price high-to-low sorts prices as text, not numbers")
def test_sort_by_price_descending(api):
    prices = [p["price"] for p in api.products(sort="price_desc").json()]
    assert prices == sorted(prices, reverse=True)


@pytest.mark.known_bug
@pytest.mark.xfail(reason="BUG-004: unknown product id returns 200 {} instead of 404")
def test_unknown_product_returns_404(api):
    r = api.product(MISSING_ID)
    assert r.status_code == 404
