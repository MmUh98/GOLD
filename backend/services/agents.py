from models.alert import Alert
from models.user import User
from models.price_log import PriceLog
from sqlalchemy import desc
from utils.notifications import send_push_notification
def _current_price():
    row = PriceLog.query.order_by(desc(PriceLog.timestamp)).first()
    return None if not row else row.price
def volatility_watchdog():
    price = _current_price()
    if price is None: return 0
    from extensions import db
    count=0; alerts = Alert.query.filter_by(active=True).all()
    for a in alerts:
        trig=False
        if a.type=="absolute":
            if a.direction=="up" and price >= a.threshold_value: trig=True
            if a.direction=="down" and price <= a.threshold_value: trig=True
        elif a.type=="percentage":
            prev = PriceLog.query.order_by(desc(PriceLog.timestamp)).offset(1).first()
            if prev:
                change_pct=(price-prev.price)/prev.price*100
                if a.direction=="up" and change_pct >= a.threshold_value: trig=True
                if a.direction=="down" and change_pct <= -a.threshold_value: trig=True
        if trig and a.push_enabled:
            token = a.fcm_token or (a.user.fcm_token if a.user else None)
            if token: send_push_notification(token, "Gold Alert ⚡", f"Price {price:.2f} met {a.type} {a.direction} {a.threshold_value}"); count+=1
    return count
def sentiment_agent(sentiment_score: float):
    if sentiment_score > 0.7 or sentiment_score < -0.7:
        users = User.query.all(); n=0
        for u in users:
            if u.fcm_token:
                title = "Positive Gold News 🟢" if sentiment_score > 0 else "Negative Gold News 🔴"
                send_push_notification(u.fcm_token, title, f"Sentiment score: {sentiment_score:.2f}"); n+=1
        return n
    return 0
