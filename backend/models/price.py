from extensions import db
from datetime import datetime

class Price(db.Model):
    __tablename__ = "prices"
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50), nullable=False)
    close = db.Column(db.Float, nullable=False)
    predicted = db.Column(db.Float, nullable=True)
    
    def __init__(self, timestamp, close, predicted=None):
        self.timestamp = timestamp
        self.close = close
        self.predicted = predicted
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "close": self.close,
            "predicted": self.predicted
        }
    
    @staticmethod
    def get_latest_prices(limit=60):
        """Get the latest N prices for prediction input"""
        return Price.query.order_by(Price.id.desc()).limit(limit).all()
    
    @staticmethod
    def get_recent_data(hours=24):
        """Get recent price data for charts"""
        return Price.query.order_by(Price.id.desc()).limit(hours * 60).all()