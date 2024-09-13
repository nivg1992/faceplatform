import os
import shutil
from glob import glob
from src.utils.paths import faces_path_full

def get_all_faces():
    faces = []
    for face_dir in glob(os.path.join(faces_path_full, '*')):
        face = {}
        pic_in_face = glob(os.path.join(face_dir, '*.jpg'))
        if len(pic_in_face) > 0:
            face['path'] = pic_in_face[0].split('/')[-1]
            face['name'] = face_dir.split('/')[-1]
            faces.append(face)

    return faces

def get_face_path_by_name(name):
    face_dir = os.path.join(faces_path_full, os.path.basename(os.path.normpath(name)))
    pic_in_face = glob(os.path.join(face_dir, '*.jpg'))
    if len(pic_in_face) > 0:
        return os.path.normpath(pic_in_face[0])
    
def get_face_gallery(name):
    gallery = []
    for img_file in glob(os.path.join(faces_path_full, os.path.basename(os.path.normpath(name)), '*.jpg')):
        gallery.append(img_file.split('/')[-1])

    return gallery

def get_face_path(name, path):
    return os.path.normpath(os.path.join(faces_path_full, os.path.basename(os.path.normpath(name)) , os.path.basename(os.path.normpath(path))))

def rename_face(src_name, dest_name):
    is_merge = False
    src_name = src_name.strip().lower()
    dest_name = dest_name.strip().lower()
    if src_name.lower() == dest_name.lower() or dest_name == '':
        return is_merge
    
    src_dir = os.path.normpath(os.path.join(faces_path_full, os.path.basename(os.path.normpath(src_name))))
    dest_dir =os.path.normpath(os.path.join(faces_path_full, os.path.basename(os.path.normpath(dest_name))))

    if not os.path.isdir(src_dir):
        raise FileNotFoundError(f"The source directory '{src_dir}' does not exist.")
    
    # Create destination directory if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    else:
        is_merge = True

    # Move all files from source to destination
    for filename in os.listdir(src_dir):
        src_file = os.path.normpath(os.path.join(src_dir, filename))
        dest_file = os.path.normpath(os.path.join(dest_dir, filename))

        # Check if it's a file before moving (skip directories)
        if os.path.isfile(src_file):
            shutil.move(src_file, dest_file)
    
    shutil.rmtree(src_dir)
    return is_merge

def delete_face(face_name):
    face_dir = os.path.normpath(os.path.join(faces_path_full, os.path.basename(os.path.normpath(face_name))))
    shutil.rmtree(face_dir)

def delete_face_img(face_name, img):
    face_dir = os.path.normpath(os.path.join(faces_path_full, os.path.basename(os.path.normpath(face_name))))
    if len(os.listdir(face_dir)) == 1:
        shutil.rmtree(face_dir)
    else:
        img_path = os.path.normpath(os.path.join(faces_path_full, os.path.basename(os.path.normpath(face_name)), os.path.basename(os.path.normpath(img))))
        os.remove(img_path)