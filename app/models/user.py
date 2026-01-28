from data.database import Database
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


class User:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def count_all(self) -> int:
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('SELECT COUNT(*) AS c FROM "User"')
            return cur.fetchone()[0]

    def list_recent(self, limit=10):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('SELECT user_id, email, role FROM "User" ORDER BY user_id DESC LIMIT ?', (limit,))
            return cur.fetchall()

    def find_by_email(self, email: str):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM "User" WHERE email = ?', (email,))
            return cur.fetchone()

    def find_by_id(self, user_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM "User" WHERE user_id = ?', (user_id,))
            return cur.fetchone()

    def create_user(self, email: str, password: str, role: str = 'student'):
        """Create a new user. Role must be 'student', 'teacher', or 'admin'."""
        hashed = generate_password_hash(password)
        try:
            with self.db.connect() as con:
                cur = con.cursor()
                cur.execute(
                    'INSERT INTO "User" (email, password, role) VALUES (?, ?, ?)',
                    (email, hashed, role)
                )
                con.commit()
                return True, self.find_by_email(email)
        except sqlite3.IntegrityError:
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

    def delete(self, user_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                'DELETE FROM "User" WHERE user_id = ?',
                (user_id,)
            )
            con.commit()

    def update_user(self, user_id: int, email: str, role: str):
        """Update user email and role. Role must be 'student', 'teacher', or 'admin'."""
        try:
            with self.db.connect() as con:
                cur = con.cursor()
                cur.execute(
                    'UPDATE "User" SET email = ?, role = ? WHERE user_id = ?',
                    (email, role, user_id)
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
            cur.execute('UPDATE "User" SET password = ? WHERE user_id = ?', (hashed, user_id))
            con.commit()

