from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from src.services.face_service import get_all_faces, get_face_path, rename_face, delete_face, get_face_gallery, delete_face_img, get_face_path_by_name
from pydantic import BaseModel

class RenameFace(BaseModel):
    source_face: str
    dest_face: str

router = APIRouter()

@router.get("/faces", tags=["faces"])
async def read_faces_controller():
    return get_all_faces()

@router.get("/faces/{face_name}/gallery", tags=["faces"])
async def get_face_gallery_controller(face_name):
    return get_face_gallery(face_name)

@router.get("/faces/{face_name}/img", tags=["faces"])
async def get_face_img_controller(face_name):
    face_path = Path(get_face_path_by_name(face_name))
    if not face_path.is_file():
        raise HTTPException(status_code=404, detail="face/path not found on the server")
    return FileResponse(face_path)

@router.get("/faces/{face_name}/{path}", tags=["faces"])
async def get_face_controller(face_name, path):
    face_path = Path(get_face_path(face_name, path))
    if not face_path.is_file():
        raise HTTPException(status_code=404, detail="face/path not found on the server")
    
    return FileResponse(face_path)

@router.post("/faces/rename", tags=["faces"])
async def rename_faces_controller(rename_face_data: RenameFace):
    rename_face(rename_face_data.source_face, rename_face_data.dest_face)

@router.delete("/faces/{face_name}", tags=["faces"])
async def delete_face_controller(face_name):
    delete_face(face_name)

@router.delete("/faces/{face_name}/{img}", tags=["faces"])
async def delete_face_img_controller(face_name, img):
    delete_face_img(face_name, img)