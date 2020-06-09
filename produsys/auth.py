import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from produsys.db import repo

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif repo.get_user_by_name(username) is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            repo.create_new_user(username, generate_password_hash(password))
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        utc_offset = int(request.form.get('utc_offset', 0))

        error = None
        user = repo.get_user_by_name(username)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.pw_hash, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            session['utc_offset'] = utc_offset
            url = request.args.get('url')
            return redirect(url or url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    user = repo.get_user_by_id(user_id)
    if user is None:
        session.clear()
        user_id = None

    if user_id is None:
        g.user = None
    else:
        g.user = user


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login') + '?url=' + request.url)
        return view(**kwargs)

    return wrapped_view
