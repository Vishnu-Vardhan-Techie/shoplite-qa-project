from .base_page import BasePage


class CartPage(BasePage):
    path = "/cart"

    def __init__(self, page):
        super().__init__(page)
        self.rows = page.get_by_test_id("cart-row")
        self.item_names = page.get_by_test_id("cart-item-name")
        self.total = page.get_by_test_id("cart-total")
        self.empty_message = page.get_by_test_id("empty-cart")
        self.checkout_button = page.get_by_test_id("checkout-button")

    def remove(self, product_id):
        self.page.get_by_test_id(f"remove-{product_id}").click()

    def total_amount(self) -> float:
        return float(self.total.inner_text())

    def checkout(self):
        self.checkout_button.click()
