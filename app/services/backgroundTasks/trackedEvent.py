import threading
import traceback
import logging

logger = logging.getLogger('uvicorn.error')


class TrackedEvent:
    def __init__(self):
        self._event = threading.Event()
        self.set_by = None
        self.set_trace = None

    def set(self):
        self.set_by = threading.current_thread().name
        self.set_trace = ''.join(traceback.format_stack(limit=5))  # optional
        logger.info(f"Event set by {self.set_by}")
        self._event.set()

    def is_set(self):
        return self._event.is_set()

    def wait(self, timeout=None):
        return self._event.wait(timeout)

    def clear(self):
        self._event.clear()
        self.set_by = None
        self.set_trace = None

    def get_set_info(self):
        return self.set_by, self.set_trace
