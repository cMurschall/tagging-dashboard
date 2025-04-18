import csv
import time
from dataclasses import asdict
from queue import Queue, Empty
from threading import Thread, Event


class BufferedCsvWriter:
    def __init__(self, csv_file_path: str, stop_event: Event, flush_interval: float = 10.0, batch_size: int = 100):
        self.csv_file_path = csv_file_path
        self.flush_interval = flush_interval
        self.batch_size = batch_size
        self.queue = Queue()
        self.stop_event = stop_event
        self.thread = Thread(target=self._writer_loop, daemon=True)
        self.thread.start()

    def _writer_loop(self):
        buffer = []
        last_flush = time.time()

        while not self.stop_event.is_set():
            try:
                data = self.queue.get(timeout=1)  # Wait max 1 second for new data
                buffer.append(data)
            except Empty:
                pass

            should_flush = (
                    len(buffer) >= self.batch_size or
                    (buffer and time.time() - last_flush >= self.flush_interval)
            )

            if should_flush:
                with open(self.csv_file_path, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=buffer[0].keys())
                    for row in buffer:
                        writer.writerow(row)
                buffer.clear()
                last_flush = time.time()

    def enqueue(self, data: dict):
        self.queue.put(data)

    def shutdown(self):
        self.stop_event.set()
        self.thread.join(timeout=5)
