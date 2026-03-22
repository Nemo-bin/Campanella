from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .health_routes import router as health_router

routers = [
    health_router,
    auth_router,
    user_router
]