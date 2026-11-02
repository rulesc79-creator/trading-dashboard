# data_market.py - Market data fetcher (MT5 primary, yfinance fallback)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from datetime import datetime, timedelta
import config

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except Exception:
    MT5_AVAILABLE = False

import yfinance as yf


def _mt5_timeframe(minutes: int):
    mapping = {1: mt5.TIMEFRAME_M1, 5: mt5.TIMEFRAME_M5, 15: mt5.TIMEFRAME_M15,
               30: mt5.TIMEFRAME_M30, 60: mt5.TIMEFRAME_H1, 240: mt5.TIMEFRAME_H4,
               1440: mt5.TIMEFRAME_D1}
    return mapping.get(minutes, mt5.TIMEFRAME_D1)


def fetch_mt5(symbol: str, tf_minutes: int, count: int) -> pd.DataFrame:
    if not MT5_AVAILABLE:
        return pd.DataFrame()
    if not mt5.initialize():
        return pd.DataFrame()
    tf = _mt5_timeframe(tf_minutes)
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
    if rates is None or len(rates) == 0:
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = df.rename(columns={'time': 'Date', 'open': 'Open', 'high': 'High',
                            'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'})
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df.set_index('Date', inplace=True)
    return df


def fetch_yfinance(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if df is None or df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        df.index.name = 'Date'
        return df
    except Exception as e:
        print(f"yfinance error {ticker}: {e}")
        return pd.DataFrame()


def fetch_asset(asset: str, timeframe: str = "D1") -> pd.DataFrame:
    """Fetch OHLCV for an asset. MT5 primary, yfinance fallback."""
    tf_minutes = config.TIMEFRAMES.get(timeframe, 1440)
    count = config.BARS_COUNT.get(timeframe, 365)

    mt5_sym = config.MT5_SYMBOLS.get(asset)
    if mt5_sym:
        df = fetch_mt5(mt5_sym, tf_minutes, count)
        if not df.empty:
            df.attrs['source'] = 'MT5'
            return df

    # fallback yfinance
    ticker = config.YF_TICKERS.get(asset)
    interval = "1d" if timeframe == "D1" else "1h"
    period = "2y" if timeframe == "D1" else "60d"
    df = fetch_yfinance(ticker, period=period, interval=interval)
    if not df.empty:
        df.attrs['source'] = 'yfinance'
    return df


def fetch_all(timeframe: str = "D1") -> dict:
    result = {}
    for asset in config.ASSETS:
        df = fetch_asset(asset, timeframe)
        result[asset] = df
        src = df.attrs.get('source', 'NONE') if not df.empty else 'EMPTY'
        print(f"{asset} [{timeframe}]: {len(df)} bars, source={src}")
    return result


if __name__ == "__main__":
    print("=== D1 ===")
    fetch_all("D1")
    print("=== H4 ===")
    fetch_all("H4")
