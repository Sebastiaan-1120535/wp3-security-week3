from data.database import Database


class StudentData:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def get_student_subjects(self, student_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('''
                SELECT DISTINCT s.subject_id, s.name
                FROM subjects s
                INNER JOIN learning_goals lg ON s.subject_id = lg.subject_id
                INNER JOIN snapshots sn ON lg.learning_goal_id = sn.learning_goal_id
                WHERE sn.student_id = ?
                ORDER BY s.name
            ''', (student_id,))
            return cur.fetchall()

    def get_student_learning_goals(self, student_id: int, subject_id: int = None):
        with self.db.connect() as con:
            cur = con.cursor()

            if subject_id:
                cur.execute('''
                    SELECT DISTINCT 
                        lg.learning_goal_id, lg.title, s.subject_id, s.name,
                        MAX(sn.at) as latest_date,
                        ROUND(AVG(ts.know), 2) as avg_know,
                        ROUND(AVG(ts.can), 2) as avg_can
                    FROM learning_goals lg
                    INNER JOIN subjects s ON lg.subject_id = s.subject_id
                    LEFT JOIN snapshots sn ON lg.learning_goal_id = sn.learning_goal_id
                    LEFT JOIN taxonomy_scores ts ON sn.snapshot_id = ts.snapshot_id
                    WHERE sn.student_id = ? AND s.subject_id = ?
                    GROUP BY lg.learning_goal_id, lg.title, s.subject_id, s.name
                    ORDER BY lg.title
                ''', (student_id, subject_id))
            else:
                cur.execute('''
                    SELECT DISTINCT 
                        lg.learning_goal_id, lg.title, s.subject_id, s.name,
                        MAX(sn.at) as latest_date,
                        ROUND(AVG(ts.know), 2) as avg_know,
                        ROUND(AVG(ts.can), 2) as avg_can
                    FROM learning_goals lg
                    INNER JOIN subjects s ON lg.subject_id = s.subject_id
                    LEFT JOIN snapshots sn ON lg.learning_goal_id = sn.learning_goal_id
                    LEFT JOIN taxonomy_scores ts ON sn.snapshot_id = ts.snapshot_id
                    WHERE sn.student_id = ?
                    GROUP BY lg.learning_goal_id, lg.title, s.subject_id, s.name
                    ORDER BY s.name, lg.title
                ''', (student_id,))

            return cur.fetchall()

    def get_learning_goal_keywords(self, learning_goal_id: str):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('''
                SELECT keyword_id, topic
                FROM keywords
                WHERE learning_goal_id = ?
                ORDER BY topic
            ''', (learning_goal_id,))
            return cur.fetchall()

    def get_snapshot_progress(self, student_id: int, learning_goal_id: str):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('''
                SELECT 
                    sn.snapshot_id, sn.at, src.type, src.display_id,
                    tl.name, 
                    ts.know, ts.can, ts.confidence
                FROM snapshots sn
                INNER JOIN sources src ON sn.source_id = src.source_id
                INNER JOIN taxonomy_scores ts ON sn.snapshot_id = ts.snapshot_id
                INNER JOIN taxonomy_levels tl ON ts.taxonomy_level_id = tl.taxonomy_level_id
                WHERE sn.student_id = ? AND sn.learning_goal_id = ?
                ORDER BY sn.at DESC, tl.taxonomy_level_id
            ''', (student_id, learning_goal_id))
            return cur.fetchall()

    def get_all_students(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute('''
                SELECT DISTINCT 
                    st.student_id, 
                    st.first_name || ' ' || COALESCE(st.last_name, '') as name,
                    COUNT(DISTINCT sn.learning_goal_id) as goal_count,
                    COUNT(DISTINCT sn.snapshot_id) as snapshot_count
                FROM students st
                LEFT JOIN snapshots sn ON st.student_id = sn.student_id
                GROUP BY st.student_id, st.first_name, st.last_name
                ORDER BY st.first_name
            ''')
            return cur.fetchall()

    def get_class_statistics(self, subject_id: int = None):
        with self.db.connect() as con:
            cur = con.cursor()

            if subject_id:
                cur.execute('''
                    SELECT 
                        lg.learning_goal_id, lg.title, s.name,
                        ROUND(AVG(ts.know), 2) as avg_know,
                        ROUND(AVG(ts.can), 2) as avg_can,
                        COUNT(DISTINCT sn.student_id) as student_count
                    FROM learning_goals lg
                    INNER JOIN subjects s ON lg.subject_id = s.subject_id
                    LEFT JOIN snapshots sn ON lg.learning_goal_id = sn.learning_goal_id
                    LEFT JOIN taxonomy_scores ts ON sn.snapshot_id = ts.snapshot_id
                    WHERE s.subject_id = ?
                    GROUP BY lg.learning_goal_id, lg.title, s.name
                    ORDER BY lg.title
                ''', (subject_id,))
            else:
                cur.execute('''
                    SELECT 
                        lg.learning_goal_id, lg.title, s.name,
                        ROUND(AVG(ts.know), 2) as avg_know,
                        ROUND(AVG(ts.can), 2) as avg_can,
                        COUNT(DISTINCT sn.student_id) as student_count
                    FROM learning_goals lg
                    INNER JOIN subjects s ON lg.subject_id = s.subject_id
                    LEFT JOIN snapshots sn ON lg.learning_goal_id = sn.learning_goal_id
                    LEFT JOIN taxonomy_scores ts ON sn.snapshot_id = ts.snapshot_id
                    GROUP BY lg.learning_goal_id, lg.title, s.name
                    ORDER BY s.name, lg.title
                ''')

            return cur.fetchall()

    def get_keywords_performance(self, student_id: int = None):
        with self.db.connect() as con:
            cur = con.cursor()

            if student_id:
                cur.execute('''
                    SELECT 
                        k.topic, lg.title,
                        ROUND(AVG(ts.know), 2) as avg_know,
                        ROUND(AVG(ts.can), 2) as avg_can,
                        COUNT(DISTINCT sn.snapshot_id) as measurement_count
                    FROM keywords k
                    INNER JOIN learning_goals lg ON k.learning_goal_id = lg.learning_goal_id
                    LEFT JOIN snapshots sn ON lg.learning_goal_id = sn.learning_goal_id
                    LEFT JOIN taxonomy_scores ts ON sn.snapshot_id = ts.snapshot_id
                    WHERE sn.student_id = ?
                    GROUP BY k.topic, lg.title
                    ORDER BY ROUND(AVG(ts.can), 2) DESC
                ''', (student_id,))
            else:
                cur.execute('''
                    SELECT 
                        k.topic, lg.title,
                        ROUND(AVG(ts.know), 2) as avg_know,
                        ROUND(AVG(ts.can), 2) as avg_can,
                        COUNT(DISTINCT sn.student_id) as student_count
                    FROM keywords k
                    INNER JOIN learning_goals lg ON k.learning_goal_id = lg.learning_goal_id
                    LEFT JOIN snapshots sn ON lg.learning_goal_id = sn.learning_goal_id
                    LEFT JOIN taxonomy_scores ts ON sn.snapshot_id = ts.snapshot_id
                    GROUP BY k.topic, lg.title
                    ORDER BY ROUND(AVG(ts.can), 2) DESC
                ''')

            return cur.fetchall()
