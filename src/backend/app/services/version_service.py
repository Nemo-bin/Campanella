from app.repositories.version_repository import get_python_version, get_flask_version, get_postgresql_version

def get_stack_versions(db):
    return {
        "python": get_python_version(),
        "flask": get_flask_version(),
        "postgresql": get_postgresql_version(db)
    }