from dotenv import load_dotenv
# Load environment variables first so they are available to any modules
# that may import TensorFlow (or other libs) during their import time.
load_dotenv()
from flask import Flask, jsonify
from extensions import db, jwt, cors, scheduler
from config import get_config
from routes import register_blueprints
from utils.scheduler import register_jobs
def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    register_blueprints(app)
    with app.app_context():
        db.create_all()
    register_jobs(app, scheduler)
    if not scheduler.running:
        scheduler.start()
    @app.get("/health")
    def health():
        return jsonify({"status":"ok"})
    @app.get("/")
    def root():
        return jsonify({"msg": "GoldPredict API", "health": "/health", "api_root": "/api"})
    return app
app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config.get("PORT", 5001))
