from datetime import datetime, timedelta
from typing import List, Dict
from models import SentimentItem, SentimentAggregate
from extensions import db
from utils.azure_openai import classify_posts


def classify_unprocessed(batch_size=25):
    items: List[SentimentItem] = (
        SentimentItem.query.filter_by(processed=False)
        .order_by(SentimentItem.created_at.asc())
        .limit(batch_size)
        .all()
    )
    if not items:
        return 0
    texts = [i.text for i in items]
    results: List[Dict] = classify_posts(texts)
    for i, res in enumerate(results):
        if i < len(items):
            itm = items[i]
            itm.label = res.get("label")
            itm.confidence = res.get("confidence")
            itm.processed = True
    db.session.commit()
    return len(items)


def aggregate_window(hours=24):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    q = SentimentItem.query.filter(
        SentimentItem.processed.is_(True), SentimentItem.created_at >= cutoff
    )
    total = q.count()
    if total == 0:
        return None
    bullish = q.filter(SentimentItem.label == "bullish").count()
    bearish = q.filter(SentimentItem.label == "bearish").count()
    neutral = q.filter(SentimentItem.label == "neutral").count()
    agg = SentimentAggregate(
        window_start=cutoff,
        window_end=datetime.utcnow(),
        bullish_pct=bullish / total * 100.0,
        bearish_pct=bearish / total * 100.0,
        neutral_pct=neutral / total * 100.0,
        total=total,
    )
    db.session.add(agg)
    db.session.commit()
    return agg
