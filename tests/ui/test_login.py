import pytest
from playwright.sync_api import expect

from tests.data.test_data import INVALID_LOGINS, LOCKED_USER, VALID_USER

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_valid_login_lands_on_products(login_page, page):
    login_page.login(**VALID_USER)
    page.wait_for_url("**/products")
    expect(page.get_by_role("heading", name="Products")).to_be_visible()


@pytest.mark.parametrize("username,password,expected", INVALID_LOGINS)
def test_invalid_login_shows_error(login_page, page, username, password, expected):
    login_page.login(username, password)
    expect(login_page.error).to_have_text(expected)
    assert page.url.endswith("/login")


def test_locked_user_cannot_login(login_page):
    login_page.login(**LOCKED_USER)
    expect(login_page.error).to_have_text("This account has been locked")


def test_password_field_is_masked(login_page):
    expect(login_page.password).to_have_attribute("type", "password")


def test_login_with_enter_key(login_page, page):
    login_page.username.fill(VALID_USER["username"])
    login_page.password.fill(VALID_USER["password"])
    login_page.password.press("Enter")
    page.wait_for_url("**/products")


@pytest.mark.parametrize("path", ["/products", "/cart", "/checkout"])
def test_protected_pages_redirect_to_login(page, path):
    page.goto(path)
    page.wait_for_url("**/login")


def test_logout_ends_session(products_page, page):
    products_page.logout()
    page.wait_for_url("**/login")
    page.goto("/products")          # back button / direct URL must not reopen the session
    page.wait_for_url("**/login")
