import sqlite3
from werkzeug.security import generate_password_hash

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self):
        """Create a connection to the SQLite database with row factory for dict-like access."""
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con
    