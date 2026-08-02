import os
from flask import Flask
from pymongo import MongoClient
from werkzeug.security import generate_password_hash


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-change-me"),
        MONGO_URI=os.getenv("MONGO_URI", "mongodb://mongo:27017/ecommerce"),
        TESTING=False,
        LOW_STOCK_THRESHOLD=int(os.getenv("LOW_STOCK_THRESHOLD", "10")),
    )
    if test_config:
        app.config.update(test_config)

    mongo_client = app.config.get("MONGO_CLIENT") or MongoClient(app.config["MONGO_URI"])
    app.mongo_client = mongo_client
    app.db = mongo_client.get_database()

    from .routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        seed_products(app.db)
        seed_admin(app.db)
    return app


def seed_products(db):
    if db.products.count_documents({}) == 0:
        db.products.insert_many([
            {"name":"Aurora Noise-Cancelling Headphones","description":"Immersive wireless sound with adaptive noise cancellation and 35-hour battery.","price":7499,"stock":20,"category":"Audio","rating":4.9,"badge":"Best Seller","image":"https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80"},
            {"name":"Nova AMOLED Smartwatch","description":"Premium health tracking, GPS and vivid always-on AMOLED display.","price":8999,"stock":15,"category":"Wearables","rating":4.8,"badge":"New","image":"https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80"},
            {"name":"Drift Urban Backpack","description":"Water-resistant minimalist backpack with padded laptop compartment.","price":2999,"stock":30,"category":"Lifestyle","rating":4.7,"badge":"Eco Pick","image":"https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80"},
            {"name":"Pulse Mechanical Keyboard","description":"Hot-swappable mechanical switches, RGB glow and precision controls.","price":5499,"stock":12,"category":"Workspace","rating":4.8,"badge":"Creator Pick","image":"https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=80"},
            {"name":"Halo Desk Lamp","description":"Sculptural LED lamp with touch dimming and adjustable colour temperature.","price":3499,"stock":18,"category":"Workspace","rating":4.6,"badge":"","image":"https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=80"},
            {"name":"Orbit Portable Speaker","description":"Compact waterproof speaker with rich bass and 18-hour playback.","price":4299,"stock":22,"category":"Audio","rating":4.7,"badge":"Trending","image":"https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=80"},
            {"name":"Lumen Instant Camera","description":"Retro-inspired instant camera for vibrant memories and creative prints.","price":6799,"stock":9,"category":"Creative","rating":4.6,"badge":"Limited","image":"https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=900&q=80"},
            {"name":"Cloud Ceramic Set","description":"Hand-finished ceramic mug set designed for calm morning rituals.","price":1899,"stock":25,"category":"Lifestyle","rating":4.9,"badge":"Handmade","image":"https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=80"},
        ])


def seed_admin(db):
    admin_email = os.getenv("ADMIN_EMAIL", "admin@lumora.local").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin@123")
    if not db.users.find_one({"email": admin_email}):
        db.users.insert_one({
            "name": "Lumora Admin",
            "email": admin_email,
            "password_hash": generate_password_hash(admin_password),
            "role": "admin",
        })
