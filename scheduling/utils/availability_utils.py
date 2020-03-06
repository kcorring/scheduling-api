import arrow

UTC = 'UTC'


class Availability():
    """Representation of a user's availability."""

    def __init__(self, start_date, end_date):
        """Initialize an availability.

        Args:
            start_date(str): The start date in ISO 8601 format.
            end_date(str): The end date in ISO 8601 format.
        """
        self.start_date = start_date
        self.end_date = end_date

    def to_json(self):
        """Serialize the availability to json.

        Returns:
            (dict): The availability object in json-serializable form.
        """
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

    def __eq__(self, other):
        if other is self:
            return True
        if type(other) != type(self):
            return False
        return (
            (other.start_date, other.end_date) ==
            (self.start_date, self.end_date)
        )


def get_user_availability(user_events, start_date, end_date):
    """Calculate a user's availability for a given date range.

    Converts a user's schedule of events into a schedule of availability
    for a given time range.

    Args:
        user_events(list(Event)): The users events that are scheduled within
            the date range. Assumed to be in ascending order by start date
            and that all events have some overlap with the provided date range.
        start_date(str): The start date of the date range for which
            availability should be calculated. Assumed to be in ISO 8601
            format, UTC.
        end_date(str): The end date of the date range for which availability
            should be calculated. Assumed to be in ISO 8601 format, UTC.

    Returns:
        (list(Availability)): A list of availabilities for user.
    """
    return _get_user_availability(
        user_events,
        start_date,
        end_date,
        add_availability_func=add_availability,
        get_date_func=lambda date: date,
    )


def get_user_work_hour_availability(user_events, start_date, end_date,
                                    working_hours, time_zone):
    """Calculate a user's availability for a given date range.

    Converts a user's schedule of events into a schedule of availability
    for a given time range, taking working hours into consideration.

    Args:
        user_events(list(Event)): The users events that are scheduled within
            the date range. Assumed to be in ascending order by start date
            and that all events have some overlap with the provided date range.
        start_date(str): The start date of the date range for which
            availability should be calculated. Assumed to be in ISO 8601
            format, UTC.
        end_date(str): The end date of the date range for which availability
            should be calculated. Assumed to be in ISO 8601 format, UTC.
        working_hours(data.models.WorkingHours): The hours during which
            a user works on a daily basis.
        time_zone(str): The time zone within which the user works.

    Returns:
        (list(Availability)): A list of availabilities for the user, within
            the user's working hours.
    """
    def get_date_func(date):
        return arrow.get(date).to(time_zone)

    add_availability_func = generate_add_work_hour_availability_function(
        working_hours,
    )

    return _get_user_availability(
        user_events,
        start_date,
        end_date,
        add_availability_func,
        get_date_func)


def _get_user_availability(user_events, start_date, end_date,
                           add_availability_func, get_date_func):
    """Utility function for ascertaining a user's availability.

    Args:
        user_events(list(Event)): The users events that are scheduled within
            the date range. Assumed to be in ascending order by start date
            and that all events have some overlap with the provided date range.
        start_date(str): The start date of the date range for which
            availability should be calculated. Assumed to be in ISO 8601
            format, UTC.
        end_date(str): The end date of the date range for which availability
            should be calculated. Assumed to be in ISO 8601 format, UTC.
        add_availability_func(function): The function responsible for
            determining if an open slot in a user's schedule is a valid
            availability for them, and adding it to the availabilities if so.
        get_date_func(function): The function responsible for converting
            an ISO 8601 UTC datestring into the format expected by the
            add_availability_func.

    Returns:
        (list(Availability)): A list of valid availabilities for the user.
    """
    availabilities = []

    start_date = get_date_func(start_date)
    end_date = get_date_func(end_date)

    availability_start = start_date

    for event in user_events:
        event_start = get_date_func(event.start_date)
        event_end = get_date_func(event.end_date)

        # Account for overlapping events
        if event_start <= availability_start:
            availability_start = max(availability_start, event_end)
            continue

        add_availability_func(
            availabilities=availabilities,
            start_date=availability_start,
            end_date=event_start,
        )

        availability_start = event_end

    # Account for any availability between the final event & the end date
    if availability_start < end_date:
        add_availability_func(
            availabilities=availabilities,
            start_date=availability_start,
            end_date=end_date,
        )

    return availabilities


def add_availability(availabilities, start_date, end_date):
    """Add an availability to a list.

    Args:
        availabilities(list(Availability)): The list to which the
            availability should be appended.
        start_date(str): The start of the availability range in ISO 8601
            format.
        end_date(str): The end of the availability range in ISO 8601
            format.
    """
    availabilities.append(Availability(start_date, end_date))


def generate_add_work_hour_availability_function(working_hours):
    """Generate a work-hour conscious function for adding availabilities.

    Args:
        working_hours(data.models.WorkingHours): The work hours to be
            considered when adding availabilities.

    Returns:
        (function): A function that determines the portions of an
            availability that do not intersect with working hours, and
            adds those to a list.
    """
    def _add_work_hour_availability(availabilities, start_date, end_date):
        add_work_hour_availability(
            availabilities,
            start_date,
            end_date,
            working_hours,
        )
    return _add_work_hour_availability


def add_work_hour_availability(availabilities, start_date,
                               end_date, working_hours):
    """Append work-hour-conscious availabilties to a list.

    If an availability window spans multiple working days, the window will
    be split into multiple availabilities that intersect with the provided
    working hours.

    Args:
        start_date(arrow.Arrow): The start date of the availability range.
        end_date(arrow.Arrow): The end date of the availability range.
        working_hours(data.models.WorkingHours): The working hours of a user.
    """
    work_day_start = start_date.replace(
        hour=working_hours.start.hour,
        minute=working_hours.start.minute,
    )
    work_day_end = start_date.replace(
        hour=working_hours.end.hour,
        minute=working_hours.end.minute,
    )

    while work_day_start < end_date:
        _add_isoformat_utc_availability(
            availabilities,
            start_date,
            end_date,
            work_day_start,
            work_day_end,
        )
        work_day_start = work_day_start.shift(days=1)
        work_day_end = work_day_end.shift(days=1)


def _add_isoformat_utc_availability(availabilities, start_date, end_date,
                                    work_day_start, work_day_end):
    """Utility function for adding an availability to a list, taking work
    hours into account.

    If, when work hours are taken into account, there is a non-zero duration
    of availability, that availability will be added to the provided list.

    Args:
        availabilities(list(Availability)): The list of availabilities to be
            added to.
        start_date(arrow.Arrow): The start of the availability range.
        end_date(arrow.Arrow): The end of the availability range.
        work_day_start(arrow.Arrow): The start of a work day.
        work_day_end(arrow.Arrow): The end of a work day.
    """
    availability_start = max(work_day_start, start_date).to(UTC).isoformat()
    availability_end = min(work_day_end, end_date).to(UTC).isoformat()

    if availability_start < availability_end:
        availability = Availability(availability_start, availability_end)
        availabilities.append(availability)


def get_intersecting_availabilities(user_availabilities):
    """Determine all intersecting availabilities for the given users.

    Args:
        user_availabilities(list(list(Availability))): A list of user
            availabilities, where each user's list of availabilities
            is ordered by ascending start time.

    Returns:
        list(Availability): A list of availabilities common to all
            given users.
    """
    iters = []

    max_start_date = ''
    for user_availability in user_availabilities:
        iterator = iter(user_availability)
        current = next(iterator)

        iters.append({'current': current, 'iterator': iterator})

        max_start_date = max(max_start_date, current.start_date)

    availabilities = []

    while True:
        min_end = min(iters,  key=lambda i: i['current'].end_date)
        min_end_date = min_end['current'].end_date
        if min_end_date > max_start_date:
            availability = Availability(max_start_date, min_end_date)
            availabilities.append(availability)

        try:
            min_end['current'] = next(min_end['iterator'])
        except StopIteration:
            break

        max_start_date = max(min_end['current'].start_date, max_start_date)

    return availabilities


# This was a first pass that I abstracted to the above; keeping it here to show
# the thought process.
def _deprecated_get_intersecting_availabilities(availabilities1,
                                                availabilities2):
    i = 0
    j = 0
    availabilities = []

    while True:
        availability1 = availabilities1[i]
        availability2 = availabilities2[j]

        max_start = max(availability1.start_date, availability2.start_date)
        min_end = min(availability1.end_date, availability2.end_date)

        if min_end > max_start:
            availabilities.append(Availability(max_start, min_end))

        if min_end == availability1.end_date:
            i += 1
            if i >= len(availabilities1):
                break
        else:
            j += 1
            if j >= len(availabilities2):
                break

    return availabilities
