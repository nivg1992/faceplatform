from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import os
from src.utils.paths import db_path

db = SqliteExtDatabase(db_path, pragmas=(
    ('cache_size', -1024 * 64),  # 64MB page-cache.
    ('journal_mode', 'wal'),  # Use WAL-mode (you should always use this!).
    ('foreign_keys', 1)))

def create_tables():
    from src.dal import event
    
    with db:
       db.create_tables([event.Event, event.FaceEvent])
