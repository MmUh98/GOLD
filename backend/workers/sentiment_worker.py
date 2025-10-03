import time
from datetime import datetime
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from app import create_app  # noqa: E402
from langgraph_workflows.sentiment_graph import classify_unprocessed, aggregate_window  # noqa: E402

app = create_app()

def run_once():
    with app.app_context():
        classified = classify_unprocessed()
        if classified:
            print(f"[sentiment_worker] Classified {classified} items @ {datetime.utcnow().isoformat()}")
        agg = aggregate_window()
        if agg:
            print(
                f"[sentiment_worker] Aggregate updated bullish={agg.bullish_pct:.1f}% bearish={agg.bearish_pct:.1f}% neutral={agg.neutral_pct:.1f}% total={agg.total}"
            )

def run_loop(interval=60):
    while True:
        run_once()
        time.sleep(interval)

if __name__ == "__main__":
    run_loop()
