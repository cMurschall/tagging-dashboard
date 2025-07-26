import threading
import time

from app.models.liveDataRow import create_random_instance
from app.services.backgroundTasks.trackedEvent import TrackedEvent


class MockProcess:
    def __init__(self, update_measurement_callback=None, interval_seconds=5.0):
        self.update_measurement_callback = update_measurement_callback
        self.interval_seconds = interval_seconds
        self._stop_event = TrackedEvent()
        self._thread = None
        self._timestamp = 0

    def start(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    def _run_loop(self):
        while not self._stop_event.is_set():
            instance = create_random_instance()
            instance["timestamp"] = self._timestamp  # simulated timestamp
            self._timestamp += self.interval_seconds  # advance "virtual clock"

            if self.update_measurement_callback:
                self.update_measurement_callback(instance)

            time.sleep(self.interval_seconds)


# Optional convenience function
def start_process(callback=None):
    mock = MockProcess(callback, 0.1)
    mock.start()
    return mock
