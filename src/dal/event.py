from peewee import *
from src.dal.base import BaseModel

class Event(BaseModel):
    id = CharField(32, unique=True, primary_key=True)
    camera = TextField()
    status = TextField(null=True)
    detect = BooleanField(null=True)
    created = DateTimeField(null=True)
    done = DateTimeField(null=True)
    stop_capture = DateTimeField(null=True)

class FaceEvent(BaseModel):
    event = ForeignKeyField(Event, backref="faces")
    name = TextField()
    confidence = FloatField()
    path = TextField()