# Smart Gold App (with Firebase Push + Agents)
See /backend/.env.example and /frontend/.env.example for required envs.
# Smart Gold App

Full‑stack gold price monitoring and prediction platform.

## Overview
- **Backend:** Flask (REST API, SQLite, JWT auth, scheduled tasks, ML predictor)
- **Frontend:** React (dashboard, TradingView advanced chart, alerts scaffold)
- **Data Sources:** Yahoo Finance (live + historical, resilient fallbacks)
- **ML:** Keras model (`ml/model.h5`) + scaler (`ml/scaler.pkl`) for next‑step price prediction (graceful SMA fallback if model unavailable)
- **Notifications:** Firebase (FCM token storage, future push alerts)
- **Charting:** TradingView Advanced Chart (spot gold `OANDA:XAUUSD`)

## Features
- Live gold price polling with multi‑symbol + multi‑method fallback and caching
- Historical + backfill endpoint to seed intraday data
- ML prediction with windowed sequence input (auto switches to model when enough points)
- TradingView embedded interactive chart (indicators, drawing tools, fullscreen, compare)
- SMA fallback when model/scaler or data window not ready
- Admin backfill to instantly populate DB for charts & predictions

## Tech Stack
| Layer | Stack |
|-------|-------|
| Backend | Python, Flask, SQLAlchemy, APScheduler |
| Frontend | React, Axios, TradingView widget |
| ML | TensorFlow / Keras (optional at runtime) |
| Storage | SQLite (`fyp.db`) |
| Auth | JWT |
| Notifications | Firebase (planned alerts) |

## Directory
```
backend/
  app.py
  routes/
  services/
  ml/ (model.h5, scaler.pkl, meta.json)
  .env
frontend/
  src/
    components/
    pages/
    services/
README.md
```

## Environment Variables

Backend (`backend/.env`)
```
FLASK_ENV=development
SECRET_KEY=...
JWT_SECRET_KEY=...
DATABASE_URL=sqlite:///fyp.db
MODEL_PATH=ml/model.h5
SCALER_PATH=ml/scaler.pkl
CORS_ORIGINS=*
PORT=5001
FIREBASE_CREDENTIALS=firebase/firebase_config.json
TF_ENABLE_ONEDNN_OPTS=0
```

Frontend (`frontend/.env`)
```
REACT_APP_API_BASE=http://localhost:5001/api
```

## Setup

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt   # ensure tensorflow==2.17.1 present if using ML
python app.py
```

### Frontend
```powershell
cd frontend
npm install
npm start
```

Navigate: http://localhost:3000

## Key API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/live-price | GET | Latest live price (with prediction + cache fallback) |
| /api/price-history?limit=N | GET | Recent stored prices |
| /api/predict | GET | Next price prediction (model or SMA fallback) |
| /api/admin/backfill-prices | GET | Backfill intraday data (range, interval params) |
| /api/chart-series?range=1d | GET | Yahoo-style series for chart |

Example backfill:
```
/api/admin/backfill-prices?range=1d&interval=1m
```

## Prediction Logic
1. Collect latest N closes (model window, e.g. 60)
2. Scale with `scaler.pkl`
3. Predict with `model.h5` (loaded compile=False)
4. If insufficient data or TF missing → SMA fallback

## TradingView Integration
Component: `frontend/src/components/TradingViewChart.js`
- Symbol default: `OANDA:XAUUSD`
- Interval default: 1D
- Autosize, dark theme, volume & indicators enabled
- Easily switch to another symbol by prop

## Common Issues
| Symptom | Fix |
|---------|-----|
| 500 on /api/live-price | Temporary Yahoo timeout → retries + cached value; retry later |
| Prediction blank | Backfill or wait until window size reached; ensure TF + model/scaler present |
| TensorFlow missing | `pip install tensorflow==2.17.1` inside venv |
| Widget symbol warning | Use spot symbol (`OANDA:XAUUSD`) |

## Adding Alerts (Planned)
1. Add button on chart page: “Create Alert”
2. Post rule to backend (price threshold / indicator)
3. Scheduler evaluates rules; sends FCM via stored tokens

## Deployment Notes
- Consider switching SQLite to Postgres in production.
- Run Flask behind a WSGI server (gunicorn/uwsgi) + reverse proxy.
- Cache external price responses (short TTL) to reduce rate limits.

## Scripts
```powershell
# Backfill then start prediction-ready system
curl http://localhost:5001/api/admin/backfill-prices?range=1d&interval=1m
```

## License
Internal / academic use (adjust as needed).

## Quick Start (TL;DR)
```powershell
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py

# Frontend
cd ../frontend
npm install
npm start
```