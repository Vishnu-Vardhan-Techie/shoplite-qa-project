from .base_page import BasePage


class CheckoutPage(BasePage):
    path = "/checkout"

    def __init__(self, page):
        super().__init__(page)
        self.full_name = page.get_by_test_id("full-name")
        self.email = page.get_by_test_id("email")
        self.pincode = page.get_by_test_id("pincode")
        self.place_order_button = page.get_by_test_id("place-order")
        self.total = page.get_by_test_id("checkout-total")
        self.success = page.get_by_test_id("order-success")
        self.order_id = page.get_by_test_id("order-id")
        self.order_total = page.get_by_test_id("order-total")

    def error_for(self, field):
        return self.page.get_by_test_id(f"error-{field}")

    def place_order(self, full_name="", email="", pincode=""):
        self.full_name.fill(full_name)
        self.email.fill(email)
        self.pincode.fill(pincode)
        self.place_order_button.click()
