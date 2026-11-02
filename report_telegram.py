# report_telegram.py - Daily report to Telegram
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import analysis
import config


SIGNAL_ES = {"LONG": "ALCISTA", "SHORT": "BAJISTA", "NEUTRAL": "LATERAL"}

def build_report(results: list) -> str:
    lines = ["📊 Reporte Matutino de Trading", ""]
    for r in results:
        if "error" in r:
            lines.append(f"{r['asset']}: ERROR {r['error']}")
            continue
        tendencia = SIGNAL_ES.get(r['signal'], r['signal'])
        emoji = "🟢" if r['signal'] == "LONG" else ("🔴" if r['signal'] == "SHORT" else "⚪")
        lines.append(f"{emoji} {r['asset']} | {tendencia} | score {r['score']} (confianza {r['confidence']})")
        lines.append(f"   Precio: {r['close']} | RSI {r['rsi']:.1f} | ADX {r['adx']:.1f}" if r.get('rsi') else f"   Precio: {r['close']}")
        if r['signal'] != "NEUTRAL":
            lines.append(f"   Entrada {r['entry']} | Stop Loss {r['stop_loss']} | Take Profit {r['take_profit']}")
        if r.get('reasons'):
            lines.append("   " + "; ".join(r['reasons'][:3]))
        lines.append("")
    lines.append("— Generado automáticamente")
    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    if not config.TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not set - printing report instead")
        print(text)
        return False
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": config.TELEGRAM_CHAT_ID, "text": text}
    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        print("Telegram sent OK")
        return True
    except Exception as e:
        print(f"Telegram error: {e}")
        return False


def run_daily_report(timeframe: str = "D1") -> str:
    results = analysis.analyze_all(timeframe)
    text = build_report(results)
    send_telegram(text)
    return text


if __name__ == "__main__":
    txt = run_daily_report("D1")
    print("\n" + txt)
