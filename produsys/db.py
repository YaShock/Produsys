class User(object):
    """docstring for User"""

    def __init__(self, id, name, pw_hash):
        self.id = id
        self.name = name
        self.pw_hash = pw_hash


class Database(object):
    """docstring for Database"""

    def __init__(self):
        self.users = {}

    def create_new_user(self, name, pw_hash):
        id = len(self.users)
        self.users[id] = User(id, name, pw_hash)

    def get_user_by_name(self, name):
        for user in self.users.values():
            if user.name == name:
                return user
        return None


db = Database()
