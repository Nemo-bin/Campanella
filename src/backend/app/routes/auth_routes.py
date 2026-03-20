from flask import Blueprint, request, jsonify, g
import jwt
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.middleware.jwt_token import AuthMiddleware

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
        return jsonify({
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@auth_bp.route("/login", methods=["POST"])
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
        return jsonify({
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    
@auth_bp.route("/refresh", methods=["POST"])
@AuthMiddleware.required
def refresh_token(current_user_id):
    data = request.json
    refresh_token = data["refresh_token"]
    user_repo = UserRepository(g.db)
    refresh_token_repo = RefreshTokenRepository(g.db)
    service = AuthService(user_repo, refresh_token_repo)

    if not refresh_token:
        return jsonify({"error": "Missing refresh token"}), 400
    
    try:
        data = jwt.decode(refresh_token, AuthMiddleware._refresh_secret, algorithms=["HS256"])
        user_id = data.get("user_id")
        
        if not service.is_valid(refresh_token["jti"]):  
            return jsonify({"error": "Invalid refresh token"}), 401

        new_access_token = AuthMiddleware.create_jwt(user_id)
        return jsonify({"access_token": new_access_token})

    except jwt.ExpiredSignatureError as e:
        return jsonify({"error": str(e)}), 401
    except (jwt.InvalidAlgorithmError, jwt.DecodeError):
        return jsonify({"error": str(e)}), 401