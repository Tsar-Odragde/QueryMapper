from flask import Flask
from .config import load_config
from .db import init_engine
from .models import Base
from .routes.oauth import oauth_bp
from .routes.meli import meli_bp

def create_app() -> Flask:
    app = Flask(__name__)
    load_config(app)              # sets secret key, etc.
    engine = init_engine()        # creates engine from DATABASE_URL

    # Create tables (ok for early dev; move to Alembic later)
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)

    # Register blueprints
    app.register_blueprint(oauth_bp)
    app.register_blueprint(meli_bp)

    @app.get("/")
    def health():
        return {"ok": True, "service": "QueryMapper OAuth bridge"}, 200

    return app
