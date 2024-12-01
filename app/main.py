import asyncio
import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from .api import router as global_router
from .api.v1 import router as v1_router
from .dependencies import get_player, get_connection_manager, get_testdata_manager

app = FastAPI()


def custom_openapi(version: str):
    def generate_openapi():
        openapi_schema = get_openapi(
            title=f"Tagging dashboard {version}",
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

# if __name__ == "__main__":
#     print("Starting server manually")
#    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
