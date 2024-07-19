import logging
import subprocess
import time
import os
import signal
import yaml
import json
import requests
from datetime import datetime
from src.utils.singleton import singleton

@singleton
class Go2RTCServerManager:
    def __init__(self):
        self.server_command = ["./app/go2rtc", "-config", "./go2rtc.yaml"]
        self.config_file = "./go2rtc.yaml"
        self.process = None
        self.url = "http://localhost:1984"
        self.go2rtc_server_enable = True

    def configure(self, output_folder, go2rtc_url):
        self.output_folder = output_folder
        if go2rtc_url != "internal":
            self.url = go2rtc_url
            self.go2rtc_server_enable = False
            
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        self.is_configure = True

    def set_streams(self, streams):
        config_go2rtc = {}
        config_go2rtc["streams"] = {}
        for stream in streams:
            config_go2rtc["streams"][stream["name"]] = stream["stream_url"]        

        with open(self.config_file, 'w') as file:
            yaml.dump(config_go2rtc, file)

        logging.info(f"Generated config file at {self.config_file}")

    def start_server(self):
        if not self.is_configure:
            raise Exception("EventsManager not configured")

        if not self.go2rtc_server_enable:
            return

        if self.process is None:
            self.process = subprocess.Popen(
                self.server_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Ensure the server process can be killed with its group
            )
            logging.info(f"Started server with PID {self.process.pid}")
        else:
            logging.info("Server is already running")

    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def stop_server(self):
        if not self.go2rtc_server_enable:
            return
        
        if self.process:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)  # Send SIGTERM to the process group
            self.process.wait()  # Wait for the process to terminate
            self.process = None
            logging.info("Server stopped")
        else:
            logging.info("Server is not running")

    def capture_image(self, eventId, source):
        try:
            # Perform the HTTP GET request
            response = requests.get(f'{self.url}/api/frame.jpeg?src={source}')
            response.raise_for_status()  # Check if the request was successful

            # Get the current timestamp and format it
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
            
            image_filename = os.path.join(self.output_folder, f'{eventId}_{timestamp}.jpg')

            # Write the image to the disk
            with open(image_filename, "wb") as file:
                file.write(response.content)

            return image_filename
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred: {e}")

    def restart_server(self):
        self.stop_server()
        time.sleep(1)  # Ensure the server has time to shut down
        self.start_server()

    def get_output(self):
        if self.process:
            stdout, stderr = self.process.communicate()
            return stdout.decode(), stderr.decode()
        else:
            return "", "Server is not running"
