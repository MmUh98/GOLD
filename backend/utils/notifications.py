import firebase_admin
from firebase_admin import credentials, messaging
from flask import current_app
_inited=False
def _ensure():
    global _inited
    if _inited: return
    if not firebase_admin._apps:
        cred = credentials.Certificate(current_app.config.get("FIREBASE_CREDENTIALS","firebase/firebase_config.json"))
        firebase_admin.initialize_app(cred)
    _inited=True
def send_push_notification(token: str, title: str, body: str, data: dict|None=None):
    _ensure()
    msg = messaging.Message(notification=messaging.Notification(title=title, body=body), token=token, data=data or {})
    return messaging.send(msg)
