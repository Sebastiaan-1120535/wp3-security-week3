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
    
    def find_by_teacher_id(self, teacher_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM "classes" WHERE teacher_id = ?', (teacher_id,))
            return cur.fetchall()
        
    def get_learings_goals(self, class_name: str):

        with self.db.connect() as con:
            cur = con.cursor()

            cur.execute('SELECT subject_id FROM "subjects" WHERE name = ?', (class_name,))
            subject = cur.fetchone()

            cur.execute('SELECT learning_goal_id, title FROM "learning_goals" WHERE subject_id = ?', (subject['subject_id'],))
            goals = cur.fetchall()

            result = []
            for goal in goals:
                cur.execute('SELECT topic FROM "keywords" WHERE learning_goal_id = ?', (goal['learning_goal_id'],))
                keywords = [kw['topic'] for kw in cur.fetchall()][:5]

                goal_dict = dict(goal)
                goal_dict['keywords'] = keywords
                result.append({
                    'id': goal_dict['learning_goal_id'],
                    'title': goal_dict['title'],
                    'subject': "Algemene Vaardigheden",
                    'keywords': keywords,
                    "has_data": len(keywords) > 0
                })

            return result
        

            