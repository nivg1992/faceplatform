
import queue
import threading
import logging
import os
import traceback
from src.face_recognition_process import worker
import multiprocessing
from src.utils.singleton import singleton
from src.utils.paths import extracted_faces_path_full, faces_path_full, events_path_full

@singleton
class FaceRecognition:
    def __init__(self):
        self.processes = []
        self.stop_event = multiprocessing.Event()
        self.task_queue_send_process = multiprocessing.JoinableQueue()
        self.task_queue_receive_process = multiprocessing.JoinableQueue()
        self.eventIdMapProccess = multiprocessing.Manager().dict()
        self.eventIdMap = {}
    
    def recognition(self, filename, event):
        self.eventIdMap[event.id] = event
        self.eventIdMapProccess[event.id] = False
        self.task_queue_send_process.put({"fileName": filename, "topic": event.camera, "eventId": event.id})

    def listen(self, num_processes):
        if not os.path.exists(extracted_faces_path_full):
            os.makedirs(extracted_faces_path_full)
        
        if not os.path.exists(faces_path_full):
            os.makedirs(faces_path_full)

        if not os.path.exists(events_path_full):
            os.makedirs(events_path_full)
            
        # Start the worker processes
        for i in range(num_processes):
            p = multiprocessing.Process(name=f"FaceProcess-{i+1}",target=worker, args=(self.task_queue_send_process, self.task_queue_receive_process, self.stop_event, self.eventIdMapProccess))
            p.start()
            self.processes.append(p)

        monitor_thread = threading.Thread(name='FaceCallback',target=self.queue_monitor)
        monitor_thread.start()
    # Monitor the task queue and submit tasks to the thread pool
    def queue_monitor(self):
        logging.info('Start face recognition Service')
        while not self.stop_event.is_set():
            try:
                data = self.task_queue_receive_process.get(timeout=1)  # Wait for a task from the queue
                if data is None:
                    break
                
                if "error" in data:
                    self.eventIdMap[data["eventId"]].file_recognize_error(data["filename"])
                else:
                    if self.eventIdMap[data["eventId"]].file_recognize(data["filename"], data["detect"], data["faces"]):
                        self.eventIdMapProccess[data["eventId"]] = True
                    
                if self.eventIdMap[data["eventId"]].is_event_done:
                    del self.eventIdMapProccess[data["eventId"]]
                    del self.eventIdMap[data["eventId"]]

                self.task_queue_receive_process.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(traceback.format_exc())

        logging.info('Service face recognition stopped.')

    def stop(self):
        self.stop_event.set()
        # Add None to the queue to unblock worker processes
        for _ in self.processes:
            self.task_queue_send_process.put(None)

        # Wait for all worker processes to finish
        for p in self.processes:
            p.join()