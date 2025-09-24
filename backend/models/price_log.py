from extensions import db
from datetime import datetime
class PriceLog(db.Model):
    __tablename__ = "price_logs"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    price = db.Column(db.Float, nullable=False)
