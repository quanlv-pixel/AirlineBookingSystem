import sqlite3

DB_NAME = "database/airline.db"

def get_connection():
    return sqlite3.connect(DB_NAME)