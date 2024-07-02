

import json
import os
import time
import threading
import paho.mqtt.client as mqtt
import uuid
from src.face_recognition import recognition
import logging
import requests
from datetime import datetime

capture_window_ms = int(os.environ.get("PF_CAPTURE_WAITING_MS", 500))

class CapturedImages:
    def __init__(self, output_folder, mqtt_broker, mqtt_port, mqtt_user, mqtt_password, go2rtc_url, go2rtc_map_file):
        self.output_folder = output_folder
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.go2rtc_url = go2rtc_url
        self.go2rtc_map_file = go2rtc_map_file
        self.topic_to_go2rtc_source = json.load(open(go2rtc_map_file))
        self.capture_threads = {}
        self.client = mqtt.Client()

    def listen(self):
        # Folder to save captured images
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

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

        if topic in self.topic_to_go2rtc_source:      
            source = self.topic_to_go2rtc_source[topic]["name"]
            if msg == "on":
                if topic not in self.capture_threads or not self.capture_threads[topic]["thread"].is_alive():
                    eventId = uuid.uuid4().hex
                    logging.info(f"Starting capture thread for topic {topic} eventId {eventId}")
                    stop_event = threading.Event()
                    capture_thread = threading.Thread(target=self.capture_images, args=(source, stop_event, topic, eventId))
                    self.capture_threads[topic] = {"thread": capture_thread, "event": stop_event, "eventId": eventId}
                    capture_thread.start()
                else:
                    logging.info(f"Capture thread already running for topic {topic}")
            elif msg == "off":
                if topic in self.capture_threads:
                    eventId = self.capture_threads[topic]["eventId"]
                    logging.info(f"Stopping capture thread for topic {topic} eventId {eventId}")
                    if self.capture_threads[topic]["thread"].is_alive():
                        stop_event = self.capture_threads[topic]["event"]
                        stop_event.set()
                        self.capture_threads[topic]["thread"].join()
                    del self.capture_threads[topic]
                else:
                    logging.info(f"Capture thread not running for topic {topic}")
        else:
            logging.info(f"Topic {topic} not recognized")

    def stop(self):
        for topic, data in self.capture_threads.items():
            stop_event = data["event"]
            stop_event.set()
            data["thread"].join()
        
        self.client.loop_stop()  # Stop the MQTT client loop
        self.client.disconnect()  # Disconnect from the MQTT broker

    def capture_images(self, source, stop_event, topic, eventId):
        while not stop_event.is_set():
            # Take Snapshot
            try:
                start_time = time.time()
                # Perform the HTTP GET request
                response = requests.get(f'{self.go2rtc_url}/api/frame.jpeg?src={source}')
                response.raise_for_status()  # Check if the request was successful

                # Get the current timestamp and format it
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
                
                image_filename = os.path.join(self.output_folder, f'{eventId}_{timestamp}.jpg')

                # Write the image to the disk
                with open(image_filename, "wb") as file:
                    file.write(response.content)

                recognition(image_filename, topic, eventId, stop_event)
                logging.debug(f"Image successfully downloaded and saved as {image_filename}")

                elapsed_time = time.time() - start_time
                sleep_time = max(0, (capture_window_ms / 1000) - elapsed_time)
                time.sleep(sleep_time)
            except requests.exceptions.RequestException as e:
                logging.error(f"An error occurred: {e}")