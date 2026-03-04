from flask import render_template, jsonify, session, request
from app.models.partial import Partial


def render_latest_results_partial(db_path: str):
    user_id = session.get('user_id')
    if not user_id:
        return '', 401
    return render_template('partials/latest_results.html')


def get_recent_results_api(db_path: str):
    user_id = session.get('user_id')
    if not user_id:
        return '', 401

    offset = request.args.get('offset', 0, type=int)
    limit = min(request.args.get('limit', 10, type=int), 50)

    partial_m = Partial(db_path)
    data = partial_m.get_recent_results(user_id, offset, limit)
    return jsonify(data)


def render_student_progress_partial(db_path: str):
    user_id = session.get('user_id')
    if not user_id:
        return '', 401

    partial_m = Partial(db_path)
    subjects = partial_m.get_subjects_for_student(user_id)
    chart_data = partial_m.get_progress_over_time(user_id)
    return render_template('partials/student_progress.html', subjects=subjects, chart_data=chart_data)


def get_subject_progress_api(db_path: str, subject_id: int):
    user_id = session.get('user_id')
    if not user_id:
        return '', 401

    partial_m = Partial(db_path)
    chart_data = partial_m.get_progress_by_subject(user_id, subject_id)
    return jsonify(chart_data)


def get_student_progress_api(db_path: str):
    user_id = session.get('user_id')
    if not user_id:
        return '', 401

    partial_m = Partial(db_path)
    progress = partial_m.get_student_progress(user_id)
    return jsonify(progress)
