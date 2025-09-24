from .auth import bp as auth_bp
from .predict import bp as predict_bp
from .alerts import bp as alerts_bp
from .prices import bp as prices_bp
from .reports import bp as reports_bp
from .users import bp as users_bp
def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(alerts_bp, url_prefix="/api")
    app.register_blueprint(prices_bp, url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/api")
    app.register_blueprint(users_bp, url_prefix="/api")
