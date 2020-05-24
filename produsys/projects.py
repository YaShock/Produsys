from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from produsys.auth import login_required
from produsys.db import repo
from datetime import timedelta

bp = Blueprint('projects', __name__, url_prefix='/projects')


@bp.route('')
@login_required
def index():
    projects = repo.get_projects_of_user(g.user.id)

    for project in projects:
        project.total_duration_str = str(project.total_duration).split('.')[0]

    return render_template('projects/index.html', projects=projects)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        error = None

        if not name:
            error = 'Name is required.'
        elif repo.get_project_by_name(g.user.id, name) is not None:
            error = 'Name is already in use.'

        if error:
            flash(error)
        else:
            repo.create_project(g.user.id, name)

    return redirect(url_for('projects.index'))


@bp.route('/delete/<project_id>', methods=('GET', 'POST'))
@login_required
def delete(project_id):
    if request.method == 'POST':
        if project_id is not None:
            repo.delete_project(project_id)

    return redirect(url_for('projects.index'))
