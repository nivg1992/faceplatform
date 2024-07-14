from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from src.services.event_service import get_all_detect_events, get_event_picture_path
import os

router = APIRouter()

@router.get("/events", tags=["events"])
async def get_events():
    return get_all_detect_events()

@router.get("/events/{event_id}/img", tags=["events"])
async def get_event_face_img(event_id):
    try:
        path = get_event_picture_path(event_id)
        return FileResponse(path)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"the event {event_id} not found")