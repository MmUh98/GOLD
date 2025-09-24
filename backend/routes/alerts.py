from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.alert import Alert
bp = Blueprint("alerts", __name__)
@bp.get("/alerts")
@jwt_required()
def list_alerts():
    uid = get_jwt_identity()
    alerts = Alert.query.filter_by(user_id=uid).all()
    return jsonify([{"id":a.id,"type":a.type,"direction":a.direction,"threshold_value":a.threshold_value,"active":a.active,"push_enabled":a.push_enabled} for a in alerts])
@bp.post("/alerts")
@jwt_required()
def create_alert():
    uid = get_jwt_identity(); d = request.get_json() or {}
    try:
        a = Alert(user_id=uid, type=d["type"], direction=d["direction"],
                  threshold_value=float(d["threshold_value"]), active=bool(d.get("active",True)),
                  push_enabled=bool(d.get("push_enabled",True)), fcm_token=d.get("fcm_token"))
        db.session.add(a); db.session.commit()
        return jsonify({"id": a.id}), 201
    except KeyError:
        return jsonify({"msg":"Missing fields"}), 400
@bp.delete("/alerts/<int:alert_id>")
@jwt_required()
def delete_alert(alert_id):
    uid = get_jwt_identity()
    a = Alert.query.filter_by(id=alert_id, user_id=uid).first()
    if not a: return jsonify({"msg":"Not found"}), 404
    db.session.delete(a); db.session.commit()
    return jsonify({"msg":"Deleted"})
