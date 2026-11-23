import pytest

from tests.data.test_data import IN_STOCK_ID, MISSING_ID, OUT_OF_STOCK_ID

pytestmark = pytest.mark.api


def test_new_user_cart_is_empty(auth_api):
    r = auth_api.cart()
    assert r.status_code == 200
    assert r.json() == {"items": [], "total": 0}


@pytest.mark.smoke
def test_add_item_to_cart(auth_api):
    r = auth_api.add_to_cart(IN_STOCK_ID, 2)
    assert r.status_code == 201
    item = r.json()["items"][0]
    assert item["id"] == IN_STOCK_ID and item["qty"] == 2
    assert r.json()["total"] == round(49.99 * 2, 2)


def test_adding_same_item_twice_increments_quantity(auth_api):
    auth_api.add_to_cart(IN_STOCK_ID, 1)
    r = auth_api.add_to_cart(IN_STOCK_ID, 1)
    assert r.json()["items"][0]["qty"] == 2


def test_cart_total_is_sum_of_line_totals(auth_api):
    auth_api.add_to_cart(1, 1)   # 49.99
    auth_api.add_to_cart(2, 3)   # 3 x 9.99
    body = auth_api.cart().json()
    assert body["total"] == round(sum(i["line_total"] for i in body["items"]), 2) == 79.96


def test_add_out_of_stock_item_returns_409(auth_api):
    r = auth_api.add_to_cart(OUT_OF_STOCK_ID)
    assert r.status_code == 409
    assert auth_api.cart().json()["items"] == []


def test_add_missing_product_returns_404(auth_api):
    assert auth_api.add_to_cart(MISSING_ID).status_code == 404


@pytest.mark.parametrize("pid,qty", [("1", 1), (1, "2"), (None, 1), (1.5, 1)])
def test_add_with_wrong_types_returns_400(auth_api, pid, qty):
    assert auth_api.add_to_cart(pid, qty).status_code == 400


@pytest.mark.known_bug
@pytest.mark.parametrize("qty", [0, -1])
@pytest.mark.xfail(reason="BUG-005: cart accepts zero/negative quantity")
def test_add_non_positive_quantity_is_rejected(auth_api, qty):
    assert auth_api.add_to_cart(IN_STOCK_ID, qty).status_code == 400


@pytest.mark.known_bug
@pytest.mark.xfail(reason="BUG-005: cart accepts quantity greater than stock")
def test_add_more_than_stock_is_rejected(auth_api):
    assert auth_api.add_to_cart(4, 6).status_code in (400, 409)   # stock is 5


def test_remove_item_from_cart(auth_api):
    auth_api.add_to_cart(IN_STOCK_ID)
    assert auth_api.remove_from_cart(IN_STOCK_ID).status_code == 204
    assert auth_api.cart().json()["items"] == []


def test_remove_item_not_in_cart_returns_404(auth_api):
    assert auth_api.remove_from_cart(IN_STOCK_ID).status_code == 404


def test_cart_persists_across_logins_for_same_user(auth_api, base_url):
    """Cart is stored server-side per user, so a new token sees the same cart."""
    from tests.api.conftest import ApiClient
    from tests.data.test_data import VALID_USER
    auth_api.add_to_cart(IN_STOCK_ID)
    other = ApiClient(base_url)
    other.authorize(other.login(**VALID_USER).json()["token"])
    assert len(other.cart().json()["items"]) == 1
