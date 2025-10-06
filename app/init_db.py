import sqlite3
import os

# Make sure the folder exists
db_folder = 'database'
db_file = 'mydb.sqlite3'
os.makedirs(db_folder, exist_ok=True)

# Full path to database file
db_path = os.path.join(db_folder, db_file)

# Connect and create tables
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Example table (change based on your actual schema)
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print(f"Database created at {db_path}")