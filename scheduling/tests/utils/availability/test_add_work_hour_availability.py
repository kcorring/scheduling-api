import arrow

from data.models import WorkingHours, WorkingHoursTime
from utils.availability_utils import add_work_hour_availability, Availability

WORKING_HOURS = WorkingHours(
    WorkingHoursTime(9, 0),
    WorkingHoursTime(17, 30),
)


def test__single_day_availability_during_work_hours():
    """If a block of availability is fully contianed during work hours, it is
    preserved."""
    availabilities = []
    start_date = arrow.get("2019-01-01T11:00:00+00:00")
    end_date = arrow.get("2019-01-01T12:00:00+00:00")

    add_work_hour_availability(availabilities, start_date,
                               end_date, WORKING_HOURS)

    assert availabilities == [
        Availability(start_date.isoformat(), end_date.isoformat()),
    ]


def test__single_day_availability_ends_after_work_hours():
    """If a block of availability ends after work hours, it is truncated."""
    availabilities = []
    start_date = arrow.get("2019-01-01T11:00:00+00:00")
    end_date = arrow.get("2019-01-01T18:00:00+00:00")

    add_work_hour_availability(availabilities, start_date,
                               end_date, WORKING_HOURS)

    assert availabilities == [
        Availability(
            start_date.isoformat(),
            arrow.get("2019-01-01T17:30:00+00:00").isoformat(),
        ),
    ]


def test__single_day_availability_starts_before_work_hours():
    """If a block of availability starts before work hours, it is truncated."""
    availabilities = []
    start_date = arrow.get("2019-01-01T05:00:00+00:00")
    end_date = arrow.get("2019-01-01T12:00:00+00:00")

    add_work_hour_availability(availabilities, start_date,
                               end_date, WORKING_HOURS)

    assert availabilities == [
        Availability(
            arrow.get("2019-01-01T09:00:00+00:00").isoformat(),
            end_date.isoformat(),
        ),
    ]


def test__availability_ends_before_work_hours():
    """No availability is added if the availability ends before work hours."""
    availabilities = []
    start_date = arrow.get("2019-01-01T05:00:00+00:00")
    end_date = arrow.get("2019-01-01T07:00:00+00:00")

    add_work_hour_availability(availabilities, start_date,
                               end_date, WORKING_HOURS)

    assert availabilities == []


def test__availability_starts_after_work_hours():
    """No availability is added if the availability starts after work hours."""
    availabilities = []
    start_date = arrow.get("2019-01-01T20:00:00+00:00")
    end_date = arrow.get("2019-01-01T23:00:00+00:00")

    add_work_hour_availability(availabilities, start_date,
                               end_date, WORKING_HOURS)

    assert availabilities == []


def test__multiday_availability():
    """If availability spans multiple work days, it is split appropriately."""
    availabilities = []
    start_date = arrow.get("2019-01-01T10:00:00+00:00")
    end_date = arrow.get("2019-01-03T12:00:00+00:00")

    add_work_hour_availability(availabilities, start_date,
                               end_date, WORKING_HOURS)

    assert availabilities == [
        Availability(
            start_date.isoformat(),
            arrow.get("2019-01-01T17:30:00+00:00").isoformat(),
        ),
        Availability(
            arrow.get("2019-01-02T09:00:00+00:00").isoformat(),
            arrow.get("2019-01-02T17:30:00+00:00").isoformat(),
        ),
        Availability(
            arrow.get("2019-01-03T09:00:00+00:00").isoformat(),
            end_date.isoformat(),
        ),
    ]
