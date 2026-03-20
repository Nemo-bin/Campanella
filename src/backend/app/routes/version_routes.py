from flask import Blueprint, jsonify, g

from app.services.version_service import get_stack_versions

version_bp = Blueprint("version", __name__, url_prefix="/version")

@version_bp.route("", methods=["GET"])
def get_version():
    return jsonify(get_stack_versions(g.db))
