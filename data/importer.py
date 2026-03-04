import json
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash
import random

try:
    import ijson

    HAS_IJSON = True
except ImportError:
    HAS_IJSON = False

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
    {
        "id": 1,
        "name": "sarah",
    },
    {
        "id": 2,
        "name": "michael",
    }
]

class DataImporter:
    BATCH_SIZE = 1000

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.con = None
        self.cur = None
        self._student_cache = {}
        self._subject_cache = {}
        self._teacher_cache = {}
        self._class_cache = {}
        self._taxonomy_level_cache = {}
        self._learning_goal_cache = set()
        self._keyword_cache = set()

    def _connect(self):
        self.con = sqlite3.connect(self.db_path)
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys = ON")
        self.con.execute("PRAGMA journal_mode = WAL")
        self.con.execute("PRAGMA synchronous = NORMAL")
        self.con.execute("PRAGMA cache_size = -64000")
        self.con.execute("PRAGMA temp_store = MEMORY")
        self.cur = self.con.cursor()

    def _close(self):
        if self.con:
            self.con.close()
            self.con = None
            self.cur = None

    def clean_up_database(self):
        self._connect()
        try:

            self._student_cache = {}
            self._subject_cache = {}
            self._teacher_cache = {}
            self._class_cache = {}
            self._taxonomy_level_cache = {}
            self._learning_goal_cache = set()
            self._keyword_cache = set()

            self.cur.execute("DELETE FROM classes")
            self.cur.execute("DELETE FROM keywords")
            self.cur.execute("DELETE FROM learning_goals")
            self.cur.execute("DELETE FROM snapshots")
            self.cur.execute("DELETE FROM sources")
            self.cur.execute("DELETE FROM students")
            self.cur.execute("DELETE FROM subjects")
            self.cur.execute("DELETE FROM taxonomy_levels")
            self.cur.execute("DELETE FROM taxonomy_scores")
            self.cur.execute("DELETE FROM teachers")
            self.cur.execute("DELETE FROM users")
            self.con.commit()

        finally:
            print("tabels geleegd, klaar voor nieuwe import")
            self._close()

    def init_schema(self):
        self._connect()
        try:
            self.cur.execute(
                """
                             CREATE TABLE IF NOT EXISTS users
                             (
                                 user_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                                 email    TEXT UNIQUE NOT NULL,
                                 password TEXT        NOT NULL,
                                 role     TEXT        NOT NULL DEFAULT 'student'
                                     CHECK (role IN ('student', 'teacher', 'admin'))
                             )
                             """
            )

            self.cur.execute(
                """
                             CREATE TABLE IF NOT EXISTS classes
                             (
                                 class_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                                 name       TEXT NOT NULL,
                                 teacher_id INTEGER,
                                 FOREIGN KEY (teacher_id) REFERENCES users (user_id)
                             )
                             """
            )

            self.cur.execute(
                """
                             CREATE TABLE IF NOT EXISTS students
                             (
                                 student_id INTEGER PRIMARY KEY,
                                 first_name TEXT NOT NULL,
                                 last_name  TEXT,
                                 user_id    INTEGER,
                                 class_id   INTEGER,
                                 FOREIGN KEY (user_id) REFERENCES users (user_id),
                                 FOREIGN KEY (class_id) REFERENCES classes (class_id)
                             )
                             """
            )

            self.cur.execute(
                """
                             CREATE TABLE IF NOT EXISTS subjects
                             (
                                 subject_id INTEGER PRIMARY KEY,
                                 name       TEXT NOT NULL
                             )
                             """
            )

            self.cur.execute(
                """
                             CREATE TABLE IF NOT EXISTS taxonomy_levels
                             (
                                 taxonomy_level_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 name              TEXT    NOT NULL,
                                 subject_id        INTEGER NOT NULL,
                                 FOREIGN KEY (subject_id) REFERENCES subjects (subject_id),
                                 UNIQUE (name, subject_id)
                             )
                             """
            )

            self.cur.execute(
                """
                             CREATE TABLE IF NOT EXISTS learning_goals
                             (
                                 learning_goal_id TEXT PRIMARY KEY,
                                 title            TEXT    NOT NULL,
                                 subject_id       INTEGER NOT NULL,
                                 FOREIGN KEY (subject_id) REFERENCES subjects (subject_id)
                             )
                             """
            )

            self.cur.execute(
                """
                             CREATE TABLE IF NOT EXISTS keywords
                             (
                                 keyword_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                                 topic            TEXT NOT NULL,
                                 learning_goal_id TEXT NOT NULL,
                                 FOREIGN KEY (learning_goal_id) REFERENCES learning_goals (learning_goal_id)
                             )
                             """
            )

            self.cur.execute(
                """
                             CREATE TABLE IF NOT EXISTS sources
                             (
                                 source_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                                 type       TEXT NOT NULL,
                                 display_id TEXT NOT NULL
                             )
                             """
            )

            self.cur.execute(
                """
                             CREATE TABLE IF NOT EXISTS snapshots
                             (
                                 snapshot_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                                 at               TEXT    NOT NULL,
                                 source_id        INTEGER NOT NULL,
                                 class_id         INTEGER,
                                 student_id       INTEGER NOT NULL,
                                 learning_goal_id TEXT    NOT NULL,
                                 FOREIGN KEY (source_id) REFERENCES sources (source_id),
                                 FOREIGN KEY (class_id) REFERENCES classes (class_id),
                                 FOREIGN KEY (student_id) REFERENCES students (student_id),
                                 FOREIGN KEY (learning_goal_id) REFERENCES learning_goals (learning_goal_id)
                             )
                             """
            )

            self.cur.execute(
                """
                             CREATE TABLE IF NOT EXISTS taxonomy_scores
                             (
                                 taxonomy_score_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 know              REAL    NOT NULL,
                                 can               REAL    NOT NULL,
                                 confidence        REAL    NOT NULL,
                                 snapshot_id       INTEGER NOT NULL,
                                 taxonomy_level_id INTEGER NOT NULL,
                                 FOREIGN KEY (snapshot_id) REFERENCES snapshots (snapshot_id),
                                 FOREIGN KEY (taxonomy_level_id) REFERENCES taxonomy_levels (taxonomy_level_id)
                             )
                             """
            )

            self.cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_snapshots_student ON snapshots(student_id)"
            )
            self.cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_snapshots_learning_goal ON snapshots(learning_goal_id)"
            )
            self.cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_snapshots_at ON snapshots(at)"
            )
            self.cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_taxonomy_scores_snapshot ON taxonomy_scores(snapshot_id)"
            )
            self.cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_keywords_learning_goal ON keywords(learning_goal_id)"
            )
            self.cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_learning_goals_subject ON learning_goals(subject_id)"
            )
            self.cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id)"
            )

            self.con.commit()
        finally:
            self._close()

    def _load_existing_data(self):
        self.cur.execute("SELECT student_id FROM students")
        for row in self.cur.fetchall():
            self._student_cache[row[0]] = row[0]

        self.cur.execute("SELECT subject_id FROM subjects")
        for row in self.cur.fetchall():
            self._subject_cache[row[0]] = row[0]

        self.cur.execute(
            "SELECT taxonomy_level_id, name, subject_id FROM taxonomy_levels"
        )
        for row in self.cur.fetchall():
            key = (row[1], row[2])
            self._taxonomy_level_cache[key] = row[0]

        self.cur.execute("SELECT learning_goal_id FROM learning_goals")
        for row in self.cur.fetchall():
            self._learning_goal_cache.add(row[0])

    def import_json(self, json_file: str):
        print("Import gestart...")
        self._connect()
        try:
            self.init_schema()
            self._connect()
            self._load_existing_data()

            file_size = Path(json_file).stat().st_size
            use_streaming = HAS_IJSON and file_size > 50 * 1024 * 1024

            if use_streaming:
                self._import_streaming(json_file)
            else:
                self._import_standard(json_file)

            self._print_summary()
        except Exception as e:
            if self.con:
                self.con.rollback()
            raise
        finally:
            self._close()

    def _import_standard(self, json_file: str):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        entries = data.get("entries", [])
        total = len(entries)

        for idx, entry in enumerate(entries, 1):
            self._import_entry(entry)
            if idx % self.BATCH_SIZE == 0:
                self.con.commit()

        self.con.commit()

    def _import_streaming(self, json_file: str):
        with open(json_file, "rb") as f:
            entries = ijson.items(f, "entries.item")

            idx = 0
            for entry in entries:
                idx += 1
                self._import_entry(entry)
                if idx % self.BATCH_SIZE == 0:
                    self.con.commit()

            self.con.commit()

    def _import_entry(self, entry: dict):
        
        student_data = entry.get("student", {})
        subject_data = entry.get("subject", {})

        learning_goals = entry.get("learningGoals", [])
        taxonomy_scale = entry.get("taxonomyScale", [])


        for teacher in TEACHERS:
            self._ensure_teacher(teacher.get("id", {}), teacher.get("name", "Unknown"))

        for cls in CLASSES:
            self._ensure_class(cls.get("id", {}), cls.get("name", "Unknown"), cls.get("teachter_id", {}))

        student_id = self._ensure_student(
            student_data.get("id"), student_data.get("name", "Unknown")
        )

        subject_id = self._ensure_subject(
            subject_data.get("id"), subject_data.get("name", "Unknown")
        )

        taxonomy_level_map = {}
        for level_name in taxonomy_scale:
            level_id = self._ensure_taxonomy_level(level_name, subject_id)
            taxonomy_level_map[level_name] = level_id

        for lg in learning_goals:
            lg_id = lg.get("id")
            lg_title = lg.get("title", "Untitled")

            self._ensure_learning_goal(lg_id, lg_title, subject_id)

            keywords = lg.get("keywords", [])
            for keyword in keywords:
                self._insert_keyword(keyword, lg_id)

            snapshots = lg.get("snapshots", [])
            for snapshot in snapshots:
                self._import_snapshot(snapshot, student_id, lg_id, taxonomy_level_map)

    def _ensure_teacher(self, teacher_id: int, name: str):

        if teacher_id in self._teacher_cache:
            return 

        email = f"{name}@test.nl"
        password_hash = generate_password_hash(email)

        if self.cur:

            self.cur.execute(
                """INSERT OR IGNORE INTO users (email, password, role)
                VALUES (?, ?, ?)""",
                (email, password_hash, "teacher"),
            )

            user_id = self.cur.lastrowid
            if user_id is None:
                return

            self.cur.execute(
                """INSERT OR IGNORE INTO teachers (first_name, last_name, user_id)
                VALUES (?, ?, ?)""",
                (name, "", user_id),
            )

            self._teacher_cache[teacher_id] = teacher_id

    def _ensure_class(self, class_id: int, name: str, teacher_id: int):

        if class_id in self._class_cache:
            return 

        if self.cur:

            self.cur.execute(
                """INSERT OR IGNORE INTO classes (class_id, name, teacher_id)
                VALUES (?, ?, ?)""",
                (class_id, name, teacher_id),
            )

            self._class_cache[class_id] = class_id
        
    
    def _ensure_student(self, student_id: int, name: str) -> int:

        if student_id in self._student_cache:
            return student_id
        
        if self.cur:

            parts = name.split(" ", 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""

            hashed = generate_password_hash(f"{first_name}@test.nl")

            self.cur.execute(
                """INSERT OR IGNORE INTO users (email, password, role)
                VALUES (?, ?, ?)""",
                (f"{first_name}@test.nl", hashed, "student"),
            )

            if self.cur:
                user_id = self.cur.lastrowid
        
                class_ids = [cls.get("id") for cls in CLASSES]
                class_id = random.choice(class_ids)

                self.cur.execute(
                    """INSERT OR IGNORE INTO students (student_id, first_name, last_name, user_id, class_id)
                    VALUES (?, ?, ?, ?, ?)""",
                    (student_id, first_name, last_name, user_id, class_id),
                )

            self._student_cache[student_id] = student_id

        return student_id

    def _ensure_subject(self, subject_id: int, name: str) -> int:
        if subject_id in self._subject_cache:
            return subject_id

        self.cur.execute(
            "INSERT OR IGNORE INTO subjects (subject_id, name) VALUES (?, ?)",
            (subject_id, name),
        )
        self._subject_cache[subject_id] = subject_id
        return subject_id

    def _ensure_taxonomy_level(self, name: str, subject_id: int) -> int:
        key = (name, subject_id)
        if key in self._taxonomy_level_cache:
            return self._taxonomy_level_cache[key]

        self.cur.execute(
            "INSERT OR IGNORE INTO taxonomy_levels (name, subject_id) VALUES (?, ?)",
            (name, subject_id),
        )

        self.cur.execute(
            "SELECT taxonomy_level_id FROM taxonomy_levels WHERE name = ? AND subject_id = ?",
            (name, subject_id),
        )
        result = self.cur.fetchone()
        level_id = result[0]
        self._taxonomy_level_cache[key] = level_id
        return level_id

    def _ensure_learning_goal(self, lg_id: str, title: str, subject_id: int):
        if lg_id in self._learning_goal_cache:
            return

        self.cur.execute(
            "INSERT OR IGNORE INTO learning_goals (learning_goal_id, title, subject_id) VALUES (?, ?, ?)",
            (lg_id, title, subject_id),
        )
        self._learning_goal_cache.add(lg_id)

    def _insert_keyword(self, topic: str, lg_id: str):
        key = (topic, lg_id)
        if key in self._keyword_cache:
            return

        self.cur.execute(
            "INSERT INTO keywords (topic, learning_goal_id) VALUES (?, ?)",
            (topic, lg_id),
        )
        self._keyword_cache.add(key)

    def _import_snapshot(
        self, snapshot: dict, student_id: int, lg_id: str, taxonomy_level_map: dict
    ) -> int:
        at = snapshot.get("at")
        source_data = snapshot.get("source", {})
        source_type = source_data.get("type", "unknown")
        source_id = source_data.get("id", "unknown")

        self.cur.execute(
            "INSERT INTO sources (type, display_id) VALUES (?, ?)",
            (source_type, source_id),
        )
        source_pk = self.cur.lastrowid

        self.cur.execute(
            """INSERT INTO snapshots (at, source_id, class_id, student_id, learning_goal_id)
               VALUES (?, ?, NULL, ?, ?)""",
            (at, source_pk, student_id, lg_id),
        )
        snapshot_id = self.cur.lastrowid

        taxonomy_data = snapshot.get("taxonomy", [])
        for tax in taxonomy_data:
            level_name = tax.get("level")
            kennen = tax.get("kennen")
            kunnen = tax.get("kunnen")
            confidence = tax.get("confidence")

            if level_name not in taxonomy_level_map:
                continue

            taxonomy_level_id = taxonomy_level_map[level_name]

            self.cur.execute(
                """INSERT INTO taxonomy_scores
                       (know, can, confidence, snapshot_id, taxonomy_level_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (kennen, kunnen, confidence, snapshot_id, taxonomy_level_id),
            )

        return snapshot_id

    def _print_summary(self):

        self.cur.execute("SELECT COUNT(*) FROM teachers")
        teachers = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM students")
        students = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM classes")
        classes = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM subjects")
        subjects = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM snapshots")
        snapshots = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM taxonomy_scores")
        scores = self.cur.fetchone()[0]

        print(
            f"Import voltooid: {teachers} teachers, {students} students, {classes} classes, {subjects} subjects, {snapshots} snapshots, {scores} scores"
        )