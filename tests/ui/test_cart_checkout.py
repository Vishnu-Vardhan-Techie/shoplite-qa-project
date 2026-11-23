import re

import pytest
from playwright.sync_api import expect

from tests.data.test_data import CHECKOUT_OK, FIVE_DIGIT_PINCODE, INVALID_PINCODES
from tests.ui.pages import CartPage, CheckoutPage

pytestmark = pytest.mark.ui


@pytest.fixture
def cart_with_items(products_page, page):
    products_page.add_to_cart(1)   # 49.99
    products_page.add_to_cart(2)   # 9.99
    products_page.add_to_cart(2)   # 9.99
    return CartPage(page).open()


@pytest.fixture
def checkout_page(cart_with_items, page):
    cart_with_items.checkout()
    page.wait_for_url("**/checkout")
    return CheckoutPage(page)


def test_cart_shows_items_and_quantities(cart_with_items):
    expect(cart_with_items.rows).to_have_count(2)
    expect(cart_with_items.item_names).to_have_text(["Canvas Backpack", "Steel Water Bottle"])


def test_cart_total_is_calculated_correctly(cart_with_items):
    assert cart_with_items.total_amount() == 69.97


def test_remove_item_updates_cart(cart_with_items):
    cart_with_items.remove(1)
    expect(cart_with_items.rows).to_have_count(1)
    assert cart_with_items.total_amount() == 19.98


def test_removing_all_items_shows_empty_cart(cart_with_items):
    cart_with_items.remove(1)
    cart_with_items.remove(2)
    expect(cart_with_items.empty_message).to_be_visible()


@pytest.mark.known_bug
@pytest.mark.xfail(reason="BUG-003: cart badge does not decrease after removing an item")
def test_badge_decreases_after_remove(cart_with_items):
    cart_with_items.remove(1)
    expect(cart_with_items.cart_badge).to_have_text("2", timeout=1_000)


def test_empty_cart_cannot_reach_checkout(products_page, page):
    page.goto("/checkout")
    page.wait_for_url("**/cart")


@pytest.mark.e2e
@pytest.mark.smoke
def test_end_to_end_purchase(checkout_page, page):
    expect(checkout_page.total).to_have_text("69.97")
    checkout_page.place_order(**CHECKOUT_OK)
    expect(checkout_page.success).to_have_text("Thank you for your order!")
    expect(checkout_page.order_id).to_have_text(re.compile(r"^ORD-[0-9A-F]{6}$"))
    expect(checkout_page.order_total).to_have_text("69.97")
    expect(checkout_page.cart_badge).to_have_text("0")


def test_all_fields_required(checkout_page):
    checkout_page.place_order()
    expect(checkout_page.error_for("full_name")).to_have_text("Full name is required")
    expect(checkout_page.error_for("email")).to_have_text("Enter a valid email address")
    expect(checkout_page.error_for("pincode")).to_have_text("Enter a valid 6-digit PIN code")


@pytest.mark.parametrize("email", ["priya", "priya@", "@example.com", "priya@example", "pri ya@example.com"])
def test_invalid_email_is_rejected(checkout_page, email):
    checkout_page.place_order(CHECKOUT_OK["full_name"], email, CHECKOUT_OK["pincode"])
    expect(checkout_page.error_for("email")).to_be_visible()


@pytest.mark.parametrize("pincode", INVALID_PINCODES)
def test_invalid_pincode_is_rejected(checkout_page, pincode):
    checkout_page.place_order(CHECKOUT_OK["full_name"], CHECKOUT_OK["email"], pincode)
    expect(checkout_page.error_for("pincode")).to_be_visible()


@pytest.mark.known_bug
@pytest.mark.xfail(reason="BUG-002: 5-digit PIN code is accepted at checkout")
def test_five_digit_pincode_is_rejected(checkout_page):
    checkout_page.place_order(CHECKOUT_OK["full_name"], CHECKOUT_OK["email"], FIVE_DIGIT_PINCODE)
    expect(checkout_page.error_for("pincode")).to_be_visible(timeout=1_000)


def test_form_keeps_values_after_validation_error(checkout_page):
    checkout_page.place_order(CHECKOUT_OK["full_name"], "bad-email", CHECKOUT_OK["pincode"])
    expect(checkout_page.full_name).to_have_value(CHECKOUT_OK["full_name"])
    expect(checkout_page.pincode).to_have_value(CHECKOUT_OK["pincode"])
