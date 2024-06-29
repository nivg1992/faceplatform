import logging

logging.basicConfig(level=logging.INFO, format=f'%(asctime)s %(processName)s %(message)s')

import os
import traceback
import signal
import threading
from src import face_recognition
from src.captured_imaged import CapturedImages
from src.go2rtc_server_manager import Go2RTCServerManager



finished_event = threading.Event()

data_folder = os.environ.get("PF_DATA_FOLDER", "data")

go2rtc_url = os.environ.get("PF_GO2RTC_URL", "http://localhost:1984")
go2rtc_map_file = os.environ.get("PF_GO2RTC_MAP_FILE", "./cameras.json")
mqtt_host = os.environ.get("PF_MQTT_HOST", "")
mqtt_port = int(os.environ.get("PF_MQTT_PORT", 1883))
mqtt_user = os.environ.get("PF_MQTT_USER", "")
mqtt_password = os.environ.get("PF_MQTT_PASSWORD", "")

captured_output_folder = os.environ.get("PF_CAPTURE_OUTPUT_FOLDER", "captured_images")
num_processes = int(os.environ.get("PF_FACE_RECOGNITION_PROCCESSES_COUNT", 1))

captured_imaged = CapturedImages(os.path.join(data_folder, captured_output_folder), mqtt_host, mqtt_port, mqtt_user, mqtt_password, go2rtc_url, go2rtc_map_file)
server_manager = Go2RTCServerManager(go2rtc_map_file)
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
        face_recognition.stop()
    except Exception as e:
        server_manager.stop_server()
        logging.error(traceback.format_exc())
        captured_imaged.stop()
        face_recognition.stop()


if __name__ == '__main__':
    main()