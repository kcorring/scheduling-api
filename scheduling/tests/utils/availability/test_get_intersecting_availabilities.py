from utils.availability_utils import (
    get_intersecting_availabilities,
    Availability,
)


def test__fully_intersecting_availabilities():
    """If availabilities fully intersect, they are preserved."""
    availability = Availability(
        "2019-01-01T11:00:00+00:00",
        "2019-01-01T15:00:00+00:00",
    )

    user1 = [availability]
    user2 = [availability]

    result = get_intersecting_availabilities([user1, user2])

    assert result == [availability]


def test__no_overlapping_availabilities():
    """If availabilities are fully disparate, they are not returned."""
    user1 = [
        Availability(
            "2019-01-01T11:00:00+00:00",
            "2019-01-01T15:00:00+00:00",
        ),
    ]
    user2 = [
        Availability(
            "2019-01-01T18:00:00+00:00",
            "2019-01-01T22:00:00+00:00",
        ),
    ]
    result = get_intersecting_availabilities([user1, user2])

    assert result == []


def test__overlapping_availabilities():
    """If availabilities overlap, only the intersection is preserved."""
    user1 = [
        Availability(
            "2019-01-01T11:00:00+00:00",
            "2019-01-01T15:00:00+00:00",
        ),
    ]
    user2 = [
        Availability(
            "2019-01-01T13:00:00+00:00",
            "2019-01-01T22:00:00+00:00",
        ),
    ]
    result = get_intersecting_availabilities([user1, user2])

    assert result == [
        Availability(
            "2019-01-01T13:00:00+00:00",
            "2019-01-01T15:00:00+00:00",
        ),
    ]


def test__different_number_of_availabilities():
    """Ensure there are no issues if users have unbalanced availabilities."""
    user1 = [
        Availability(
            "2019-01-01T11:00:00+00:00",
            "2019-01-01T15:00:00+00:00",
        ),
    ]
    user2 = [
        Availability(
            "2019-01-01T08:00:00+00:00",
            "2019-01-01T12:00:00+00:00",
        ),
        Availability(
            "2019-01-01T13:00:00+00:00",
            "2019-01-01T22:00:00+00:00",
        ),
    ]
    result = get_intersecting_availabilities([user1, user2])

    assert result == [
        Availability(
            "2019-01-01T11:00:00+00:00",
            "2019-01-01T12:00:00+00:00",
        ),
        Availability(
            "2019-01-01T13:00:00+00:00",
            "2019-01-01T15:00:00+00:00",
        ),
    ]
