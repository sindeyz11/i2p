import sqlite3

conn = sqlite3.connect("airline.db")
cursor = conn.cursor()

passengers = cursor.execute("SELECT * FROM passengers").fetchall()
for p in passengers:
    print(p)

conn.close()
