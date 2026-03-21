from flask import Blueprint, request, jsonify, g
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.middleware.auth_middleware import AuthMiddleware

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route("/update", methods=["POST"])
@AuthMiddleware.required
def update_user(current_user_id):
    data = request.json
    repo = UserRepository(g.db)
    service = UserService(repo)

    required_fields = ["fields"]
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": "Missing fields"}), 400
    
    try:
        user = service.update_user(current_user_id, data["fields"])
        return jsonify(user.to_dict()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    
@users_bp.route("/delete", methods=["POST"])
@AuthMiddleware.required
def delete_user(current_user_id):
    repo = UserRepository(g.db)
    service = UserService(repo)

    try:
        service.delete_user(current_user_id)
        return jsonify({"message": "User deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 401
