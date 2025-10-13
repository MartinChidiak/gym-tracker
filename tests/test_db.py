import pytest
from src.utils.db import get_connection, create_exercise_table, insert_exercise, get_exercise_history

@pytest.fixture
def db_connection():
    connection = get_connection()
    yield connection
    connection.close()

def test_create_exercise_table(db_connection):
    create_exercise_table(db_connection)
    cursor = db_connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exercises';")
    table_exists = cursor.fetchone() is not None
    assert table_exists

def test_insert_exercise(db_connection):
    create_exercise_table(db_connection)
    insert_exercise(db_connection, weight=100, repetitions=10, series=3)
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM exercises;")
    exercises = cursor.fetchall()
    assert len(exercises) == 1
    assert exercises[0] == (1, 100, 10, 3)  # Assuming the table has an auto-incrementing id

def test_get_exercise_history(db_connection):
    create_exercise_table(db_connection)
    insert_exercise(db_connection, weight=100, repetitions=10, series=3)
    insert_exercise(db_connection, weight=80, repetitions=12, series=4)
    history = get_exercise_history(db_connection)
    assert len(history) == 2
    assert history[0][1] == 100  # Check weight of first exercise
    assert history[1][1] == 80   # Check weight of second exercise