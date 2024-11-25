from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from threading import Thread

from DataProcess import DataProcess

app = FastAPI()

# Instantiate the DataProcess class and start the update thread
data_processor = DataProcess()

# Start a separate thread to simulate measurement updates
update_thread = Thread(target=data_processor.update_measurements, daemon=True)
update_thread.start()


class Measurement(BaseModel):
    value: float
    timestamp: float


@app.get("/measurement", response_model=Measurement)
async def get_measurement():
    """Fetch the latest measurement."""
    latest_measurement = data_processor.get_latest_measurement()
    if latest_measurement is None:
        return {"value": 0.0, "timestamp": 0.0}  # Return default values if no data is available
    return latest_measurement



if __name__ == "__main__":
    print("Starting the server on http://localhost:8000")
    uvicorn.run("__main__:app", host="localhost", port=8000, reload=True, workers=2)