from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    theme = db.Column(db.String(20), default="dark")
    language = db.Column(db.String(10), default="en")
    fcm_token = db.Column(db.String(600))
    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw) -> bool: return check_password_hash(self.password_hash, pw)
    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "theme": self.theme, "language": self.language, "fcm_token": self.fcm_token}
