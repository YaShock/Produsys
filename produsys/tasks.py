from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from produsys.auth import login_required
from produsys.db import db

bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@bp.route('/', defaults={'project_id': None})
@bp.route('/<project_id>')
@login_required
def index(project_id):
    print('tasks index: project_id {}'.format(project_id))
    projects = db.get_projects_of_user(g.user.id)
    project = None
    if project_id is not None:
        project = db.get_project_by_id(g.user.id, int(project_id))
    tasks = []

    if project is not None:
        tasks = db.get_tasks_of_project(project)

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
