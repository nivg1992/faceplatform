import os
import shutil
from glob import glob

data_folder = os.environ.get("PF_DATA_FOLDER", "data")
output_dir_faces = os.environ.get("PF_FACES_FOLDER", "faces")
output_dir_found_face = os.environ.get("PF_FOUND_FACE_FOLDER", "found_faces")

faces_dir = os.path.join(data_folder, output_dir_faces)
found_faces_dir = os.path.join(data_folder, output_dir_found_face)

def get_all_faces():
    faces = []
    for face_dir in glob(os.path.join(faces_dir, '*')):
        face = {}
        pic_in_face = glob(os.path.join(face_dir, '*.jpg'))
        if len(pic_in_face) > 0:
            face['path'] = pic_in_face[0].split('/')[-1]
            face['name'] = face_dir.split('/')[-1]
            faces.append(face)

    return faces

def get_face_gallery(name):
    gallery = []
    for img_file in glob(os.path.join(faces_dir, name, '*.jpg')):
        gallery.append(img_file.split('/')[-1])

    return gallery

def get_face_path(name, path):
    return os.path.join(faces_dir, name , path)

def rename_face(src_name, dest_name):
    if src_name.lower() == dest_name.lower():
        return
    
    src_dir = os.path.join(faces_dir, src_name)
    dest_dir = os.path.join(faces_dir, dest_name)

    if not os.path.isdir(src_dir):
        raise FileNotFoundError(f"The source directory '{src_dir}' does not exist.")
    
    # Create destination directory if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Move all files from source to destination
    for filename in os.listdir(src_dir):
        src_file = os.path.join(src_dir, filename)
        dest_file = os.path.join(dest_dir, filename)

        # Check if it's a file before moving (skip directories)
        if os.path.isfile(src_file):
            shutil.move(src_file, dest_file)
    
    shutil.rmtree(src_dir)

def delete_face(face_name):
    face_dir = os.path.join(faces_dir, face_name)
    shutil.rmtree(face_dir)

def delete_face_img(face_name, img):
    face_dir = os.path.join(faces_dir, face_name)
    if len(os.listdir(face_dir)) == 1:
        shutil.rmtree(face_dir)
    else:
        img_path = os.path.join(faces_dir,face_name, img)
        os.remove(img_path)