from flask import g, current_app, render_template, Blueprint, redirect, session, url_for, flash, request
from werkzeug.exceptions import abort
from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT A.USER_NAME, A.USER_ID, B.AUTHOR_ID, B.CREATED, B.POST_ID, B.TITLE,"
                   " B.BODY FROM USER A JOIN POST B ON "
                   "A.USER_ID=B.AUTHOR_ID ORDER BY CREATED DESC")
    posts = cursor.fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        db = get_db()
        cursor = db.cursor()
        error = None

        if not title:
            error = "Title required!!"
        elif error is not None:
            flash(error)
        else:
            cursor.execute("INSERT INTO POST(TITLE, BODY, AUTHOR_ID) VALUES(%s, %s, %s)",
                           (title, body, g.user['USER_ID']))
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(post_id, check_author=True):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT A.USER_NAME, A.USER_ID, B.AUTHOR_ID, B.CREATED, B.POST_ID, B.TITLE,"
                   " B.BODY FROM USER A JOIN POST B ON "
                   "A.USER_ID=B.AUTHOR_ID WHERE B.POST_ID=%s", (post_id, ))
    post = cursor.fetchone()

    if post is None:
        abort(404, "Post id {} doesn't exist.".format(post_id))
    elif check_author and post['AUTHOR_ID'] != g.user['USER_ID']:
        abort(403, "Forbidden")

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = "Enter suitable Title!!!"
        else:
            if error is None:
                db = get_db()
                cursor = db.cursor()
                cursor.execute("UPDATE POST SET TITLE = %s, BODY = %s WHERE POST_ID= %s",
                               (title, body, id))
                db.commit()
                return redirect(url_for('blog.index'))
            else:
                flash(error)

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('GET', 'POST'))
def delete(id):
    get_post(post_id=id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM POST WHERE POST_ID = %s", (id, ))
    db.commit()
    return redirect(url_for('blog.index'))
