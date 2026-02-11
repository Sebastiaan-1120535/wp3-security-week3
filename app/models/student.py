from data.database import Database
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

class Student:
    def __init__(self, db_path: str):
        self.db = Database(db_path)
    
    def find_by_id(self, student_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM "Student" WHERE student_id = ?', (student_id,))
            return cur.fetchone()
        
    def list_recent(self, limit=10):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM "Student" ', ())
            return cur.fetchall() 
        
