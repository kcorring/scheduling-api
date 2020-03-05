from http import HTTPStatus

from flask import jsonify


def _response(message, status_code):
    return jsonify({'message': message}), status_code


def bad_request(message='BAD REQUEST'):
    """Create a 400 response.

    Args:
        message(str): The error message to be provided to the end user,
            defaults to "BAD REQUEST".
    Returns:
        (HTTPResponse): A 400 HTTP response.
    """
    return _response(message, HTTPStatus.BAD_REQUEST)


def not_found(message='NOT FOUND'):
    """Create a 404 response.

    Args:
        message(str): The error message to be provided to the end user,
            defaults to "NOT FOUND".

    Returns:
        (HTTPResponse): A 404 HTTP response.
    """
    return _response(message, HTTPStatus.NOT_FOUND)


def success_json_list(data):
    """Create a 200 response containing a list of JSON data.

    Args:
        data(list): A list of JSON-serializable data for the response.

    Returns:
        (HTTPResponse): A 200 HTTP response.
    """
    return jsonify({'data': [item.to_json() for item in data]}), HTTPStatus.OK
