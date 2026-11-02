# news.py - News fetching (RSS primary, NewsAPI/Finnhub optional)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import feedparser
import config
from datetime import datetime, timedelta


RSS_FEEDS = [
    "https://www.investing.com/rss/news.rss",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.fxstreet.com/rss/news",
]

# Keyword filters per asset (for relevance)
ASSET_KEYWORDS = {
    "XAUUSD": ["gold", "xau", "bullion", "precious metal"],
    "NAS100": ["nasdaq", "tech", "nas100", "ndx"],
    "US30": ["dow", "dow jones", "us30", "djia"],
    "US500": ["s&p", "s&p500", "sp500", "us500"],
    "EURUSD": ["euro", "ecb", "eurusd", "eurozone"],
    "GBPUSD": ["pound", "boe", "bank of england", "gbpusd", "sterling"],
}


def _relevant(title: str, asset: str) -> bool:
    t = title.lower()
    kws = ASSET_KEYWORDS.get(asset, [])
    # macro keywords always relevant
    macro = ["fed", "inflation", "cpi", "nfp", "gdp", "rates", "dollar", "dxy"]
    if any(k in t for k in macro):
        return True
    return any(k in t for k in kws)


def fetch_rss(asset: str, limit: int = 20) -> list:
    out = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:limit]:
                title = getattr(e, 'title', '')
                if _relevant(title, asset):
                    out.append({
                        "title": title,
                        "link": getattr(e, 'link', ''),
                        "published": getattr(e, 'published', ''),
                        "source": url,
                    })
        except Exception as ex:
            print(f"RSS error {url}: {ex}")
    # dedupe by title
    seen = set()
    uniq = []
    for n in out:
        if n['title'] not in seen:
            seen.add(n['title'])
            uniq.append(n)
    return uniq[:limit]


def fetch_newsapi(asset: str, limit: int = 20) -> list:
    if not config.NEWSAPI_KEY:
        return []
    kws = " OR ".join(ASSET_KEYWORDS.get(asset, [asset]))
    url = "https://newsapi.org/v2/everything"
    params = {"q": kws, "language": "en", "sortBy": "publishedAt",
              "pageSize": limit, "apiKey": config.NEWSAPI_KEY}
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        out = []
        for a in data.get("articles", []):
            out.append({"title": a.get("title", ""), "link": a.get("url", ""),
                        "published": a.get("publishedAt", ""), "source": "newsapi"})
        return out
    except Exception as e:
        print(f"NewsAPI error: {e}")
        return []


def fetch_news(asset: str, limit: int = 20) -> list:
    items = fetch_rss(asset, limit)
    if config.NEWSAPI_KEY:
        items += fetch_newsapi(asset, limit)
    # dedupe
    seen = set()
    uniq = []
    for n in items:
        if n['title'] not in seen:
            seen.add(n['title'])
            uniq.append(n)
    return uniq[:limit]


if __name__ == "__main__":
    import json
    for a in config.ASSETS:
        news = fetch_news(a, 5)
        print(f"\n=== {a}: {len(news)} titulares ===")
        for n in news[:3]:
            print(" -", n['title'][:90])
