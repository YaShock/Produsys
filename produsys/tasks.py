from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from produsys.auth import login_required
from produsys.db import repo
from produsys.task_utils import get_hierarchical_tasks

bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@bp.route('/', defaults={'project_id': None})
@bp.route('/<project_id>')
@login_required
def index(project_id):
    projects = repo.get_projects_of_user(g.user.id)
    project = None
    if project_id is not None:
        project = repo.get_project_by_id(project_id)
    tasks = []

    display_archived = session.get('display_all_tasks')

    if project is not None:
        tasks = repo.get_tasks_of_project(project)
        tasks = get_hierarchical_tasks(project.id, tasks)

    return render_template('tasks/index.html',
                           project=project, projects=projects, tasks=tasks, display_archived=display_archived)


@bp.route('/create/<project_id>', methods=('GET', 'POST'))
@login_required
def create(project_id):
    if request.method == 'POST':
        project = repo.get_project_by_id(project_id)
        name = request.form['name']
        error = None

        if not name:
            error = 'Name is required.'

        if error:
            flash(error)
        elif project is not None:
            repo.create_task(name, project)

    return redirect(url_for('tasks.index', project_id=project_id))


@bp.route('/edit/<project_id>/<task_id>', methods=('GET', 'POST'))
@login_required
def edit(project_id, task_id):
    task = repo.get_task_by_id(task_id)

    if task:
        if request.method == 'POST':
            name = request.form['name']
            error = None

            if not name:
                error = 'Name is required.'

            if error:
                flash(error)
            else:
                task.name = name
                repo.db.session.commit()
        else:
            return render_template(
                'tasks/edit.html', task=task, project_id=project_id)

    return redirect(url_for('tasks.index', project_id=project_id))


@bp.route('/subtask/<project_id>/<parent_id>', methods=('GET', 'POST'))
@login_required
def subtask(project_id, parent_id):
    parent = None
    if parent_id is not None:
        parent = repo.get_task_by_id(parent_id)
    if parent is None:
        return redirect(
            url_for('tasks.index', project_id=project_id))

    if request.method == 'POST':
        name = request.form['name']
        error = None

        if not name:
            error = 'Name is required.'

        if error:
            flash(error)
        else:
            repo.create_task(name, parent.project, parent)
        return redirect(
            url_for('tasks.index', project_id=project_id))
    else:
        return render_template('tasks/subtask.html',
                               project_id=project_id, task=parent)


@bp.route('/delete/<project_id>/<task_id>', methods=('GET', 'POST'))
@login_required
def delete(project_id, task_id):
    if request.method == 'POST':
        if task_id is not None:
            repo.delete_task(task_id)

    return redirect(url_for('tasks.index', project_id=project_id))


@bp.route('/archive/<project_id>/<task_id>', methods=('GET', 'POST'))
@login_required
def archive(project_id, task_id):
    if request.method == 'POST':
        if task_id is not None:
            repo.task_set_archived(task_id, True)

    return redirect(url_for('tasks.index', project_id=project_id))


@bp.route('/unarchive/<project_id>/<task_id>', methods=('GET', 'POST'))
@login_required
def unarchive(project_id, task_id):
    if request.method == 'POST':
        if task_id is not None:
            repo.task_set_archived(task_id, False)

    return redirect(url_for('tasks.index', project_id=project_id))


@bp.route('/filter', methods=('GET', 'POST'))
@login_required
def set_filter():
    if request.method == 'POST':
        display_all = request.form.get('display_all', 'false')
        session['display_all_tasks'] = display_all == 'true'

    return redirect(url_for('tasks.index'))
