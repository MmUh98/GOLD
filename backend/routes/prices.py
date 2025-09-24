from flask import Blueprint, jsonify, request
from models.price_log import PriceLog
from models.price import Price
from extensions import db
from datetime import datetime
from sqlalchemy import desc
import yfinance as yf
import numpy as np
import joblib
import tensorflow as tf
import os
import traceback
import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

bp = Blueprint("prices", __name__)
from services.predictor import Predictor
_predictor = Predictor()

logger = logging.getLogger(__name__)

_HTTP_SESSION = None
def _http():
    global _HTTP_SESSION
    if _HTTP_SESSION is None:
        s = requests.Session()
        retry = Retry(total=2, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"]) 
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        _HTTP_SESSION = s
    return _HTTP_SESSION

@bp.get("/prices")
def prices_list():
    start = request.args.get("start"); end = request.args.get("end")
    limit = int(request.args.get("limit", "500"))
    q = PriceLog.query
    if start: q = q.filter(PriceLog.timestamp >= datetime.fromisoformat(start))
    if end: q = q.filter(PriceLog.timestamp <= datetime.fromisoformat(end))
    rows = q.order_by(desc(PriceLog.timestamp)).limit(limit).all()
    return jsonify([{"t": r.timestamp.isoformat(), "price": r.price} for r in reversed(rows)])

def _from_quote_api(symbol: str):
    """Use Yahoo quote API to get last price and market time."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        url = f"https://query2.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        r = _http().get(url, headers=headers, timeout=4)
        if r.status_code != 200:
            return None
        j = r.json() or {}
        result = (j.get("quoteResponse") or {}).get("result") or []
        if not result:
            return None
        q = result[0]
        price = q.get("regularMarketPrice") or q.get("postMarketPrice") or q.get("preMarketPrice")
        tsec = q.get("regularMarketTime") or q.get("postMarketTime") or q.get("preMarketTime")
        if price is None:
            return None
        if tsec is None:
            # fallback to now if no time provided
            ts = datetime.utcnow().isoformat() + "Z"
        else:
            ts = datetime.utcfromtimestamp(int(tsec)).isoformat() + "Z"
        return ts, float(price), f"{symbol}:quote"
    except Exception as e:
        logger.warning("quote api failed for %s: %s", symbol, e)
        return None

def _from_chart_api(symbol: str):
    """Call Yahoo's chart API directly as a robust fallback.
    Returns (timestamp_str, price_float, source) or None.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    combos = [("1d", "1m"), ("5d", "5m"), ("1mo", "1d")]
    for rng, itv in combos:
        try:
            url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?interval={itv}&range={rng}&includePrePost=true"
            r = _http().get(url, headers=headers, timeout=12)
            if r.status_code != 200:
                continue
            data = r.json()
            result = (data or {}).get("chart", {}).get("result")
            if not result:
                continue
            r0 = result[0]
            ts_list = r0.get("timestamp") or []
            quote = (r0.get("indicators") or {}).get("quote") or [{}]
            closes = quote[0].get("close") or []
            # find last non-null close
            for i in range(len(closes) - 1, -1, -1):
                p = closes[i]
                if p is not None and i < len(ts_list):
                    ts = datetime.utcfromtimestamp(ts_list[i]).isoformat() + "Z"
                    return ts, float(p), f"{symbol}:chart_{rng}_{itv}"
        except Exception as e:
            logger.warning("chart api failed for %s %s/%s: %s", symbol, rng, itv, e)
    return None

def _chart_series(symbol: str, rng: str = "5d", itv: str = "5m"):
    """Fetch a full series of closes from Yahoo Chart API.
    Returns list of (iso_timestamp, close_float)."""
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?interval={itv}&range={rng}&includePrePost=true"
    r = _http().get(url, headers=headers, timeout=12)
    r.raise_for_status()
    data = r.json() or {}
    result = (data.get("chart") or {}).get("result") or []
    if not result:
        return []
    r0 = result[0]
    ts_list = r0.get("timestamp") or []
    quote = (r0.get("indicators") or {}).get("quote") or [{}]
    closes = quote[0].get("close") or []
    out = []
    for i, p in enumerate(closes):
        if p is None: continue
        if i >= len(ts_list): continue
        ts = datetime.utcfromtimestamp(int(ts_list[i])).isoformat() + "Z"
        out.append((ts, float(p)))
    return out

def _chart_series_full(symbol: str, rng: str, itv: str):
    """Fetch full series and meta from Yahoo Chart API.
    Returns (series_list, meta_dict) where series_list is list[(iso_ts, close_float)]."""
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?interval={itv}&range={rng}&includePrePost=true"
    r = _http().get(url, headers=headers, timeout=12)
    r.raise_for_status()
    data = r.json() or {}
    result = (data.get("chart") or {}).get("result") or []
    if not result:
        return [], {}
    r0 = result[0]
    meta = r0.get("meta", {})
    ts_list = r0.get("timestamp") or []
    quote = (r0.get("indicators") or {}).get("quote") or [{}]
    closes = quote[0].get("close") or []
    out = []
    for i, p in enumerate(closes):
        if p is None: continue
        if i >= len(ts_list): continue
        ts = datetime.utcfromtimestamp(int(ts_list[i])).isoformat() + "Z"
        out.append((ts, float(p)))
    return out, meta

def _try_get_price(symbol: str):
    """Try multiple methods to get a recent price. Returns (timestamp_str, price_float, source) or None."""
    # 1) Quote API (quick and resilient)
    result = _from_quote_api(symbol)
    if result:
        return result
    # 2) Direct chart API (robust for intraday series)
    result = _from_chart_api(symbol)
    if result:
        return result

    # 3) yfinance: history via Ticker
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="1d", interval="1m")
        if df is not None and not df.empty:
            price = float(df["Close"].iloc[-1])
            ts = df.index[-1].to_pydatetime().astimezone(None).isoformat()
            return ts, price, f"{symbol}:history_1d_1m"
    except Exception:
        traceback.print_exc()

    # 4) yfinance: download helper
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False, group_by="column", threads=False)
        if df is not None and not df.empty:
            price = float(df["Close"].iloc[-1])
            ts = df.index[-1].to_pydatetime().astimezone(None).isoformat()
            return ts, price, f"{symbol}:download_1d_1m"
    except Exception:
        traceback.print_exc()

    # 5) Fallback 5d/5m
    try:
        df = yf.download(symbol, period="5d", interval="5m", progress=False, group_by="column", threads=False)
        if df is not None and not df.empty:
            price = float(df["Close"].iloc[-1])
            ts = df.index[-1].to_pydatetime().astimezone(None).isoformat()
            return ts, price, f"{symbol}:download_5d_5m"
    except Exception:
        traceback.print_exc()
    return None

def _get_cached_latest():
    last = Price.query.order_by(Price.id.desc()).first()
    if last:
        return last.timestamp, float(last.close), "cache"
    return None


@bp.get("/live-price")
def live_price():
    try:
        # Try GC=F (futures), then spot XAUUSD=X, then GLD ETF
        symbols = ["GC=F", "XAUUSD=X", "GLD"]
        result = None
        last_errors = []
        for sym in symbols:
            try:
                result = _try_get_price(sym)
                if result:
                    break
            except Exception as e:
                last_errors.append(f"{sym}: {e}")
        if not result:
            # Fallback to last cached DB value (return 200 but mark as cached)
            cached = _get_cached_latest()
            if cached:
                ts, price, source = cached
                return jsonify({
                    "timestamp": ts,
                    "price": price,
                    "predicted": None,
                    "source": source,
                    "is_cache": True,
                    "message": "Live price unavailable; returning last cached value"
                }), 200
            msg = "Live price not available from Yahoo Finance right now."
            if last_errors:
                msg += " Errors: " + "; ".join(last_errors)
            return jsonify({"error": msg}), 503

        timestamp, latest_price, source = result

        # Generate prediction (optional) using cached Predictor
        predicted_price = None
        try:
            # Load once so window/scaler/model are ready
            _predictor._load()
            # Build recent window using DB values plus current price
            recent = Price.query.order_by(Price.id.desc()).limit(max(1, _predictor.window-1)).all()
            recent_vals = [p.close for p in reversed(recent)] + [latest_price]
            if len(recent_vals) >= _predictor.window:
                predicted_price, _ = _predictor.predict_next(recent_vals)
        except Exception as e:
            print(f"Prediction error: {e}")

        # Save to database
        price_record = Price(
            timestamp=timestamp,
            close=latest_price,
            predicted=predicted_price
        )
        db.session.add(price_record)
        db.session.commit()

        return jsonify({
            "timestamp": timestamp,
            "price": latest_price,
            "predicted": predicted_price,
            "source": source
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Admin/utility endpoint to backfill intraday prices into prices table
@bp.get("/admin/backfill-prices")
def backfill_prices():
    try:
        rng = request.args.get("range", "5d")
        itv = request.args.get("interval", "5m")
        symbols = request.args.get("symbols")
        if symbols:
            sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        else:
            sym_list = ["GC=F", "XAUUSD=X", "GLD"]

        inserted = 0
        used_symbol = None
        for sym in sym_list:
            try:
                series = _chart_series(sym, rng, itv)
                if not series:
                    continue
                used_symbol = sym
                # naive de-dup by timestamp string
                for ts, price in series:
                    if not Price.query.filter_by(timestamp=ts).first():
                        db.session.add(Price(timestamp=ts, close=price))
                        inserted += 1
                        if inserted % 500 == 0:
                            db.session.commit()
                break
            except Exception:
                traceback.print_exc()
                continue
        db.session.commit()
        if used_symbol is None:
            return jsonify({"msg": "No data fetched from any symbol"}), 503
        return jsonify({"msg": "backfill complete", "inserted": inserted, "symbol": used_symbol, "range": rng, "interval": itv})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bp.get("/price-history")
def price_history():
    """Get recent price history for charts"""
    limit = int(request.args.get("limit", "100"))
    prices = Price.query.order_by(Price.id.desc()).limit(limit).all()
    
    return jsonify([{
        "timestamp": p.timestamp,
        "price": p.close,
        "predicted": p.predicted
    } for p in reversed(prices)])

@bp.get("/chart-series")
def chart_series():
    """Yahoo-like chart series passthrough with range/interval presets.
    Query params: range (e.g., 1d,5d,1mo,6mo,1y,5y,max), interval (1m,5m,1d,1wk,1mo), symbol (default GC=F).
    """
    try:
        rng = request.args.get("range", "1d")
        itv = request.args.get("interval")
        symbol = request.args.get("symbol", "GC=F")
        # choose sensible defaults if interval omitted
        if not itv:
            defaults = {
                "1d": "1m",
                "5d": "5m",
                "1mo": "1d",
                "3mo": "1d",
                "6mo": "1d",
                "1y": "1d",
                "2y": "1wk",
                "5y": "1wk",
                "10y": "1mo",
                "ytd": "1d",
                "max": "1mo",
            }
            itv = defaults.get(rng, "1d")
        series, meta = _chart_series_full(symbol, rng, itv)
        return jsonify({
            "symbol": symbol,
            "range": rng,
            "interval": itv,
            "points": [{"timestamp": ts, "price": v} for ts, v in series],
            "meta": {
                "previousClose": meta.get("chartPreviousClose") or meta.get("previousClose"),
                "regularMarketPrice": meta.get("regularMarketPrice"),
                "timezone": meta.get("timezone"),
                "currency": meta.get("currency"),
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def generate_prediction(current_price):
    """Generate price prediction using the trained model"""
    try:
        # Get the last 60 prices for model input
        recent_prices = Price.query.order_by(Price.id.desc()).limit(59).all()
        
        if len(recent_prices) < 59:
            return None  # Not enough historical data
        
        # Prepare data sequence (including current price)
        prices_sequence = [p.close for p in reversed(recent_prices)] + [current_price]
        
        # Load scaler and model
        model_path = os.getenv('MODEL_PATH', 'ml/model.h5')
        scaler_path = os.getenv('SCALER_PATH', 'ml/scaler.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            return None

        scaler = joblib.load(scaler_path)
        # Load model for inference only to avoid deserializing metrics/loss
        model = tf.keras.models.load_model(model_path, compile=False)
        
        # Scale the data
        prices_scaled = scaler.transform(np.array(prices_sequence).reshape(-1, 1))
        
        # Reshape for model input (1, 60, 1)
        X = prices_scaled.reshape(1, 60, 1)
        
        # Make prediction
        prediction_scaled = model.predict(X, verbose=0)
        prediction = scaler.inverse_transform(prediction_scaled)[0][0]
        
        return float(prediction)
        
    except Exception as e:
        print(f"Prediction generation error: {e}")
        return None
