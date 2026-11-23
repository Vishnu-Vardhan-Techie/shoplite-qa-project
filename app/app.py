"""
ShopLite - a small e-commerce app used as the Application Under Test (AUT).

It intentionally contains a handful of seeded defects (see docs/bug-reports.md)
so the QA work in this repository has real bugs to find, report and track.
Search for "SEEDED BUG" to see where they live.
"""
import re
import secrets
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "shoplite-demo-secret"

USERS = {
    "standard_user": {"password": "secret123", "locked": False},
    "locked_user": {"password": "secret123", "locked": True},
}

PRODUCTS = [
    {"id": 1, "name": "Canvas Backpack", "price": 49.99, "stock": 12},
    {"id": 2, "name": "Steel Water Bottle", "price": 9.99, "stock": 40},
    {"id": 3, "name": "Wireless Mouse", "price": 15.99, "stock": 25},
    {"id": 4, "name": "Mechanical Keyboard", "price": 129.00, "stock": 5},
    {"id": 5, "name": "Desk Lamp", "price": 24.50, "stock": 0},
]

API_TOKENS = {}   # token -> username
API_CARTS = {}    # username -> {product_id: qty}


def find_product(pid):
    return next((p for p in PRODUCTS if p["id"] == pid), None)


def authenticate(username, password):
    """Returns (ok, error_message)."""
    if not username or not password:
        return False, "Username and password are required"
    user = USERS.get(username)
    if not user or user["password"] != password:
        return False, "Invalid username or password"
    if user["locked"]:
        return False, "This account has been locked"
    return True, None


def sort_products(products, sort):
    if sort == "name_asc":
        return sorted(products, key=lambda p: p["name"])
    if sort == "name_desc":
        return sorted(products, key=lambda p: p["name"], reverse=True)
    if sort == "price_asc":
        return sorted(products, key=lambda p: p["price"])
    if sort == "price_desc":
        # SEEDED BUG (BUG-001): sorts by the price *string*, not the number.
        return sorted(products, key=lambda p: str(p["price"]), reverse=True)
    return products


def cart_lines(cart):
    lines = []
    for pid, qty in cart.items():
        p = find_product(int(pid))
        if p:
            lines.append({**p, "qty": qty, "line_total": round(p["price"] * qty, 2)})
    return lines


def cart_total(lines):
    return round(sum(l["line_total"] for l in lines), 2)


# ----------------------------------------------------------------- Web UI ---

@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        ok, error = authenticate(username, request.form.get("password", ""))
        if ok:
            session.clear()
            session["user"] = username
            session["cart"] = {}
            session["badge"] = 0
            return redirect(url_for("products"))
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def require_login():
    return "user" in session


@app.route("/products")
def products():
    if not require_login():
        return redirect(url_for("login"))
    sort = request.args.get("sort", "name_asc")
    return render_template("products.html", products=sort_products(PRODUCTS, sort),
                           sort=sort, badge=session.get("badge", 0))


@app.route("/cart/add/<int:pid>", methods=["POST"])
def cart_add(pid):
    if not require_login():
        return redirect(url_for("login"))
    p = find_product(pid)
    if p and p["stock"] > 0:
        cart = session.get("cart", {})
        cart[str(pid)] = cart.get(str(pid), 0) + 1
        session["cart"] = cart
        session["badge"] = session.get("badge", 0) + 1
    return redirect(request.referrer or url_for("products"))


@app.route("/cart/remove/<int:pid>", methods=["POST"])
def cart_remove(pid):
    if not require_login():
        return redirect(url_for("login"))
    cart = session.get("cart", {})
    cart.pop(str(pid), None)
    session["cart"] = cart
    # SEEDED BUG (BUG-003): badge counter is never decremented on removal.
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    if not require_login():
        return redirect(url_for("login"))
    lines = cart_lines(session.get("cart", {}))
    return render_template("cart.html", lines=lines, total=cart_total(lines),
                           badge=session.get("badge", 0))


def validate_checkout(form):
    errors = {}
    name = form.get("full_name", "").strip()
    email = form.get("email", "").strip()
    pincode = form.get("pincode", "").strip()
    if not name:
        errors["full_name"] = "Full name is required"
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        errors["email"] = "Enter a valid email address"
    # SEEDED BUG (BUG-002): Indian PIN codes are exactly 6 digits, but 5 is accepted.
    if not re.fullmatch(r"\d{5,6}", pincode):
        errors["pincode"] = "Enter a valid 6-digit PIN code"
    return errors


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if not require_login():
        return redirect(url_for("login"))
    lines = cart_lines(session.get("cart", {}))
    if not lines:
        return redirect(url_for("cart"))
    errors, form = {}, {}
    if request.method == "POST":
        form = request.form
        errors = validate_checkout(form)
        if not errors:
            order_id = "ORD-" + secrets.token_hex(3).upper()
            total = cart_total(lines)
            session["cart"] = {}
            session["badge"] = 0
            return render_template("complete.html", order_id=order_id, total=total, badge=0)
    return render_template("checkout.html", lines=lines, total=cart_total(lines),
                           errors=errors, form=form, badge=session.get("badge", 0))


# ---------------------------------------------------------------- REST API ---

def api_user():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return API_TOKENS.get(auth[7:])
    return None


@app.post("/api/login")
def api_login():
    body = request.get_json(silent=True) or {}
    ok, error = authenticate(body.get("username"), body.get("password"))
    if not ok:
        status = 403 if error == "This account has been locked" else 401
        if error == "Username and password are required":
            status = 400
        return jsonify(error=error), status
    token = secrets.token_hex(16)
    API_TOKENS[token] = body["username"]
    API_CARTS.setdefault(body["username"], {})
    return jsonify(token=token), 200


@app.get("/api/products")
def api_products():
    return jsonify(sort_products(PRODUCTS, request.args.get("sort", ""))), 200


@app.get("/api/products/<int:pid>")
def api_product(pid):
    p = find_product(pid)
    if not p:
        # SEEDED BUG (BUG-004): should be 404, returns 200 with an empty body.
        return jsonify({}), 200
    return jsonify(p), 200


@app.get("/api/cart")
def api_cart_get():
    user = api_user()
    if not user:
        return jsonify(error="Unauthorized"), 401
    lines = cart_lines(API_CARTS[user])
    return jsonify(items=lines, total=cart_total(lines)), 200


@app.post("/api/cart")
def api_cart_add():
    user = api_user()
    if not user:
        return jsonify(error="Unauthorized"), 401
    body = request.get_json(silent=True) or {}
    pid, qty = body.get("product_id"), body.get("quantity", 1)
    if not isinstance(pid, int) or not isinstance(qty, int):
        return jsonify(error="product_id and quantity must be integers"), 400
    p = find_product(pid)
    if not p:
        return jsonify(error="Product not found"), 404
    if p["stock"] == 0:
        return jsonify(error="Product is out of stock"), 409
    # SEEDED BUG (BUG-005): no check for quantity <= 0 or quantity > stock.
    cart = API_CARTS[user]
    cart[pid] = cart.get(pid, 0) + qty
    lines = cart_lines(cart)
    return jsonify(items=lines, total=cart_total(lines)), 201


@app.delete("/api/cart/<int:pid>")
def api_cart_delete(pid):
    user = api_user()
    if not user:
        return jsonify(error="Unauthorized"), 401
    if pid not in API_CARTS[user]:
        return jsonify(error="Item not in cart"), 404
    del API_CARTS[user][pid]
    return "", 204


@app.post("/api/reset")
def api_reset():
    """Test hook: clears all API state so tests stay independent."""
    API_TOKENS.clear()
    API_CARTS.clear()
    return "", 204


if __name__ == "__main__":
    app.run(port=5000, debug=False)
