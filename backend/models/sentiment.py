from datetime import datetime, timedelta
from extensions import db

class SentimentItem(db.Model):
    __tablename__ = "sentiment_items"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    source = db.Column(db.String(32), index=True)  # twitter, news, auto
    author = db.Column(db.String(128))
    text = db.Column(db.Text, nullable=False)
    label = db.Column(db.String(16), index=True)  # bullish, bearish, neutral
    confidence = db.Column(db.Float)
    processed = db.Column(db.Boolean, default=False, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "source": self.source,
            "author": self.author,
            "text": self.text,
            "label": self.label,
            "confidence": self.confidence,
        }


class SentimentAggregate(db.Model):
    __tablename__ = "sentiment_aggregates"
    id = db.Column(db.Integer, primary_key=True)
    window_start = db.Column(db.DateTime, index=True)
    window_end = db.Column(db.DateTime, index=True)
    bullish_pct = db.Column(db.Float)
    bearish_pct = db.Column(db.Float)
    neutral_pct = db.Column(db.Float)
    total = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "window_start": self.window_start.isoformat() if self.window_start else None,
            "window_end": self.window_end.isoformat() if self.window_end else None,
            "bullish_pct": self.bullish_pct,
            "bearish_pct": self.bearish_pct,
            "neutral_pct": self.neutral_pct,
            "total": self.total,
            "created_at": self.created_at.isoformat(),
        }

    @staticmethod
    def latest(session):
        return session.query(SentimentAggregate).order_by(SentimentAggregate.created_at.desc()).first()
