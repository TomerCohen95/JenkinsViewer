from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    last_build = db.Column(db.Integer)
    last_result = db.Column(db.Integer)
    last_console = db.Column(db.String())
    url = db.Column(db.String())

    def __init__(self, name, last_build, last_result, last_console, url):
        self.name = name
        self.last_build = last_build
        self.last_result = last_result
        self.last_console = last_console
        self.url = url

    def __repr__(self):
        return '<id {}>'.format(self.id)
