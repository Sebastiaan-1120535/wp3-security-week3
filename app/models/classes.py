from data.database import Database
import sqlite3

class Classes:
    def __init__(self, db_path: str):
        self.db = Database(db_path)
    
    def find_by_id(self, class_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM "classes" WHERE class_id = ?', (class_id,))
            return cur.fetchone()
        
    def list_recent(self, limit=10):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM "classes"', ())
            return cur.fetchall()
