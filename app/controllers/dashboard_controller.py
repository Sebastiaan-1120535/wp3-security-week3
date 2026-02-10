from flask import render_template, session
from app.models.user import User
from app.models.student_data import StudentData


def render_dashboard_page(db_path: str) -> str:
    user_m = User(db_path)
    student_m = StudentData(db_path)

    current_user = session.get('user')

    if not current_user:
        users = user_m.list_recent(limit=10)
        return render_template('pages/dashboard.html', users=users)

    user_data = user_m.find_by_email(current_user)
    role = user_data['role'] if user_data else 'student'

    if role == 'teacher':
        students = student_m.get_all_students()
        keywords_perf = student_m.get_keywords_performance()
        return render_template(
            'pages/dashboard.html',
            role=role,
            students=students,
            keywords_performance=keywords_perf,
            user_email=current_user
        )
    else:
        user_id = user_data['user_id'] if user_data else None

        from data.database import Database
        db = Database(db_path)
        with db.connect() as con:
            cur = con.cursor()
            cur.execute('SELECT student_id FROM students WHERE user_id = ?', (user_id,))
            student_result = cur.fetchone()
            student_id = student_result[0] if student_result else None

        if student_id:
            subjects = student_m.get_student_subjects(student_id)
            learning_goals = student_m.get_student_learning_goals(student_id)
            keywords_perf = student_m.get_keywords_performance(student_id)

            return render_template(
                'pages/dashboard.html',
                role=role,
                student_id=student_id,
                subjects=subjects,
                learning_goals=learning_goals,
                keywords_performance=keywords_perf,
                user_email=current_user
            )

        users = user_m.list_recent(limit=10)
        return render_template('pages/dashboard.html', users=users)
