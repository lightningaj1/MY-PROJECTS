import sqlite3
import os

def get_db():
    # Use database in project root for consistency
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'minerals.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
