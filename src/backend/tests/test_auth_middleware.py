import pytest
import jwt
import datetime
from flask import Flask, request
from backend.app.middleware.auth_middleware import AuthMiddleware
from unittest.mock import patch

# -------------------------------
# 1) Setup secrets for testing
# -------------------------------
@pytest.fixture(autouse=True)
def init_auth_middleware():
    AuthMiddleware.init(secret_key="test_secret", refresh_secret_key="refresh_secret")
    yield
    # Reset after tests
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
    assert delta.total_seconds() <= 3600 + 5  # allow 5 seconds tolerance

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
    assert delta.total_seconds() <= 2*24*3600 + 5  # 2 days tolerance

# -------------------------------
# 4) Test @required decorator
# -------------------------------
def test_required_decorator_allows_valid_token():
    app = Flask(__name__)
    token = AuthMiddleware.create_jwt(user_id=99)

    @AuthMiddleware.required
    def protected_route(current_user_id):
        return current_user_id

    # Simulate request context with Authorization header
    with app.test_request_context(headers={"Authorization": f"Bearer {token}"}):
        result = protected_route()
        assert result == 99

def test_required_decorator_missing_token_raises():
    app = Flask(__name__)

    @AuthMiddleware.required
    def protected_route(current_user_id):
        return current_user_id

    with app.test_request_context(headers={}):
        with pytest.raises(Exception) as excinfo:
            protected_route()
        assert "Token missng" in str(excinfo.value)

def test_required_decorator_invalid_token_raises():
    app = Flask(__name__)

    @AuthMiddleware.required
    def protected_route(current_user_id):
        return current_user_id

    with app.test_request_context(headers={"Authorization": "Bearer invalidtoken"}):
        with pytest.raises(Exception) as excinfo:
            protected_route()
        assert "Invalid token" in str(excinfo.value)