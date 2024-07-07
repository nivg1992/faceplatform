import logging
import logging.config
import os

# logging.basicConfig(
#     level=os.environ.get('PF_LOG_LEVEL', 'INFO').upper(),
#     format=f'%(asctime)s %(processName)s %(message)s'
#     )

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {  # root logger
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "DEBUG",
            "propagate": False,
            "handlers": ["default"],
        },
        "uvicorn.access": {
            "level": "DEBUG",
            "propagate": False,
            "handlers": ["default"],
        },
        "tensorflow": {
            "level": "DEBUG",
            "propagate": False,
            "handlers": ["default"],
        },
        
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

import traceback
import signal
import threading
from src.face_recognition import FaceRecognition
from src.go2rtc_server_manager import Go2RTCServerManager
from src.events_manager import EventsManager
import uvicorn
from src.uvicorn import Server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import faces
from starlette.responses import RedirectResponse

from src.inputs.input_manager import InputManager
import json

finished_event = threading.Event()

capture_window_ms = int(os.environ.get("PF_CAPTURE_WAITING_MS", 1000))
data_folder = os.environ.get("PF_DATA_FOLDER", "data")

go2rtc_url = os.environ.get("PF_GO2RTC_URL", "internal")
go2rtc_map_file = os.environ.get("PF_GO2RTC_MAP_FILE", "./cameras.json")

captured_output_folder = os.environ.get("PF_CAPTURE_OUTPUT_FOLDER", "captured_images")
num_processes = int(os.environ.get("PF_FACE_RECOGNITION_PROCCESSES_COUNT", 1))
captured_output_folder_full = os.path.join(data_folder, captured_output_folder)

events_manager = EventsManager()
events_manager.configure(capture_window_ms, captured_output_folder_full)

server_manager = Go2RTCServerManager()
server_manager.configure(captured_output_folder_full, go2rtc_url)

input_manager = InputManager()
inputs_config_file = json.load(open(go2rtc_map_file))
input_manager.configure(inputs_config_file, server_manager)

face_recognition = FaceRecognition()

app = FastAPI()
app.include_router(faces.router)

origins = [    
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("", StaticFiles(directory="client/dist", html=True), name="client")

@app.get('/')
async def client():  return RedirectResponse(url="client")

def main():
    try:
        logging.info("------------ boot ------------")
        def signal_handler(sig, frame):
            finished_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        input_manager.init()
        input_manager.listen()
        face_recognition.listen(num_processes)
        config = uvicorn.Config("src.main:app", host="0.0.0.0", port=5000, log_level="info")
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