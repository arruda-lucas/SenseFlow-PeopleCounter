from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta
import time
import asyncio
import json

app = FastAPI()
frontend_dir = Path(__file__).parent.parent / "frontend"

# Variáveis de cache
cache = {
    "current_count": {"value": 0, "timestamp": datetime.min},  # Usando datetime mínimo inicial
    "today_hourly": {"value": [], "timestamp": datetime.min},
    "last_hour": {"value": [], "timestamp": datetime.min},
    "heatmap_data": {"value": [], "timestamp": datetime.min}
}
CACHE_DURATION = 5  # segundos

def get_db():
    conn = sqlite3.connect(Path(__file__).parent / "people_count.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT (datetime('now', '-3 hours')),
        direction TEXT CHECK(direction IN ('in', 'out'))
    )
    """)
    return conn

def refresh_cache(key: str):
    """Atualiza o cache para uma chave específica se necessário"""
    now = datetime.now()
    if (now - cache[key]["timestamp"]).total_seconds() > CACHE_DURATION:
        conn = get_db()
        try:
            if key == "current_count":
                cursor = conn.execute("""
                    SELECT SUM(CASE WHEN direction = 'in' THEN 1 ELSE -1 END)
                    FROM events
                    WHERE timestamp >= datetime('now', '-1 day')
                """)
                value = cursor.fetchone()[0] or 0
            elif key == "today_hourly":
                cursor = conn.execute("""
                    SELECT strftime('%H', timestamp) as hour,
                           SUM(CASE WHEN direction = 'in' THEN 1 ELSE -1 END) as net_flow
                    FROM events
                    WHERE date(timestamp) = date('now', '-3 hours')
                    GROUP BY hour
                    ORDER BY hour
                """)
                value = cursor.fetchall()
            elif key == "last_hour":
                cursor = conn.execute("""
                    SELECT 
                        strftime('%Y-%m-%d %H:%M:00', timestamp) as minute,
                        SUM(CASE WHEN direction = 'in' THEN 1 ELSE 0 END) as entries,
                        SUM(CASE WHEN direction = 'out' THEN 1 ELSE 0 END) as exits
                    FROM events
                    WHERE timestamp >= datetime('now', '-1 hour', 'localtime')
                    GROUP BY minute
                    ORDER BY minute
                """)
                raw_data = cursor.fetchall()
                now = datetime.now()
                value = []
                for i in range(60):
                    target_minute = (now - timedelta(minutes=59 - i)).strftime('%Y-%m-%d %H:%M:00')
                    found = next((row for row in raw_data if row[0] == target_minute), None)
                    label = (now - timedelta(minutes=59 - i)).strftime('%H:%M')
                    if found:
                        value.append([label, found[1], found[2]])
                    else:
                        value.append([label, 0, 0])
            elif key == "heatmap_data":
                cursor = conn.execute("""
                    SELECT strftime('%H', timestamp) as hour,
                           strftime('%w', timestamp) as weekday,
                           COUNT(*) as count
                    FROM events
                    GROUP BY weekday, hour
                """)
                value = cursor.fetchall()
            
            cache[key]["value"] = value
            cache[key]["timestamp"] = now
        finally:
            conn.close()

@app.post("/log_event")
async def log_event(direction: str):
    conn = get_db()
    conn.execute("INSERT INTO events (direction) VALUES (?)", (direction,))
    conn.commit()
    # Invalida o cache após nova inserção
    for key in cache:
        cache[key]["timestamp"] = 0
    return {"status": "success"}

@app.get("/current_count")
async def get_current_count():
    refresh_cache("current_count")
    return {"count": cache["current_count"]["value"]}

@app.get("/today_hourly")
async def get_today_hourly():
    refresh_cache("today_hourly")
    return cache["today_hourly"]["value"]

@app.get("/last_hour")
async def get_last_hour():
    refresh_cache("last_hour")
    return cache["last_hour"]["value"]

@app.get("/heatmap_data")
async def get_heatmap_data():
    refresh_cache("heatmap_data")
    return cache["heatmap_data"]["value"]

@app.get('/updates')
async def message_stream():
    async def event_generator():
        last_count = None
        while True:
            refresh_cache("current_count")
            current_count = cache["current_count"]["value"]

            # Verifica se houve mudança na contagem
            if current_count != last_count:
                last_count = current_count
                yield f"data: {json.dumps({'current_count': current_count, 'charts_updated': True})}\n\n"
                refresh_cache("today_hourly")
                refresh_cache("last_hour")
            else:
                yield f"data: {json.dumps({'current_count': current_count, 'charts_updated': False})}\n\n"

            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")