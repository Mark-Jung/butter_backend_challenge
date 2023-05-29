from app import app
from db import db
from cache import cache

cache.init_app(app)
db.init_app(app)
with app.app_context():
    db.create_all()