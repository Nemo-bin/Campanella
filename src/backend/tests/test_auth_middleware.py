import pytest
import jwt
import datetime
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.middleware.auth_middleware import AuthMiddleware


# -------------------------------
# 1) Setup secrets for testing
# -------------------------------
@pytest.fixture(autouse=True)
def init_auth_middleware():
    AuthMiddleware.init(secret_key="test_secret", refresh_secret_key="refresh_secret")
    yield
    AuthMiddleware._secret = None
    AuthMiddleware._refresh_secret = None


# -------------------------------
# 2) Test create_jwt
# -------------------------------
def test_create_jwt_contains_user_id():
    token = AuthMiddleware.create_jwt(user_id=123)
    payload = jwt.decode(token, "test_secret", algorithms=["HS256"])

    assert payload["user_id"] == 123
    assert "exp" in payload
    assert "iat" in payload


def test_create_jwt_expiration():
    token = AuthMiddleware.create_jwt(user_id=1, expires_hours=1)
    payload = jwt.decode(token, "test_secret", algorithms=["HS256"])

    now = datetime.datetime.utcnow()
    exp = datetime.datetime.utcfromtimestamp(payload["exp"])
    delta = exp - now

    assert delta.total_seconds() > 0
    assert delta.total_seconds() <= 3600 + 5


# -------------------------------
# 3) Test create_refresh_token
# -------------------------------
def test_create_refresh_token_contains_jti_and_user_id():
    token = AuthMiddleware.create_refresh_token(user_id=42)
    payload = jwt.decode(token, "refresh_secret", algorithms=["HS256"])

    assert payload["user_id"] == 42
    assert "jti" in payload
    assert "exp" in payload
    assert "iat" in payload


def test_create_refresh_token_expiration():
    token = AuthMiddleware.create_refresh_token(user_id=1, expires_days=2)
    payload = jwt.decode(token, "refresh_secret", algorithms=["HS256"])

    now = datetime.datetime.utcnow()
    exp = datetime.datetime.utcfromtimestamp(payload["exp"])
    delta = exp - now

    assert delta.total_seconds() > 0
    assert delta.total_seconds() <= 2 * 24 * 3600 + 5


# -------------------------------
# 4) Test Auth dependency
# -------------------------------
def create_test_app():
    app = FastAPI()

    @app.get("/protected")
    def protected_route(current_user_id: int = Depends(AuthMiddleware.required)):
        return {"user_id": current_user_id}

    return app


def test_required_allows_valid_token():
    app = create_test_app()
    client = TestClient(app)

    token = AuthMiddleware.create_jwt(user_id=99)

    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == 99


def test_required_missing_token():
    app = create_test_app()
    client = TestClient(app)

    response = client.get("/protected")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing token"


def test_required_invalid_token():
    app = create_test_app()
    client = TestClient(app)

    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer invalidtoken"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"