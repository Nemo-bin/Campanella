from flask import Blueprint, request, jsonify, g
import jwt
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.middleware.auth_middleware import AuthMiddleware

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json
    user_repo = UserRepository(g.db)
    refresh_token_repo = RefreshTokenRepository(g.db)
    service = AuthService(user_repo, refresh_token_repo)

    required_fields = ["email", "username", "password"]
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    try:
        user = service.register_user(
            email=data["email"],
            password=data["password"],
            username=data["username"]
        )
        access_token = AuthMiddleware.create_jwt(user.id)
        refresh_token = AuthMiddleware.create_refresh_token(user.id)
        decoded_refresh_token = jwt.decode(refresh_token, AuthMiddleware._refresh_secret, algorithms=["HS256"])
        jti = decoded_refresh_token.get("jti")
        refresh_token_repo.create_refresh_token(jti=jti, user_id=user.id)
        return jsonify({
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@auth_bp.route("/login", methods=["GET"])
def login_user():
    data = request.json
    user_repo = UserRepository(g.db)
    refresh_token_repo = RefreshTokenRepository(g.db)
    service = AuthService(user_repo, refresh_token_repo)

    required_fields = ["email", "password"]
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    try:
        user = service.login_user(
            email= data["email"],
            password=data["password"]
        )
        access_token = AuthMiddleware.create_jwt(user.id)
        refresh_token = AuthMiddleware.create_refresh_token(user.id)
        decoded_refresh_token = jwt.decode(refresh_token, AuthMiddleware._refresh_secret, algorithms=["HS256"])
        jti = decoded_refresh_token.get("jti")
        refresh_token_repo.create_refresh_token(jti=jti, user_id=user.id)
        return jsonify({
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    
@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    data = request.json
    user_repo = UserRepository(g.db)
    refresh_token_repo = RefreshTokenRepository(g.db)
    service = AuthService(user_repo, refresh_token_repo)

    required_fields = ["refresh_token", "user_id"]
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    refresh_token = data.get("refresh_token")

    try:
        user_id = data.get("user_id")
        decoded_refresh_token = jwt.decode(refresh_token, AuthMiddleware._refresh_secret, algorithms=["HS256"])
        jti = decoded_refresh_token.get("jti")
        if not service.is_valid(jti):  
            return jsonify({"error": "Invalid refresh token"}), 401

        new_access_token = AuthMiddleware.create_jwt(user_id)
        return jsonify({"access_token": new_access_token})

    except jwt.ExpiredSignatureError as e:
        return jsonify({"error": str(e)}), 401
    except (jwt.InvalidAlgorithmError, jwt.DecodeError) as e:
        return jsonify({"error": str(e)}), 401
    
@auth_bp.route("/logout", methods=["POST"])
@AuthMiddleware.required
def logout_user(current_user_id):
    data = request.json
    user_repo = UserRepository(g.db)
    refresh_token_repo = RefreshTokenRepository(g.db)
    service = AuthService(user_repo, refresh_token_repo)

    if not data or "refresh_token" not in data:
        return jsonify({"error": "Missing refresh_token"}), 400

    refresh_token = data.get("refresh_token")

    try:
        decoded = jwt.decode(
            refresh_token,
            AuthMiddleware._refresh_secret,
            algorithms=["HS256"]
        )

        jti = decoded.get("jti")
        token_user_id = decoded.get("user_id")

        if token_user_id != current_user_id:
            return jsonify({"error": "Token does not belong to user"}), 403

        service.revoke_refresh_token(jti)

        return jsonify({"message": "Logged out successfully"}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expired"}), 401
    except (jwt.InvalidAlgorithmError, jwt.DecodeError):
        return jsonify({"error": "Invalid refresh token"}), 401