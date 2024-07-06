
from src.utils.singleton import singleton
from src.inputs.mqtt_input import MQTTInput

@singleton
class InputManager:
    def __init__(self):
        self.inputs = []
        self.streams = []

    def configure(self, configs, go2rtc_server):
        self.configs = configs
        self.go2rtc_server = go2rtc_server
        self.is_configure = True

    def add_input(self, config):
        if config["type"] == "mqtt_trigger":
            mqtt_input = MQTTInput(self.go2rtc_server)
            mqtt_input.configure(config)
            self.inputs.append(mqtt_input)

    def init(self):
        if not self.is_configure:
            raise Exception("InputManager not configured")
        
        for config in self.configs:
           self.add_input(config)

        for input in self.inputs:
            self.streams += input.get_streams()
        
        self.go2rtc_server.set_streams(self.streams)

    def listen(self):
        if not self.is_configure:
            raise Exception("InputManager not configured")
        
        self.go2rtc_server.start_server()

        for input in self.inputs:
            input.listen()
            
    def stop(self):
        for input in self.inputs:
            input.stop()

        self.go2rtc_server.stop_server()
        
