import functools
from flask import g, current_app, render_template, Blueprint, redirect, session, url_for, flash, request

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(buffered=True, dictionary=True)
        error = None

        if not username:
            error = "Username required!!"
        elif not password:
            error = "Password required!!"
        else:
            cursor.execute("SELECT * FROM USER WHERE USER_NAME=%s", (username,))
            user = cursor.fetchone()
            if user:
                error = "User account already created.Please login!!"
                flash(error)
                return redirect(url_for('auth.login'))
            else:
                print(username, generate_password_hash(password))
                cursor.execute("INSERT INTO USER(USER_NAME, PASSWORD) VALUES(%s, %s)", (
                 username, generate_password_hash(password)))
                db.commit()
                return redirect(url_for('auth.login'))

            cursor.close()
            db.close()

            flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(buffered=True, dictionary=True)
        error = None
        if not username:
            error = "Username required!!"
        elif not password:
            error = "Password required!!"
        else:
            cursor.execute("SELECT * FROM USER WHERE USER_NAME=%s", (username,))
            user = cursor.fetchone()
            if user is None:
                error = "Invalid username"
            elif not check_password_hash(user['PASSWORD'], password):
                error = "Invalid Password"

        if error is None:
            session.clear()
            session['user_id'] = user['USER_ID']
            return redirect(url_for('index'))
        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM USER WHERE USER_ID=%s", (user_id,))
        g.user = cursor.fetchone()


@bp.route('/logout', methods=('GET', 'POST'))
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view
