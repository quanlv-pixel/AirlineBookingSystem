import sqlite3
import os

DB_PATH = "database/airline.db"
SCHEMA_PATH = "database/schema.sql"

def init_db():
    conn = sqlite3.connect(DB_PATH)

    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())

    conn.commit()
    conn.close()