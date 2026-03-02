from ..repositories.version_repository import get_python_version, get_flask_version, get_postgresql_version
from .. import get_db

def get_stack_versions():
    db = get_db()
    if db is None:
        raise RuntimeError("Database connection not available")

    return {
        "python": get_python_version(),
        "flask": get_flask_version(),
        "postgresql": get_postgresql_version(db)
    }