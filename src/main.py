import logging
import os

logging.basicConfig(
    level=os.environ.get('PF_LOG_LEVEL', 'INFO').upper(),
    format=f'%(asctime)s %(processName)s %(message)s'
    )

import traceback
import signal
import threading
from src.face_recognition import FaceRecognition
from src.captured_imaged import CapturedImages
from src.go2rtc_server_manager import Go2RTCServerManager
from src.events_manager import EventsManager

finished_event = threading.Event()

capture_window_ms = int(os.environ.get("PF_CAPTURE_WAITING_MS", 1000))
data_folder = os.environ.get("PF_DATA_FOLDER", "data")

go2rtc_url = os.environ.get("PF_GO2RTC_URL", "http://localhost:1984")
go2rtc_map_file = os.environ.get("PF_GO2RTC_MAP_FILE", "./cameras.json")
mqtt_host = os.environ.get("PF_MQTT_HOST", "")
mqtt_port = int(os.environ.get("PF_MQTT_PORT", 1883))
mqtt_user = os.environ.get("PF_MQTT_USER", "")
mqtt_password = os.environ.get("PF_MQTT_PASSWORD", "")

captured_output_folder = os.environ.get("PF_CAPTURE_OUTPUT_FOLDER", "captured_images")
num_processes = int(os.environ.get("PF_FACE_RECOGNITION_PROCCESSES_COUNT", 1))
captured_output_folder_full = os.path.join(data_folder, captured_output_folder)


captured_imaged = CapturedImages()
captured_imaged.configure(mqtt_host, mqtt_port, mqtt_user, mqtt_password)

server_manager = Go2RTCServerManager()
server_manager.configure(go2rtc_map_file, captured_output_folder_full, go2rtc_url)

events_manager = EventsManager()
events_manager.configure(capture_window_ms, captured_output_folder_full, go2rtc_map_file)

face_recognition = FaceRecognition()

def main():
    try:
        logging.info("------------ boot ------------")
        def signal_handler(sig, frame):
            finished_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        server_manager.start_server()

        face_recognition.listen(num_processes)
        captured_imaged.listen()

        finished_event.wait()
        # end 
        server_manager.stop_server()
        captured_imaged.stop()
        events_manager.stop_all()
        face_recognition.stop()
    except Exception as e:
        server_manager.stop_server()
        logging.error(traceback.format_exc())
        captured_imaged.stop()
        events_manager.stop_all()
        face_recognition.stop()


if __name__ == '__main__':
    main()