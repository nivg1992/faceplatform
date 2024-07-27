from src.utils.logger import init
init()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import faces, events
from starlette.responses import RedirectResponse
from fastapi import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

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

class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except (HTTPException, StarletteHTTPException) as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex

app.mount("/", SPAStaticFiles(directory="client/dist", html=True), name="client_root")
app.mount("/events", SPAStaticFiles(directory="client/dist", html=True), name="client_root")