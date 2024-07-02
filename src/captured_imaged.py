

import paho.mqtt.client as mqtt
import logging
from src.events_manager import EventsManager

class CapturedImages:
    def __init__(self):
        self.client = mqtt.Client()
        self.events_manager = EventsManager()

    def configure(self, mqtt_broker, mqtt_port, mqtt_user, mqtt_password):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.is_configure = True

    def listen(self):
        if not self.is_configure:
            raise Exception("EventsManager not configured")

        # Folder to save captured images
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.mqtt_user, self.mqtt_password)
        self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
        self.client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc):
        logging.debug("Connected with result code " + str(rc))
        self.client.subscribe("nygai/#")

    def on_message(self, client, userdata, message):
        topic = message.topic
        msg = message.payload.decode()

        if msg == "on":
            self.events_manager.start_capture_topic(topic)
        elif msg == "off":
            self.events_manager.stop_capture_topic(topic)

    def stop(self):
        self.client.loop_stop()  # Stop the MQTT client loop
        self.client.disconnect()  # Disconnect from the MQTT broker