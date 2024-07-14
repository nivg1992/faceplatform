from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import os

data_folder = os.environ.get("PF_DATA_FOLDER", "data")
db_path = os.path.join(data_folder, "faceplatform.db")

db = SqliteExtDatabase(db_path, pragmas=(
    ('cache_size', -1024 * 64),  # 64MB page-cache.
    ('journal_mode', 'wal'),  # Use WAL-mode (you should always use this!).
    ('foreign_keys', 1)))

def create_tables():
    from src.dal import event
    
    with db:
       db.create_tables([event.Event, event.FaceEvent])
