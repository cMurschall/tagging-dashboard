import asyncio
import logging
from dataclasses import asdict
import time
import functools
from threading import Lock, Timer

from .trackedEvent import TrackedEvent
from ..bufferedCsvWriter import BufferedCsvWriter
from ..dataSources.simulatedPantheraDataSource import start_process as start_simulated_process
from ..dataSources.replayPantheraDataSource import start_replay as start_replay_process

# only inport if panthera module is present
try:
    from ..dataSources.pantheraDataSource import start_process as start_panthera_process

    PANTHERA_AVAILABLE = True
except ImportError:
    PANTHERA_AVAILABLE = False

from ...dependencies import get_testdata_manager, get_connection_manager_data, get_connection_manager_simulation_time
from ...models.liveDataRow import LiveDataRow

logger = logging.getLogger('uvicorn.error')


def throttle_latest(seconds: float):
    # Always sends the latest call, without dropping important updates.
    def decorator(func):
        last_called = [0.0]
        latest_args = [None]
        latest_kwargs = [None]
        lock = Lock()

        def sender():
            with lock:
                if latest_args[0] is not None:
                    func(*latest_args[0], **latest_kwargs[0])
                    latest_args[0] = None
                    latest_kwargs[0] = None
                    last_called[0] = time.time()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            with lock:
                if now - last_called[0] >= seconds:
                    # Enough time passed: send immediately
                    last_called[0] = now
                    func(*args, **kwargs)
                else:
                    # Too fast: overwrite the latest
                    latest_args[0] = args
                    latest_kwargs[0] = kwargs

            # Schedule sending latest after throttle period
            delay = seconds - (now - last_called[0])
            if delay > 0:
                Timer(delay, sender).start()

        return wrapper

    return decorator


def process_live_data(stop_event: TrackedEvent, loop: asyncio.AbstractEventLoop):
    live_data_source = None
    buffered_writer = None

    try:
        while not stop_event.is_set():
            service = get_testdata_manager()
            test_drive_data = service.get_active_testdrive()

            has_live_test_drive = test_drive_data is not None and test_drive_data.is_live

            if has_live_test_drive:
                if live_data_source is None:
                    csv_file = test_drive_data.test_drive_data_info.csv_file_full_path
                    buffered_writer = BufferedCsvWriter(csv_file)

                    @throttle_latest(0.5)
                    def new_live_data_arrived(data: LiveDataRow):
                        logger.info(f"Live Data Arrived @ {data.timestamp}s")

                        asyncio.run_coroutine_threadsafe(
                            get_connection_manager_data().broadcast_json(asdict(data)),
                            loop
                        )
                        asyncio.run_coroutine_threadsafe(
                            get_connection_manager_simulation_time().broadcast_json({
                                "timestamp": data.timestamp
                            }),
                            loop
                        )

                    if PANTHERA_AVAILABLE:
                        live_data_source = start_panthera_process(new_live_data_arrived)
                    else:
                        live_data_source = start_simulated_process(new_live_data_arrived)

            elif live_data_source is not None:
                if buffered_writer:
                    buffered_writer.shutdown()
                live_data_source.stop()
                live_data_source = None
                buffered_writer = None

            sleep_with_event(stop_event, 2)

    except Exception as e:
        logger.exception("Exception in live data processing loop")

    finally:
        if live_data_source:
            live_data_source.stop()
        if buffered_writer:
            buffered_writer.shutdown()


def sleep_with_event(stop_event, duration):
    """
    Sleeps for the specified duration in small intervals,
    checking the stop_event to terminate early.
    """
    interval = 0.1  # Check every 0.1 seconds
    elapsed = 0
    while elapsed < duration:
        if stop_event.is_set():
            break
        time.sleep(interval)
        elapsed += interval
