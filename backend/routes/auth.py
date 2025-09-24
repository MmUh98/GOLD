from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models.user import User
bp = Blueprint("auth", __name__)
@bp.post("/signup")
def signup():
    data = request.get_json() or {}
    name, email, password = data.get("name"), data.get("email"), data.get("password")
    if not all([name, email, password]): return jsonify({"msg":"Missing fields"}), 400
    if User.query.filter_by(email=email).first(): return jsonify({"msg":"Email in use"}), 409
    user = User(name=name, email=email); user.set_password(password)
    db.session.add(user); db.session.commit()
    token = create_access_token(identity=user.id)
    return jsonify({"token":token, "user": user.to_dict()}), 201
@bp.post("/login")
def login():
    data = request.get_json() or {}
    email, password = data.get("email"), data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password): return jsonify({"msg":"Invalid creds"}), 401
    token = create_access_token(identity=user.id)
    return jsonify({"token":token, "user": user.to_dict()}), 200
@bp.get("/me")
@jwt_required()
def me():
    user = User.query.get(get_jwt_identity())
    return jsonify(user.to_dict())
@bp.post("/token/fcm")
@jwt_required()
def save_fcm_token():
    user = User.query.get(get_jwt_identity())
    data = request.get_json() or {}
    user.fcm_token = data.get("token")
    db.session.commit()
    return jsonify({"msg":"saved"})
