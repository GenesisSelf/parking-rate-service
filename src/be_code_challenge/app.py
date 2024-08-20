from logging.handlers import RotatingFileHandler
from flask import Flask
from src.be_code_challenge.routes.rates import rates_bp
from src.be_code_challenge.routes.price import price_bp
from src.be_code_challenge.models.db import db
from src.be_code_challenge.services.service_instance import parking_rate_service
import os
import sys
import logging
from dotenv import load_dotenv


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Register blueprints
app.register_blueprint(rates_bp, url_prefix="/rates")
app.register_blueprint(price_bp, url_prefix="/price")

def create_app():
    with app.app_context():
        # Create the database tables if they don't exist
        db.create_all()

        # load rates within the app context
        parking_rate_service.load_rates(app.app_context())

        if not app.debug:
            log_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../error.log'))
            handler = RotatingFileHandler(log_file_path, maxBytes=10240, backupCount=10)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            app.logger.addHandler(handler)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5000, debug=False)