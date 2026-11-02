# config.py - Trading dashboard configuration
import os
from pathlib import Path
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "trading.db")

# Timezone (Jalisco, Mexico)
TZ = ZoneInfo("America/Mexico_City")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = "8941318934"

# MT5 symbols mapping: logical name -> MT5 symbol (None = use yfinance fallback)
MT5_SYMBOLS = {
    "XAUUSD": "XAUUSD",
    "US30": "US30",
    "US500": "US500",
    "EURUSD": "EURUSD",
    "GBPUSD": "GBPUSD",
    "NAS100": None,  # fallback to yfinance ^NDX
}

# yfinance fallback tickers
YF_TICKERS = {
    "XAUUSD": "GC=F",
    "NAS100": "^NDX",
    "US30": "^DJI",
    "US500": "^GSPC",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
}

ASSETS = ["XAUUSD", "NAS100", "US30", "US500", "EURUSD", "GBPUSD"]

# Timeframes for MT5 (minutes)
TIMEFRAMES = {
    "D1": 1440,
    "H4": 240,
}

# Bars to fetch
BARS_COUNT = {
    "D1": 365,
    "H4": 500,
}

# Cron hour (local TZ)
CRON_HOUR = 7
CRON_MINUTE = 0

# NewsAPI (free tier) - set via env
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# Finnhub (free tier) - set via env
FINNHUB_KEY = os.getenv("FINNHUB_KEY", "")

# Indicator thresholds
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
ADX_STRONG = 25
