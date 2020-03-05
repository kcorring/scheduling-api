import json

from data.models import User
from data.exceptions import UserNotFoundException


class Database():
    def __init__(self, db):
        self._db = db

    def get_user(self, user_id):
        user = self._db.get(user_id)
        if not user:
            raise UserNotFoundException
        return user

    def get_user_events(self, user_id, start_date, end_date):
        user = self.get_user(user_id)

        events_in_range = [
            event
            for event in user.events
            if event.start_date < end_date and event.end_date > start_date
        ]

        return sorted(events_in_range, key=lambda e: e.start_date)

    @classmethod
    def from_file(cls, filename='data/db.json'):
        with open(filename) as f:
            data = json.load(f)

        db = {}
        for user_data in data:
            db[user_data['user_id']] = User.from_json(user_data)

        return cls(db)
