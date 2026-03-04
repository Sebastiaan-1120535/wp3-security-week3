from flask import Flask, request, redirect, url_for, session, render_template, flash
from app.controllers.dashboard_controller import render_dashboard_page, get_student_progress_api
from app.controllers.auth_controller import login_view, register_view, logout_view
from app.models.user import User
from data.importer import DataImporter
import os
import tempfile

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


@app.route('/api/partial/users')
def partials_users():
    user_m = User(DB_PATH)
    users = user_m.list_recent(limit=10)
    return render_template('partials/user_list.html', users=users)


@app.route('/api/student/progress')
def student_progress():
    if not session.get('user'):
        return 401
    return get_student_progress_api(DB_PATH)


@app.route('/import', methods=['POST'])
def import_data():
    if session.get('role') != 'teacher':
        return redirect(url_for('dashboard'))

    if 'file' not in request.files:
        flash('Geen bestand geselecteerd.')
        return redirect(url_for('dashboard'))

    file = request.files['file']
    if file.filename == ' ':
        flash('Geen bestand geselecteerd.')
        return redirect(url_for('dashboard'))

    if not file.filename.endswith('.json'):
        flash('Alleen .json bestanden zijn toegestaan.')
        return redirect(url_for('dashboard'))

    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(suffix='.json')
        os.close(fd)

        file.save(tmp_path)
        importer = DataImporter(DB_PATH)
        importer.import_json(tmp_path)

        flash('Data succesvol geimporteerd!')

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
