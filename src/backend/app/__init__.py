from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.infrastructure.db import init_db
from app.middleware.auth_middleware import AuthMiddleware
from app.routes import routers


def create_app() -> FastAPI:
    app = FastAPI()

    jwt_secret = os.environ.get("JWT_SECRET")
    if not jwt_secret:
        raise RuntimeError("JWT_SECRET not set")

    refresh_secret = os.environ.get("JWT_REFRESH_SECRET")
    if not refresh_secret:
        raise RuntimeError("JWT_REFRESH_SECRET not set")

    AuthMiddleware.init(jwt_secret, refresh_secret)

    init_db()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for router in routers:
        app.include_router(router)

    return app

app = create_app()