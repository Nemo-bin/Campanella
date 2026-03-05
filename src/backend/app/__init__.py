from flask import Flask, g
from flask_cors import CORS
from app.infrastructure.db.session import SessionLocal

def create_app():
    app = Flask(__name__)
    CORS(app)

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