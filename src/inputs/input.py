from src.events_manager import EventsManager
from abc import ABC, abstractmethod

class Input(ABC):
    @abstractmethod
    def __init__(self):
        self.events_manager = EventsManager()
        self.inputs = {}
        self.streams = []

    @abstractmethod
    def add_input(self, config):
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

    def start_capture_topic(self, camera):
        self.events_manager.start_capture_topic(camera)
    
    def stop_capture_topic(self, camera):
        self.events_manager.stop_capture_topic(camera)