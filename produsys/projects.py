from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from produsys.auth import login_required
from produsys.db import repo
from datetime import timedelta

bp = Blueprint('projects', __name__, url_prefix='/projects')


@bp.route('/')
@login_required
def index():
    projects = repo.get_projects_of_user(g.user.id)
    projects.sort(key=lambda p: p.name)

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


@bp.route('/edit/<project_id>', methods=('GET', 'POST'))
@login_required
def edit(project_id):
    project = repo.get_project_by_id(project_id)

    if project:
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
                project.name = name
                repo.db.session.commit()
        else:
            return render_template(
                'projects/edit.html', project=project)

    return redirect(url_for('projects.index'))


@bp.route('/delete/<project_id>', methods=('GET', 'POST'))
@login_required
def delete(project_id):
    if request.method == 'POST':
        if project_id is not None:
            repo.delete_project(project_id)

    return redirect(url_for('projects.index'))


@bp.route('/archive/<project_id>', methods=('GET', 'POST'))
@login_required
def archive(project_id):
    if request.method == 'POST':
        if project_id is not None:
            repo.project_set_archived(project_id, True)

    return redirect(url_for('projects.index'))


@bp.route('/unarchive/<project_id>', methods=('GET', 'POST'))
@login_required
def unarchive(project_id):
    if request.method == 'POST':
        if project_id is not None:
            repo.project_set_archived(project_id, False)

    return redirect(url_for('projects.index'))


@bp.route('/filter', methods=('GET', 'POST'))
@login_required
def set_filter():
    if request.method == 'POST':
        display_all = request.form.get('display_all', 'false')
        session['display_all_projects'] = display_all == 'true'

    return redirect(url_for('projects.index'))
