from data.database import Database
import sqlite3

class Classes:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    @staticmethod
    def _safe_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    
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

    def get_class_average_score(self, class_name: str, class_id: int, goal_id: str | None = None):
        with self.db.connect() as con:
            cur = con.cursor()

            subject = self._get_subject_by_name(cur, class_name)

            if not subject:
                return {
                    'labels': [],
                    'datasets': []
                }

            levels = self._get_taxonomy_levels(cur, subject['subject_id'])
            goals = self._get_learning_goals(cur, subject['subject_id'])

            if not goals:
                return {
                    'labels': [],
                    'datasets': []
                }

            labels = [level['name'] for level in levels]
            selected_goal_id = self._select_goal_id(goals, goal_id)
            if not selected_goal_id:
                return {
                    'labels': labels,
                    'datasets': []
                }

            can_scores, know_scores, confidence_scores = self._get_goal_level_averages(
                cur, class_id, selected_goal_id, levels,
            )

            return {
                'labels': labels,
                'datasets': build_score_datasets(can_scores, know_scores, confidence_scores)
            }
        
    def _get_subject_by_name(self, cur, class_name: str):
        cur.execute('SELECT subject_id FROM "subjects" WHERE name = ?', (class_name,))
        return cur.fetchone()

    def _get_taxonomy_levels(self, cur, subject_id):
        cur.execute('SELECT taxonomy_level_id, name FROM "taxonomy_levels" WHERE subject_id = ?', (subject_id,))
        return [dict(level) for level in cur.fetchall()]

    def _get_learning_goals(self, cur, subject_id):
        cur.execute('SELECT learning_goal_id, title FROM "learning_goals" WHERE subject_id = ?', (subject_id,))
        return [dict(goal) for goal in cur.fetchall()]

    def _select_goal_id(self, goals: list[dict], goal_id: str | None):
        if goal_id in (None, ''):
            return str(goals[0]['learning_goal_id']) if goals else None

        selected_goal_id = str(goal_id)
        if any(str(goal['learning_goal_id']) == selected_goal_id for goal in goals):
            return selected_goal_id

        return None

    def _get_goal_level_averages(self, cur, class_id: int, selected_goal_id: str, levels: list[dict]):
        cur.execute(
            '''SELECT
                   ts.taxonomy_level_id,
                   AVG(CAST(ts.can AS REAL)) AS avg_can,
                   AVG(CAST(ts.know AS REAL)) AS avg_know,
                   AVG(CAST(ts.confidence AS REAL)) AS avg_confidence
               FROM "taxonomy_scores" ts
               JOIN "snapshots" s ON s.snapshot_id = ts.snapshot_id
               JOIN "students" st ON st.student_id = s.student_id
               JOIN (
                   SELECT student_id, learning_goal_id, MAX(snapshot_id) AS latest_snapshot_id
                   FROM "snapshots"
                   GROUP BY student_id, learning_goal_id
               ) latest ON latest.latest_snapshot_id = s.snapshot_id
               WHERE st.class_id = ?
                 AND s.learning_goal_id = ?
               GROUP BY ts.taxonomy_level_id''',
            (class_id, selected_goal_id)
        )
        
        score_rows = {
            row['taxonomy_level_id']: row
            for row in cur.fetchall()
        }

        can_scores = []
        know_scores = []
        confidence_scores = []

        for level in levels:
            score_row = score_rows.get(level['taxonomy_level_id'])

            can_scores.append(int(self._safe_float(score_row['avg_can'] if score_row else 0) * 100))
            know_scores.append(int(self._safe_float(score_row['avg_know'] if score_row else 0) * 100))
            confidence_scores.append(int(self._safe_float(score_row['avg_confidence'] if score_row else 0) * 100))
            
        return can_scores, know_scores, confidence_scores


def build_score_datasets(can_scores: list[int], know_scores: list[int], confidence_scores: list[int]):
    return [
        {'label': 'Kunnen', 'data': can_scores, 'stack': 1},
        {'label': 'Weten', 'data': know_scores, 'stack': 2},
        {'label': 'Vertrouwen', 'data': confidence_scores, 'stack': 3}
    ]


            