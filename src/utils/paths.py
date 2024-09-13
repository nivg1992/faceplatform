import os

data_path = os.environ.get("PF_DATA_FOLDER", "data")
extracted_faces_path = os.environ.get("PF_EXTRACTED_FACES_FOLDER", "extracted_faces")
faces_path = os.environ.get("PF_FACES_FOLDER", "faces")
events_path = os.environ.get("PF_EVENTS_FOLDER", "events")
captured_path = os.environ.get("PF_CAPTURE_OUTPUT_FOLDER", "captured_images")


extracted_faces_path_full = os.path.join(data_path, extracted_faces_path)
faces_path_full = os.path.join(data_path, faces_path)
events_path_full = os.path.join(data_path, events_path)
captured_path_full = os.path.join(data_path, captured_path)
deepface_path_full = os.path.join(data_path, ".deepface")
db_path = os.path.join(data_path, "faceplatform.db")