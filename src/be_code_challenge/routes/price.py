from flask import Blueprint, request, jsonify, current_app
from src.be_code_challenge.services.service_instance import parking_rate_service
from src.be_code_challenge.utils.helpers import parse_iso_datetime
import pytz
import os
from dotenv import load_dotenv

load_dotenv()
price_bp = Blueprint("price", __name__)
local_timezone = os.getenv("LOCAL_TIMEZONE")
local_tz = pytz.timezone(local_timezone)


@price_bp.route("", methods=["GET"])
def get_price():
    start = request.args.get("start")
    end = request.args.get("end")
    # Used because url encoding wants '+' to be '%2B'
    start = start.replace(" ", "+")
    end = end.replace(" ", "+")

    if not start or not end:
        current_app.logger.warning("Missing start or end rate time parameters.")
        return jsonify({"error": "start and end parameters are required"}), 400

    try:
        # Parse ISO 8601 date strings into datetime objects
        start_dt = parse_iso_datetime(start)
        end_dt = parse_iso_datetime(end)

        # Convert to local timezone
        start_dt_local = start_dt.astimezone(local_tz)
        end_dt_local = end_dt.astimezone(local_tz)

        # Ensure end datetime is after start datetime
        if end_dt_local <= start_dt_local:
            current_app.logger.warning("End dt is before start dt")
            return jsonify({"error": "end must be after start"}), 400
        # Check if the dates span more than one day; could be improved for when there are rates that span overnight or multi-days
        if start_dt_local.date() != end_dt_local.date():
            current_app.logger.warning(
                "No support for rates that span over one date at the moment"
            )
            return jsonify({"price": "unavailable"}), 200

        # Call the parking_rate_service to get the price
        price = parking_rate_service.price_for_range(start_dt_local, end_dt_local)
        current_app.logger.info("Successfully fetched pricing information")

        return jsonify({"price": price})
    except ValueError as e:
        current_app.logger.error("Formatting error has occurred: %s", str(e))
        return (
            jsonify(
                {"status": "error", "message": "Invalid date format", "error": str(e)}
            ),
            400,
        )
    except Exception as e:
        current_app.logger.error("Unexpected error has occurred: %s", str(e))
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "An unexpected error occurred",
                    "error": str(e),
                }
            ),
            500,
        )
