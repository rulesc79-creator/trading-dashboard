# macro.py - Macroeconomic calendar (Finnhub free tier + fallback)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import config
from datetime import datetime, timedelta


def fetch_finnhub_calendar(days: int = 3) -> list:
    if not config.FINNHUB_KEY:
        return []
    today = datetime.utcnow().date()
    end = today + timedelta(days=days)
    url = "https://finnhub.io/api/v1/calendar/economic"
    params = {"from": str(today), "to": str(end), "token": config.FINNHUB_KEY}
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        out = []
        for e in data.get("economicCalendar", []):
            out.append({
                "event": e.get("event", ""),
                "country": e.get("country", ""),
                "impact": e.get("impact", ""),
                "actual": e.get("actual"),
                "estimate": e.get("estimate"),
                "prev": e.get("prev"),
                "time": e.get("time", ""),
            })
        return out
    except Exception as ex:
        print(f"Finnhub error: {ex}")
        return []


def high_impact_events(days: int = 3) -> list:
    events = fetch_finnhub_calendar(days)
    return [e for e in events if str(e.get("impact", "")).lower() in ("high", "3")]


def macro_risk_score(asset: str, days: int = 3) -> float:
    """Return -1..+1 risk tilt based on high-impact events. Negative = risk-off pressure."""
    events = high_impact_events(days)
    if not events:
        return 0.0
    # Simple heuristic: more high-impact USD events = more volatility; gold benefits from risk-off
    us_events = [e for e in events if e.get("country", "").upper() in ("US", "USA")]
    n = len(us_events)
    score = -min(1.0, n / 5.0) * 0.3
    if asset == "XAUUSD":
        score += 0.2  # gold tends to benefit from macro uncertainty
    return round(score, 3)


if __name__ == "__main__":
    if not config.FINNHUB_KEY:
        print("FINNHUB_KEY not set - macro module returns empty (set env var to enable)")
    else:
        ev = high_impact_events(3)
        print(f"High-impact events (3d): {len(ev)}")
        for e in ev[:10]:
            print(f"  [{e['country']}] {e['event']} ({e['impact']})")
    print("macro_risk_score XAUUSD:", macro_risk_score("XAUUSD"))
