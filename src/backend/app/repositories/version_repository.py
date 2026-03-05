import sys
import flask
import psycopg2
from sqlalchemy import text

def get_python_version():
    return sys.version.split()[0]

def get_flask_version():
    return flask.__version__

def get_postgresql_version(db):
    result = db.execute(text("SELECT version();"))
    version_str = result.scalar()
    return version_str