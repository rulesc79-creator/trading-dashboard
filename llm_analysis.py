import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
import config
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"
SYSTEM_PROMPT = """Eres un analista de trading profesional. Te doy un reporte técnico con
indicadores, sentimiento de noticias, macro y un score compuesto (-100 a +100).
Para cada activo responde en español con:
1. Recomendación: COMPRAR / VENDER / MANTENER
2. Confianza: 1-10
3. Razón principal (1 línea)
4. Riesgo clave (1 línea)
5. Niveles: entrada, stop loss, take profit (si aplica)
Sé conciso. No inventes datos que no estén en el reporte. Máximo 5 líneas por activo.
Al final una línea de "Riesgo global:" con el riesgo principal del día."""
def analyze_report(report_text: str) -> str | None:
    api_key = (getattr(config, "GROQ_API_KEY", "") or "").strip() or os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return None
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": report_text},
        ],
        "temperature": 0.3,
        "max_tokens": 800,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        r = requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Groq error: {e}")
        return None
if __name__ == "__main__":
    import sys
    text = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not text:
        text = "📊 Reporte Matutino de Trading\n⚪ XAUUSD | LATERAL | score -13.4"
    res = analyze_report(text)
    if res:
        print("🤖 Análisis IA:\n" + res)
    else:
        print("GROQ_API_KEY not set or error")
