import pytest
import sys
import os

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.be_code_challenge.app import create_app
from src.be_code_challenge.models.db import db
# from models.db import db

@pytest.fixture
def app():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

    yield app

    # Test teardown
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
