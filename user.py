import uuid


class UserMap:
    def __init__(self):
        self.map = {}

    def add_user(self):
        user = User()
        user_id = user.user_id
        self.map[user_id] = user
        return user_id

    def add_lookup(self, user_id):
        self.map[user_id].add_lookup()

    def get_user(self, user_id):
        return self.map[user_id]

    def set_reading(self, user_id, article_id):
        self.map[user_id].set_reading(article_id)


class User:
    def __init__(self):
        self.user_id = uuid.uuid4()
        self.reading = None
        self.lookups = {}

    def set_reading(self, article_id):
        self.reading = article_id

    def add_lookup(self):
        article_id = self.reading
        if article_id in self.lookups:
            self.lookups[article_id] += 1
        else:
            self.lookups[article_id] = 1
        print(self.lookups[article_id])
