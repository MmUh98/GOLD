from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
from models.prediction import Prediction
from services.predictor import Predictor
from services.data_fetcher import get_recent_prices_from_db_or_yf
from models.price import Price
bp = Blueprint("predict", __name__)
predictor = Predictor()
@bp.get("/predict")
def predict_public():
    try:
        # Load model to determine the correct window size
        predictor._load()
        # Prefer intraday prices (our 'prices' table). If insufficient, fall back to daily series.
        intraday = Price.query.order_by(Price.id.desc()).limit(predictor.window).all()
        recent_vals = [p.close for p in reversed(intraday)]
        if len(recent_vals) < predictor.window:
            series = get_recent_prices_from_db_or_yf(limit=predictor.window)
            try:
                recent_vals = series.tolist()
            except Exception:
                recent_vals = list(series)

        # If still not enough, return a simple SMA fallback to keep UI populated
        if len(recent_vals) < 1:
            return jsonify({"msg": "No recent prices available"}), 400

        # Use model when enough values for the window; otherwise use SMA fallback
        if len(recent_vals) >= predictor.window and predictor.model and predictor.scaler:
            pred, conf = predictor.predict_next(recent_vals)
            return jsonify({"predicted_price": float(pred), "confidence": conf, "mode": "model", "window": predictor.window, "used": len(recent_vals)})
        else:
            w = min(len(recent_vals), predictor.window)
            sma = sum(recent_vals[-w:]) / w
            return jsonify({"predicted_price": float(sma), "confidence": None, "mode": "sma_fallback", "window": predictor.window, "used": len(recent_vals)})
    except Exception as e:
        return jsonify({"msg": str(e)}), 400
@bp.post("/predict")
@jwt_required(optional=True)
def predict_post():
    data = request.get_json() or {}
    series = data.get("recent_prices")
    if not series: return jsonify({"msg":"recent_prices required"}), 400
    pred, conf = predictor.predict_next(series)
    user_id = get_jwt_identity()
    if user_id:
        rec = Prediction(user_id=user_id, predicted_price=pred, confidence=conf)
        db.session.add(rec); db.session.commit()
    return jsonify({"predicted_price": pred, "confidence": conf})
