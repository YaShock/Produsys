from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from produsys.auth import login_required
from produsys.db import repo
from datetime import timedelta

bp = Blueprint('projects', __name__, url_prefix='/projects')


@bp.route('/', defaults={'display_archived': 0})
@bp.route('/<int:display_archived>')
@login_required
def index(display_archived):
    projects = repo.get_projects_of_user(g.user.id)
    projects.sort(key=lambda p: p.name)

    display_archived = display_archived == 1

    for project in projects:
        project.total_duration_str = str(project.total_duration).split('.')[0]

    return render_template('projects/index.html',
                           projects=projects, display_archived=display_archived)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    display_archived = request.form.get('displayArchived', False)
    display_val = 1 if display_archived == 'true' else 0

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

    return redirect(url_for('projects.index', display_archived=display_val))


@bp.route('/delete/<project_id>', methods=('GET', 'POST'))
@login_required
def delete(project_id):
    display_archived = request.form.get('displayArchived', False)
    display_val = 1 if display_archived == 'true' else 0

    if request.method == 'POST':
        if project_id is not None:
            repo.delete_project(project_id)

    return redirect(url_for('projects.index', display_archived=display_val))


@bp.route('/archive/<project_id>', methods=('GET', 'POST'))
@login_required
def archive(project_id):
    display_archived = request.form.get('displayArchived', False)
    display_val = 1 if display_archived == 'true' else 0

    if request.method == 'POST':
        if project_id is not None:
            repo.project_set_archived(project_id, True)

    return redirect(url_for('projects.index', display_archived=display_val))


@bp.route('/unarchive/<project_id>', methods=('GET', 'POST'))
@login_required
def unarchive(project_id):
    display_archived = request.form.get('displayArchived', False)
    display_val = 1 if display_archived == 'true' else 0

    if request.method == 'POST':
        if project_id is not None:
            repo.project_set_archived(project_id, False)

    return redirect(url_for('projects.index', display_archived=display_val))
