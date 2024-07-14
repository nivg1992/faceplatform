import uuid
import logging
from src.event import Event
from src.face_recognition import FaceRecognition
from src.utils.singleton import singleton
import traceback

@singleton
class EventsManager:
     def __init__(self):
          self.face_recognition = FaceRecognition()
          self.events = {}
          self.topics = {}
     
     def configure(self, capture_window):
          self.capture_window = capture_window
          self.is_configure = True

     def start_capture_topic(self, topic, input):
          if not self.is_configure:
               raise Exception("EventsManager not configured")
          
          if topic in self.topics and self.events[self.topics[topic]].is_capture_running:
               logging.info(f"Capture already running for topic {topic}")
          else:
               eventId = uuid.uuid4().hex
               event = Event(eventId, topic, self)
               self.topics[topic] = eventId
               self.events[eventId] = event
               logging.info(f"Starting event thread for topic {topic} eventId {eventId}")
               event.start_capture(input)
               return event
          
     def stop_capture_topic(self, topic):
          if topic not in self.topics:
               logging.info(f"Capture thread not running for topic {topic}")
          else:
               event = self.events[self.topics[topic]]
               logging.info(f"Stopping capture thread for topic {topic} eventId {event.id}")
               del self.topics[topic]
               event.stop_capture()

     def get_event_by_id(self, eventId):
          return self.events[eventId]

     def clean_event(self, eventId):
          del self.events[eventId]

     def stop_all(self):
          for key, value in self.topics.items():
               try:
                    self.events[value].stop_capture()
               except Exception as e:
                    logging.error(traceback.format_exc())
