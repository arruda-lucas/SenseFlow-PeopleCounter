import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "people_count.db"


def init_db():
    """Inicializa o banco de dados com a tabela correta"""
    conn = sqlite3.connect(DB_PATH)
    try:
        # Query em uma única linha para evitar problemas de formatação
        conn.execute(
            "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT (datetime('now', '+4 hours')), direction TEXT CHECK(direction IN ('in', 'out')))"
        )
        conn.commit()
    finally:
        conn.close()


def get_db():
    """Retorna uma conexão com o banco de dados"""
    init_db()  # Garante que a tabela existe
    return sqlite3.connect(DB_PATH)
