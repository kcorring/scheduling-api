from collections import namedtuple

WorkingHours = namedtuple('WorkingHours', ['start', 'end'])
WorkingHoursTime = namedtuple('WorkingHoursTime', ['hour', 'minute'])


def _parse_work_hours(time):
    hours, minutes = time.split(':')
    return int(hours), int(minutes)


class User:
    def __init__(self, id, working_hours, time_zone, events):
        self.id = id
        self._working_hours = working_hours
        self.working_hours = WorkingHours(
            WorkingHoursTime(*_parse_work_hours(working_hours.start)),
            WorkingHoursTime(*_parse_work_hours(working_hours.end)),
        )
        self.time_zone = time_zone
        self.events = events

    def to_json(self):
        return {
            'id': self.id,
            'working_hours': {
                'start': self._working_hours.start,
                'end': self._working_hours.end,
            },
            'time_zone': self.time_zone,
            'events': [event.to_json() for event in self.events]
        }

    @classmethod
    def from_json(cls, data):
        events = [
            Event.from_json(event)
            for event in data['events']
        ]

        return cls(
            id=data['user_id'],
            working_hours=WorkingHours(
               data['working_hours']['start'],
               data['working_hours']['end'],
            ),
            time_zone=data['time_zone'],
            events=events,
        )


class Event:
    def __init__(self, id, title, start_date, end_date):
        self.id = id
        self.title = title
        self.start_date = start_date
        self.end_date = end_date

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'start': self.start_date,
            'end': self.end_date,
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            id=data['id'],
            title=data['title'],
            start_date=data['start'],
            end_date=data['end'],
        )
