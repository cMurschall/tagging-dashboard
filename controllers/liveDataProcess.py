import time
from threading import Lock

from models.measurementModel import create_random_instance


class LiveDataProcess:
    """Simulates a class that receives a new measurement every 10 microseconds."""

    def __init__(self):
        self.latest_measurement = None
        self.lock = Lock()

    def update_measurements(self):
        """Updates the latest measurement every 10 microseconds."""
        while True:
            with self.lock:
                # Simulate receiving a new measurement
                self.latest_measurement = create_random_instance()
            time.sleep(1e-5)  # 10 microseconds

    def get_latest_measurement(self):
        """Returns the latest measurement."""
        with self.lock:
            return self.latest_measurement
