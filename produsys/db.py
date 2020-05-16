import datetime


class User(object):
    ID_COUNTER = 0

    def __init__(self, id, name, pw_hash):
        self.id = id
        self.name = name
        self.pw_hash = pw_hash


class Project(object):
    ID_COUNTER = 0

    def __init__(self, id, user_id, name):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.total_duration = datetime.timedelta()


class Task(object):
    ID_COUNTER = 0

    def __init__(self, id, name, project: Project, parent=None):
        self.id = id
        self.name = name
        self.project = project
        self.parent = parent
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


class TaskChunk(object):
    ID_COUNTER = 0

    def __init__(self, id, task_name, start, end):
        self.id = id
        self.task_name = task_name
        self.start = start
        self.end = end
        self.duration = end - start


class Database(object):
    """docstring for Database"""

    def __init__(self):
        self.users = {}
        self.projects = {}
        self.tasks = {}
        self.task_chunks = {}

    def create_new_user(self, name, pw_hash):
        id = User.ID_COUNTER
        User.ID_COUNTER += 1
        self.users[id] = User(id, name, pw_hash)
        self.projects[id] = []
        self.tasks[id] = []
        self.task_chunks[id] = []

    def get_user_by_name(self, name):
        for user in self.users.values():
            if user.name == name:
                return user

    def create_project(self, user_id, name):
        id = Project.ID_COUNTER
        Project.ID_COUNTER += 1
        self.projects[user_id].append(Project(id, user_id, name))

    def get_project_by_name(self, user_id, project_name):
        for project in self.projects[user_id]:
            if project.name == project_name:
                return project

    def delete_project(self, user_id, project_id):
        idx = None
        for i, project in enumerate(self.projects[user_id]):
            if project.id == project_id:
                idx = i
                break
        if idx is not None:
            # Delete all tasks in project
            task_ids = [t.id for t in self.tasks[user_id] if (
                t.project.id == project_id)]
            for i in task_ids:
                self.delete_task(user_id, i)
            del self.projects[user_id][idx]

    def get_project_by_id(self, user_id, project_id):
        for project in self.projects[user_id]:
            if project.id == project_id:
                return project

    def get_projects_of_user(self, user_id):
        return self.projects[user_id]

    def get_tasks_of_user(self, user_id):
        return self.tasks[user_id]

    def get_tasks_of_project(self, project):
        return [task for task in self.tasks[project.user_id] if (
            task.project.id == project.id)]

    def create_task(self, name, project, parent=None):
        id = Task.ID_COUNTER
        Task.ID_COUNTER += 1
        self.tasks[project.user_id].append(Task(id, name, project, parent))

    def get_task_by_id(self, user_id, task_id):
        for task in self.tasks[user_id]:
            if task.id == task_id:
                return task

    def delete_task(self, user_id, task_id):
        ids = [task.id for task in self.tasks[user_id] if (
            task.parent and task.parent.id == task_id)]
        for i in ids:
            self.delete_task(user_id, i)
        idx = None
        for i, task in enumerate(self.tasks[user_id]):
            if task.id == task_id:
                idx = i
                break
        if idx is not None:
            # self.delete_chunks_of_task(user_id, self.tasks[user_id][idx].id)
            del self.tasks[user_id][idx]

    def create_task_chunk(self, user_id, task_id, start, end):
        id = TaskChunk.ID_COUNTER
        TaskChunk.ID_COUNTER += 1
        self.task_chunks[user_id].append(TaskChunk(id, task_id, start, end))

    def get_task_chunks(self, user_id, task_id):
        return [t for t in self.task_chunks[user_id] if t.task_id == task_id]

    def task_chunks_on_day(self, user_id, day):
        return [t for t in self.task_chunks[user_id] if (
            t.start.date() >= day and t.end.date() <= day)]

    def delete_chunks_of_task(self, user_id, task_id):
        self.task_chunks[user_id] = [t for t in self.task_chunks[user_id] if (
            t.task_id != task_id)]


db = Database()
