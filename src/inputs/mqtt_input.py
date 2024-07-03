import paho.mqtt.client as mqtt
import logging
from src.inputs.input import Input

class MQTTInput(Input):
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.client = mqtt.Client()
        self.topic_to_input = {}
        super().__init__()
    
    def add_input(self, config):
        self.inputs[config["name"]] = config["topic"]
        self.topic_to_input[config["topic"]] = config["name"]
        self.streams.append({"name": config["name"], "stream_protocol": config["stream_protocol"], "stream_url": config["stream_url"]})

    def get_streams(self):
        return self.streams
    
    def listen(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.user, self.password)
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        logging.debug("Connected with result code " + str(rc))
        for key, value in self.inputs.items():
            self.client.subscribe(value)

    def on_message(self, client, userdata, message):
        topic = message.topic
        if topic in self.topic_to_input:
            msg = message.payload.decode()

            if msg == "on":
                super().start_capture_topic(self.topic_to_input[topic])
            elif msg == "off":
                super().stop_capture_topic(self.topic_to_input[topic])
        else:
            logging.info(f"Topic {topic} not recognized")

    def stop(self):
        self.client.loop_stop()  # Stop the MQTT client loop
        self.client.disconnect()  # Disconnect from the MQTT broker