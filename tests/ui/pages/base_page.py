from playwright.sync_api import Page


class BasePage:
    """Common header elements shared by every logged-in page."""
    path = "/"

    def __init__(self, page: Page):
        self.page = page
        self.cart_badge = page.get_by_test_id("cart-badge")
        self.nav_cart = page.get_by_test_id("nav-cart")
        self.nav_logout = page.get_by_test_id("nav-logout")

    def open(self):
        self.page.goto(self.path)
        return self

    def badge_count(self) -> int:
        return int(self.cart_badge.inner_text())

    def logout(self):
        self.nav_logout.click()
