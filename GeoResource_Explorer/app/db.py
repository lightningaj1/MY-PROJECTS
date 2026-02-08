import sqlite3
import os
from flask import g, current_app

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'minerals.db')

def get_db():
    """
    Get or create a database connection for the current request.
    Connections are cached in Flask's application context (g object).
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False,
            timeout=5.0  # 5 second timeout for database lock
        )
        g.db.row_factory = sqlite3.Row
        # Enable foreign keys for referential integrity
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(e=None):
    """
    Close database connection at the end of request.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db_connection(app):
    """
    Initialize database connection handling for Flask app.
    """
    app.teardown_appcontext(close_db)
