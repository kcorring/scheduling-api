from flask import request
import arrow

from data.database import Database
from data.exceptions import UserNotFoundException
from utils.availability_utils import (
    get_user_availability,
    get_user_work_hour_availability,
    get_intersecting_availabilities,
)
from utils.responses import bad_request, not_found, success_json_list

INVALID_DATE_FORMAT = 'Invalid {}: ISO 8601 format required'

db = Database.from_file()


def get_availability():
    user_ids = [int(id) for id in request.args.getlist('user_id')]

    if not user_ids:
        return bad_request('At least one user_id is required')

    start_date_param = request.args.get('start_date', '')
    try:
        start_date = arrow.get(start_date_param).to('utc').isoformat()
    except ValueError:
        return bad_request(INVALID_DATE_FORMAT.format('start_date'))

    end_date_param = request.args.get('end_date', '')
    try:
        end_date = arrow.get(end_date_param).to('utc').isoformat()
    except ValueError:
        return bad_request(INVALID_DATE_FORMAT.format('end_date'))

    if start_date >= end_date:
        return bad_request("Start date must be less than end date")

    should_include_non_working_hours = (
        request.args.get('include_non_working_hours') == 'true'
    )

    if should_include_non_working_hours:
        def get_availability(user_id, user_events):
            return get_user_availability(
                user_events,
                start_date,
                end_date,
            )
    else:
        def get_availability(user_id, user_events):
            user = db.get_user(user_id)
            return get_user_work_hour_availability(
                user_events,
                start_date,
                end_date,
                working_hours=user.working_hours,
                time_zone=user.time_zone
            )

    user_availabilities = []
    for user_id in user_ids:
        try:
            user_events = db.get_user_events(user_id, start_date, end_date)
        except UserNotFoundException:
            return not_found(f'User id {user_id} does not exist')

        user_availability = get_availability(user_id, user_events)

        # If any user has zero availability in the given timeframe, bail early
        if not len(user_availability):
            return success_json_list([])

        user_availabilities.append(user_availability)

    if len(user_availabilities) == 1:
        return success_json_list(user_availabilities[0])

    availabilities = get_intersecting_availabilities(user_availabilities)

    return success_json_list(availabilities)
