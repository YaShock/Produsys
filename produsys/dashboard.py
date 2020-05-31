from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from produsys.auth import login_required
from produsys.db import repo
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def task_chunks_between_dates(user_id, start_date, end_date):
    task_chunks = []
    current = end_date

    while current >= start_date:
        tc = repo.task_chunks_on_day(user_id, current)
        total_dur = timedelta()

        for chunk in tc:
            chunk.duration_text = str(chunk.duration).split('.')[0]
            total_dur += chunk.duration

        task_chunks.append({
            'date': current,
            'chunks': tc,
            'total_duration': str(total_dur).split('.')[0]
        })
        current -= timedelta(days=1)
    return task_chunks


@bp.route('/', defaults={'task_id': None})
@bp.route('/<task_id>')
@login_required
def index(task_id):
    task = None
    if task_id:
        task = repo.get_task_by_id(int(task_id))
    tasks = repo.get_tasks_of_user(g.user.id)

    if task:
        task.start_time_elapsed = None
        if task.start_time:
            task.start_time_elapsed = str(
                datetime.utcnow() - task.start_time).split('.')[0]

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date is None:
        start_date = datetime.utcnow().date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    if end_date is None:
        end_date = datetime.utcnow().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Fill out the displayed days
    task_chunks = task_chunks_between_dates(g.user.id, start_date, end_date)

    return render_template('dashboard/index.html',
                           tasks=tasks, task=task, task_chunks=task_chunks,
                           start_date=start_date, end_date=end_date)


@bp.route('/start/<task_id>', methods=('GET', 'POST'))
@login_required
def start(task_id):
    return_url = request.form.get('return_url')

    if request.method == 'POST':
        if task_id:
            task = repo.get_task_by_id(int(task_id))
            if task:
                task.start()
                repo.db.session.commit()

    if return_url:
        return redirect(return_url)
    return redirect(url_for('dashboard.index', task_id=task_id))


@bp.route('/stop/<task_id>', methods=('GET', 'POST'))
@login_required
def stop(task_id):
    return_url = request.form.get('return_url')

    if request.method == 'POST':
        if task_id:
            task = repo.get_task_by_id(int(task_id))
            if task:
                if task.started:
                    start = task.start_time
                    end = datetime.utcnow()
                    repo.create_task_chunk(
                        g.user.id, task.id, task.name, start, end)
                task.stop()
                repo.db.session.commit()

    if return_url:
        return redirect(return_url)
    return redirect(url_for('dashboard.index', task_id=task_id))
