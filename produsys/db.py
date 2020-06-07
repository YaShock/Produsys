import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    pw_hash = db.Column(db.String(120), nullable=False)

    def __init__(self, name, pw_hash):
        self.name = name
        self.pw_hash = pw_hash


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    total_duration = db.Column(
        db.Interval,
        nullable=False,
        default=datetime.timedelta())
    archived = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.total_duration = datetime.timedelta()


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    started = db.Column(db.Boolean, nullable=False)
    start_time = db.Column(db.DateTime)
    total_duration = db.Column(
        db.Interval,
        nullable=False,
        default=datetime.timedelta())
    archived = db.Column(db.Boolean, default=False)

    project_id = db.Column(
        db.Integer,
        db.ForeignKey('project.id', ondelete='CASCADE'),
        nullable=False)
    project = db.relationship(
        'Project', backref=backref(
            'tasks', passive_deletes=True))

    parent_id = db.Column(
        db.Integer,
        db.ForeignKey(id))
    chilren = db.relationship(
        'Task',
        cascade='all, delete-orphan',
        backref=backref('parent', remote_side=id))

    def __init__(self, name, project_id, parent=None):
        self.name = name
        self.project_id = project_id
        self.parent_id = parent.id if parent else None
        self.started = False
        self.start_time = None
        self.total_duration = datetime.timedelta()

    def start(self):
        if not self.started:
            self.started = True
            self.start_time = datetime.datetime.utcnow()

    def stop(self):
        if self.started:
            interval = datetime.datetime.utcnow() - self.start_time
            self.started = False
            self.start_time = None
            self._add_duration(interval)

    def _add_duration(self, duration):
        self.total_duration += duration
        if self.parent is None:
            self.project.total_duration += duration
        else:
            self.parent._add_duration(duration)


class TaskChunk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Interval, nullable=False)

    task_id = db.Column(
        db.Integer,
        db.ForeignKey('task.id', ondelete='CASCADE'),
        nullable=False)
    task = db.relationship('Task')

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False)

    def __init__(self, task_id, user_id, start, end):
        self.task_id = task_id
        self.user_id = user_id
        self.start = start
        self.end = end
        self.duration = end - start


class Repository(object):
    def __init__(self, db):
        self.db = db

    def init_app(self, app):
        self.db.init_app(app)
        self.db.create_all()

    def create_new_user(self, name, pw_hash):
        user = User(name, pw_hash)
        self.db.session.add(user)
        self.db.session.commit()

    def get_user_by_id(self, user_id):
        return User.query.filter_by(id=user_id).first()

    def get_user_by_name(self, name):
        return User.query.filter_by(name=name).first()

    def create_project(self, user_id, name):
        project = Project(user_id, name)
        self.db.session.add(project)
        self.db.session.commit()

    def get_project_by_name(self, user_id, project_name):
        return Project.query.filter(
            Project.name == project_name, Project.user_id == user_id).first()

    def delete_project(self, project_id):
        project = Project.query.filter_by(id=project_id).first()
        self.db.session.delete(project)
        self.db.session.commit()

    def project_set_archived(self, project_id, val):
        project = Project.query.filter_by(id=project_id).first()
        project.archived = val
        self.db.session.commit()

    def get_project_by_id(self, project_id):
        return Project.query.filter_by(id=project_id).first()

    def get_projects_of_user(self, user_id):
        return Project.query.filter_by(user_id=user_id).all()

    def get_tasks_of_user(self, user_id):
        return Task.query.filter(Task.project.has(user_id=user_id)).all()

    def get_tasks_of_project(self, project):
        return Task.query.filter_by(project_id=project.id).all()

    def create_task(self, name, project, parent=None):
        task = Task(name, project.id, parent)
        self.db.session.add(task)
        self.db.session.commit()

    def get_task_by_id(self, task_id):
        return Task.query.filter_by(id=task_id).first()

    def delete_task(self, task_id):
        task = Task.query.filter_by(id=task_id).first()
        self.db.session.delete(task)
        self.db.session.commit()

    def task_set_archived(self, id, val):
        def _task_set_archived(task, val):
            task.archived = val
            for t in task.chilren:
                _task_set_archived(t, val)

        task = Task.query.filter_by(id=id).first()
        _task_set_archived(task, val)
        self.db.session.commit()

    def get_task_chunk_by_id(self, id):
        return TaskChunk.query.filter_by(id=id).first()

    def create_task_chunk(self, user_id, task_id, start, end):
        task_chunk = TaskChunk(task_id, user_id, start, end)
        self.db.session.add(task_chunk)
        self.db.session.commit()

    def get_task_chunks(self, user_id, task_id):
        return TaskChunk.query.filter_by(task_id=task_id.id).all()

    def task_chunks_on_day(self, user_id, day):
        all_tc = TaskChunk.query.filter_by(user_id=user_id).all()
        return [t for t in all_tc if (
            t.start.date() >= day and t.end.date() <= day)]

    def delete_task_chunk(self, id):
        task = TaskChunk.query.filter_by(id=id).first()
        self.db.session.delete(task)
        self.db.session.commit()


repo = Repository(db)
