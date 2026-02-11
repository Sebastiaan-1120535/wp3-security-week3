from flask import render_template
from app.models.user import User
from app.models.teacher import Teacher



def render_dashboard_page(db_path: str) -> str:
    user_m = User(db_path)
    users = user_m.list_recent(limit=10)
    teacher_m = Teacher(db_path)
    teachers = teacher_m.list_recent(limit=10)
    return render_template('pages/dashboard.html', users=users, teachers=teachers)
