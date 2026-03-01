from flask import Flask, g
from flask_cors import CORS

import psycopg2

import os

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "appdb"),
            user=os.getenv("DB_USER", "appuser"),
            password=os.getenv("DB_PASSWORD", "password")
        )
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.teardown_appcontext(close_db)

    from .routes import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)

    return app