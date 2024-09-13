import threading
import time
import logging
import datetime
from src.dal.event import Event as EventDAL, FaceEvent
from src.dal.db import db


class Event:
    def __init__(self, id, camera, event_manager):
          self.id = id
          self.camera = camera
          self.event_manager = event_manager
          self.stop_event = threading.Event()
          self.thread = None
          self.is_capture_running = False
          self.files = {}
          self.is_event_done = False
          self.detect = False
          self.status = "cerated"
          self.faces_saved = False
          
    def start_capture(self, input):
         self.input = input
         self.thread = threading.Thread(target=self.capture_loop, args=())
         self.thread.start()
         self.status = "capture"
         self.is_capture_running = True
         self.save()

    def stop_capture(self):
        if(self.thread.is_alive()):
            self.stop_event.set()
            self.thread.join()
        self.is_capture_running = False
        self.stop_capture_datetime = datetime.datetime.now()
        self.done()

    def capture_loop(self):
         while not self.stop_event.is_set():
            try:
                start_time = time.time()

                # Call Capture
                filename = self.input.capture(self.id, self.camera)
                self.files[filename] = ({"status": "send"})
                self.event_manager.face_recognition.recognition(filename, self)
                
                elapsed_time = time.time() - start_time
                sleep_time = max(0, (self.event_manager.capture_window / 1000) - elapsed_time)
                time.sleep(sleep_time)
            except Exception as e:
                logging.error(f"An error occurred: {e}")

    # return if detect
    def file_recognize(self, filename, detect, faces):
        self.files[filename]["status"] = "done"
        self.files[filename]["detect"] = detect
        self.files[filename]["faces"] = faces

        if detect:            
            self.recognize_faces(faces)
            self.save()

            return True
        else:
            self.done()
            return False
    
    def file_recognize_error(self, filename):
        self.files[filename]["status"] = "error"
        self.done()

    def save(self):
        with db.transaction() as txn:
            event, created = EventDAL.get_or_create(id=self.id, camera=self.camera)
            if(created):
                event = EventDAL.get(id=self.id)
                event.created = datetime.datetime.now()

            if(self.status == 'done'):
                event.done = self.done_timestamp

            if not self.is_capture_running:
                event.stop_capture = self.stop_capture_datetime

            event.status = self.status
            event.detect = self.detect
            event.save()
            if self.detect and not self.faces_saved:
                for face in self.faces:
                    faceEvent = FaceEvent(event=event, name=face["name"], confidence=face["confidence"], path=face["path"])
                    faceEvent.save(force_insert=True)
                
                self.faces_saved = True
        logging.info(f'Event {self.id} is stored to DB')

    def done(self):
        if self.is_capture_running:
            return
        
        for key, value in self.files.items():
            if value["status"] == "send":
                return

        logging.info(f'Event {self.id} is done')
        self.is_event_done = True
        self.status = 'done'
        self.done_timestamp = datetime.datetime.now()
        self.save()
        self.clean()

    def clean(self):
        self.event_manager.clean_event(self.id)

    def recognize_faces(self, faces):
        self.detect = True
        self.faces = faces

        for face in faces:
            face_name = face["name"]
            logging.info(f"--------- Face name {face_name} on {self.camera} eventId {self.id} -------------")
        self.faces = faces
        self.stop_capture()