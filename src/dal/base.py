from peewee import *
from src.dal.db import db

class BaseModel(Model):
    class Meta:
        database = db


