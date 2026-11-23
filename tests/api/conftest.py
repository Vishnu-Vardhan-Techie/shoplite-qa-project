import pytest
import requests

from tests.data.test_data import VALID_USER


class ApiClient:
    """Thin wrapper over requests so tests read like the API contract."""

    def __init__(self, base_url):
        self.base = base_url + "/api"
        self.s = requests.Session()

    def login(self, username, password):
        return self.s.post(f"{self.base}/login", json={"username": username, "password": password})

    def authorize(self, token):
        self.s.headers["Authorization"] = f"Bearer {token}"

    def products(self, **params):
        return self.s.get(f"{self.base}/products", params=params)

    def product(self, pid):
        return self.s.get(f"{self.base}/products/{pid}")

    def cart(self):
        return self.s.get(f"{self.base}/cart")

    def add_to_cart(self, product_id, quantity=1):
        return self.s.post(f"{self.base}/cart", json={"product_id": product_id, "quantity": quantity})

    def remove_from_cart(self, pid):
        return self.s.delete(f"{self.base}/cart/{pid}")


@pytest.fixture(autouse=True)
def reset_state(base_url):
    requests.post(f"{base_url}/api/reset")


@pytest.fixture
def api(base_url):
    return ApiClient(base_url)


@pytest.fixture
def auth_api(api):
    token = api.login(**VALID_USER).json()["token"]
    api.authorize(token)
    return api
