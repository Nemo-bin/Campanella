from flask import Blueprint, request, jsonify, g
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.middleware.jwt_token import AuthMiddleware

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
