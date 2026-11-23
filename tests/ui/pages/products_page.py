from .base_page import BasePage


class ProductsPage(BasePage):
    path = "/products"

    def __init__(self, page):
        super().__init__(page)
        self.cards = page.get_by_test_id("product-card")
        self.names = page.get_by_test_id("product-name")
        self.prices = page.get_by_test_id("product-price")
        self.sort_select = page.get_by_test_id("sort-select")

    def add_to_cart(self, product_id):
        self.page.get_by_test_id(f"add-to-cart-{product_id}").click()

    def add_button(self, product_id):
        return self.page.get_by_test_id(f"add-to-cart-{product_id}")

    def sort_by(self, value):
        with self.page.expect_navigation():
            self.sort_select.select_option(value)

    def product_names(self):
        return self.names.all_inner_texts()

    def product_prices(self):
        return [float(p) for p in self.prices.all_inner_texts()]
