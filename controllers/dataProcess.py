import random
import time
from threading import Lock


class DataProcess:
    """Simulates a class that receives a new measurement every 10 microseconds."""
    def __init__(self):
        self.latest_measurement = None
        self.lock = Lock()

    def update_measurements(self):
        """Updates the latest measurement every 10 microseconds."""
        while True:
            with self.lock:
                # Simulate receiving a new measurement

                self.latest_measurement = {
                    "value": random.uniform(0, 100),  # Random value for simulation
                    "timestamp": time.time()
                }
            time.sleep(1e-5)  # 10 microseconds

    def get_latest_measurement(self):
        """Returns the latest measurement."""
        with self.lock:
            return self.latest_measurement
