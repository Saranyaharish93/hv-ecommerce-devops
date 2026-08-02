from app import create_app
from mongomock import MongoClient


def make_app():
    return create_app({"TESTING": True, "SECRET_KEY": "test", "MONGO_CLIENT": MongoClient("mongodb://localhost/test")})


def register_and_login(client, email="user@example.com"):
    return client.post("/register", data={"name":"User","email":email,"password":"secret1","confirm_password":"secret1"}, follow_redirects=True)


def test_forgot_password_creates_token():
    app = make_app(); client = app.test_client(); register_and_login(client); client.get("/logout")
    response = client.post("/forgot-password", data={"email":"user@example.com"}, follow_redirects=True)
    assert response.status_code == 200
    assert app.db.password_resets.count_documents({}) == 1
    assert app.db.email_outbox.count_documents({"subject":"Lumora password reset"}) == 1


def test_admin_reports_requires_admin():
    app = make_app(); client = app.test_client()
    response = client.get("/admin/reports")
    assert response.status_code == 302


def test_review_requires_purchase():
    app = make_app(); client = app.test_client(); register_and_login(client)
    product = app.db.products.find_one()
    response = client.post(f"/product/{product['_id']}/reviews", data={"rating":"5","comment":"Excellent"}, follow_redirects=True)
    assert b"Only customers who purchased" in response.data
    assert app.db.reviews.count_documents({}) == 0


def test_health_endpoint():
    app = make_app(); client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "UP"
