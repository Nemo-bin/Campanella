from .version_routes import version_bp
from .auth_routes import auth_bp
from .user_routes import users_bp

blueprints = [
    version_bp,
    auth_bp,
    users_bp
]