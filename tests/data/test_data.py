"""Central test data, so test values live in one place (not hard-coded in tests)."""
VALID_USER = {"username": "standard_user", "password": "secret123"}
LOCKED_USER = {"username": "locked_user", "password": "secret123"}

INVALID_LOGINS = [
    # (username, password, expected error)  -- equivalence partitions for login
    ("standard_user", "wrong", "Invalid username or password"),
    ("unknown_user", "secret123", "Invalid username or password"),
    ("STANDARD_USER", "secret123", "Invalid username or password"),
    ("", "secret123", "Username and password are required"),
    ("standard_user", "", "Username and password are required"),
    ("", "", "Username and password are required"),
]

PRODUCT_COUNT = 5
IN_STOCK_ID, OUT_OF_STOCK_ID, MISSING_ID = 1, 5, 999

CHECKOUT_OK = {"full_name": "Priya Sharma", "email": "priya@example.com", "pincode": "600001"}

# Boundary-value analysis on the 6-digit PIN code field
INVALID_PINCODES = ["", "6000011", "60A001", "  "]
FIVE_DIGIT_PINCODE = "60000"  # BUG-002: wrongly accepted
