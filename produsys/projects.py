from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from produsys.auth import login_required
from produsys.db import db

bp = Blueprint('projects', __name__, url_prefix='/projects')


@bp.route('')
@login_required
def index():
    projects = db.get_projects_of_user(g.user.id)
    return render_template('projects/index.html', projects=projects)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        error = None

        if not name:
            error = 'Name is required.'
        elif db.get_project_by_name(g.user.id, name) is not None:
            error = 'Name is already in use.'

        if error:
            flash(error)
        else:
            db.create_project(g.user.id, name)

    return redirect(url_for('projects.index'))
