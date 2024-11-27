from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocket

from api import router as global_router
from api.v1 import router as v1_router
from api.v1.playerController import PlayerController
from api.websocket.webSocketConnectionHandler import WebSocketConnectionHandler

app = FastAPI()

# Include global endpoints
app.include_router(global_router, prefix="/api")

# Include API routers
app.include_router(v1_router, prefix="/api/v1")

# Serve static files
# Note: We must mount the static files at last, because otherwise it overrides all / routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")




# Initialize controllers
player_controller = PlayerController()

def get_websocket_handler():
    """Dependency to get the current WebSocket handler."""
    if not player_controller.playback:
        return None
    return WebSocketConnectionHandler(player_controller.playback)



# WebSocket endpoint
@app.websocket("/ws/replay")
async def websocket_endpoint(websocket: WebSocket, handler: WebSocketConnectionHandler = Depends(get_websocket_handler)):
    if not handler:
        await websocket.close(reason="No CSV file loaded for playback")
        return
    await handler.handle(websocket)
#
# from threading import Thread
#
# from DataProcess import DataProcess
#
# app = FastAPI()
#
# # Instantiate the DataProcess class and start the update thread
# data_processor = DataProcess()
#
# # Start a separate thread to simulate measurement updates
# update_thread = Thread(target=data_processor.update_measurements, daemon=True)
# update_thread.start()
#
#
# class Measurement(BaseModel):
#     value: float
#     timestamp: float
#
#
# @app.get("/measurement", response_model=Measurement)
# async def get_measurement():
#     """Fetch the latest measurement."""
#     latest_measurement = data_processor.get_latest_measurement()
#     if latest_measurement is None:
#         return {"value": 0.0, "timestamp": 0.0}  # Return default values if no data is available
#     return latest_measurement
#
