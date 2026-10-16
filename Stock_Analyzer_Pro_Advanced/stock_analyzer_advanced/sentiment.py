POSITIVE = {
    "beat", "beats", "growth", "surge", "surges", "gain", "gains", "profit", "profits",
    "strong", "record", "upgrade", "upgraded", "buy", "bullish", "rise", "rises",
    "rally", "rallies", "positive", "outperform", "higher", "revenue", "deal", "approval"
}
NEGATIVE = {
    "miss", "misses", "loss", "losses", "fall", "falls", "drop", "drops", "decline",
    "weak", "downgrade", "downgraded", "sell", "bearish", "lawsuit", "fraud", "risk",
    "cuts", "cut", "warning", "lower", "slump", "crash", "debt", "probe", "investigation"
}

def score_title(title):
    words = [w.strip(".,:;!?()[]{}'\"").lower() for w in title.split()]
    pos = sum(1 for w in words if w in POSITIVE)
    neg = sum(1 for w in words if w in NEGATIVE)
    total = pos + neg
    return max(-1.0, min(1.0, (pos - neg) / total)) if total else 0.0

def score_news(news):
    items = []
    scores = []
    for item in news:
        score = score_title(item.get("title", ""))
        label = "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"
        items.append({**item, "score": score, "label": label})
        scores.append(score)
    avg = sum(scores) / len(scores) if scores else 0.0
    label = "Positive" if avg > 0.1 else "Negative" if avg < -0.1 else "Neutral / Mixed"
    return {"average": avg, "label": label, "items": items}
