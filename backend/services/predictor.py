import os, numpy as np
from joblib import load
try:
    import tensorflow as tf
except Exception:
    tf = None
from flask import current_app
class Predictor:
    def __init__(self):
        self._loaded=False; self.model=None; self.scaler=None; self.window=60
    def _load(self):
        if self._loaded: return
        model_path=current_app.config["MODEL_PATH"]; scaler_path=current_app.config["SCALER_PATH"]
        if os.path.exists(model_path) and os.path.exists(scaler_path) and tf is not None:
            # Load for inference only (no need to deserialize metrics/loss)
            try:
                self.model=tf.keras.models.load_model(model_path, compile=False)
            except Exception:
                # Fallback for legacy models
                self.model=tf.keras.models.load_model(model_path, compile=False, safe_mode=False)
            self.scaler=load(scaler_path)
            try: self.window=self.model.input_shape[1] or 60
            except Exception: self.window=60
            # Warm up the model once to create the tf.function graph and reduce retracing later
            try:
                dummy=np.zeros((1, self.window, 1), dtype=np.float32)
                _=self.model.predict(dummy, verbose=0)
            except Exception:
                pass
        else:
            # If TF or files not available, leave model None; scaler may still be attempted
            try:
                if os.path.exists(scaler_path):
                    self.scaler = load(scaler_path)
            except Exception:
                self.scaler = None
        self._loaded=True
    def predict_next(self, recent_prices:list[float]):
        self._load()
        if self.model and self.scaler:
            if len(recent_prices) < self.window: raise ValueError(f"Need {self.window} values")
            arr=np.array(recent_prices[-self.window:], dtype=np.float32).reshape(-1,1)
            scaled=self.scaler.transform(arr).astype(np.float32).reshape(1,self.window,1)
            pred_scaled=self.model.predict(scaled, verbose=0)[0][0]
            pred=float(self.scaler.inverse_transform([[pred_scaled]])[0][0])
            return pred, None
        w=min(len(recent_prices), self.window); sma=sum(recent_prices[-w:])/w; return float(sma), None
