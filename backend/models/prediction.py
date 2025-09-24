from extensions import db
from datetime import datetime
class Prediction(db.Model):
    __tablename__ = "predictions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    predicted_price = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float)
