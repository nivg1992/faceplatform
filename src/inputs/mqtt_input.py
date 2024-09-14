import paho.mqtt.client as mqtt
import logging
import traceback
from src.inputs.input import Input

class MQTTInput(Input):
    def __init__(self,go2rtc_server):
        self.go2rtc_server = go2rtc_server
        self.client = mqtt.Client()
        self.topic_to_input = {}
        super().__init__()
    
    def configure(self, config):
        self.host = config["mqtt_host"]
        self.port = config["mqtt_port"]
        self.user = config["mqtt_user"]
        self.password = config["mqtt_password"]
        for camera in config["cameras"]:
            self.inputs[camera["name"]] = camera["topic"]
            self.topic_to_input[camera["topic"]] = camera["name"]
            self.streams.append({"name": camera["name"], "stream_protocol": camera["stream_protocol"], "stream_url": camera["stream_url"]})

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
        try:
            topic = message.topic
            if topic in self.topic_to_input:
                msg = message.payload.decode()

                if msg == "on":
                    super().start_capture_topic(self.topic_to_input[topic])
                elif msg == "off":
                    super().stop_capture_topic(self.topic_to_input[topic])
            else:
                logging.info(f"Topic {topic} not recognized")
        except Exception as e:
            logging.error(traceback.format_exc())

    def capture(self, event_id, camera):
        return self.go2rtc_server.capture_image(event_id, camera)

    def stop(self):
        self.client.loop_stop()  # Stop the MQTT client loop
        self.client.disconnect()  # Disconnect from the MQTT broker