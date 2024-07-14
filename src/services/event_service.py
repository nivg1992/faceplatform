from peewee import JOIN, DoesNotExist
import json
import os
from playhouse.shortcuts import model_to_dict
from src.dal.db import db
from src.dal.event import Event as EventDAL, FaceEvent

data_folder = os.environ.get("PF_DATA_FOLDER", "data")
output_dir_events = os.environ.get("PF_FACES_FOLDER", "events")

events_dir = os.path.join(data_folder, output_dir_events)

def get_all_detect_events():
    try:
        events = (EventDAL.select(EventDAL)
            .where(EventDAL.detect == True)
            .order_by(EventDAL.created.desc()))
            #.join_from(EventDAL, FaceEvent, JOIN.LEFT_OUTER))
            #.join(FaceEvent, on=(EventDAL.id == FaceEvent.event), join_type=JOIN.LEFT_OUTER)).get()

        return [model_to_dict(event, backrefs=True) for event in events]
    except DoesNotExist:
        return []
    
    
def get_event_picture_path(event_id):
    try:
        face_path = (EventDAL.select(FaceEvent.path)
            .join_from(EventDAL, FaceEvent, JOIN.INNER)
            .where(EventDAL.id == event_id)).get()

        return face_path.faceevent.path
    except DoesNotExist:
        raise ValueError('not found')

