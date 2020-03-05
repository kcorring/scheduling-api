from data.models import Event
from utils.availability_utils import get_user_availability, Availability

START_DATE = '2019-01-01T10:00:00+0000'
END_DATE = '2019-01-01T18:00:00+0000'


def test__no_events():
    """If there are no events, the full date range should be marked as
    available.
    """
    result = get_user_availability(
        user_events=[],
        start_date=START_DATE,
        end_date=END_DATE,
    )

    assert result == [
        Availability(START_DATE, END_DATE),
    ]


def test__event_overlapping_with_start_date():
    """If event overlaps with start date, the earliest availability starts
    after that event ends.
    """
    event = Event(
        id=1,
        title='A',
        start_date='2019-01-01T09:00:00+00:00',
        end_date='2019-01-01T12:00:00+00:00',
    )

    result = get_user_availability(
        user_events=[event],
        start_date=START_DATE,
        end_date=END_DATE,
    )

    assert result == [
        Availability(event.end_date, END_DATE),
    ]


def test__event_overlapping_with_end_date():
    """If event overlaps with start date, the last availability ends
    when that event starts.
    """
    event = Event(
        id=1,
        title='A',
        start_date='2019-01-01T12:00:00+00:00',
        end_date='2019-01-01T20:00:00+00:00',
    )

    result = get_user_availability(
        user_events=[event],
        start_date=START_DATE,
        end_date=END_DATE,
    )

    assert result == [
        Availability(START_DATE, event.start_date),
    ]


def test__overlapping_events():
    """If events overlaps, their earliest start date and latest end date
    are used when computing availability.
    """
    event1 = Event(
        id=1,
        title='A',
        start_date='2019-01-01T12:00:00+00:00',
        end_date='2019-01-01T14:00:00+00:00',
    )
    event2 = Event(
        id=2,
        title='B',
        start_date='2019-01-01T13:00:00+00:00',
        end_date='2019-01-01T15:00:00+00:00',
    )

    result = get_user_availability(
        user_events=[event1, event2],
        start_date=START_DATE,
        end_date=END_DATE,
    )

    assert result == [
        Availability(START_DATE, event1.start_date),
        Availability(event2.end_date, END_DATE),
    ]


def test__multiple_availabilities():
    """All availabilities are correctly identified."""
    event1 = Event(
        id=1,
        title='A',
        start_date='2019-01-01T12:00:00+00:00',
        end_date='2019-01-01T14:00:00+00:00',
    )
    event2 = Event(
        id=2,
        title='B',
        start_date='2019-01-01T15:00:00+00:00',
        end_date='2019-01-01T16:00:00+00:00',
    )
    event3 = Event(
        id=3,
        title='C',
        start_date='2019-01-01T17:00:00+00:00',
        end_date='2019-01-01T17:30:00+00:00',
    )

    result = get_user_availability(
        user_events=[event1, event2, event3],
        start_date=START_DATE,
        end_date=END_DATE,
    )

    assert result == [
        Availability(START_DATE, event1.start_date),
        Availability(event1.end_date, event2.start_date),
        Availability(event2.end_date, event3.start_date),
        Availability(event3.end_date, END_DATE),
    ]
