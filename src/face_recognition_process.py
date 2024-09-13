
import time
import logging
import logging.config
from multiprocessing import current_process
import os
from src.utils.paths import extracted_faces_path_full, faces_path_full, events_path_full, deepface_path_full

os.environ["DEEPFACE_HOME"] = deepface_path_full
always_find = False

def extract_and_save_faces(image_path, eventId):
    from deepface import DeepFace
    from deepface.commons import image_utils
    import matplotlib.pyplot as plt
    from keras import backend
    import cv2
    import uuid
    import traceback
    import shutil

    face_result = []
    try:
        # Load the image
        img = cv2.imread(image_path)
        start = time.process_time()
        # Extract faces
        faces = DeepFace.extract_faces(img, detector_backend="dlib", expand_percentage=70,enforce_detection=False)
        logging.debug(f"extract_faces time: {time.process_time() - start}")
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Save each face to a separate file
        for i, face in enumerate(faces):
            confidence = face["confidence"]
            
            if confidence < 0.1 and always_find == False:
                logging.debug(f"Face {i} skip by confidence: {confidence}")
                continue
            
            output_path = os.path.join(extracted_faces_path_full, f"face_{i}_{uuid.uuid4().hex}.jpg")
            extractFace = face["face"]
            extractFace = extractFace * 255

            cv2.imwrite(output_path, extractFace[:, :, ::-1])

            storage_images = image_utils.list_images(path=faces_path_full)

            if len(storage_images) > 0:
                #cv2.imwrite(output_path, face["face"])
                try:
                    dfs = DeepFace.find(img_path = output_path, db_path = faces_path_full, detector_backend="skip", model_name="Facenet512")
                except ValueError as e:
                    os.remove(output_path)
                    continue
            else:
                dfs = []

            name = ""
            if len(dfs) > 0 and not dfs[0].empty and dfs[0].shape[0] > 0:
                identity = dfs[0].iloc[0]["identity"]
                name = identity.split("/")[-2]

                img_path = save_event(eventId, name, img)
                if not name.startswith('unknown-'):
                    face_result.append({"name":name, "confidence": confidence, "path": img_path})
            else:                
                name = "unknown-" + uuid.uuid4().hex
                dest_fpath = os.path.join(faces_path_full, name)
                os.makedirs(dest_fpath, exist_ok=True)
                shutil.copy(output_path, dest_fpath + "/" + uuid.uuid4().hex + ".jpg")

                save_event(eventId, name, img)
                
            logging.debug(f"--------- Face {i} name {name} confidence: {confidence} -------------")
            os.remove(output_path)

        backend.clear_session() 
        return face_result
    except Exception as e:
        logging.error(traceback.format_exc())
        backend.clear_session() 
        return face_result

def save_event(event_id, faceName, img):
    import cv2
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
    dest_fpath_images = os.path.join(events_path_full, event_id)
    os.makedirs(dest_fpath_images, exist_ok=True)
    img_path = os.path.join(dest_fpath_images, f'{event_id}_{faceName}_{timestamp}.jpg')
    cv2.imwrite(img_path, img)
    return img_path

def process_task(fileName, eventId):
    import traceback

    try:
        start = time.process_time()
        face = extract_and_save_faces(fileName, eventId)
        logging.info(f"extract_and_save_faces time: {time.process_time() - start}")
        os.remove(fileName)
        return face
    except Exception as e:
        logging.error(traceback.format_exc())
        return []

def worker(task_queue, task_queue_receive_process, stop_event, eventIdMap):
    from src.utils.logger import init
    init()
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = "2"
    import traceback
    from deepface import DeepFace

    import queue
    # Configure logging for each worker process

    logging.info(f"Start face recognition process")
    while not stop_event.is_set():
        try:
            data = task_queue.get(timeout=1)  # Wait for a task from the queue
            if data is None:
                break
            
            try:
                filename = data['fileName']
                if filename and os.path.isfile(filename):
                    logging.debug(f"process file {data}")
                    eventId = data['eventId']
                    if eventId in eventIdMap and not eventIdMap[eventId]:
                        faces = process_task(filename, eventId)  # Simulate a task taking some time to complete
                        return_message = {"eventId": eventId, "filename": filename ,"faces": faces, "detect": len(faces) > 0}
                        if eventId in eventIdMap and not eventIdMap[eventId]:
                            task_queue_receive_process.put(return_message)
                        else:
                            task_queue_receive_process.put({ "eventId": eventId, "filename": filename, "faces": [], "detect": False })

                        logging.debug(f"Task {data} completed")
                    else:
                        task_queue_receive_process.put({ "eventId": eventId, "filename": filename, "faces": [], "detect": False })
                        os.remove(filename)
                else:
                    logging.error(f'provided file doen\'t exist {filename}')
            except Exception as e:
                logging.error(traceback.format_exc())
                return_message = {"eventId": eventId, "filename": filename,"detect": False, "error": True}
                task_queue_receive_process.put(return_message)
            
            task_queue.task_done()
        except queue.Empty:
            continue
        