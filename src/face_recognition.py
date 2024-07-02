
import queue
import threading
import logging
import os
from src.face_recognition_process import worker
import multiprocessing
from src.utils.singleton import singleton

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
        self.task_queue_send_process.put({"fileName": filename, "topic": event.topic, "eventId": event.id})

    def listen(self, num_processes):
        # Start the worker processes
        for _ in range(num_processes):
            p = multiprocessing.Process(target=worker, args=(self.task_queue_send_process, self.task_queue_receive_process, self.stop_event, self.eventIdMapProccess))
            p.start()
            self.processes.append(p)

        monitor_thread = threading.Thread(target=self.queue_monitor)
        monitor_thread.start()
    # Monitor the task queue and submit tasks to the thread pool
    def queue_monitor(self):
        logging.info('Start face recognition Service')
        while not self.stop_event.is_set():
            try:
                data = self.task_queue_receive_process.get(timeout=1)  # Wait for a task from the queue
                if data is None:
                    break
                
                if self.eventIdMap[data["eventId"]].file_status(data["filename"], data["detect"], data["faces"]):
                    self.eventIdMapProccess[data["eventId"]] = True
                    del self.eventIdMap[data["eventId"]]

                self.task_queue_receive_process.task_done()
            except queue.Empty:
                continue
        logging.info('Service face recognition stopped.')

    def stop(self):
        self.stop_event.set()
        # Add None to the queue to unblock worker processes
        for _ in self.processes:
            self.task_queue_send_process.put(None)

        # Wait for all worker processes to finish
        for p in self.processes:
            p.join()