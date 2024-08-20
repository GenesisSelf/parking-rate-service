# Spothero Parking Rate API
An API used to calculate parking rates based off time and date inputs!

## Setup
Create and active virtualenv. Project was built using python 3.9.

`python3 -m venv venv source venv/bin/activate`

Install dependencies:
`poetry install`

Build project:
`poetry build`

Database setup
If a previous database has not been created, the application will set it up for you automatically based off the data in the rates.json file.

TODO: set up database migrations

## Running app
Please ensure debug on app.py is set to `True` and run 
```
export PYTHONPATH=src

export FLASK_APP=src.be_code_challenge.app:create_app

poetry run flask run
```

Examples of api calls:

Getting a price: `curl -X GET "http://127.0.0.1:5000/price?start=2015-07-04T15:00:00+00:00&end=2015-07-04T20:00:00+00:00"`

Expected output: ```
{
  "price": 2000
}```

Getting a list of rates:

`curl -X GET "http://127.0.0.1:5000/rates/"`

Updating the list of rates: (Please note that at the moment the entire list gets updated.
)
```curl -X PUT -H "Content-Type: application/json" -d '{
    "rates": [
        {
            "days": "mon,tues,thurs",
            "times": "0900-2100",
            "tz": "America/Chicago",
            "price": 1500
        },
        {
            "days": "fri,sat,sun",
            "times": "0900-2100",
            "tz": "America/Chicago",
            "price": 2000
        },
        {
            "days": "wed",
            "times": "0600-1800",
            "tz": "America/Chicago",
            "price": 1750
        },
        {
            "days": "mon,wed,sat",
            "times": "0100-0500",
            "tz": "America/Chicago",
            "price": 1000
        },
        {
            "days": "sun,tues",
            "times": "0100-0700",
            "tz": "America/Chicago",
            "price": 925
        }
    ]
}' http://127.0.0.1:5000/rates/
```


## Running tests
`poetry run pytest --cov --cov-report=html -vv`
