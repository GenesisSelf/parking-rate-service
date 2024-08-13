import json
import pytz
import os
from flask import current_app
from datetime import datetime
from src.be_code_challenge.models.db import db, Rate
from src.be_code_challenge.utils.helpers import load_rates_from_json, is_time_within_range, parse_time_range, get_day_of_week

class ParkingRateService:
    def __init__(self):
        self.rates = []

    def load_rates(self, app_context):
        with app_context:
            # Check if database is empty
            if Rate.query.count() == 0:
                current_app.logger.info("Loading rates from JSON file")
                try:
                    rates_file_path = os.path.join(os.path.dirname(__file__), '../../../rates.json')

                    rates = load_rates_from_json(rates_file_path)
                    # Populate the database with JSON data
                    for rate_data in rates:
                        rate = Rate(
                            days=rate_data['days'],
                            times=rate_data['times'],
                            tz=rate_data['tz'],
                            price=rate_data['price']
                        )
                        db.session.add(rate)

                    try:
                        db.session.commit()
                    except Exception as e:
                        current_app.logger.error("There was an issue committing data to the database %s", str(e))
                        return e

                except FileNotFoundError as e:
                    current_app.logger.error("Loading rates from database: %s", str(e))
                except json.JSONDecodeError as e:
                    current_app.logger.error("Error decoding rates JSON file.: %s", str(e))
            else:
                current_app.logger.info("Loading rates from database")
                self.rates = [{
                    'days': rate.days,
                    'times': rate.times,
                    'tz': rate.tz,
                    'price': rate.price
                } for rate in Rate.query.all()]

    def price_for_range(self, start_dt, end_dt):
        current_app.logger.info("Calculating price for range")
        rates = Rate.query.all()
        start_day = get_day_of_week(start_dt)

        for rate in rates:
            rate_tz = pytz.timezone(rate.tz)
            rate_days = rate.days.split(',')

            # Only consider rates that apply to the current day
            if start_day not in rate_days:
                continue

            rate_start_time, rate_end_time = parse_time_range(rate.times)

            rate_start = rate_tz.localize(datetime.combine(start_dt.date(), rate_start_time))
            rate_end = rate_tz.localize(datetime.combine(start_dt.date(), rate_end_time))

            if not is_time_within_range(start_dt.time(), rate_start_time, rate_end_time):
                continue

            if is_time_within_range(start_dt.time(), rate_start_time, rate_end_time) and \
               is_time_within_range(end_dt.time(), rate_start_time, rate_end_time):

                if rate_start <= start_dt < rate_end and rate_start <= end_dt <= rate_end:
                    return rate.price

        return "unavailable"
