import sqlite3
from pathlib import Path

DB_PATH = Path("data/app.db")
SCHEMA_PATH = Path("repositories/schema.sql")

def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row #permite acceder por el nombre de columna
    return conn

def init_db():
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    # Ejecuta query de SQL para crear la tabla "conversations"
    with get_connection() as conn:
        conn.executescript(schema)