
from pathlib import Path
import sqlite3
from typing import List, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "exercises.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_name TEXT,
    weight REAL NOT NULL,
    repetitions INTEGER NOT NULL,
    series INTEGER NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)

def create_exercise_table(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    conn.commit()

def insert_exercise(conn: sqlite3.Connection, exercise_name: str, weight: float, repetitions: int, series: int) -> None:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO exercises (exercise_name, weight, repetitions, series) VALUES (?, ?, ?, ?)",
        (exercise_name, weight, repetitions, series),
    )
    conn.commit()

def get_exercise_history(conn: Optional[sqlite3.Connection] = None) -> List[Dict]:
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    create_exercise_table(conn)
    cursor = conn.cursor()
    cursor.execute("SELECT id, exercise_name, weight, repetitions, series, date FROM exercises ORDER BY date DESC")
    rows = cursor.fetchall()

    history = [
        {
            "id": r[0],
            "exercise_name": r[1],
            "weight": r[2],
            "repetitions": r[3],
            "series": r[4],
            "date": r[5],
        }
        for r in rows
    ]

    if close_conn:
        conn.close()
    return history

def log_exercise(weight: float, repetitions: int, series: int, exercise_name: str = "") -> None:
    conn = get_connection()
    try:
        create_exercise_table(conn)
        insert_exercise(conn, exercise_name, weight, repetitions, series)
    finally:
        conn.close()

# --- NUEVA FUNCIÓN: eliminar registro por id ---
def delete_exercise(record_id: int) -> None:
    """
    Borra un registro por su id (columna 'id' en la tabla 'exercises').
    """
    conn = get_connection()
    try:
        create_exercise_table(conn)
        cur = conn.cursor()
        cur.execute("DELETE FROM exercises WHERE id = ?", (int(record_id),))
        conn.commit()
    finally:
        conn.close()
