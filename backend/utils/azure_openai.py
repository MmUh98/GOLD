import os
import json
from typing import List, Dict
try:
    from openai import AzureOpenAI
except Exception:  # pragma: no cover
    AzureOpenAI = None  # type: ignore

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4-1")
api_key = os.getenv("AZURE_API_KEY")

client = None
if endpoint and api_key and AzureOpenAI:
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            azure_endpoint=endpoint,
        )
    except TypeError:
        # Library signature mismatch; treat as unavailable and use heuristic
        client = None
    except Exception:
        client = None

SYSTEM_PROMPT = (
    "You are a financial sentiment classifier for gold-related market text. "
    "Classify each item as bullish, bearish, or neutral for gold prices. "
    "Return strict JSON list with objects: {id: <index>, label: one of bullish|bearish|neutral, confidence: 0-1}. "
    "Only output JSON."
)

def classify_posts(posts: List[str]) -> List[Dict]:
    if not client or not posts:
        # Fallback naive heuristic if Azure not configured
        out = []
        for i, p in enumerate(posts):
            txt = p.lower()
            if any(w in txt for w in ["rally", "gain", "up", "surge", "bull"]):
                label = "bullish"
            elif any(w in txt for w in ["fall", "down", "drop", "sell", "bear"]):
                label = "bearish"
            else:
                label = "neutral"
            out.append({"id": i, "label": label, "confidence": 0.5})
        return out

    user_content = json.dumps({"items": posts})
    try:
        resp = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
            max_tokens=300,
        )
        content = resp.choices[0].message.content.strip()
        data = json.loads(content)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    # Fallback to heuristic if API call failed or response unparsable
    out = []
    for i, p in enumerate(posts):
        txt = p.lower()
        if any(w in txt for w in ["rally", "gain", "up", "surge", "bull"]):
            label = "bullish"
        elif any(w in txt for w in ["fall", "down", "drop", "sell", "bear"]):
            label = "bearish"
        else:
            label = "neutral"
        out.append({"id": i, "label": label, "confidence": 0.4})
    return out
