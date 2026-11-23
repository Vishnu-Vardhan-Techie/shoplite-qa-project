import pytest
from playwright.sync_api import expect

from tests.data.test_data import VALID_USER
from tests.ui.pages import LoginPage, ProductsPage

expect.set_options(timeout=5_000)


@pytest.fixture(scope="session", autouse=True)
def _use_data_test_attribute(playwright):
    """The app exposes stable `data-test` hooks; point get_by_test_id at them."""
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture
def login_page(page):
    return LoginPage(page).open()


@pytest.fixture
def products_page(page):
    """A page that is already logged in as the standard user."""
    LoginPage(page).open().login(**VALID_USER)
    page.wait_for_url("**/products")
    return ProductsPage(page)
