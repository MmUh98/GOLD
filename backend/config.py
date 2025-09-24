import os
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret")
    MODEL_PATH = os.getenv("MODEL_PATH", "ml/model.h5")
    SCALER_PATH = os.getenv("SCALER_PATH", "ml/scaler.pkl")
    SCHEDULER_API_ENABLED = True
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    PORT = int(os.getenv("PORT", "5001"))
    FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "firebase/firebase_config.json")
class DevConfig(Config): DEBUG = True
class ProdConfig(Config): DEBUG = False
def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return DevConfig if env == "development" else ProdConfig
