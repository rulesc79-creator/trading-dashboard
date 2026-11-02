# dashboard.py - FastAPI web dashboard
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import analysis
import config

app = FastAPI(title="Trading Dashboard")

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Trading Dashboard</title>
<style>
body{font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:20px;}
h1{color:#38bdf8;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;}
.card{background:#1e293b;border-radius:12px;padding:16px;border:1px solid #334155;}
.asset{font-size:1.3em;font-weight:700;}
.signal{font-weight:700;padding:4px 10px;border-radius:6px;display:inline-block;}
.LONG{background:#16a34a;color:#fff;}
.SHORT{background:#dc2626;color:#fff;}
.NEUTRAL{background:#475569;color:#fff;}
.score{font-size:1.1em;margin:8px 0;}
.reasons{font-size:0.85em;color:#94a3b8;margin-top:8px;}
.levels{font-size:0.9em;margin-top:6px;color:#cbd5e1;}
button{background:#38bdf8;color:#0f172a;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;font-weight:600;}
</style>
</head>
<body>
<h1>📈 Trading Dashboard</h1>
<p>Activos: XAUUSD, NAS100, US30, US500, EURUSD, GBPUSD</p>
<button onclick="load()">Actualizar análisis</button>
<div id="grid" class="grid"></div>
<script>
async function load(){
  const r = await fetch('/api/analyze');
  const data = await r.json();
  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  data.forEach(d=>{
    const card = document.createElement('div');
    card.className='card';
    const sig = d.signal||'NEUTRAL';
    const levels = sig!=='NEUTRAL' ? `<div class="levels">Entry ${d.entry} | SL ${d.stop_loss} | TP ${d.take_profit}</div>` : '';
    card.innerHTML = `
      <div class="asset">${d.asset}</div>
      <div><span class="signal ${sig}">${sig}</span></div>
      <div class="score">Score: ${d.score} (conf ${d.confidence}) | Close ${d.close}</div>
      <div>RSI ${d.rsi?d.rsi.toFixed(1):'-'} | ADX ${d.adx?d.adx.toFixed(1):'-'} | ATR ${d.atr?d.atr.toFixed(4):'-'}</div>
      <div>Sentimiento: ${d.sentiment.avg} (n=${d.sentiment.count})</div>
      ${levels}
      <div class="reasons">${(d.reasons||[]).join(' · ')}</div>
    `;
    grid.appendChild(card);
  });
}
load();
</script>
</body></html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    return HTML


@app.get("/api/analyze")
def api_analyze():
    return analysis.analyze_all("D1")


@app.get("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
