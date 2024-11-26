from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api import router as global_router
from api.v1 import router as v1_router


app = FastAPI()

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Include global endpoints
app.include_router(global_router)

# Include API routers
app.include_router(v1_router, prefix="/api/v1")



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

