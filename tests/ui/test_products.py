import pytest
from playwright.sync_api import expect

from tests.data.test_data import OUT_OF_STOCK_ID, PRODUCT_COUNT

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_all_products_are_listed(products_page):
    expect(products_page.cards).to_have_count(PRODUCT_COUNT)


def test_default_sort_is_name_a_to_z(products_page):
    names = products_page.product_names()
    assert names == sorted(names)


def test_sort_by_name_z_to_a(products_page):
    products_page.sort_by("name_desc")
    names = products_page.product_names()
    assert names == sorted(names, reverse=True)


def test_sort_by_price_low_to_high(products_page):
    products_page.sort_by("price_asc")
    prices = products_page.product_prices()
    assert prices == sorted(prices)


@pytest.mark.known_bug
@pytest.mark.xfail(reason="BUG-001: price high-to-low sorts prices as text, not numbers")
def test_sort_by_price_high_to_low(products_page):
    products_page.sort_by("price_desc")
    prices = products_page.product_prices()
    assert prices == sorted(prices, reverse=True)


def test_out_of_stock_product_cannot_be_added(products_page):
    button = products_page.add_button(OUT_OF_STOCK_ID)
    expect(button).to_be_disabled()
    expect(button).to_have_text("Out of stock")


def test_add_to_cart_updates_badge(products_page):
    expect(products_page.cart_badge).to_have_text("0")
    products_page.add_to_cart(1)
    expect(products_page.cart_badge).to_have_text("1")
    products_page.add_to_cart(2)
    expect(products_page.cart_badge).to_have_text("2")
