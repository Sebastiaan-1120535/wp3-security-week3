from data.database import Database
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

class User:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def count_all(self) -> int:
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) AS c FROM users")
            return cur.fetchone()[0]

    def list_recent(self, limit=10):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id, email, role, status FROM users ORDER BY id DESC LIMIT ?", (limit,))
            return cur.fetchall()

    def find_by_email(self, email: str):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE email = ?", (email,))
            return cur.fetchone()
        
    def find_by_id(self, user_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cur.fetchone()

    def create_user(self, email: str, password: str, role: str = 'expert', status: str = 'nieuw', organization_id=None):
        hashed = generate_password_hash(password)
        try:
            with self.db.connect() as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO users (email, password, role, status, organization_id) VALUES (?, ?, ?, ?, ?)",
                    (email, hashed, role, status, organization_id)
                )
                con.commit()
                return True, self.find_by_email(email)
        except sqlite3.IntegrityError as e:
            return False, "E-mail is al in gebruik."
        except Exception as e:
            return False, str(e)

    def authenticate(self, email: str, password: str):
        user = self.find_by_email(email)
        if not user:
            return None
        stored = user['password']
        try:
            if stored.startswith('pbkdf2:') or stored.startswith('scrypt:') or stored.startswith('argon2:'):
                ok = check_password_hash(stored, password)
                return user if ok else None
        except Exception:
            pass
        if stored == password:
            return user
        try:
            if check_password_hash(stored, password):
                return user
        except Exception:
            pass
        return None
    
    def update_status(self, user_id: int, status: str):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE users SET status = ? WHERE id = ?",
                (status, user_id)
            )
            con.commit()

    def list_pending(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM users WHERE status = 'pending' ORDER BY id"
            )
            return cur.fetchall()
        
    def delete(self, user_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,)
            )
            con.commit()
    
    def list_accepted(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id, email, role, status FROM users WHERE status = 'goedgekeurd' ORDER BY id")
            return cur.fetchall()

    def update_user(self, user_id: int, email: str, role: str, status: str):
        try:
            with self.db.connect() as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE users SET email = ?, role = ?, status = ? WHERE id = ?",
                    (email, role, status, user_id)
                )
                con.commit()
            return True, None
        except sqlite3.IntegrityError:
            return False, "E-mail is al in gebruik."
        except Exception as e:
            return False, str(e)

    def update_password(self, user_id: int, password: str):
        hashed = generate_password_hash(password)
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
            con.commit()

