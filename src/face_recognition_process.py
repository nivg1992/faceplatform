
import time
import logging
import logging.config
from multiprocessing import current_process
import os

data_folder = os.environ.get("PF_DATA_FOLDER", "data")
output_dir = os.environ.get("PF_EXTRACTED_FACES_FOLDER", "extracted_faces")
output_dir_faces = os.environ.get("PF_FACES_FOLDER", "faces")
output_dir_found_face = os.environ.get("PF_FOUND_FACE_FOLDER", "found_faces")

extracted_faces_dir = os.path.join(data_folder, output_dir)
faces_dir = os.path.join(data_folder, output_dir_faces)
found_faces_dir = os.path.join(data_folder, output_dir_found_face)

os.environ["DEEPFACE_HOME"] = os.path.join(data_folder, ".deepface")


def extract_and_save_faces(image_path):
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
            
            if confidence < 0.1:
                logging.debug(f"Face {i} skip by confidence: {confidence}")
                continue
            
            output_path = os.path.join(extracted_faces_dir, f"face_{i}_{uuid.uuid4().hex}.jpg")
            extractFace = face["face"]
            extractFace = extractFace * 255

            cv2.imwrite(output_path, extractFace[:, :, ::-1])

            storage_images = image_utils.list_images(path=faces_dir)

            if len(storage_images) > 0:
                #cv2.imwrite(output_path, face["face"])
                try:
                    dfs = DeepFace.find(img_path = output_path, db_path = faces_dir, detector_backend="skip", model_name="Dlib")
                except ValueError as e:
                    os.remove(output_path)
                    continue
            else:
                dfs = []

            name = ""
            if len(dfs) > 0:
                df = dfs[0]
                if not df.empty and df.shape[0] > 0:
                    identity = df.iloc[0]["identity"]
                    name = identity.split("/")[-2]
                    # distance = float(df['distance'])
                    # threshold = float(df['threshold'])
                    dest_fpath_images = os.path.join(found_faces_dir, name)
                    os.makedirs(dest_fpath_images, exist_ok=True)
                    cv2.imwrite(dest_fpath_images + "/" + os.path.basename(image_path), img)
                    shutil.copy(output_path, dest_fpath_images + f"/face-{i}-" + os.path.basename(image_path))
                    face_result.append(name)
                else:
                    name = "unknown-" + uuid.uuid4().hex
                    dest_fpath = os.path.join(faces_dir, name)
                    os.makedirs(dest_fpath, exist_ok=True)
                    shutil.copy(output_path, dest_fpath + "/" + uuid.uuid4().hex + ".jpg")

                    dest_fpath_images = os.path.join(found_faces_dir, name)
                    os.makedirs(dest_fpath_images, exist_ok=True)
                    cv2.imwrite(dest_fpath_images + "/" + os.path.basename(image_path), img)
                    shutil.copy(output_path, dest_fpath_images + f"/face-{i}" + os.path.basename(image_path))
            else:                
                name = "unknown-" + uuid.uuid4().hex
                dest_fpath = os.path.join(faces_dir, name)
                os.makedirs(dest_fpath, exist_ok=True)
                shutil.copy(output_path, dest_fpath + "/" + uuid.uuid4().hex + ".jpg")

                dest_fpath_images = os.path.join(found_faces_dir, name)
                os.makedirs(dest_fpath_images, exist_ok=True)
                cv2.imwrite(dest_fpath_images + "/" + os.path.basename(image_path), img)
                
            logging.debug(f"--------- Face {i} name {name} confidence: {confidence} -------------")
            os.remove(output_path)

        backend.clear_session() 
        return face_result
    except Exception as e:
        logging.error(traceback.format_exc())
        backend.clear_session() 
        return face_result

def process_task(fileName):
    import traceback

    try:
        start = time.process_time()
        face = extract_and_save_faces(fileName)
        logging.info(f"extract_and_save_faces time: {time.process_time() - start}")
        os.remove(fileName)
        return face
    except Exception as e:
        logging.error(traceback.format_exc())
        return []

def worker(task_queue, task_queue_receive_process, stop_event, eventIdMap):
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
            "tensorflow": {
                "level": "DEBUG",
                "handlers": ["default"],
            },
            
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
    # os.environ['TF_CPP_MIN_LOG_LEVEL'] = "2"
    import traceback
    from deepface import DeepFace

    import queue
    # Configure logging for each worker process

    if not os.path.exists(extracted_faces_dir):
        os.makedirs(extracted_faces_dir)
    
    if not os.path.exists(faces_dir):
        os.makedirs(faces_dir)

    if not os.path.exists(found_faces_dir):
        os.makedirs(found_faces_dir)

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
                        faces = process_task(filename)  # Simulate a task taking some time to complete
                        return_message = {"eventId": eventId, "filename": filename ,"faces": faces, "detect": len(faces) > 0}
                        task_queue_receive_process.put(return_message)
                        logging.debug(f"Task {data} completed")
                    else:
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
        