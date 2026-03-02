from flask import Blueprint, jsonify

from ..services.version_service import get_stack_versions

version_bp = Blueprint("version", __name__, url_prefix="/version")

@version_bp.route("/", methods=["GET"])
def get_version():
    """
    GET /version
    Returns the versions of Python, Flask, and PostgreSQL in the stack.
    """
    return jsonify(get_stack_versions())
