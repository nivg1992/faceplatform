from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from src.services.event_service import get_all_detect_events, get_event_picture_path

router = APIRouter()

@router.get("/events", tags=["events"])
async def get_events():
    return get_all_detect_events()

@router.get("/events/{event_id}/{name}", tags=["events"])
async def get_event_face_img(event_id, name):
    try:
        path = get_event_picture_path(event_id, name)
        return FileResponse(path)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"the event {event_id} and the name {name} not found")