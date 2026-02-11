import json
import sqlite3
import sys
from pathlib import Path


class DataImporter:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.con = sqlite3.connect(db_path)
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA journal_mode=WAL;")
        self.con.execute("PRAGMA foreign_keys = ON;")
        self.cur = self.con.cursor()

    def import_json(self, json_file: str):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        entries = data.get('entries', [])

        for idx, entry in enumerate(entries, 1):
            self._import_entry(entry)
            if idx % 10 == 0:
                self.con.commit()

        self.con.commit()
        self._print_summary()
        self.con.close()


    def _import_entry(self, entry: dict):
        student_data = entry.get('student', {})
        subject_data = entry.get('subject', {})
        learning_goals = entry.get('learningGoals', [])
        taxonomy_scale = entry.get('taxonomyScale', [])

        student_id = self._ensure_student(
            student_data.get('id'),
            student_data.get('name', 'Unknown')
        )

        subject_id = self._ensure_subject(
            subject_data.get('id'),
            subject_data.get('name', 'Unknown')
        )

        taxonomy_level_map = {}
        for level_name in taxonomy_scale:
            level_id = self._ensure_taxonomy_level(level_name, subject_id)
            taxonomy_level_map[level_name] = level_id

        for lg in learning_goals:
            lg_id = lg.get('id')
            lg_title = lg.get('title', 'Untitled')

            self._ensure_learning_goal(lg_id, lg_title, subject_id)

            keywords = lg.get('keywords', [])
            for keyword in keywords:
                self._insert_keyword(keyword, lg_id)

            snapshots = lg.get('snapshots', [])
            for snapshot in snapshots:
                self._import_snapshot(
                    snapshot,
                    student_id,
                    lg_id,
                    taxonomy_level_map
                )

    def _ensure_student(self, student_id: int, name: str) -> int:
        self.cur.execute(
            'SELECT student_id FROM students WHERE student_id = ?',
            (student_id,)
        )
        result = self.cur.fetchone()
        if result:
            return result[0]

        parts = name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        self.cur.execute(
            '''INSERT INTO students (student_id, first_name, last_name, user_id, class_id)
               VALUES (?, ?, ?, NULL, NULL)''',
            (student_id, first_name, last_name)
        )
        return student_id

    def _ensure_subject(self, subject_id: int, name: str) -> int:
        self.cur.execute(
            'SELECT subject_id FROM subjects WHERE subject_id = ?',
            (subject_id,)
        )
        result = self.cur.fetchone()
        if result:
            return result[0]

        self.cur.execute(
            'INSERT INTO subjects (subject_id, name) VALUES (?, ?)',
            (subject_id, name)
        )
        return subject_id

    def _ensure_taxonomy_level(self, name: str, subject_id: int) -> int:
        self.cur.execute(
            'SELECT taxonomy_level_id FROM taxonomy_levels WHERE name = ? AND subject_id = ?',
            (name, subject_id)
        )
        result = self.cur.fetchone()
        if result:
            return result[0]

        self.cur.execute(
            'INSERT INTO taxonomy_levels (name, subject_id) VALUES (?, ?)',
            (name, subject_id)
        )
        return self.cur.lastrowid

    def _ensure_learning_goal(self, lg_id: str, title: str, subject_id: int):
        self.cur.execute(
            'SELECT learning_goal_id FROM learning_goals WHERE learning_goal_id = ?',
            (lg_id,)
        )
        result = self.cur.fetchone()
        if not result:
            self.cur.execute(
                'INSERT INTO learning_goals (learning_goal_id, title, subject_id) VALUES (?, ?, ?)',
                (lg_id, title, subject_id)
            )

    def _insert_keyword(self, topic: str, lg_id: str):
        self.cur.execute(
            'INSERT INTO keywords (topic, learning_goal_id) VALUES (?, ?)',
            (topic, lg_id)
        )

    def _import_snapshot(self, snapshot: dict, student_id: int, lg_id: str,
                        taxonomy_level_map: dict) -> int:
        at = snapshot.get('at')
        source_data = snapshot.get('source', {})
        source_type = source_data.get('type', 'unknown')
        source_id = source_data.get('id', 'unknown')

        self.cur.execute(
            'INSERT INTO sources (type, display_id) VALUES (?, ?)',
            (source_type, source_id)
        )
        source_pk = self.cur.lastrowid

        self.cur.execute(
            '''INSERT INTO snapshots (at, source_id, class_id, student_id, learning_goal_id)
               VALUES (?, ?, NULL, ?, ?)''',
            (at, source_pk, student_id, lg_id)
        )
        snapshot_id = self.cur.lastrowid

        taxonomy_data = snapshot.get('taxonomy', [])
        for tax in taxonomy_data:
            level_name = tax.get('level')
            kennen = tax.get('kennen')
            kunnen = tax.get('kunnen')
            confidence = tax.get('confidence')

            if level_name not in taxonomy_level_map:
                print(f"WARNING: Unknown taxonomy level '{level_name}'")
                continue

            taxonomy_level_id = taxonomy_level_map[level_name]

            self.cur.execute(
                '''INSERT INTO taxonomy_scores 
                   (know, can, confidence, snapshot_id, taxonomy_level_id)
                   VALUES (?, ?, ?, ?, ?)''',
                (kennen, kunnen, confidence, snapshot_id, taxonomy_level_id)
            )

        return snapshot_id

    def _print_summary(self):
        self.cur.execute('SELECT COUNT(*) FROM students')
        students = self.cur.fetchone()[0]

        self.cur.execute('SELECT COUNT(*) FROM subjects')
        subjects = self.cur.fetchone()[0]

        self.cur.execute('SELECT COUNT(*) FROM learning_goals')
        learning_goals = self.cur.fetchone()[0]

        self.cur.execute('SELECT COUNT(*) FROM snapshots')
        snapshots = self.cur.fetchone()[0]

        self.cur.execute('SELECT COUNT(*) FROM taxonomy_scores')
        scores = self.cur.fetchone()[0]

        print("\n" + "="*50)
        print("IMPORT SUMMARY")
        print("="*50)
        print(f"Students:         {students}")
        print(f"Subjects:         {subjects}")
        print(f"Learning Goals:   {learning_goals}")
        print(f"Snapshots:        {snapshots}")
        print(f"Taxonomy Scores:  {scores}")
        print("="*50)


def main():
    if len(sys.argv) < 2:
        print("Usage: python import_data.py <json_file>")
        print("Example: python import_data.py data-sample-small.json")
        sys.exit(1)

    json_file = sys.argv[1]

    base_dir = Path(__file__).parent
    db_path = base_dir / 'prod.sqlite'

    print(f"Database: {db_path}")
    print(f"JSON File: {json_file}")
    print()

    importer = DataImporter(str(db_path))
    importer.import_json(json_file)


if __name__ == '__main__':
    main()
 