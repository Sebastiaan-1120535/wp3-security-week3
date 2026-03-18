from data.database import Database
from datetime import datetime, timedelta


MAX_POINTS = 10
COLORS = ['#004DF5', '#36AF4E', '#5B677A', '#94A3B8', '#E5484D', '#F4B740']


def _score_to_label(score: float) -> str:
    if score >= 0.7:
        return 'Sterk'
    elif score >= 0.5:
        return 'Voldoende'
    return 'Zwak'


def _parse_date(date_str: str) -> datetime:
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return datetime.strptime(date_str[:10], '%Y-%m-%d')


def _bucket_dates(sorted_dates: list, max_points: int = MAX_POINTS) -> list:
    if len(sorted_dates) <= max_points:
        return [(d, d) for d in sorted_dates]

    parsed = [_parse_date(d) for d in sorted_dates]
    dt_min = parsed[0]
    dt_max = parsed[-1]
    total_days = (dt_max - dt_min).days or 1
    bucket_days = total_days / max_points

    buckets = []
    for i in range(max_points):
        start = dt_min + timedelta(days=bucket_days * i)
        end = dt_min + timedelta(days=bucket_days * (i + 1))
        label = start.strftime('%Y-%m-%d')
        buckets.append((label, start, end))

    return buckets


def _bucket_chart_data(series: dict, sorted_dates: list) -> tuple[list, dict]:
    if len(sorted_dates) <= MAX_POINTS:
        return sorted_dates, series

    buckets = _bucket_dates(sorted_dates)
    parsed_lookup = {d: _parse_date(d) for d in sorted_dates}

    bucket_labels = [b[0] for b in buckets]
    bucketed_series = {}

    for name, date_scores in series.items():
        bucket_values = []
        for label, start, end in buckets:
            vals = []
            for d, score in date_scores.items():
                dt = parsed_lookup[d]
                if start <= dt < end or (end == buckets[-1][2] and dt == end):
                    vals.append(score)
            if vals:
                bucket_values.append(round(sum(vals) / len(vals), 1))
            else:
                bucket_values.append(None)
        bucketed_series[name] = dict(zip(bucket_labels, bucket_values))

    return bucket_labels, bucketed_series


def _build_chart_datasets(series: dict, labels: list) -> list:
    datasets = []
    for i, (name, date_scores) in enumerate(series.items()):
        color = COLORS[i % len(COLORS)]
        data = [date_scores.get(d, None) for d in labels]
        non_null_points = sum(1 for value in data if value is not None)
        chart_type = 'bar' if non_null_points <= 1 else 'line'
        datasets.append({
            'label': name,
            'data': data,
            'borderColor': color,
            'backgroundColor': color,
            'tension': 0.3,
            'fill': False,
            'stack': 'combined',
            'type': chart_type
        })
    return datasets


def _resolve_student_id(cur, user_id: int):
    cur.execute("SELECT student_id FROM students WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    return row['student_id'] if row else None


def _enrich_snapshot(cur, snapshot_id: int, learning_goal_id: str) -> dict:
    cur.execute("""
        SELECT AVG((ts.know + ts.can) / 2) as avg_score
        FROM taxonomy_scores ts
        WHERE ts.snapshot_id = ?
    """, (snapshot_id,))
    score_row = cur.fetchone()
    avg_score = score_row['avg_score'] if score_row and score_row['avg_score'] else None

    cur.execute("SELECT topic FROM keywords WHERE learning_goal_id = ?", (learning_goal_id,))
    keywords = [kw['topic'] for kw in cur.fetchall()][:5]

    has_data = avg_score is not None
    return {
        'score': _score_to_label(avg_score) if has_data else None,
        'score_numeric': round(avg_score * 100, 1) if has_data else None,
        'has_data': has_data,
        'keywords': keywords
    }


class Partial:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def get_recent_results(self, user_id: int, offset: int = 0, limit: int = 10) -> dict:
        con = self.db.connect()
        cur = con.cursor()

        student_id = _resolve_student_id(cur, user_id)
        if not student_id:
            con.close()
            return {'results': [], 'has_more': False}

        cur.execute("""
            SELECT
                snap.snapshot_id,
                snap.at as snapshot_date,
                lg.learning_goal_id,
                lg.title,
                s.name as subject_name
            FROM snapshots snap
            JOIN learning_goals lg ON lg.learning_goal_id = snap.learning_goal_id
            JOIN subjects s ON s.subject_id = lg.subject_id
            WHERE snap.student_id = ?
            ORDER BY snap.at DESC
            LIMIT ? OFFSET ?
        """, (student_id, limit + 1, offset))

        rows = cur.fetchall()
        has_more = len(rows) > limit
        rows = rows[:limit]

        results = []
        for row in rows:
            enriched = _enrich_snapshot(cur, row['snapshot_id'], row['learning_goal_id'])
            results.append({
                'id': row['learning_goal_id'],
                'title': row['title'],
                'subject': row['subject_name'],
                'date': row['snapshot_date'],
                **enriched
            })

        con.close()
        return {'results': results, 'has_more': has_more}

    def get_student_progress(self, user_id: int) -> list:
        con = self.db.connect()
        cur = con.cursor()

        student_id = _resolve_student_id(cur, user_id)
        if not student_id:
            con.close()
            return []

        cur.execute("""
            WITH latest_snapshots AS (
                SELECT
                    snap.snapshot_id,
                    snap.learning_goal_id,
                    snap.at,
                    ROW_NUMBER() OVER (PARTITION BY snap.learning_goal_id ORDER BY snap.at DESC) as rn
                FROM snapshots snap
                WHERE snap.student_id = ?
            )
            SELECT
                lg.learning_goal_id,
                lg.title,
                s.name as subject_name,
                ls.snapshot_id,
                ls.at as snapshot_date
            FROM learning_goals lg
            JOIN subjects s ON s.subject_id = lg.subject_id
            JOIN latest_snapshots ls ON ls.learning_goal_id = lg.learning_goal_id AND ls.rn = 1
            ORDER BY s.name, lg.title
            LIMIT 20
        """, (student_id,))

        goals = []
        for row in cur.fetchall():
            enriched = _enrich_snapshot(cur, row['snapshot_id'], row['learning_goal_id'])
            goals.append({
                'id': row['learning_goal_id'],
                'title': row['title'],
                'subject': row['subject_name'],
                'date': row['snapshot_date'],
                **enriched
            })

        con.close()
        return goals

    def get_progress_over_time(self, user_id: int) -> dict:
        con = self.db.connect()
        cur = con.cursor()

        student_id = _resolve_student_id(cur, user_id)
        if not student_id:
            con.close()
            return {'labels': [], 'datasets': []}

        cur.execute("""
            SELECT
                snap.at,
                s.name as subject_name,
                AVG((ts.know + ts.can) / 2.0) as avg_score
            FROM snapshots snap
            JOIN learning_goals lg ON lg.learning_goal_id = snap.learning_goal_id
            JOIN subjects s ON s.subject_id = lg.subject_id
            LEFT JOIN taxonomy_scores ts ON ts.snapshot_id = snap.snapshot_id
            WHERE snap.student_id = ?
            GROUP BY snap.at, s.name
            ORDER BY snap.at ASC
        """, (student_id,))

        rows = cur.fetchall()
        con.close()

        subjects = {}
        dates = set()
        for row in rows:
            subject = row['subject_name']
            date = row['at']
            score = round(row['avg_score'] * 100, 1) if row['avg_score'] else 0
            dates.add(date)
            if subject not in subjects:
                subjects[subject] = {}
            subjects[subject][date] = score

        sorted_dates = sorted(dates)
        bucketed_labels, bucketed_subjects = _bucket_chart_data(subjects, sorted_dates)
        datasets = _build_chart_datasets(bucketed_subjects, bucketed_labels)
        return {'labels': bucketed_labels, 'datasets': datasets}

    def get_keyword_scores(self, user_id: int) -> list:
        """Get all keywords with scores based on avg taxonomy_scores of all snapshots per learning goal."""
        con = self.db.connect()
        cur = con.cursor()

        student_id = _resolve_student_id(cur, user_id)
        if not student_id:
            con.close()
            return []

        cur.execute("""
            SELECT
                k.keyword_id,
                k.topic,
                lg.learning_goal_id,
                lg.title AS goal_title,
                s.name AS subject_name,
                AVG((ts.know + ts.can) / 2.0) AS avg_score
            FROM keywords k
            JOIN learning_goals lg ON lg.learning_goal_id = k.learning_goal_id
            JOIN subjects s ON s.subject_id = lg.subject_id
            JOIN snapshots snap ON snap.learning_goal_id = lg.learning_goal_id AND snap.student_id = ?
            LEFT JOIN taxonomy_scores ts ON ts.snapshot_id = snap.snapshot_id
            GROUP BY k.keyword_id
            ORDER BY avg_score ASC
        """, (student_id,))

        results = []
        for row in cur.fetchall():
            avg = row['avg_score']
            has_data = avg is not None
            results.append({
                'keyword_id': row['keyword_id'],
                'topic': row['topic'],
                'goal_title': row['goal_title'],
                'subject': row['subject_name'],
                'score': _score_to_label(avg) if has_data else None,
                'score_numeric': round(avg * 100, 1) if has_data else None,
                'has_data': has_data,
            })

        con.close()
        return results

    def get_subjects_for_student(self, user_id: int) -> list:
        con = self.db.connect()
        cur = con.cursor()

        student_id = _resolve_student_id(cur, user_id)
        if not student_id:
            con.close()
            return []

        cur.execute("""
            SELECT DISTINCT s.subject_id, s.name
            FROM subjects s
            JOIN learning_goals lg ON lg.subject_id = s.subject_id
            JOIN snapshots snap ON snap.learning_goal_id = lg.learning_goal_id
            WHERE snap.student_id = ?
            ORDER BY s.name
        """, (student_id,))
        subjects = [{'subject_id': r['subject_id'], 'name': r['name']} for r in cur.fetchall()]
        con.close()
        return subjects

    def get_progress_by_subject(self, user_id: int, subject_id: int) -> dict:
        con = self.db.connect()
        cur = con.cursor()

        student_id = _resolve_student_id(cur, user_id)
        if not student_id:
            con.close()
            return {'labels': [], 'datasets': []}

        cur.execute("""
            SELECT
                snap.at,
                lg.title as goal_title,
                AVG((ts.know + ts.can) / 2.0) as avg_score
            FROM snapshots snap
            JOIN learning_goals lg ON lg.learning_goal_id = snap.learning_goal_id
            LEFT JOIN taxonomy_scores ts ON ts.snapshot_id = snap.snapshot_id
            WHERE snap.student_id = ? AND lg.subject_id = ?
            GROUP BY snap.at, lg.learning_goal_id
            ORDER BY snap.at ASC
        """, (student_id, subject_id))

        rows = cur.fetchall()
        con.close()

        goals = {}
        dates = set()
        for row in rows:
            goal = row['goal_title']
            date = row['at']
            score = round(row['avg_score'] * 100, 1) if row['avg_score'] else 0
            dates.add(date)
            if goal not in goals:
                goals[goal] = {}
            goals[goal][date] = score

        sorted_dates = sorted(dates)
        bucketed_labels, bucketed_goals = _bucket_chart_data(goals, sorted_dates)
        datasets = _build_chart_datasets(bucketed_goals, bucketed_labels)
        return {'labels': bucketed_labels, 'datasets': datasets}
