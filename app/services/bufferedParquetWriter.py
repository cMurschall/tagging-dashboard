import time
from dataclasses import asdict
from queue import Queue, Empty
from threading import Thread, Event
from pathlib import Path
import pandas as pd


class BufferedParquetWriter:
    def __init__(self, parquet_file_path: str, stop_event: Event, flush_interval: float = 10.0, batch_size: int = 100):
        self.parquet_file_path = Path(parquet_file_path)
        self.flush_interval = flush_interval
        self.batch_size = batch_size
        self.queue = Queue()
        self.stop_event = stop_event
        self.thread = Thread(target=self._writer_loop, daemon=True)
        self._has_written_schema = self.parquet_file_path.exists()
        self.thread.start()

    def _writer_loop(self):
        buffer = []
        last_flush = time.time()

        while not self.stop_event.is_set():
            try:
                data = self.queue.get(timeout=1)
                buffer.append(data)
            except Empty:
                pass

            should_flush = (
                    len(buffer) >= self.batch_size or
                    (buffer and time.time() - last_flush >= self.flush_interval)
            )

            if should_flush:
                df = pd.DataFrame(buffer)

                if self.parquet_file_path.exists():
                    # Append to file -> does now work....
                    df.to_parquet(self.parquet_file_path, engine='pyarrow', index=False, compression='snappy',
                                  append=True)
                else:
                    # Write new file
                    df.to_parquet(self.parquet_file_path, engine='pyarrow', index=False, compression='snappy')

                buffer.clear()
                last_flush = time.time()

    def enqueue(self, data: dict):
        self.queue.put(data)

    def shutdown(self):
        self.stop_event.set()
        self.thread.join(timeout=5)
