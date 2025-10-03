import os
import time
from datetime import datetime
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
import praw  # noqa: E402
from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from models import SentimentItem  # noqa: E402

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "gold-sentiment-bot/0.1")

SUBREDDITS = ["Gold", "WallStreetBets", "Commodities", "Investing"]
KEYWORDS = ["gold", "xauusd"]

app = create_app()

reddit = None
if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )
    except Exception as e:
        print("[sentiment_seeder] Failed to init Reddit:", e)

def post_matches(p):
    content = f"{p.title}\n{getattr(p,'selftext','') or ''}".lower()
    return any(k in content for k in KEYWORDS)

def seed_once(limit_per_sub=15):
    if not reddit:
        print("[sentiment_seeder] Reddit not configured.")
        return 0
    added = 0
    with app.app_context():
        for sub in SUBREDDITS:
            try:
                for post in reddit.subreddit(sub).new(limit=limit_per_sub):
                    if not post_matches(post):
                        continue
                    rid = getattr(post, "id", None)
                    if not rid:
                        continue
                    existing = SentimentItem.query.filter_by(source="reddit", author=rid).first()
                    if existing:
                        continue
                    text = (f"{post.title}\n{getattr(post,'selftext','') or ''}").strip()
                    item = SentimentItem(
                        source="reddit",
                        author=rid,  # store reddit id in author field for uniqueness
                        text=text,
                        created_at=datetime.utcfromtimestamp(getattr(post, 'created_utc', time.time())),
                    )
                    db.session.add(item)
                    added += 1
            except Exception as e:
                print(f"[sentiment_seeder] Error fetching subreddit {sub}: {e}")
        if added:
            db.session.commit()
        print(f"[sentiment_seeder] Added {added} reddit posts at {datetime.utcnow().isoformat()}")
    return added

def run_loop(interval=900):  # 15 minutes default
    while True:
        seed_once()
        time.sleep(interval)

if __name__ == "__main__":
    run_loop()
