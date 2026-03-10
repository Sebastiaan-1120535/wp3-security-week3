from flask import render_template, session
from app.models.user import User


def render_dashboard_page(db_path: str) -> str:
    user_m = User(db_path)
    users = user_m.list_recent(limit=10)
    role = session.get('role', 'student')
    return render_template(f'pages/dashboard/{role}.html', users=users, role=role)

