import asyncio
import sys

from threading import Thread, Event as ThreadingEvent
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .api import router as global_router
from .api.v1 import router as v1_router
from .dependencies import get_player, get_connection_manager, get_testdata_manager, get_settings


def start_background_tasks(background_threads, stop_event):
    from .services.backgroundTasks.projectDataUpdater import process_projects

    process_projects_thread = Thread(target=process_projects, args=(stop_event,), daemon=True)
    background_threads.append(process_projects_thread)

    # loop over all background threads and start them
    for thread in background_threads:
        thread.start()

    return background_threads, stop_event


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    stop_event = ThreadingEvent()
    background_threads = []
    start_background_tasks(background_threads, stop_event)
    print(f"Starting {len(background_threads)} background tasks.")
    yield
    stop_event.set()
    for thread in background_threads:
        thread.join()


app = FastAPI(title=get_settings().APP_NAME, debug=get_settings().DEBUG, lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)


def custom_openapi(version: str):
    def generate_openapi():
        openapi_schema = get_openapi(
            title=f"Tagging Dashboard {version}",
            version=version,
            description=f"This is version {version} of the backend API.",
            routes=app.routes,  # Use the app's current routes
        )
        return openapi_schema

    return generate_openapi


# Add version-specific OpenAPI schemas
app.openapi = custom_openapi("1.0.0")

# Include global endpoints
app.include_router(global_router, prefix="/api")

# Include API routers
app.include_router(v1_router, prefix="/api/v1")

for route in app.routes:
    if isinstance(route, APIRoute):
        pass
        # route.operation_id = route.name  # in this case, 'read_items'

# Serve static files
# Note: We must mount the static files at last, because otherwise it overrides all / routes
if "pytest" not in sys.modules:
    app.mount("/", StaticFiles(directory="app/static", html=True), name="static")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await get_connection_manager().connect(websocket)
    try:
        while True:
            await websocket.send_text("ping")  # keep alive
            await asyncio.sleep(20)  # should be okay so clients may not time out and close the connection
    except WebSocketDisconnect:
        get_connection_manager().disconnect(websocket)

    if __name__ == "__main__":
        print("Starting server manually")
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8888, log_level="info")
