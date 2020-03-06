# scheduling-api
API for determining user schedule availability.

## Development
### Prerequisites
- Python 3

### Environment Set Up
1. Create a virual environment:
    ```
    py -3 -m venv venv
    ```

1. Activate the virtual environment:
    ```
    . venv/bin/activate
    ```

1. Install the project dependencies in the virtual environment:
    ```
    pip install -r requirements.txt
    ```

### Running the API Locally
```
. venv/bin/activate
cd scheduling
flask run
```

The command line output will indicate where the server is running,
typically `http://127.0.0.1:5000/`

### Tests
To run the unit test suite:

```
. venv/bin/activate
cd scheduling
py -m pytest
```

## API Reference
All endpoints are prefixed with `/scheduling`

### `GET /availability/`
Retrieve the common availability between one or more users, for a given
date range.

#### Supported Parameters

#### `user_id`
Database identifier for a user. At least one is required.

#### `start_date`
ISO 8601 formatted date string. Must be less than the value of `end_date`. Required.

#### `end_date`
ISO 8601 formatted date string. Must be greater than the value of `start_date`. Required.

#### `include_non_working_hours`
If set to `true`, then availability outside of the provided users' working hours will
be considered as valid availability.

By default, the only availabilities returned will be those that fall within the users'
working hours.

#### Response Format
The response will include ta list of availabilities common to all requested users.

Each availability will include a start and end date as an ISO 8601 date string, in
UTC, e.g.:

```json
{
    "data": [
        {
            "start_date": "2019-01-01T10:00:00+0000",
            "end_date": "2019-01-01T12:00:00+0000"
        },
        {
            "start_date": "2019-01-01T14:45:00+0000",
            "end_date": "2019-01-01T16:00:00+0000"
        }
    ]
}
```