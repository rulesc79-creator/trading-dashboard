# analysis.py - Composite scoring per asset
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import data_market, indicators, sentiment, macro, config


def technical_score(s: dict) -> tuple:
    """Return (score -100..100, reasons list)."""
    score = 0.0
    reasons = []
    close = s['close']
    rsi = s.get('rsi')
    macd_hist = s.get('macd_hist')
    ema20 = s.get('ema20'); ema50 = s.get('ema50'); ema200 = s.get('ema200')
    adx = s.get('adx'); adx_pos = s.get('adx_pos'); adx_neg = s.get('adx_neg')
    stoch_k = s.get('stoch_k')
    bb_low = s.get('bb_low'); bb_high = s.get('bb_high')
    pattern = s.get('candle_pattern')

    # RSI
    if rsi is not None:
        if rsi < 30:
            score += 20; reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > 70:
            score -= 20; reasons.append(f"RSI overbought ({rsi:.1f})")
        elif rsi < 45:
            score += 8
        elif rsi > 55:
            score -= 8

    # MACD
    if macd_hist is not None:
        if macd_hist > 0:
            score += 15; reasons.append("MACD hist positive")
        else:
            score -= 15; reasons.append("MACD hist negative")

    # EMAs trend
    if ema20 and ema50 and ema200:
        if close > ema20 > ema50 > ema200:
            score += 25; reasons.append("Price above EMAs (bullish stack)")
        elif close < ema20 < ema50 < ema200:
            score -= 25; reasons.append("Price below EMAs (bearish stack)")
        elif close > ema200:
            score += 8
        else:
            score -= 8

    # ADX strength + direction
    if adx is not None and adx > config.ADX_STRONG:
        if adx_pos and adx_neg and adx_pos > adx_neg:
            score += 12; reasons.append(f"ADX strong bullish ({adx:.1f})")
        elif adx_pos and adx_neg and adx_neg > adx_pos:
            score -= 12; reasons.append(f"ADX strong bearish ({adx:.1f})")

    # Stochastic
    if stoch_k is not None:
        if stoch_k < 20:
            score += 8
        elif stoch_k > 80:
            score -= 8

    # Bollinger position
    if bb_low and bb_high:
        if close <= bb_low:
            score += 8; reasons.append("Price at lower BB")
        elif close >= bb_high:
            score -= 8; reasons.append("Price at upper BB")

    # Candle pattern
    if pattern == "hammer":
        score += 6; reasons.append("Hammer candle")
    elif pattern == "shooting_star":
        score -= 6; reasons.append("Shooting star candle")

    return score, reasons


def analyze_asset(asset: str, timeframe: str = "D1") -> dict:
    df = data_market.fetch_asset(asset, timeframe)
    if df.empty:
        return {"asset": asset, "error": "no data"}
    s = indicators.latest_summary(df)
    tech_score, tech_reasons = technical_score(s)

    sent = sentiment.analyze_news(asset, 15)
    sent_score = sent['avg'] * 25  # -25..+25

    macro_score = macro.macro_risk_score(asset) * 20  # -6..+6

    # structure score: distance to support/resistance
    struct_score = 0.0
    close = s['close']
    sup = s.get('nearest_support'); res = s.get('nearest_resistance')
    if sup and res:
        mid = (sup + res) / 2
        if close < mid:
            struct_score += 5  # closer to support
        else:
            struct_score -= 5

    total = tech_score * 0.4 + sent_score + macro_score + struct_score
    total = max(-100, min(100, total))

    # signal
    if total >= 25:
        signal = "LONG"
    elif total <= -25:
        signal = "SHORT"
    else:
        signal = "NEUTRAL"

    # levels by ATR
    atr = s.get('atr') or (close * 0.01)
    if signal == "LONG":
        entry = close
        sl = close - 1.5 * atr
        tp = close + 3 * atr
    elif signal == "SHORT":
        entry = close
        sl = close + 1.5 * atr
        tp = close - 3 * atr
    else:
        entry = close; sl = None; tp = None

    return {
        "asset": asset,
        "timeframe": timeframe,
        "close": round(close, 5),
        "score": round(total, 1),
        "signal": signal,
        "confidence": round(abs(total), 1),
        "technical_score": round(tech_score, 1),
        "sentiment_score": round(sent_score, 1),
        "macro_score": round(macro_score, 1),
        "structure_score": round(struct_score, 1),
        "rsi": s.get('rsi'),
        "adx": s.get('adx'),
        "atr": atr,
        "nearest_support": sup,
        "nearest_resistance": res,
        "candle_pattern": s.get('candle_pattern'),
        "sentiment": {"avg": sent['avg'], "pos": sent['pos'], "neg": sent['neg'], "count": sent['count']},
        "entry": round(entry, 5) if entry else None,
        "stop_loss": round(sl, 5) if sl else None,
        "take_profit": round(tp, 5) if tp else None,
        "reasons": tech_reasons,
    }


def analyze_all(timeframe: str = "D1") -> list:
    out = []
    for a in config.ASSETS:
        out.append(analyze_asset(a, timeframe))
    return out


if __name__ == "__main__":
    import json
    res = analyze_all("D1")
    for r in res:
        print(f"{r['asset']}: score={r['score']} signal={r['signal']} conf={r['confidence']}")
    print("\nFull JSON (first asset):")
    print(json.dumps(res[0], indent=2, default=str))
