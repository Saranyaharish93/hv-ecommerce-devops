from datetime import datetime, timezone, timedelta
from functools import wraps
from io import BytesIO
import os
import secrets
from pathlib import Path
from bson import ObjectId
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

bp = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login to continue", "warning")
            return redirect(url_for("main.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login to continue", "warning")
            return redirect(url_for("main.login"))
        if session.get("role") != "admin":
            flash("Administrator access is required", "danger")
            return redirect(url_for("main.home"))
        return view(*args, **kwargs)
    return wrapped


def serialize_product(p):
    return {
        "id": str(p["_id"]),
        "name": p["name"],
        "description": p.get("description", ""),
        "price": p["price"],
        "stock": p.get("stock", 0),
        "image": p.get("image", ""),
        "category": p.get("category", "Featured"),
        "rating": p.get("rating", 4.7),
        "badge": p.get("badge", ""),
        "review_count": p.get("review_count", 0),
    }



def prepare_order(order):
    """Convert a MongoDB order into a template-safe view model."""
    order["id"] = str(order["_id"])
    safe_items = []
    for item in order.get("items", []):
        view_item = dict(item)
        product = None
        product_id = item.get("product_id")
        if product_id:
            try:
                product = current_app.db.products.find_one({"_id": ObjectId(product_id)})
            except Exception:
                product = None
        if product:
            view_item.setdefault("image", product.get("image", ""))
            view_item.setdefault("category", product.get("category", ""))
        view_item.setdefault("image", "")
        view_item.setdefault("category", "")
        view_item.setdefault("quantity", 1)
        view_item.setdefault("price", 0)
        view_item.setdefault("subtotal", view_item["price"] * view_item["quantity"])
        safe_items.append(view_item)
    order["order_items"] = safe_items
    order.setdefault("status", "CONFIRMED")
    order.setdefault("shipping", 0)
    order.setdefault("total", sum(i.get("subtotal", 0) for i in safe_items) + order["shipping"])
    return order


def get_cart_count():
    return sum(session.get("cart", {}).values())


def get_wishlist_count():
    if not session.get("user_id"):
        return 0
    return current_app.db.wishlists.count_documents({"user_id": session["user_id"]})


@bp.app_context_processor
def inject_global_values():
    return {
        "cart_count": get_cart_count(),
        "wishlist_count": get_wishlist_count(),
        "current_year": datetime.now().year,
        "logged_in_user": session.get("user_name"),
        "logged_in_role": session.get("role"),
    }


@bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("main.home"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        if not name or not email or not password:
            flash("All fields are required", "danger")
        elif len(password) < 6:
            flash("Password must contain at least 6 characters", "danger")
        elif password != confirm_password:
            flash("Passwords do not match", "danger")
        elif current_app.db.users.find_one({"email": email}):
            flash("An account already exists with this email", "warning")
        else:
            result = current_app.db.users.insert_one({
                "name": name, "email": email,
                "password_hash": generate_password_hash(password),
                "role": "customer", "created_at": datetime.now(timezone.utc)
            })
            session.clear()
            session.update(user_id=str(result.inserted_id), user_name=name, role="customer")
            flash("Welcome to Lumora! Your account is ready.", "success")
            return redirect(url_for("main.home"))
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("main.home"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = current_app.db.users.find_one({"email": email})
        if not user or not check_password_hash(user.get("password_hash", ""), password):
            flash("Invalid email or password", "danger")
        elif user.get("is_active", True) is False:
            flash("Your account is inactive. Please contact the administrator.", "danger")
        else:
            session.clear()
            session.update(user_id=str(user["_id"]), user_name=user["name"], role=user.get("role", "customer"))
            flash(f"Welcome back, {user['name']}!", "success")
            next_url = request.args.get("next", "")
            return redirect(next_url if next_url.startswith("/") else url_for("main.home"))
    return render_template("login.html")


@bp.get("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("main.home"))


@bp.get("/account")
@login_required
def account():
    user = current_app.db.users.find_one({"_id": ObjectId(session["user_id"])})
    recent_orders = list(current_app.db.orders.find({"user_id": session["user_id"]}).sort("created_at", -1).limit(3))
    recent_orders = [prepare_order(order) for order in recent_orders]
    return render_template("account.html", user=user, recent_orders=recent_orders)




@bp.route("/account/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = current_app.db.users.find_one({"_id": ObjectId(session["user_id"])})
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        if not name:
            flash("Name is required", "danger")
        else:
            current_app.db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"name": name, "phone": phone, "address": address, "updated_at": datetime.now(timezone.utc)}}
            )
            session["user_name"] = name
            flash("Profile updated successfully", "success")
            return redirect(url_for("main.account"))
    return render_template("edit_profile.html", user=user)


@bp.post("/orders/<order_id>/cancel")
@login_required
def cancel_order(order_id):
    try:
        oid = ObjectId(order_id)
    except Exception:
        flash("Invalid order number", "danger")
        return redirect(url_for("main.orders"))
    order = current_app.db.orders.find_one({"_id": oid, "user_id": session["user_id"]})
    if not order:
        flash("Order not found", "danger")
    elif order.get("status") not in {"CONFIRMED", "PACKED"}:
        flash("This order can no longer be cancelled", "warning")
    else:
        current_app.db.orders.update_one({"_id": oid}, {"$set": {"status": "CANCELLED", "updated_at": datetime.now(timezone.utc)}})
        for item in order.get("items", []):
            try:
                current_app.db.products.update_one({"_id": ObjectId(item["product_id"])}, {"$inc": {"stock": item.get("quantity", 1)}})
            except Exception:
                pass
        flash("Order cancelled and stock restored", "success")
    return redirect(url_for("main.order_view", order_id=order_id))


@bp.post("/orders/<order_id>/buy-again")
@login_required
def buy_again(order_id):
    try:
        order = current_app.db.orders.find_one({"_id": ObjectId(order_id), "user_id": session["user_id"]})
    except Exception:
        order = None
    if not order:
        flash("Order not found", "danger")
        return redirect(url_for("main.orders"))
    cart = session.get("cart", {})
    added = 0
    for item in order.get("items", []):
        product_id = item.get("product_id")
        try:
            product = current_app.db.products.find_one({"_id": ObjectId(product_id)})
        except Exception:
            product = None
        if product and product.get("stock", 0) > 0:
            requested = item.get("quantity", 1)
            cart[product_id] = min(cart.get(product_id, 0) + requested, product.get("stock", 0))
            added += 1
    session["cart"] = cart
    flash(f"{added} product(s) added to your bag", "success" if added else "warning")
    return redirect(url_for("main.cart"))


@bp.get("/orders")
@login_required
def orders():
    order_docs = list(current_app.db.orders.find({"user_id": session["user_id"]}).sort("created_at", -1))
    order_docs = [prepare_order(order) for order in order_docs]
    return render_template("orders.html", orders=order_docs)


@bp.get("/orders/<order_id>")
@login_required
def order_view(order_id):
    try:
        query = {"_id": ObjectId(order_id)}
    except Exception:
        flash("Invalid order number", "danger")
        return redirect(url_for("main.orders"))
    if session.get("role") != "admin":
        query["user_id"] = session["user_id"]
    order = current_app.db.orders.find_one(query)
    if not order:
        flash("Order not found", "danger")
        return redirect(url_for("main.orders"))
    order = prepare_order(order)
    return render_template("order_view.html", order=order)


@bp.get("/admin")
@admin_required
def admin_dashboard():
    stats = {
        "products": current_app.db.products.count_documents({}),
        "customers": current_app.db.users.count_documents({"role": "customer"}),
        "orders": current_app.db.orders.count_documents({}),
        "revenue": sum(order.get("total", 0) for order in current_app.db.orders.find({}, {"total": 1})),
    }
    recent_orders = list(current_app.db.orders.find().sort("created_at", -1).limit(8))
    for order in recent_orders:
        order["id"] = str(order["_id"])
    threshold = int(current_app.config.get("LOW_STOCK_THRESHOLD", 10))
    low_stock = list(current_app.db.products.find({"stock": {"$lte": threshold}}).sort("stock", 1).limit(10))
    monthly = {}
    for order in current_app.db.orders.find({}, {"created_at": 1, "total": 1, "status": 1}):
        if order.get("status") == "CANCELLED":
            continue
        created = order.get("created_at") or datetime.now(timezone.utc)
        key = created.strftime("%b")
        monthly[key] = monthly.get(key, 0) + float(order.get("total", 0))
    revenue_chart = [{"label": k, "value": v} for k, v in list(monthly.items())[-6:]]
    return render_template("admin_dashboard.html", stats=stats, recent_orders=recent_orders, low_stock=low_stock, revenue_chart=revenue_chart, low_stock_threshold=threshold)


@bp.get("/admin/orders")
@admin_required
def admin_orders():
    status = request.args.get("status", "").strip().upper()
    query = {"status": status} if status else {}
    order_docs = list(current_app.db.orders.find(query).sort("created_at", -1))
    for order in order_docs:
        order["id"] = str(order["_id"])
    return render_template("admin_orders.html", orders=order_docs, selected_status=status)


@bp.post("/admin/orders/<order_id>/status")
@admin_required
def update_order_status(order_id):
    allowed = {"CONFIRMED", "PACKED", "SHIPPED", "DELIVERED", "CANCELLED"}
    status = request.form.get("status", "").upper()
    if status not in allowed:
        flash("Invalid order status", "danger")
    else:
        try:
            current_app.db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}})
            flash("Order status updated", "success")
        except Exception:
            flash("Unable to update order", "danger")
    return redirect(request.referrer or url_for("main.admin_orders"))


def _product_form_values():
    """Validate and normalize values used by admin product forms."""
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    image = request.form.get("image", "").strip()
    uploaded = request.files.get("image_file")
    if uploaded and uploaded.filename:
        ext = Path(uploaded.filename).suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            return None, "Upload a JPG, PNG, WEBP or GIF image"
        filename = f"{secrets.token_hex(8)}{ext}"
        upload_dir = Path(current_app.root_path) / "static" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        uploaded.save(upload_dir / secure_filename(filename))
        image = url_for("static", filename=f"uploads/{filename}")
    badge = request.form.get("badge", "").strip()
    try:
        price = float(request.form.get("price", "0"))
        stock = int(request.form.get("stock", "0"))
        rating = float(request.form.get("rating", "4.5"))
    except ValueError:
        return None, "Price, stock and rating must be valid numbers"
    if not name or not description or not category:
        return None, "Name, description and category are required"
    if price < 0 or stock < 0:
        return None, "Price and stock cannot be negative"
    if not 0 <= rating <= 5:
        return None, "Rating must be between 0 and 5"
    return {
        "name": name,
        "description": description,
        "category": category,
        "image": image,
        "badge": badge,
        "price": price,
        "stock": stock,
        "rating": rating,
        "updated_at": datetime.now(timezone.utc),
    }, None


@bp.get("/admin/products")
@admin_required
def admin_products():
    search = request.args.get("q", "").strip()
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"category": {"$regex": search, "$options": "i"}},
        ]
    products = [serialize_product(product) for product in current_app.db.products.find(query).sort("name", 1)]
    return render_template("admin_products.html", products=products, search=search)


@bp.route("/admin/products/new", methods=["GET", "POST"])
@admin_required
def admin_product_new():
    if request.method == "POST":
        values, error = _product_form_values()
        if error:
            flash(error, "danger")
        else:
            values["created_at"] = datetime.now(timezone.utc)
            current_app.db.products.insert_one(values)
            flash("Product added successfully", "success")
            return redirect(url_for("main.admin_products"))
    return render_template("admin_product_form.html", product=None, page_title="Add product")


@bp.route("/admin/products/<product_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_product_edit(product_id):
    try:
        oid = ObjectId(product_id)
    except Exception:
        flash("Invalid product number", "danger")
        return redirect(url_for("main.admin_products"))
    product = current_app.db.products.find_one({"_id": oid})
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for("main.admin_products"))
    if request.method == "POST":
        values, error = _product_form_values()
        if error:
            flash(error, "danger")
        else:
            current_app.db.products.update_one({"_id": oid}, {"$set": values})
            flash("Product updated successfully", "success")
            return redirect(url_for("main.admin_products"))
    return render_template("admin_product_form.html", product=product, page_title="Edit product")


@bp.post("/admin/products/<product_id>/delete")
@admin_required
def admin_product_delete(product_id):
    try:
        result = current_app.db.products.delete_one({"_id": ObjectId(product_id)})
    except Exception:
        result = None
    if result and result.deleted_count:
        flash("Product deleted from the catalogue", "success")
    else:
        flash("Unable to delete product", "danger")
    return redirect(url_for("main.admin_products"))


@bp.get("/admin/customers")
@admin_required
def admin_customers():
    search = request.args.get("q", "").strip()
    query = {"role": "customer"}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
        ]
    customers = list(current_app.db.users.find(query).sort("created_at", -1))
    rows = []
    for customer in customers:
        user_id = str(customer["_id"])
        orders = list(current_app.db.orders.find({"user_id": user_id}, {"total": 1}))
        rows.append({
            **customer,
            "id": user_id,
            "order_count": len(orders),
            "spent": sum(order.get("total", 0) for order in orders),
        })
    return render_template("admin_customers.html", customers=rows, search=search)


@bp.get("/admin/customers/<customer_id>")
@admin_required
def admin_customer_view(customer_id):
    try:
        customer = current_app.db.users.find_one({"_id": ObjectId(customer_id), "role": "customer"})
    except Exception:
        customer = None
    if not customer:
        flash("Customer not found", "danger")
        return redirect(url_for("main.admin_customers"))
    orders = [prepare_order(order) for order in current_app.db.orders.find({"user_id": customer_id}).sort("created_at", -1)]
    return render_template("admin_customer_view.html", customer=customer, customer_id=customer_id, orders=orders)


@bp.post("/admin/customers/<customer_id>/toggle")
@admin_required
def admin_customer_toggle(customer_id):
    try:
        oid = ObjectId(customer_id)
        customer = current_app.db.users.find_one({"_id": oid, "role": "customer"})
    except Exception:
        customer = None
    if not customer:
        flash("Customer not found", "danger")
    else:
        new_status = not customer.get("is_active", True)
        current_app.db.users.update_one({"_id": oid}, {"$set": {"is_active": new_status, "updated_at": datetime.now(timezone.utc)}})
        flash("Customer account activated" if new_status else "Customer account deactivated", "success")
    return redirect(request.referrer or url_for("main.admin_customers"))


@bp.get("/wishlist")
@login_required
def wishlist():
    records = list(current_app.db.wishlists.find({"user_id": session["user_id"]}).sort("created_at", -1))
    products = []
    for record in records:
        try:
            product = current_app.db.products.find_one({"_id": ObjectId(record["product_id"])})
        except Exception:
            product = None
        if product:
            products.append(serialize_product(product))
    return render_template("wishlist.html", products=products)


@bp.post("/wishlist/toggle/<product_id>")
@login_required
def toggle_wishlist(product_id):
    try:
        product = current_app.db.products.find_one({"_id": ObjectId(product_id)})
    except Exception:
        product = None
    if not product:
        flash("Product not found", "danger")
        return redirect(request.referrer or url_for("main.shop"))
    query = {"user_id": session["user_id"], "product_id": product_id}
    existing = current_app.db.wishlists.find_one(query)
    if existing:
        current_app.db.wishlists.delete_one({"_id": existing["_id"]})
        flash("Removed from wishlist", "info")
    else:
        current_app.db.wishlists.insert_one({**query, "created_at": datetime.now(timezone.utc)})
        flash("Added to wishlist", "success")
    return redirect(request.referrer or url_for("main.wishlist"))


@bp.post("/wishlist/<product_id>/move-to-cart")
@login_required
def wishlist_to_cart(product_id):
    try:
        product = current_app.db.products.find_one({"_id": ObjectId(product_id)})
    except Exception:
        product = None
    if not product or product.get("stock", 0) < 1:
        flash("This product is currently unavailable", "warning")
        return redirect(url_for("main.wishlist"))
    cart = session.get("cart", {})
    cart[product_id] = min(cart.get(product_id, 0) + 1, product.get("stock", 1))
    session["cart"] = cart
    current_app.db.wishlists.delete_one({"user_id": session["user_id"], "product_id": product_id})
    flash("Product moved to your bag", "success")
    return redirect(url_for("main.wishlist"))


@bp.get("/health")
def health():
    current_app.db.command("ping")
    return {"status": "UP", "service": "hv-ecommerce"}, 200


@bp.get("/")
def home():
    products = [serialize_product(p) for p in current_app.db.products.find().limit(8)]
    categories = list(current_app.db.products.distinct("category"))
    return render_template("index.html", products=products, categories=categories)


@bp.get("/shop")
def shop():
    selected_category = request.args.get("category", "").strip()
    search = request.args.get("q", "").strip()
    query = {}
    if selected_category:
        query["category"] = selected_category
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"category": {"$regex": search, "$options": "i"}},
        ]
    products = [serialize_product(p) for p in current_app.db.products.find(query).sort("name", 1)]
    categories = sorted(current_app.db.products.distinct("category"))
    return render_template("shop.html", products=products, categories=categories,
                           selected_category=selected_category, search=search)


@bp.get("/product/<product_id>")
def product_detail(product_id):
    try:
        product = current_app.db.products.find_one({"_id": ObjectId(product_id)})
    except Exception:
        product = None
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for("main.shop"))
    related = [serialize_product(p) for p in current_app.db.products.find({
        "category": product.get("category"), "_id": {"$ne": product["_id"]}
    }).limit(3)]
    reviews = list(current_app.db.reviews.find({"product_id": product_id}).sort("created_at", -1))
    return render_template("product_detail.html", product=serialize_product(product), related=related, reviews=reviews)


@bp.get("/categories")
def categories():
    category_cards = []
    for category in sorted(current_app.db.products.distinct("category")):
        sample = current_app.db.products.find_one({"category": category})
        category_cards.append({
            "name": category,
            "count": current_app.db.products.count_documents({"category": category}),
            "image": sample.get("image", "") if sample else "",
        })
    return render_template("categories.html", categories=category_cards)


@bp.get("/about")
def about():
    return render_template("about.html")


@bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Please complete all fields", "danger")
        else:
            current_app.db.messages.insert_one({
                "name": name, "email": email, "message": message,
                "created_at": datetime.now(timezone.utc)
            })
            flash("Thanks! Your message has been received.", "success")
            return redirect(url_for("main.contact"))
    return render_template("contact.html")


@bp.route("/track-order", methods=["GET", "POST"])
def track_order():
    order = None
    searched = False
    if request.method == "POST":
        searched = True
        order_id = request.form.get("order_id", "").strip()
        email = request.form.get("email", "").strip()
        try:
            order_doc = current_app.db.orders.find_one({"_id": ObjectId(order_id), "email": email})
        except Exception:
            order_doc = None
        if order_doc:
            order = {**order_doc, "id": str(order_doc["_id"])}
    return render_template("track_order.html", order=order, searched=searched)


@bp.get("/api/products")
def api_products():
    return jsonify([serialize_product(p) for p in current_app.db.products.find()])


@bp.post("/cart/add/<product_id>")
def add_to_cart(product_id):
    try:
        product = current_app.db.products.find_one({"_id": ObjectId(product_id)})
    except Exception:
        product = None
    if not product:
        return {"error": "Product not found"}, 404
    quantity = max(1, int(request.form.get("quantity", 1)))
    cart = session.get("cart", {})
    cart[product_id] = min(cart.get(product_id, 0) + quantity, product.get("stock", 1))
    session["cart"] = cart
    flash(f"{product['name']} added to your bag", "success")
    return redirect(request.referrer or url_for("main.shop"))


@bp.get("/cart")
def cart():
    raw_cart = session.get("cart", {})
    items, total = [], 0
    for product_id, quantity in raw_cart.items():
        try:
            p = current_app.db.products.find_one({"_id": ObjectId(product_id)})
        except Exception:
            p = None
        if p:
            subtotal = p["price"] * quantity
            total += subtotal
            items.append({**serialize_product(p), "quantity": quantity, "subtotal": subtotal})
    shipping = 0 if total >= 3000 or total == 0 else 149
    return render_template("cart.html", items=items, total=total, shipping=shipping, grand_total=total + shipping)


@bp.post("/cart/update/<product_id>")
def update_cart(product_id):
    quantity = max(0, int(request.form.get("quantity", 1)))
    cart = session.get("cart", {})
    if quantity == 0:
        cart.pop(product_id, None)
    elif product_id in cart:
        cart[product_id] = quantity
    session["cart"] = cart
    return redirect(url_for("main.cart"))


@bp.post("/cart/remove/<product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(product_id, None)
    session["cart"] = cart
    flash("Item removed from your bag", "info")
    return redirect(url_for("main.cart"))


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    raw_cart = session.get("cart", {})
    if not raw_cart:
        flash("Your bag is empty", "warning")
        return redirect(url_for("main.cart"))

    user = current_app.db.users.find_one({"_id": ObjectId(session["user_id"])})
    items, subtotal = [], 0
    for product_id, quantity in raw_cart.items():
        try:
            product = current_app.db.products.find_one({"_id": ObjectId(product_id)})
        except Exception:
            product = None
        if not product or product.get("stock", 0) < quantity:
            flash("One or more products are unavailable. Please review your bag.", "danger")
            return redirect(url_for("main.cart"))
        item_total = product["price"] * quantity
        subtotal += item_total
        items.append({**serialize_product(product), "quantity": quantity, "subtotal": item_total})

    shipping = 0 if subtotal >= 3000 else 149
    grand_total = subtotal + shipping
    if request.method == "GET":
        return render_template(
            "checkout.html", user=user, items=items, subtotal=subtotal,
            shipping=shipping, grand_total=grand_total
        )

    customer_name = request.form.get("customer_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()
    city = request.form.get("city", "").strip()
    state = request.form.get("state", "").strip()
    postal_code = request.form.get("postal_code", "").strip()
    payment_method = request.form.get("payment_method", "COD").strip().upper()
    allowed_payments = {"COD", "UPI", "CARD"}
    if not all([customer_name, email, phone, address, city, state, postal_code]):
        flash("Please complete all delivery details", "danger")
        return render_template("checkout.html", user=user, items=items, subtotal=subtotal, shipping=shipping, grand_total=grand_total)
    if payment_method not in allowed_payments:
        flash("Please choose a valid payment method", "danger")
        return redirect(url_for("main.checkout"))

    order_items = [
        {
            "product_id": item["id"], "name": item["name"], "quantity": item["quantity"],
            "price": item["price"], "subtotal": item["subtotal"], "image": item["image"],
            "category": item["category"],
        }
        for item in items
    ]
    now = datetime.now(timezone.utc)
    order = {
        "customer_name": customer_name, "email": email, "phone": phone,
        "address": address, "city": city, "state": state, "postal_code": postal_code,
        "payment_method": payment_method, "payment_status": "PENDING" if payment_method == "COD" else "PAID (DEMO)",
        "user_id": session["user_id"], "items": order_items,
        "subtotal": subtotal, "shipping": shipping, "total": grand_total,
        "status": "CONFIRMED", "created_at": now,
        "estimated_delivery": now + timedelta(days=5),
    }
    result = current_app.db.orders.insert_one(order)
    for item in order_items:
        current_app.db.products.update_one(
            {"_id": ObjectId(item["product_id"])}, {"$inc": {"stock": -item["quantity"]}}
        )
    current_app.db.users.update_one(
        {"_id": ObjectId(session["user_id"])},
        {"$set": {"name": customer_name, "phone": phone, "address": address,
                  "city": city, "state": state, "postal_code": postal_code, "updated_at": now}}
    )
    session["cart"] = {}
    email_record = {
        "to": email, "subject": f"Lumora order #{str(result.inserted_id)[-8:].upper()} confirmed",
        "order_id": str(result.inserted_id), "status": "SIMULATED_SENT", "created_at": now
    }
    current_app.db.email_outbox.insert_one(email_record)
    log_dir = Path(current_app.root_path).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    with (log_dir / "order_emails.log").open("a", encoding="utf-8") as fh:
        fh.write(f"{now.isoformat()} | TO={email} | ORDER={result.inserted_id} | TOTAL={grand_total} | SIMULATED_SENT\n")
    return render_template("success.html", order_id=str(result.inserted_id), total=grand_total)


@bp.get("/orders/<order_id>/invoice")
@login_required
def download_invoice(order_id):
    try:
        query = {"_id": ObjectId(order_id)}
    except Exception:
        flash("Invalid order number", "danger")
        return redirect(url_for("main.orders"))
    if session.get("role") != "admin":
        query["user_id"] = session["user_id"]
    order = current_app.db.orders.find_one(query)
    if not order:
        flash("Order not found", "danger")
        return redirect(url_for("main.orders"))
    order = prepare_order(order)

    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Brand", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=23, textColor=colors.HexColor("#7157ff"), spaceAfter=3))
    story = [
        Paragraph("LUMORA", styles["Brand"]),
        Paragraph("Tax Invoice / Order Receipt", styles["Heading2"]),
        Spacer(1, 7*mm),
        Paragraph(f"<b>Invoice:</b> LUM-{order['id'][-8:].upper()}", styles["BodyText"]),
        Paragraph(f"<b>Order date:</b> {order.get('created_at').strftime('%d %B %Y') if order.get('created_at') else '-'}", styles["BodyText"]),
        Paragraph(f"<b>Status:</b> {order.get('status', 'CONFIRMED')}", styles["BodyText"]),
        Spacer(1, 5*mm),
        Paragraph("<b>Bill to / Deliver to</b>", styles["Heading3"]),
        Paragraph(f"{order.get('customer_name','')}<br/>{order.get('email','')}<br/>{order.get('phone','')}<br/>{order.get('address','')}, {order.get('city','')}<br/>{order.get('state','')} - {order.get('postal_code','')}", styles["BodyText"]),
        Spacer(1, 6*mm),
    ]
    table_data = [["Product", "Qty", "Unit price", "Amount"]]
    for item in order["order_items"]:
        table_data.append([item.get("name", "Product"), str(item.get("quantity", 1)), f"INR {item.get('price',0):,.0f}", f"INR {item.get('subtotal',0):,.0f}"])
    table_data.extend([
        ["", "", "Subtotal", f"INR {order.get('total',0)-order.get('shipping',0):,.0f}"],
        ["", "", "Shipping", "FREE" if order.get("shipping",0) == 0 else f"INR {order.get('shipping',0):,.0f}"],
        ["", "", "Grand total", f"INR {order.get('total',0):,.0f}"],
    ])
    table = Table(table_data, colWidths=[92*mm, 18*mm, 30*mm, 32*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17151c")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#d7d1c8")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#c8ff45")),
        ("FONTNAME", (2,-1), (-1,-1), "Helvetica-Bold"),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.extend([table, Spacer(1, 7*mm), Paragraph(f"Payment: {order.get('payment_method','Not recorded')} · {order.get('payment_status','')}", styles["BodyText"]), Paragraph("Thank you for shopping with Lumora.", styles["BodyText"])])
    doc.build(story)
    output.seek(0)
    return send_file(output, mimetype="application/pdf", as_attachment=True, download_name=f"Lumora-Invoice-{order['id'][-8:].upper()}.pdf")


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    reset_link = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = current_app.db.users.find_one({"email": email})
        if user:
            token = secrets.token_urlsafe(24)
            current_app.db.password_resets.delete_many({"user_id": str(user["_id"])})
            current_app.db.password_resets.insert_one({
                "user_id": str(user["_id"]), "token": token,
                "expires_at": datetime.now(timezone.utc) + timedelta(minutes=30),
                "created_at": datetime.now(timezone.utc)
            })
            reset_link = url_for("main.reset_password", token=token, _external=True)
            current_app.db.email_outbox.insert_one({
                "to": email, "subject": "Lumora password reset", "reset_link": reset_link,
                "status": "SIMULATED_SENT", "created_at": datetime.now(timezone.utc)
            })
        flash("If that email is registered, a simulated reset email has been generated.", "info")
    return render_template("forgot_password.html", reset_link=reset_link)


@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    record = current_app.db.password_resets.find_one({"token": token})
    now = datetime.now(timezone.utc)
    if not record or record.get("expires_at") < now:
        flash("This reset link is invalid or expired", "danger")
        return redirect(url_for("main.forgot_password"))
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if len(password) < 6:
            flash("Password must contain at least 6 characters", "danger")
        elif password != confirm:
            flash("Passwords do not match", "danger")
        else:
            current_app.db.users.update_one(
                {"_id": ObjectId(record["user_id"])},
                {"$set": {"password_hash": generate_password_hash(password), "updated_at": now}}
            )
            current_app.db.password_resets.delete_many({"user_id": record["user_id"]})
            flash("Password updated. You can now login.", "success")
            return redirect(url_for("main.login"))
    return render_template("reset_password.html", token=token)


@bp.post("/product/<product_id>/reviews")
@login_required
def add_review(product_id):
    if session.get("role") == "admin":
        flash("Administrators cannot review products", "warning")
        return redirect(url_for("main.product_detail", product_id=product_id))
    try:
        product = current_app.db.products.find_one({"_id": ObjectId(product_id)})
        rating = int(request.form.get("rating", "0"))
    except Exception:
        product, rating = None, 0
    comment = request.form.get("comment", "").strip()
    purchased = current_app.db.orders.find_one({
        "user_id": session["user_id"], "items.product_id": product_id,
        "status": {"$in": ["CONFIRMED", "PACKED", "SHIPPED", "DELIVERED"]}
    })
    if not product:
        flash("Product not found", "danger")
    elif not purchased:
        flash("Only customers who purchased this product can review it", "warning")
    elif rating not in range(1, 6) or len(comment) < 3:
        flash("Choose 1–5 stars and enter a review", "danger")
    else:
        current_app.db.reviews.update_one(
            {"product_id": product_id, "user_id": session["user_id"]},
            {"$set": {"rating": rating, "comment": comment, "user_name": session.get("user_name"), "created_at": datetime.now(timezone.utc)}},
            upsert=True
        )
        reviews = list(current_app.db.reviews.find({"product_id": product_id}))
        avg = sum(x["rating"] for x in reviews) / len(reviews)
        current_app.db.products.update_one({"_id": ObjectId(product_id)}, {"$set": {"rating": round(avg, 1), "review_count": len(reviews)}})
        flash("Thanks for sharing your review", "success")
    return redirect(url_for("main.product_detail", product_id=product_id))


@bp.get("/admin/reports")
@admin_required
def admin_reports():
    product_sales = {}
    category_sales = {}
    for order in current_app.db.orders.find({"status": {"$ne": "CANCELLED"}}):
        for item in order.get("items", []):
            name = item.get("name", "Unknown")
            category = item.get("category", "Other")
            qty = int(item.get("quantity", 0))
            revenue = float(item.get("subtotal", 0))
            row = product_sales.setdefault(name, {"name": name, "quantity": 0, "revenue": 0})
            row["quantity"] += qty
            row["revenue"] += revenue
            crow = category_sales.setdefault(category, {"category": category, "quantity": 0, "revenue": 0})
            crow["quantity"] += qty
            crow["revenue"] += revenue
    products = sorted(product_sales.values(), key=lambda x: x["revenue"], reverse=True)
    categories = sorted(category_sales.values(), key=lambda x: x["revenue"], reverse=True)
    threshold = int(current_app.config.get("LOW_STOCK_THRESHOLD", 10))
    low_stock = list(current_app.db.products.find({"stock": {"$lte": threshold}}).sort("stock", 1))
    return render_template("admin_reports.html", products=products, categories=categories, low_stock=low_stock, threshold=threshold)


@bp.get("/admin/email-outbox")
@admin_required
def admin_email_outbox():
    emails = list(current_app.db.email_outbox.find().sort("created_at", -1).limit(100))
    return render_template("admin_email_outbox.html", emails=emails)
