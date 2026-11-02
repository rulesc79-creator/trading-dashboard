# sentiment.py - Sentiment scoring with VADER
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import news
import config

analyzer = SentimentIntensityAnalyzer()

# Asset-relevant terms boost
BOOST = {
    "XAUUSD": {"gold": 0.3, "dollar": -0.2, "inflation": 0.2, "rates": -0.15},
    "NAS100": {"tech": 0.2, "rally": 0.2, "crash": -0.3},
    "US30": {"dow": 0.1},
    "US500": {"s&p": 0.1},
    "EURUSD": {"euro": 0.15, "ecb": 0.1},
    "GBPUSD": {"pound": 0.15, "boe": 0.1},
}


def score_text(text: str, asset: str = None) -> float:
    s = analyzer.polarity_scores(text)['compound']
    if asset and asset in BOOST:
        tl = text.lower()
        for k, v in BOOST[asset].items():
            if k in tl:
                s += v
    return max(-1.0, min(1.0, s))


def analyze_news(asset: str, limit: int = 20) -> dict:
    items = news.fetch_news(asset, limit)
    scores = [score_text(n['title'], asset) for n in items]
    if not scores:
        return {"count": 0, "avg": 0.0, "pos": 0, "neg": 0, "neu": 0, "titles": []}
    pos = sum(1 for s in scores if s > 0.05)
    neg = sum(1 for s in scores if s < -0.05)
    neu = len(scores) - pos - neg
    return {
        "count": len(scores),
        "avg": round(sum(scores) / len(scores), 4),
        "pos": pos, "neg": neg, "neu": neu,
        "titles": [(n['title'], round(s, 3)) for n, s in zip(items, scores)],
    }


if __name__ == "__main__":
    import json
    for a in config.ASSETS:
        r = analyze_news(a, 10)
        print(f"{a}: n={r['count']} avg={r['avg']} pos={r['pos']} neg={r['neg']} neu={r['neu']}")
