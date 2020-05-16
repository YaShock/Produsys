from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from produsys.auth import login_required
from produsys.db import db

bp = Blueprint('tasks', __name__, url_prefix='/tasks')


def get_subtasks(parent_id, all_tasks):
    print('get_subtasks for {}'.format(parent_id))
    tasks = []
    for task in all_tasks:
        if task.parent and task.parent.id == parent_id:
            tasks.append(task)
            print('subtask {}'.format(task.id))
    for task in tasks:
        task.subtasks = get_subtasks(task.id, all_tasks)
    return tasks


def get_hierarchical_tasks(project_id, all_tasks):
    tasks = []
    for task in all_tasks:
        if task.parent is None and task.project.id == project_id:
            tasks.append(task)
    for task in tasks:
        task.subtasks = get_subtasks(task.id, all_tasks)
    return tasks


@bp.route('/', defaults={'project_id': None})
@bp.route('/<project_id>')
@login_required
def index(project_id):
    projects = db.get_projects_of_user(g.user.id)
    project = None
    if project_id is not None:
        project = db.get_project_by_id(g.user.id, int(project_id))
    tasks = []

    if project is not None:
        tasks = db.get_tasks_of_project(project)
        tasks = get_hierarchical_tasks(project.id, tasks)

    return render_template('tasks/index.html',
                           project=project, projects=projects, tasks=tasks)


@bp.route('/create/<project_id>', methods=('GET', 'POST'))
@login_required
def create(project_id):
    if request.method == 'POST':
        project = db.get_project_by_id(g.user.id, int(project_id))
        name = request.form['name']
        error = None

        if not name:
            error = 'Name is required.'

        if error:
            flash(error)
        elif project is not None:
            db.create_task(name, project)

    return redirect(url_for('tasks.index', project_id=project_id))


@bp.route('/subtask/<project_id>/<parent_id>', methods=('GET', 'POST'))
@login_required
def subtask(project_id, parent_id):
    parent = None
    if parent_id is not None:
        parent = db.get_task_by_id(g.user.id, int(parent_id))
    if parent is None:
        return redirect(url_for('tasks.index', project_id=project_id))

    if request.method == 'POST':
        name = request.form['name']
        error = None

        if not name:
            error = 'Name is required.'

        if error:
            flash(error)
        else:
            db.create_task(name, parent.project, parent)
        return redirect(url_for('tasks.index', project_id=project_id))
    else:
        return render_template('tasks/subtask.html',
                               project_id=project_id, task=parent)


@bp.route('/delete/<project_id>/<task_id>', methods=('GET', 'POST'))
@login_required
def delete(project_id, task_id):
    if request.method == 'POST':
        if task_id is not None:
            db.delete_task(g.user.id, int(task_id))

    return redirect(url_for('tasks.index', project_id=project_id))
