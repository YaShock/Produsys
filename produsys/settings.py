from flask import (
    Blueprint, g, render_template, url_for, request, redirect, send_file
)
from produsys.auth import login_required
from produsys.db import repo
from produsys.to_serializable import to_serializable
import json

bp = Blueprint('settings', __name__, url_prefix='/settings')


def save_user_data(path):
    with open(path, 'w') as file:
        # Save projects
        projects = repo.get_projects_of_user(g.user.id)
        file.write(
            '{}\n'.format(
                json.dumps(
                    {'projects': projects},
                    default=to_serializable)))
        # Save tasks
        tasks = repo.get_tasks_of_user(g.user.id)
        file.write(
            '{}\n'.format(
                json.dumps(
                    {'tasks': tasks},
                    default=to_serializable)))
        # Save task chunks
        for task in tasks:
            task_chunks = repo.get_task_chunks(g.user.id, task.id)
            file.write(
                '{}\n'.format(
                    json.dumps(
                        {'task_chunks': task_chunks},
                        default=to_serializable)))


@bp.route('/')
@login_required
def index():
    return render_template('settings/index.html')


@bp.route('/save', methods=('GET', 'POST'))
@login_required
def save():
    if request.method == 'POST':
        save_user_data('produsys/data.txt')
        return send_file('data.txt', as_attachment=True)
    return redirect(url_for('settings.index'))
