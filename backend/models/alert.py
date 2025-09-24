from extensions import db
from datetime import time
class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(20), nullable=False)   # absolute | percentage
    direction = db.Column(db.String(10), nullable=False)  # up | down
    threshold_value = db.Column(db.Float, nullable=False)
    active = db.Column(db.Boolean, default=True)
    active_start = db.Column(db.Time, default=time(9, 0))
    active_end = db.Column(db.Time, default=time(18, 0))
    push_enabled = db.Column(db.Boolean, default=True)
    fcm_token = db.Column(db.String(600))
