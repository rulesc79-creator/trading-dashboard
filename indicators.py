# indicators.py - Technical indicators (uses 'ta' library)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import ta


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    d = df.copy()
    # RSI
    d['rsi'] = ta.momentum.RSIIndicator(d['Close'], window=14).rsi()
    # MACD
    macd = ta.trend.MACD(d['Close'], window_slow=26, window_fast=12, window_sign=9)
    d['macd'] = macd.macd()
    d['macd_signal'] = macd.macd_signal()
    d['macd_hist'] = macd.macd_diff()
    # EMAs
    d['ema20'] = ta.trend.EMAIndicator(d['Close'], window=20).ema_indicator()
    d['ema50'] = ta.trend.EMAIndicator(d['Close'], window=50).ema_indicator()
    d['ema200'] = ta.trend.EMAIndicator(d['Close'], window=200).ema_indicator()
    # Bollinger
    bb = ta.volatility.BollingerBands(d['Close'], window=20, window_dev=2)
    d['bb_high'] = bb.bollinger_hband()
    d['bb_low'] = bb.bollinger_lband()
    d['bb_mid'] = bb.bollinger_mavg()
    # ATR
    d['atr'] = ta.volatility.AverageTrueRange(d['High'], d['Low'], d['Close'], window=14).average_true_range()
    # ADX
    adx = ta.trend.ADXIndicator(d['High'], d['Low'], d['Close'], window=14)
    d['adx'] = adx.adx()
    d['adx_pos'] = adx.adx_pos()
    d['adx_neg'] = adx.adx_neg()
    # Stochastic
    stoch = ta.momentum.StochasticOscillator(d['High'], d['Low'], d['Close'], window=14, smooth_window=3)
    d['stoch_k'] = stoch.stoch()
    d['stoch_d'] = stoch.stoch_signal()
    # OBV
    d['obv'] = ta.volume.OnBalanceVolumeIndicator(d['Close'], d['Volume']).on_balance_volume()
    return d


def _fractals(df: pd.DataFrame, n: int = 2) -> tuple:
    highs = df['High'].values
    lows = df['Low'].values
    res_levels, sup_levels = [], []
    for i in range(n, len(df) - n):
        if highs[i] == max(highs[i-n:i+n+1]):
            res_levels.append(highs[i])
        if lows[i] == min(lows[i-n:i+n+1]):
            sup_levels.append(lows[i])
    return sup_levels, res_levels


def latest_summary(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {}
    d = add_indicators(df)
    last = d.iloc[-1]
    sup, res = _fractals(d.tail(60))
    close = float(last['Close'])
    # nearest support/resistance
    sup_below = [x for x in sup if x < close]
    res_above = [x for x in res if x > close]
    nearest_sup = max(sup_below) if sup_below else None
    nearest_res = min(res_above) if res_above else None
    # candle pattern (last bar)
    o, h, l, c = float(last['Open']), float(last['High']), float(last['Low']), float(last['Close'])
    body = abs(c - o)
    rng = h - l if h - l > 0 else 1e-9
    pattern = "neutral"
    if body / rng < 0.1:
        pattern = "doji"
    elif (min(o, c) - l) > 2 * body and (h - max(o, c)) < body:
        pattern = "hammer"
    elif (h - max(o, c)) > 2 * body and (min(o, c) - l) < body:
        pattern = "shooting_star"
    return {
        "close": close,
        "rsi": float(last['rsi']) if pd.notna(last['rsi']) else None,
        "macd": float(last['macd']) if pd.notna(last['macd']) else None,
        "macd_signal": float(last['macd_signal']) if pd.notna(last['macd_signal']) else None,
        "macd_hist": float(last['macd_hist']) if pd.notna(last['macd_hist']) else None,
        "ema20": float(last['ema20']) if pd.notna(last['ema20']) else None,
        "ema50": float(last['ema50']) if pd.notna(last['ema50']) else None,
        "ema200": float(last['ema200']) if pd.notna(last['ema200']) else None,
        "bb_high": float(last['bb_high']) if pd.notna(last['bb_high']) else None,
        "bb_low": float(last['bb_low']) if pd.notna(last['bb_low']) else None,
        "atr": float(last['atr']) if pd.notna(last['atr']) else None,
        "adx": float(last['adx']) if pd.notna(last['adx']) else None,
        "adx_pos": float(last['adx_pos']) if pd.notna(last['adx_pos']) else None,
        "adx_neg": float(last['adx_neg']) if pd.notna(last['adx_neg']) else None,
        "stoch_k": float(last['stoch_k']) if pd.notna(last['stoch_k']) else None,
        "stoch_d": float(last['stoch_d']) if pd.notna(last['stoch_d']) else None,
        "nearest_support": nearest_sup,
        "nearest_resistance": nearest_res,
        "candle_pattern": pattern,
        "bars": len(d),
    }


if __name__ == "__main__":
    import json
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import data_market
    df = data_market.fetch_asset("XAUUSD", "D1")
    s = latest_summary(df)
    print(json.dumps(s, indent=2, default=str))
