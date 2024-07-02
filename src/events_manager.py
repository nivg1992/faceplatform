import uuid
import json
import logging
import threading
from src.event import Event
from src.go2rtc_server_manager import Go2RTCServerManager
from src.face_recognition import FaceRecognition
from src.utils.singleton import singleton

@singleton
class EventsManager:
     def __init__(self):
          self.go2rtc_server = Go2RTCServerManager()
          self.face_recognition = FaceRecognition()
          self.events = {}
          self.topics = {}
     
     def configure(self, capture_window, output_folder, go2rtc_map_file):
          self.capture_window = capture_window
          self.output_folder = output_folder
          self.go2rtc_map_file = go2rtc_map_file
          self.topic_to_go2rtc_source = json.load(open(go2rtc_map_file))
          self.is_configure = True

     def start_capture_topic(self, topic):
          if not self.is_configure:
               raise Exception("EventsManager not configured")
          
          if topic in self.topic_to_go2rtc_source:
               if topic in self.topics and self.events[self.topics[topic]].is_capture_running:
                    logging.info(f"Capture already running for topic {topic}")
               else:
                    eventId = uuid.uuid4().hex
                    source = self.topic_to_go2rtc_source[topic]["name"]
                    event = Event(eventId, source, topic, self)
                    self.topics[topic] = eventId
                    self.events[eventId] = event
                    logging.info(f"Starting event thread for topic {topic} eventId {eventId}")
                    event.start_capture()
                    return event
          else:
               logging.info(f"Topic {topic} not recognized")
          
     def stop_capture_topic(self, topic):
          if topic not in self.topics:
               logging.info(f"Capture thread not running for topic {topic}")
          else:
               event = self.events[self.topics[topic]]
               logging.info(f"Stopping capture thread for topic {topic} eventId {event.id}")
               event.stop_capture()
               del self.topics[topic]

     def clean_event(self, eventId):
          del self.events[eventId]

     def stop_all(self):
          for key, value in self.topics.items():
               self.events[value].stop_capture()