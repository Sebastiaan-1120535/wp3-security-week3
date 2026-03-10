from flask import Flask, request, redirect, url_for, session, render_template, flash
from app.controllers.dashboard_controller import render_dashboard_page
from app.controllers.partial_controller import render_latest_results_partial, render_student_progress_partial, render_student_goals_partial, get_student_progress_api, get_subject_progress_api, get_recent_results_api
from app.controllers.auth_controller import login_view, register_view, logout_view
from app.models.user import User
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.classes import Classes

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


@app.route('/docenten')
def teachers_page():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('role') != 'teacher':
        return redirect(url_for('dashboard'))
    return render_template('pages/teachers.html')


@app.route('/studenten')
def students_page():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('role') != 'student':
        return redirect(url_for('dashboard'))
    return render_template('pages/students.html')

@app.route('/class/<int:class_id>')
def view_class(class_id):
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('role') != 'teacher':
        return redirect(url_for('dashboard'))

    # ensure the logged-in user actually owns this class
    teacher_id = session.get('teacher_id')
    if not teacher_id:
        teacher_m = Teacher(DB_PATH)
        teacher_row = teacher_m.find_by_user_id(session.get('user_id'))
        if not teacher_row:
            return redirect(url_for('dashboard'))
        teacher_id = teacher_row['teacher_id']
    class_m = Classes(DB_PATH)
    cls = class_m.find_by_id(class_id)
    if not cls or cls['teacher_id'] != teacher_id:
        return redirect(url_for('dashboard'))

    student_m = Student(DB_PATH)
    students = student_m.find_by_class_id(class_id)
    return render_template('pages/class_detail.html', cls=cls, students=students)




@app.route('/api/partial/users')
def partials_users():
    user_m = User(DB_PATH)
    users = user_m.list_recent(limit=10)
    return render_template('partials/user_list.html', users=users)

@app.route('/api/partial/teachers')
def partials_teachers():
    teacher_m = Teacher(DB_PATH)
    teachers = teacher_m.list_recent(limit=10)
    return render_template('partials/teacher_list.html', teachers=teachers)

@app.route('/api/partial/students')
def partials_student():
    student_m = Student(DB_PATH)
    student = student_m.list_recent(limit=10)
    return render_template('partials/student_list.html', students=student)

@app.route('/api/partial/classes')
def partials_classes():
    if not session.get('user'):
        return 401
    if session.get('role') != 'teacher':
        return 403

    # map logged-in user to their teacher record (prefer cached session value)
    teacher_id = session.get('teacher_id')
    if not teacher_id:
        teacher_m = Teacher(DB_PATH)
        teacher_row = teacher_m.find_by_user_id(session.get('user_id'))
        if not teacher_row:
            return 403
        teacher_id = teacher_row['teacher_id']
    class_m = Classes(DB_PATH)
    classes = class_m.find_by_teacher_id(teacher_id)

    # attach students to each class
    student_m = Student(DB_PATH)
    enriched = []
    for cls in classes:
        cls = dict(cls)
        cls['students'] = student_m.find_by_class_id(cls['class_id'])
        enriched.append(cls)
    return render_template('partials/classes_list.html', classes=enriched)

@app.route('/api/partial/latest-results')
def partial_latest_results():
    if not session.get('user'):
        return '', 401
    return render_latest_results_partial(DB_PATH)


@app.route('/api/student/recent-results')
def recent_results():
    if not session.get('user'):
        return '', 401
    return get_recent_results_api(DB_PATH)


@app.route('/api/partial/student-progress')
def partial_student_progress():
    if not session.get('user'):
        return '', 401
    return render_student_progress_partial(DB_PATH)


@app.route('/api/partial/student-goals')
def partial_student_goals():
    if not session.get('user'):
        return '', 401
    return render_student_goals_partial(DB_PATH)


@app.route('/api/student/progress')
def student_progress():
    if not session.get('user'):
        return '', 401
    return get_student_progress_api(DB_PATH)


@app.route('/api/student/progress/subject/<int:subject_id>')
def student_progress_by_subject(subject_id):
    if not session.get('user'):
        return '', 401
    return get_subject_progress_api(DB_PATH, subject_id)


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