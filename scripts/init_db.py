import sqlite3

def init_db():
    conn = sqlite3.connect('exercises.db')
    cursor = conn.cursor()

    # Create table for exercises
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT NOT NULL,
            weight REAL NOT NULL,
            repetitions INTEGER NOT NULL,
            series INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()