from flask import render_template, request, redirect, url_for, session, flash
from app.models.user import User


def login_view(db_path: str):
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash('Voer e-mail en wachtwoord in.')
            return redirect(url_for('login'))
        user = User(db_path).authenticate(email, password)
        if user:
            session['user'] = user['email']
            session['role'] = user['role']
            session['user_id'] = user['user_id']
            # if teacher, also fetch corresponding teacher_id
            if user['role'] == 'teacher':
                from app.models.teacher import Teacher
                teacher_row = Teacher(db_path).find_by_user_id(user['user_id'])
                if teacher_row:
                    session['teacher_id'] = teacher_row['teacher_id']
            flash('Inloggen gelukt.')
            return redirect(url_for('home'))
        else:
            flash('Onjuiste e-mail of wachtwoord.')
            return redirect(url_for('login'))

    return render_template('pages/login.html')


def register_view(db_path: str):
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if not email or not password:
            flash('Vul e-mail en wachtwoord in.')
            return redirect(url_for('register'))
        if password != password2:
            flash('Wachtwoorden komen niet overeen.')
            return redirect(url_for('register'))
        ok, result = User(db_path).create_user(email, password)
        if ok:
            session['user'] = result['email']
            session['role'] = result['role']
            session['user_id'] = result['user_id']
            # new registrants are not automatically teachers in `teachers` table
            # so we only add teacher_id if the record already exists
            if result['role'] == 'teacher':
                from app.models.teacher import Teacher
                teacher_row = Teacher(db_path).find_by_user_id(result['user_id'])
                if teacher_row:
                    session['teacher_id'] = teacher_row['teacher_id']
            flash('Registratie gelukt. Je bent ingelogd.')
            return redirect(url_for('home'))
        else:
            flash(result)
            return redirect(url_for('register'))

    return render_template('pages/register.html')


def logout_view(db_path: str):
    session.pop('user', None)
    session.pop('role', None)
    session.pop('user_id', None)
    flash('Je bent uitgelogd.')
    return redirect(url_for('home'))
