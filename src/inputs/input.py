from src.events_manager import EventsManager
from abc import ABC, abstractmethod

class Input(ABC):
    """
    Abstract class for defining various input sources for the application.
    
    This class provides common properties:
    - events_manager: Manages events for the input source.
    - inputs: A dictionary to store input-related data.
    - streams: A list to manage active streams.
    
    Subclass this `Input` class to create custom input sources and implement all abstract methods.
    """
    @abstractmethod
    def __init__(self):
        """
        Initialize the input source and any required components.
        
        Example:
        ```python
        def __init__(self):
            super().__init__()
            # Initialize custom components here
        ```
        """
        self.events_manager = EventsManager()
        self.inputs = {}
        self.streams = []

    @abstractmethod
    def configure(self, config):
        """
        Configure the input source with the given configuration.
        
        Parameters:
        - config (dict): A dictionary containing configuration parameters.
        
        Example:
        ```python
        def configure(self, config):
            self.host = config["mqtt_host"]
            self.port = config["mqtt_port"]
            self.user = config["mqtt_user"]
        ```
        """
        pass

    @abstractmethod
    def get_streams(self):
        """
        Retrieve the current input streams.
        
        Returns:
        - list: A list of active input streams.
        
        Example:
        ```python
        def get_streams(self):
            return self.streams
        ```
        """
        pass

    @abstractmethod
    def listen(self):
        """
        Start listening to the input source for events.
        
        Example:
        ```python
        def listen(self):
            # Code to start listening to the input source
        ```
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stop listening to the input source.
        
        Example:
        ```python
        def stop(self):
            # Code to stop listening to the input source
        ```
        """
        pass

    @abstractmethod
    def capture(self):
        """
        Capture data from the input source.
        
        Returns:
        - data: The captured data.
        
        Example:
        ```python
        def capture(self, event_id, camera):
            return self.go2rtc_server.capture_image(event_id, camera)
        ```
        """
        pass
    
    def start_capture_topic(self, camera):
        """
        Start capturing data from the specified camera using the events manager.
        
        Parameters:
        - camera: The camera name from which to start capturing data.
        
        Example:
        ```python
        # Assuming `input_instance` is an instance of a subclass of `Input`
        input_instance.start_capture_topic(camera_instance)
        ```
        """
        self.events_manager.start_capture_topic(camera, self)
    
    def stop_capture_topic(self, camera):
        """
        Stop capturing data from the specified camera using the events manager.
        
        Parameters:
        - camera: The camera name from which to stop capturing data.
        
        Example:
        ```python
        # Assuming `input_instance` is an instance of a subclass of `Input`
        input_instance.stop_capture_topic(camera_instance)
        ```
        """
        self.events_manager.stop_capture_topic(camera)