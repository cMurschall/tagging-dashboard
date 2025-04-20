import threading
import time
import csv
from pathlib import Path
from typing import Optional, Callable
from app.models.liveDataRow import LiveDataRow


class ReplayProcess:
    def __init__(self, update_measurement_callback: Callable, csv_path: str, speed: float = 1.0):
        self.csv_path = csv_path
        self.update_measurement_callback = update_measurement_callback
        self.speed = speed
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    def _run_loop(self):

        with open(self.csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            previous_timestamp = None

            for row in reader:
                if self._stop_event.is_set():
                    break
                try:
                    # Filter only fields present in LiveDataRow
                    filtered_row = {
                        k: self._convert(v)
                        for k, v in row.items()
                        if k in LiveDataRow.__dataclass_fields__
                    }

                    instance = LiveDataRow(**filtered_row)
                    current_timestamp = float(instance.timestamp)

                    if previous_timestamp is not None:
                        wait_time = (current_timestamp - previous_timestamp) / self.speed
                        if wait_time > 0:
                            time.sleep(wait_time)

                    previous_timestamp = current_timestamp

                    if self.update_measurement_callback:
                        self.update_measurement_callback(instance)

                except Exception as e:
                    print(f"[Replay] Skipping corrupt row: {row} - Reason: {e}")

    @staticmethod
    def _convert(value: str):
        value = value.strip()
        for cast in (int, float):
            try:
                return cast(value)
            except ValueError:
                continue
        return value  # fallback to string


def start_replay(callback: Callable = None, csv_path: Optional[str] = None, speed: float = 1.0) -> ReplayProcess:
    if csv_path is None:
        csv_path = Path("D:\FahrsimulatorDaten\Logger\paul_timing_cw2.csv").resolve()
    replay = ReplayProcess(callback, csv_path, speed)
    replay.start()
    return replay
