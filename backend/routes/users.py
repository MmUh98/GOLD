from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
bp = Blueprint("users", __name__)
@bp.get("/settings")
@jwt_required()
def get_settings():
    u = User.query.get(get_jwt_identity())
    return jsonify(u.to_dict())
@bp.put("/settings")
@jwt_required()
def update_settings():
    u = User.query.get(get_jwt_identity())
    d = request.get_json() or {}
    u.theme = d.get("theme", u.theme)
    u.language = d.get("language", u.language)
    if "fcm_token" in d: u.fcm_token = d["fcm_token"]
    from extensions import db; db.session.commit()
    return jsonify(u.to_dict())
