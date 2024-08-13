from flask import Blueprint, request, jsonify, current_app
from src.be_code_challenge.models.db import db, Rate
from src.be_code_challenge.utils.helpers import write_to_file
from dotenv import load_dotenv
import os

load_dotenv()

rates_bp = Blueprint("rates", __name__)
rates_file = os.getenv("RATES_FILE")


@rates_bp.route("/", methods=["GET", "PUT"])
def manage_rates():
    try:
        if request.method == "GET":
            current_app.logger.info("Rates are being fetched")
            rates = Rate.query.all()
            return jsonify(
                [
                    {
                        "days": rate.days,
                        "times": rate.times,
                        "tz": rate.tz,
                        "price": rate.price,
                    }
                    for rate in rates
                ]
            )

        if request.method == "PUT":
            current_app.logger.info("Rates are being updated in database")
            data = request.json["rates"]

            Rate.query.delete()  # Clear existing rates
            for item in data:
                rate = Rate(
                    days=item["days"],
                    times=item["times"],
                    tz=item["tz"],
                    price=item["price"],
                )
                db.session.add(rate)
            try:
                db.session.commit()
            except Exception as e:
                current_app.logger.error("There was an issue committing data to the database %s", str(e))
                return e

            current_app.logger.info("Writing to file as a backup")

            write_to_file(data, rates_file)

            return jsonify({"status": "success"}), 200
    except Exception as e:
        current_app.logger.error("Failed to add rate: %s", str(e))
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Failed to update rates",
                    "error": str(e),
                }
            ),
            500,
        )

    current_app.logger.error("Failed to send request")
    return jsonify({"status": "error", "message": "Invalid request method"}), 405
