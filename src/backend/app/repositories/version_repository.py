import sys
import flask
import psycopg2

def get_python_version():
    return sys.version.split()[0]

def get_flask_version():
    return flask.__version__

def get_postgresql_version(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        return cur.fetchone()[0]