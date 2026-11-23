import pytest

from tests.data.test_data import INVALID_LOGINS, LOCKED_USER, VALID_USER

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_login_with_valid_credentials_returns_token(api):
    r = api.login(**VALID_USER)
    assert r.status_code == 200
    assert len(r.json()["token"]) == 32


def test_each_login_issues_a_unique_token(api):
    t1 = api.login(**VALID_USER).json()["token"]
    t2 = api.login(**VALID_USER).json()["token"]
    assert t1 != t2


@pytest.mark.parametrize("username,password,expected", INVALID_LOGINS)
def test_login_with_invalid_credentials_is_rejected(api, username, password, expected):
    r = api.login(username, password)
    assert r.status_code in (400, 401)
    assert r.json()["error"] == expected
    assert "token" not in r.json()


def test_locked_user_gets_403(api):
    r = api.login(**LOCKED_USER)
    assert r.status_code == 403
    assert r.json()["error"] == "This account has been locked"


def test_login_with_malformed_body_returns_400(api):
    r = api.s.post(f"{api.base}/login", data="not-json", headers={"Content-Type": "application/json"})
    assert r.status_code == 400


@pytest.mark.parametrize("header", [None, "Bearer invalid-token", "Token abc", "Bearer "])
def test_cart_requires_valid_bearer_token(api, header):
    if header:
        api.s.headers["Authorization"] = header
    r = api.cart()
    assert r.status_code == 401
    assert r.json() == {"error": "Unauthorized"}
