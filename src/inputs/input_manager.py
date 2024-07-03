
from src.utils.singleton import singleton

@singleton
class InputManager:
    def __init__(self):
        self.inputs = {}
        self.streams = []

    def configure(self, configs, go2rtc_server):
        self.configs = configs
        self.go2rtc_server = go2rtc_server
        self.is_configure = True

    def add_input(self, input_name, input):
        self.inputs[input_name] = input

    def init(self):
        if not self.is_configure:
            raise Exception("InputManager not configured")
        
        for config in self.configs:
            if config["type"] in self.inputs:
                self.inputs[config["type"]].add_input(config)

        
        for key, value in self.inputs.items():
            self.streams += value.get_streams()
        
        self.go2rtc_server.set_streams(self.streams)

    def listen(self):
        if not self.is_configure:
            raise Exception("InputManager not configured")
        
        self.go2rtc_server.start_server()

        for key, value in self.inputs.items():
            value.listen()

    def capture(self, event_id, camera):
        return self.go2rtc_server.capture_image(event_id, camera)

    def stop(self):
        for key, value in self.inputs.items():
            value.stop()

        self.go2rtc_server.stop_server()
        
