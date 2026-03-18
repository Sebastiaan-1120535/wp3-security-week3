from data.database import Database
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

class Student:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def find_by_user_id(self, user_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('''
                        SELECT * FROM "students" 
                            JOIN "classes" ON students.class_id = classes.class_id 
                        WHERE user_id = ?''', (user_id,))
            return cur.fetchone()
    
    def find_by_id(self, student_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('''
                        SELECT * FROM "students" 
                            JOIN "classes" ON students.class_id = classes.class_id 
                        WHERE students.student_id = ?''', (student_id,))
            return cur.fetchone()
        
    def list_recent(self, class_id=None, limit=10):
        with self.db.connect() as con:
            cur = con.cursor()

            if class_id is None:
                cur.execute('''
                            SELECT * FROM "students" 
                                JOIN "classes" ON students.class_id = classes.class_id 
                            ORDER BY classes.name
                            LIMIT ?''', (limit,))
            else:

                cur.execute('''
                            SELECT * FROM "students" 
                                JOIN "classes" ON students.class_id = classes.class_id 
                                WHERE students.class_id = ?
                            ORDER BY students.first_name
                            LIMIT ?''', (class_id, limit,))
            
            return cur.fetchall()
    
    def find_by_class_id(self, class_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('''
                        SELECT * FROM "students" 
                            JOIN "classes" ON students.class_id = classes.class_id
                        WHERE students.class_id = ?''', (class_id,))
            return cur.fetchall() 
        
    
        
