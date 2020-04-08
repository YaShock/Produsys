class User(object):
    ID_COUNTER = 0

    def __init__(self, id, name, pw_hash):
        self.id = id
        self.name = name
        self.pw_hash = pw_hash


class Project(object):
    ID_COUNTER = 0

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.total_hours = 0


class Database(object):
    """docstring for Database"""

    def __init__(self):
        self.users = {}
        self.projects = {}

    def create_new_user(self, name, pw_hash):
        id = User.ID_COUNTER
        User.ID_COUNTER += 1
        self.users[id] = User(id, name, pw_hash)
        self.projects[id] = []

    def get_user_by_name(self, name):
        for user in self.users.values():
            if user.name == name:
                return user
        return None

    def create_project(self, user_id, name):
        self.projects[user_id].append(Project(user_id, name))

    def get_projects_of_user(self, user_id):
        return self.projects[user_id]


db = Database()
