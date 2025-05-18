import sqlite3

def get_db():
    conn = sqlite3.connect("airline.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS aircraft (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT NOT NULL,
        capacity INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_number TEXT NOT NULL,
        departure TEXT NOT NULL,
        arrival TEXT NOT NULL,
        datetime TEXT NOT NULL,
        aircraft_id INTEGER,
        FOREIGN KEY (aircraft_id) REFERENCES aircraft(id)
    );

    CREATE TABLE IF NOT EXISTS passengers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        flight_id INTEGER,
        FOREIGN KEY (flight_id) REFERENCES flights(id)
    );
    """)

    conn.commit()
    conn.close()

