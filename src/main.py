
import os
from src.utils.logger import init
init()

import logging
import traceback
import signal
import threading
from src.face_recognition import FaceRecognition
from src.go2rtc_server_manager import Go2RTCServerManager
from src.events_manager import EventsManager
import uvicorn
from src.uvicorn import Server
from src.dal.db import create_tables
from src.utils.paths import captured_path_full

from src.inputs.input_manager import InputManager
import json

finished_event = threading.Event()

capture_window_ms = int(os.environ.get("PF_CAPTURE_WAITING_MS", 1000))

go2rtc_url = os.environ.get("PF_GO2RTC_URL", "internal")
go2rtc_map_file = os.environ.get("PF_GO2RTC_MAP_FILE", "./cameras.json")

num_processes = int(os.environ.get("PF_FACE_RECOGNITION_PROCCESSES_COUNT", 1))

events_manager = EventsManager()
events_manager.configure(capture_window_ms)

server_manager = Go2RTCServerManager()
server_manager.configure(captured_path_full, go2rtc_url)

input_manager = InputManager()
inputs_config_file = json.load(open(go2rtc_map_file))
input_manager.configure(inputs_config_file, server_manager)

face_recognition = FaceRecognition()

def main():
    try:
        logging.info("------------ boot ------------")
        def signal_handler(sig, frame):
            finished_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        create_tables()

        input_manager.init()
        input_manager.listen()
        face_recognition.listen(num_processes)
        config = uvicorn.Config("src.router:app", host="0.0.0.0", port=5000, log_level="info")
        server = Server(config=config)

        with server.run_in_thread():
            finished_event.wait()
            # end 
            input_manager.stop()
            events_manager.stop_all()
            face_recognition.stop()
    except Exception as e:
        logging.error(traceback.format_exc())
        input_manager.stop()
        events_manager.stop_all()
        face_recognition.stop()


if __name__ == '__main__':
    main()