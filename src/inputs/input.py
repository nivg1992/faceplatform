from src.events_manager import EventsManager
from abc import ABC, abstractmethod

class Input(ABC):
    @abstractmethod
    def __init__(self):
        self.events_manager = EventsManager()
        self.inputs = {}
        self.streams = []

    @abstractmethod
    def configure(self, config):
        pass

    @abstractmethod
    def get_streams(self):
        pass

    @abstractmethod
    def listen(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def capture(self):
        pass

    def start_capture_topic(self, camera):
        self.events_manager.start_capture_topic(camera, self)
    
    def stop_capture_topic(self, camera):
        self.events_manager.stop_capture_topic(camera)