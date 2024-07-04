import threading
import time
import logging


class Event:
    def __init__(self, id, topic, event_manager):
          self.id = id
          self.topic = topic
          self.event_manager = event_manager
          self.stop_event = threading.Event()
          self.thread = None
          self.is_capture_running = False
          self.files = {}
          self.is_event_done = False
          
    def start_capture(self, input):
         self.input = input
         self.thread = threading.Thread(target=self.capture_loop, args=())
         self.thread.start()
         self.is_capture_running = True

    def stop_capture(self):
        if(self.thread.is_alive()):
            self.stop_event.set()
            self.thread.join()
        self.is_capture_running = False
        self.clean()

    def capture_loop(self):
         while not self.stop_event.is_set():
            try:
                start_time = time.time()

                # Call Capture
                filename = self.input.capture(self.id, self.topic)
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
            return True
        
        self.clean()

        return False
    
    def file_recognize_error(self, filename):
        self.files[filename]["status"] = "error"
        self.clean()

    def clean(self):
        if self.is_capture_running:
            return
        
        for key, value in self.files.items():
            if value["status"] == "send":
                return
        
        self.event_manager.clean_event(self.id)
        self.is_event_done = True

    def recognize_faces(self, faces):
        logging.info(f"--------- Face name {','.join(faces)} on {self.topic} eventId {self.id} -------------")
        self.faces = faces
        self.stop_capture()