import pytest
from src.be_code_challenge.app import create_app
from src.be_code_challenge.models.db import db, Rate


@pytest.fixture
def client(request):
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            if request.param == "filled":
                # Clear existing data
                db.session.query(Rate).delete()

                # Add test data
                db.session.add(
                    Rate(
                        days="mon,tues,thurs",
                        times="0900-2100",
                        tz="America/Chicago",
                        price=1500,
                    )
                )
                db.session.add(
                    Rate(
                        days="fri,sat,sun",
                        times="0900-2100",
                        tz="America/Chicago",
                        price=2000,
                    )
                )
                db.session.add(
                    Rate(
                        days="wed", times="0600-1800", tz="America/Chicago", price=1750
                    )
                )
                db.session.add(
                    Rate(
                        days="mon,wed,sat",
                        times="0100-0500",
                        tz="America/Chicago",
                        price=1000,
                    )
                )
                db.session.add(
                    Rate(
                        days="sun,tues",
                        times="0100-0700",
                        tz="America/Chicago",
                        price=925,
                    )
                )
                db.session.commit()
            elif request.param == "empty":
                db.session.query(Rate).delete()
                db.session.commit()

        yield client
        # Drop all tables after tests
        with app.app_context():
            db.drop_all()


@pytest.mark.parametrize("client", ["filled"], indirect=True)
def test_get_rates(client):
    response = client.get("/rates/")
    assert response.status_code == 200

    expected_response = [
        {
            "days": "mon,tues,thurs",
            "times": "0900-2100",
            "tz": "America/Chicago",
            "price": 1500,
        },
        {
            "days": "fri,sat,sun",
            "times": "0900-2100",
            "tz": "America/Chicago",
            "price": 2000,
        },
        {"days": "wed", "times": "0600-1800", "tz": "America/Chicago", "price": 1750},
        {
            "days": "mon,wed,sat",
            "times": "0100-0500",
            "tz": "America/Chicago",
            "price": 1000,
        },
        {
            "days": "sun,tues",
            "times": "0100-0700",
            "tz": "America/Chicago",
            "price": 925,
        },
    ]

    actual_response = response.json

    # Sort both lists by a consistent key to compare
    def sort_key(item):
        return (item["days"], item["times"], item["tz"], item["price"])

    expected_response_sorted = sorted(expected_response, key=sort_key)
    actual_response_sorted = sorted(actual_response, key=sort_key)

    assert actual_response_sorted == expected_response_sorted


@pytest.mark.parametrize("client", ["empty"], indirect=True)
def test_get_rates_none_avail(client):
    response = client.get("/rates/")
    assert response.status_code == 200
    assert response.json == []


@pytest.mark.parametrize("client", ["filled"], indirect=True)
def test_put_rates(client):
    data = {
        "rates": [
            {
                "days": "mon,tues,wed",
                "times": "0900-1700",
                "tz": "America/Chicago",
                "price": 1500,
            }
        ]
    }
    response = client.put("/rates/", json=data)
    assert response.status_code == 200
    assert response.json["status"] == "success"


@pytest.mark.parametrize("client", ["filled"], indirect=True)
def test_get_price(client):
    data = {
        "rates": [
            {
                "days": "mon,tues,wed",
                "times": "0900-1700",
                "tz": "America/Chicago",
                "price": 1500,
            }
        ]
    }
    client.put("/rates/", json=data)

    response = client.get(
        "/price",
        query_string={
            "start": "2024-08-14T10:00:00-05:00",
            "end": "2024-08-14T11:00:00-05:00",
        },
    )
    assert response.status_code == 200
    assert response.json["price"] == 1500


@pytest.mark.parametrize("client", ["filled"], indirect=True)
def test_get_price_unavailable(client):
    data = {
        "rates": [
            {
                "days": "mon,tues,wed",
                "times": "0900-1700",
                "tz": "America/Chicago",
                "price": "1500",
            }
        ]
    }

    client.put("/rates/", json=data)

    response = client.get(
        "/price",
        query_string={
            "start": "2024-08-14T18:00:00-05:00",
            "end": "2024-08-14T19:00:00-05:00",
        },
    )

    assert response.status_code == 200
    assert response.json["price"] == "unavailable"
