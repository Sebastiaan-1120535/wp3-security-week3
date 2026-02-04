from flask import Flask, request, redirect, url_for, session, render_template, flash, jsonify
from werkzeug.utils import secure_filename
from app.controllers.dashboard_controller import render_dashboard_page
from app.controllers.auth_controller import login_view, register_view, logout_view
from app.models.user import User
from app.models.student_data import StudentData
from data.importer import DataImporter
from data.database import Database
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DB_PATH = os.path.join(BASE_DIR, 'data', 'prod.sqlite')

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, 'public', 'src'),
    template_folder=os.path.join(BASE_DIR, 'public', 'views')
)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_view(DB_PATH)


@app.route('/registreren', methods=['GET', 'POST'])
def register():
    return register_view(DB_PATH)


@app.route('/logout')
def logout():
    return logout_view(DB_PATH)


@app.route('/')
def home():
    if session.get('user'):
        return render_dashboard_page(DB_PATH)
    return render_template('pages/home.html')


@app.route('/dashboard')
def dashboard():
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_dashboard_page(DB_PATH)


@app.route('/upload-json', methods=['POST'])
def upload_json():
    if not session.get('user'):
        return redirect(url_for('login'))

    file = request.files.get('json_file')

    if not file or not file.filename or not file.filename.lower().endswith('.json'):
        flash('Ongeldig bestand (alleen .json toegestaan).')
        return redirect(url_for('dashboard'))

    upload_dir = os.path.join(BASE_DIR, 'data', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, secure_filename(file.filename))
    file.save(file_path)

    try:
        DataImporter(DB_PATH).import_json(file_path)
        flash('Import gelukt.')
    except Exception as e:
        flash(f'Import mislukt: {e}')

    return redirect(url_for('dashboard'))

@app.route('/api/partial/users')
def partials_users():
    user_m = User(DB_PATH)
    users = user_m.list_recent(limit=10)
    return render_template('partials/user_list.html', users=users)


@app.route('/api/student/<int:student_id>/subjects')
def api_student_subjects(student_id):
    student_m = StudentData(DB_PATH)
    subjects = student_m.get_student_subjects(student_id)
    return jsonify([{
        'id': s[0],
        'name': s[1]
    } for s in subjects])


@app.route('/api/student/<int:student_id>/learning-goals')
def api_student_learning_goals(student_id):
    subject_id = request.args.get('subject_id', type=int)
    student_m = StudentData(DB_PATH)
    goals = student_m.get_student_learning_goals(student_id, subject_id)
    return jsonify([{
        'id': g[0],
        'title': g[1],
        'subject_id': g[2],
        'subject_name': g[3],
        'latest_date': g[4],
        'avg_know': float(g[5]) if g[5] else 0,
        'avg_can': float(g[6]) if g[6] else 0
    } for g in goals])


@app.route('/api/student/<int:student_id>/keywords')
def api_student_keywords(student_id):
    student_m = StudentData(DB_PATH)
    keywords = student_m.get_keywords_performance(student_id)
    return jsonify([{
        'topic': k[0],
        'learning_goal': k[1],
        'avg_know': float(k[2]) if k[2] else 0,
        'avg_can': float(k[3]) if k[3] else 0,
        'measurements': k[4]
    } for k in keywords])


@app.route('/api/class/statistics')
def api_class_statistics():
    subject_id = request.args.get('subject_id', type=int)
    student_m = StudentData(DB_PATH)
    stats = student_m.get_class_statistics(subject_id)
    return jsonify([{
        'learning_goal_id': s[0],
        'title': s[1],
        'subject': s[2],
        'avg_know': float(s[3]) if s[3] else 0,
        'avg_can': float(s[4]) if s[4] else 0,
        'student_count': s[5]
    } for s in stats])

if __name__ == '__main__':
    app.run(debug=True)
