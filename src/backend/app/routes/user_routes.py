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
        return jsonify(user.to_dict()), 201

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
        return jsonify(user.to_dict()), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

@users_bp.route("/update", methods=["POST"])
def update_user():
    data = request.json
    repo = UserRepository(g.db)
    service = UserService(repo)

    required_fields = ["user_id", "fields"]
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": "Missing fields"}), 400
    
    try:
        user = service.update_user(data["user_id"], data["fields"])
        return jsonify(user.to_dict()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 401
