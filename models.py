from dataclasses import dataclass
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin
from app import db


@dataclass
class Result(db.Model, SerializerMixin):
    __tablename__ = 'results'
    name: str
    last_build: int
    last_result: str
    last_exception: str
    traceback: str
    url: str
    last_update: datetime

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    last_build = db.Column(db.Integer)
    last_result = db.Column(db.String())
    last_exception = db.Column(db.Text())
    traceback = db.Column(db.Text())
    url = db.Column(db.String())
    last_update = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
