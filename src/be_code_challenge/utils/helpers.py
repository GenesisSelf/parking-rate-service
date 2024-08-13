import json
from datetime import datetime
from dateutil import parser
from flask import current_app


def parse_iso_datetime(date_str):
    return parser.isoparse(date_str)


def get_day_of_week(dt):
    return dt.strftime("%a").lower()


def parse_time_range(time_range_str):
    start_str, end_str = time_range_str.split("-")
    return (
        datetime.strptime(start_str, "%H%M").time(),
        datetime.strptime(end_str, "%H%M").time(),
    )


def is_time_within_range(t, start_time, end_time):
    if start_time <= end_time:
        return start_time <= t <= end_time
    else:
        return t >= start_time or t <= end_time


def load_rates_from_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)["rates"]
    except FileNotFoundError as e:
        current_app.logger.error("Rates JSON file not found: %s", str(e))
        return []
    except json.JSONDecodeError as e:
        current_app.logger.error("Error decoding rates JSON file: %s", str(e))
        return []


def write_to_file(data, file_path):
    try:
        with open(file_path, "w") as f:
            json.dump({"rates": data}, f, indent=4)
    except IOError as e:
        current_app.logger.error("Failed to write to file: %s", str(e))
