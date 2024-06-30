
import queue
import threading
import logging
import os
from src.face_recognition_process import worker
import multiprocessing

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

processes = []
stop_event = multiprocessing.Event()
task_queue_send_process = multiprocessing.JoinableQueue()
task_queue_receive_process = multiprocessing.JoinableQueue()
eventIdMap = {}
filenames = {}


def recognition(filename, topic, eventId, stop_recognition_event):
    if filename in filenames:
        logging.error(f"filename already scanned")
    else:
        eventIdMap[eventId] = {"stop_event": stop_recognition_event, "topic": topic}
        filenames[filename] = topic
        task_queue_send_process.put({"fileName": filename, "topic": topic, "eventId": eventId})

def listen(num_processes):
    # Start the worker processes
    for _ in range(num_processes):
        p = multiprocessing.Process(target=worker, args=(task_queue_send_process, task_queue_receive_process, stop_event))
        p.start()
        processes.append(p)

    # Monitor the task queue and submit tasks to the thread pool
    def queue_monitor():
        logging.info('Start face recognition Service')
        while not stop_event.is_set():
            try:
                data = task_queue_receive_process.get(timeout=1)  # Wait for a task from the queue
                if data is None:
                    break
                
                eventId = data["eventId"]
                topic = eventIdMap[data["eventId"]]["topic"]
                faces = data["faces"]
                logging.info(f"--------- Face name {','.join(faces)} on {topic} eventId {eventId} -------------")
                eventIdMap[data["eventId"]]["stop_event"].set()
                task_queue_receive_process.task_done()
            except queue.Empty:
                continue
        logging.info('Service face recognition stopped.')

    # Start the queue monitor thread
    monitor_thread = threading.Thread(target=queue_monitor)
    monitor_thread.start()


def stop():
    stop_event.set()
    # Add None to the queue to unblock worker processes
    for _ in processes:
        task_queue_send_process.put(None)

    # Wait for all worker processes to finish
    for p in processes:
        p.join()