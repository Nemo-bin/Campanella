import pytest
import jwt

from app.utils.jwt_utils import JWTManager


# -------------------------------
# 1) Reset JWTManager before tests
# -------------------------------
@pytest.fixture(autouse=True)
def reset_jwt_manager():
    JWTManager._secret = None
    JWTManager._refresh_secret = None
    yield
    JWTManager._secret = None
    JWTManager._refresh_secret = None


# -------------------------------
# 2) Test init
# -------------------------------
def test_init_sets_secrets():
    JWTManager.init("access_secret", "refresh_secret")

    assert JWTManager._secret == "access_secret"
    assert JWTManager._refresh_secret == "refresh_secret"


# -------------------------------
# 3) Access token tests
# -------------------------------
def test_create_access_token_success():
    JWTManager.init("access_secret")

    token = JWTManager.create_access_token(user_id=123)

    decoded = jwt.decode(token, "access_secret", algorithms=["HS256"])

    assert decoded["user_id"] == 123
    assert "exp" in decoded
    assert "iat" in decoded


def test_create_access_token_without_secret_raises():
    with pytest.raises(RuntimeError) as excinfo:
        JWTManager.create_access_token(user_id=1)

    assert "JWT secret not configured" in str(excinfo.value)


# -------------------------------
# 4) Refresh token tests
# -------------------------------
def test_create_refresh_token_success():
    JWTManager.init("access_secret", "refresh_secret")

    token = JWTManager.create_refresh_token(user_id=999)

    decoded = jwt.decode(token, "refresh_secret", algorithms=["HS256"])

    assert decoded["user_id"] == 999
    assert "jti" in decoded
    assert "exp" in decoded
    assert "iat" in decoded


def test_create_refresh_token_without_secret_raises():
    JWTManager.init("access_secret")

    with pytest.raises(RuntimeError) as excinfo:
        JWTManager.create_refresh_token(user_id=1)

    assert "Refresh JWT secret not configured" in str(excinfo.value)


# -------------------------------
# 5) Decode access token
# -------------------------------
def test_decode_access_token_success():
    JWTManager.init("access_secret")

    token = JWTManager.create_access_token(user_id=5)

    decoded = JWTManager.decode_access_token(token)

    assert decoded["user_id"] == 5


def test_decode_access_token_without_secret_raises():
    with pytest.raises(RuntimeError) as excinfo:
        JWTManager.decode_access_token("fake_token")

    assert "JWT secret not configured" in str(excinfo.value)


# -------------------------------
# 6) Decode refresh token
# -------------------------------
def test_decode_refresh_token_success():
    JWTManager.init("access_secret", "refresh_secret")

    token = JWTManager.create_refresh_token(user_id=10)

    decoded = JWTManager.decode_refresh_token(token)

    assert decoded["user_id"] == 10
    assert "jti" in decoded


def test_decode_refresh_token_without_secret_raises():
    JWTManager.init("access_secret")

    with pytest.raises(RuntimeError) as excinfo:
        JWTManager.decode_refresh_token("fake_token")

    assert "Refresh JWT secret not configured" in str(excinfo.value)