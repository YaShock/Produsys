from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from produsys.auth import login_required
from produsys.db import repo
from produsys.task_utils import set_task_full_paths
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
        task = repo.get_task_by_id(task_id)
    tasks = repo.get_tasks_of_user(g.user.id)

    set_task_full_paths(tasks)
    tasks.sort(key=lambda task: task.full_path)

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
            task = repo.get_task_by_id(task_id)
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
            task = repo.get_task_by_id(task_id)
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


@bp.route('/delete/<tc_id>', methods=('GET', 'POST'))
@login_required
def delete_task_chunk(tc_id):
    task_chunk = repo.get_task_chunk_by_id(tc_id)
    return_url = request.form.get('return_url')

    if request.method == 'POST':
        task = repo.get_task_by_id(task_chunk.task_id)
        duration = task_chunk.start - task_chunk.end
        task._add_duration(duration)
        repo.delete_task_chunk(tc_id)

    if return_url:
        return redirect(return_url)
    return redirect(url_for('dashboard.index', task_id=task_chunk.task_id))


@bp.route('/task_chunk/<task_id>', defaults={'tc_id': None}, methods=('GET', 'POST'))
@bp.route('/task_chunk/<task_id>/<tc_id>', methods=('GET', 'POST'))
@login_required
def edit_task_chunk(task_id, tc_id):
    task = repo.get_task_by_id(task_id)

    if request.method == 'POST':
        return_url = request.form.get('return_url')

        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        if start_time:
            start_time = datetime.strptime(start_time, '%Y/%m/%d %H:%M:%S')
        if end_time:
            end_time = datetime.strptime(end_time, '%Y/%m/%d %H:%M:%S')

        if start_time and end_time and end_time > start_time:
            if tc_id:
                task_chunk = repo.get_task_chunk_by_id(tc_id)
                # Modify task/project times
                new_duration = end_time - start_time
                delta = new_duration - task_chunk.duration
                task_chunk.start = start_time
                task_chunk.end = end_time
                task_chunk.duration = new_duration
                task._add_duration(delta)
                repo.db.session.commit()
            else:
                duration = end_time - start_time
                task._add_duration(duration)
                repo.create_task_chunk(
                    g.user.id, task.id, task.name, start_time, end_time)
                repo.db.session.commit()

        if return_url:
            return redirect(return_url)
        return redirect(url_for('dashboard.index'))

    return_url = request.args.get('return_url')

    start_time = ''
    end_time = ''
    if tc_id:
        task_chunk = repo.get_task_chunk_by_id(tc_id)
        start_time = datetime.strftime(task_chunk.start, '%Y/%m/%d %H:%M:%S')
        end_time = datetime.strftime(task_chunk.end, '%Y/%m/%d %H:%M:%S')
    return render_template('dashboard/edit_task_chunk.html',
                           tc_id=tc_id, task=task, return_url=return_url,
                           start_time=start_time, end_time=end_time)
