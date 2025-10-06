import os
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

# Get base path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "app.db")

# Ensure the directory exists
os.makedirs(BASE_DIR, exist_ok=True)

# Connect and create table
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Document logs table
cursor.execute("""
CREATE TABLE IF NOT EXISTS document_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    document_name TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES user (id)
)
""")

# Insert a test admin user with hashed password
admin_password_hash = generate_password_hash("admin123")
cursor.execute("""
INSERT OR IGNORE INTO user (username, password_hash, email, is_active)
VALUES (?, ?, ?, ?)
""", ("admin", admin_password_hash, "admin@example.com", True))

# Save and close
conn.commit()
conn.close()

print(f"Database created at: {db_path}")