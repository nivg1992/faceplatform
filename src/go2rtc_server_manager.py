import logging
import subprocess
import time
import os
import signal
import yaml
import json

class Go2RTCServerManager:
    def __init__(self, config_path):
        self.server_command = ["/app/go2rtc", "-config", "./go2rtc.yaml"]
        self.config_path = config_path
        self.config_file = "./go2rtc.yaml"
        self.process = None

    def generate_config_file(self):
        config_cameras = json.load(open(self.config_path))
        config_go2rtc = {}
        config_go2rtc["streams"] = {}
        for key, value in config_cameras.items():
            config_go2rtc["streams"][value["name"]] = value["url"
                                                            ]
        with open(self.config_file, 'w') as file:
            yaml.dump(config_go2rtc, file)
        logging.info(f"Generated config file at {self.config_file}")

    def start_server(self):
        self.generate_config_file()
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
        if self.process:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)  # Send SIGTERM to the process group
            self.process.wait()  # Wait for the process to terminate
            self.process = None
            logging.info("Server stopped")
        else:
            logging.info("Server is not running")

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
