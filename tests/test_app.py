import mongomock
from app import create_app


def app_client():
    mongo = mongomock.MongoClient("mongodb://localhost/ecommerce_test")
    app = create_app({"TESTING": True, "SECRET_KEY": "test", "MONGO_URI": "mongodb://localhost/ecommerce_test", "MONGO_CLIENT": mongo})
    return app.test_client()


def test_health():
    client = app_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "UP"


def test_products_api_has_seed_data():
    client = app_client()
    response = client.get("/api/products")
    assert response.status_code == 200
    assert len(response.json) >= 4
