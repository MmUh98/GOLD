from flask import Blueprint, jsonify
from models import SentimentItem, SentimentAggregate
from extensions import db

bp = Blueprint("sentiment", __name__)

@bp.get("/sentiment/feed")
def sentiment_feed():
    items = (
        SentimentItem.query.filter(SentimentItem.processed.is_(True))
        .order_by(SentimentItem.created_at.desc())
        .limit(50)
        .all()
    )
    return jsonify([i.to_dict() for i in items])

@bp.get("/sentiment/summary")
def sentiment_summary():
    agg = (
        SentimentAggregate.query.order_by(SentimentAggregate.created_at.desc()).first()
    )
    if not agg:
        return jsonify({
            "bullish_pct": 0,
            "bearish_pct": 0,
            "neutral_pct": 0,
            "total": 0,
        })
    return jsonify(agg.to_dict())
