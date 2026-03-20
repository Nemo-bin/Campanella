from flask import Flask, g
from flask_cors import CORS
import os
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db import init_db
from backend.app.middleware.auth_middleware import AuthMiddleware

def create_app():
    app = Flask(__name__)
    CORS(app)

    jwt_secret = os.environ.get("JWT_SECRET")
    if not jwt_secret:
        raise RuntimeError("JWT_SECRET not set")
    refresh_secret = os.environ.get("JWT_REFRESH_SECRET")
    if not refresh_secret:
        raise RuntimeError("JWT_REFRESH_SECRET not set")
    AuthMiddleware.init(jwt_secret, refresh_secret)

    init_db()

    @app.before_request
    def create_session():
        g.db = SessionLocal()

    @app.teardown_appcontext
    def close_session(exception=None):
        db = g.pop("db", None)
        if db is not None:
            if exception:
                db.rollback()
            db.close()

    from .routes import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)

    return app