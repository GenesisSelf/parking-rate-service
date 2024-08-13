from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Rate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    days = db.Column(db.String(50))
    times = db.Column(db.String(20))
    tz = db.Column(db.String(50))
    price = db.Column(db.Integer)
