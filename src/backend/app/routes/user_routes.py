from flask import Blueprint, request, jsonify, g
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json
    repo = UserRepository(g.db)
    service = UserService(repo)

    required_fields = ["email", "username", "password"]
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    try:
        user = service.register_user(
            email=data["email"],
            password=data["password"],
            username=data["username"]
        )
        return jsonify({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "created_at": user.created_at.isoformat(),
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@users_bp.route("/login", methods=["POST"])
def login_user():
    data = request.json
    repo = UserRepository(g.db)
    service = UserService(repo)

    required_fields = ["email", "password"]
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    try:
        user = service.login_user(
            email=data["email"],
            password=data["password"]
        )
        return jsonify({
            "id": user.id,
            "email": user.email,
            "username": user.username,
        }), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 401