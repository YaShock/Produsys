from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from produsys.auth import login_required
from produsys.db import repo
from produsys.task_utils import get_subtasks
from datetime import datetime, timedelta

bp = Blueprint('statistics', __name__, url_prefix='/statistics')

def calc_stats(items, parent=None):
    dur_sum = timedelta()

    for item in items:
        item.total_duration_str = str(item.total_duration).split('.')[0]
        dur_sum += item.total_duration

    for item in items:
        if parent:
            dur_sum = parent.total_duration
        if dur_sum.total_seconds() == 0:
            item.percentage = '0 %'
        else:
            r = item.total_duration / dur_sum
            item.percentage = '{} %'.format(r * 100)


@bp.route('/')
@login_required
def index():
    projects = repo.get_projects_of_user(g.user.id)
    calc_stats(projects)

    return render_template('statistics/index.html',
                           projects=projects, section='all projects')

@bp.route('/project/<id>')
@login_required
def project(id):
    project = repo.get_project_by_id(id)

    if project is None:
        return redirect(url_for('statistics.index'))

    tasks = repo.get_tasks_of_project(project)
    top_tasks = [task for task in tasks if task.parent is None]
    calc_stats(top_tasks, project)

    return render_template('statistics/tasks.html',
                           tasks=top_tasks, section=project.name)


@bp.route('/task/<id>')
def task(id):
    task = repo.get_task_by_id(id)
    tasks = repo.get_tasks_of_user(g.user.id)
    subtasks = get_subtasks(task.id, tasks)
    calc_stats(subtasks, task)

    return render_template('statistics/tasks.html',
                           tasks=subtasks, section=task.name)
