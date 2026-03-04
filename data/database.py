import sqlite3
from werkzeug.security import generate_password_hash

CLASSES = [
    {
        "id": 1,
        "name": "1A",
        "teachter_id": 1,   
    },
    {
        "id": 2,
        "name": "1B",
        "teachter_id": 2,
    }
]


TEACHERS = [
    "sarah", "michael",
]


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self):
        """Create a connection to the SQLite database with row factory for dict-like access."""
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con
    
    def setup(self):

        with self.connect() as con:
            cur = con.cursor()

            # Insert initial teachers if they don't exist
            for teacher_name in TEACHERS:

                email = f"{teacher_name}@test.nl"
                hashed = generate_password_hash(email)

                cur.execute(
                    """INSERT OR IGNORE INTO users (email, password, role)
                    VALUES (?, ?, ?)""",
                    (f"{teacher_name}@test.nl", hashed, "teacher"),
                )

                user_id = cur.lastrowid

                print(user_id)

                if user_id and user_id >= 1:
                    cur.execute(
                        """INSERT OR IGNORE INTO teachers (first_name, last_name, user_id)
                        VALUES (?, ?, ?)""",
                        (teacher_name, "", user_id),
                    )

            # Insert initial classes if they don't exist
            for cls in CLASSES:
                cur.execute(
                    """INSERT OR IGNORE INTO classes (class_id, name, teacher_id)
                    VALUES (?, ?, ?)""",
                    (cls["id"], cls["name"], cls["teachter_id"]),
                )

            con.commit()



