from flask import Blueprint, jsonify, request
from models.price_log import PriceLog
from datetime import datetime, timedelta
bp = Blueprint("reports", __name__)
@bp.get("/reports")
def reports():
    r = request.args.get("range","daily")
    now = datetime.utcnow()
    since = now - (timedelta(days=7) if r=="weekly" else timedelta(days=30) if r=="monthly" else timedelta(days=1))
    rows = PriceLog.query.filter(PriceLog.timestamp >= since).all()
    values = [x.price for x in rows]
    if not values:
        return jsonify({"count":0,"avg":None,"min":None,"max":None,"volatility_pct":None})
    avg = sum(values)/len(values); mn=min(values); mx=max(values)
    vol = (mx-mn)/avg*100 if avg else None
    return jsonify({"count":len(values),"avg":avg,"min":mn,"max":mx,"volatility_pct":vol})
