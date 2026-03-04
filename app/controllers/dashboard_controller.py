from flask import render_template, jsonify, session
from app.models.user import User
from app.models.teacher import Teacher

from data.database import Database


def score_to_label(score: float) -> str:
    if score >= 0.7:
        return 'Sterk'
    elif score >= 0.5:
        return 'Voldoende'
    return 'Zwak'


def get_student_progress(db_path: str, user_id: int) -> list:
    db = Database(db_path)
    con = db.connect()
    cur = con.cursor()

    cur.execute("SELECT student_id FROM students WHERE user_id = ?", (user_id,))
    student_row = cur.fetchone()

    if not student_row:
        con.close()
        return []

    student_id = student_row['student_id']

    cur.execute("""
        WITH latest_snapshots AS (
            SELECT 
                snap.snapshot_id,
                snap.learning_goal_id,
                ROW_NUMBER() OVER (PARTITION BY snap.learning_goal_id ORDER BY snap.at DESC) as rn
            FROM snapshots snap
            WHERE snap.student_id = ?
        )
        SELECT 
            lg.learning_goal_id,
            lg.title,
            s.name as subject_name,
            ls.snapshot_id
        FROM learning_goals lg
        JOIN subjects s ON s.subject_id = lg.subject_id
        JOIN latest_snapshots ls ON ls.learning_goal_id = lg.learning_goal_id AND ls.rn = 1
        ORDER BY s.name, lg.title
        LIMIT 20
    """, (student_id,))

    goals = []
    for row in cur.fetchall():
        learning_goal_id = row['learning_goal_id']
        snapshot_id = row['snapshot_id']

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

        goals.append({
            'id': learning_goal_id,
            'title': row['title'],
            'subject': row['subject_name'],
            'score': score_to_label(avg_score) if has_data else None,
            'score_numeric': round(avg_score * 100, 1) if has_data else None,
            'has_data': has_data,
            'keywords': keywords
        })

    con.close()
    return goals


def render_dashboard_page(db_path: str) -> str:
    user_m = User(db_path)
    users = user_m.list_recent(limit=10)
    teacher_m = Teacher(db_path)
    teachers = teacher_m.list_recent(limit=10)
    return render_template('pages/dashboard.html', users=users, teachers=teachers)

    role = session.get('role', 'student')
    user_id = session.get('user_id')

    progress = []
    if user_id:
        progress = get_student_progress(db_path, user_id)

    return render_template('pages/dashboard.html', users=users, role=role, progress=progress)


def get_student_progress_api(db_path: str):
    user_id = session.get('user_id')
    if not user_id:
        return 401

    progress = get_student_progress(db_path, user_id)
    return jsonify(progress)
