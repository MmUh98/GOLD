import pandas as pd, yfinance as yf
from extensions import db
from models.price_log import PriceLog
from sqlalchemy import desc
def fetch_from_yf(period="2y", interval="1d"):
    df = yf.download("GC=F", period=period, interval=interval, progress=False)
    return df["Close"].dropna()
def seed_db_from_yf(limit=500):
    series = fetch_from_yf(period="2y", interval="1d").tail(limit)
    for ts, price in series.items():
        db.session.add(PriceLog(timestamp=ts.to_pydatetime(), price=float(price)))
    db.session.commit()
def get_recent_prices_from_db_or_yf(limit=60):
    rows = PriceLog.query.order_by(desc(PriceLog.timestamp)).limit(limit).all()
    if len(rows) < limit:
        series = fetch_from_yf(period="6mo", interval="1d").tail(limit)
        return series
    values = [r.price for r in reversed(rows)]
    return pd.Series(values)
def insert_latest_price_if_new():
    series = fetch_from_yf(period="5d", interval="1d").tail(1)
    if series.empty: return None
    ts = series.index[-1].to_pydatetime(); price = float(series.iloc[-1])
    exists = PriceLog.query.filter(PriceLog.timestamp==ts).first()
    if not exists:
        db.session.add(PriceLog(timestamp=ts, price=price)); db.session.commit(); return price
    return None
