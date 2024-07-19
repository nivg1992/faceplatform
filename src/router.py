from src.utils.logger import init
init()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import faces, events
from starlette.responses import RedirectResponse

app = FastAPI()
app.include_router(faces.router)
app.include_router(events.router)

origins = [    
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("", StaticFiles(directory="client/dist", html=True), name="client")

@app.get('/')
async def client():  return RedirectResponse(url="client")

@app.get('/events')
async def client():  return RedirectResponse(url="client")