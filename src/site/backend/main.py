from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta

app = FastAPI()
frontend_dir = Path(__file__).parent.parent / "frontend"

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

@app.post("/log_event")
async def log_event(direction: str):
    conn = get_db()
    conn.execute("INSERT INTO events (direction) VALUES (?)", (direction,))
    conn.commit()
    return {"status": "success"}

@app.get("/current_count")
async def get_current_count():
    conn = get_db()
    cursor = conn.execute("""
        SELECT SUM(CASE WHEN direction = 'in' THEN 1 ELSE -1 END)
        FROM events
        WHERE timestamp >= datetime('now', '-1 day')
    """)
    count = cursor.fetchone()[0] or 0
    return {"count": count}

@app.get("/today_hourly")
async def get_today_hourly():
    conn = get_db()
    cursor = conn.execute("""
        SELECT strftime('%H', timestamp) as hour,
               SUM(CASE WHEN direction = 'in' THEN 1 ELSE -1 END) as net_flow
        FROM events
        WHERE date(timestamp) = date('now', '-3 hours')
        GROUP BY hour
        ORDER BY hour
    """)
    return cursor.fetchall()

@app.get("/last_hour")
async def get_last_hour():
    conn = get_db()
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
    
    # Preenche minutos faltantes com zeros
    now = datetime.now()
    result = []
    for i in range(60):
        target_minute = (now - timedelta(minutes=59 - i)).strftime('%Y-%m-%d %H:%M:00')
        found = next((row for row in raw_data if row[0] == target_minute), None)
        label = (now - timedelta(minutes=59 - i)).strftime('%H:%M')
        if found:
            result.append([label, found[1], found[2]])
        else:
            result.append([label, 0, 0])
    
    return result

@app.get("/heatmap_data")
async def get_heatmap_data():
    conn = get_db()
    cursor = conn.execute("""
        SELECT strftime('%H', timestamp) as hour,
               strftime('%w', timestamp) as weekday,
               COUNT(*) as count
        FROM events
        GROUP BY weekday, hour
    """)
    return cursor.fetchall()

app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")