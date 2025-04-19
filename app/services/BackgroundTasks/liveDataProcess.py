import asyncio
import csv
import time
import logging
from dataclasses import asdict
from threading import Event

from pyarrow import timestamp

from ..bufferedCsvWriter import BufferedCsvWriter
from ..dataSources.simulatedPantheraDataSource import start_process
from ...dependencies import get_testdata_manager, get_connection_manager_data, get_connection_manager_simulation_time
from ...models.liveDataRow import LiveDataRow

logger = logging.getLogger('uvicorn.error')


def process_live_data(stop_event: Event, loop: asyncio.AbstractEventLoop):
    live_data_source = None
    while not stop_event.is_set():
        service = get_testdata_manager()

        test_drive_data = service.get_active_testdrive()

        has_live_test_drive = test_drive_data is not None and test_drive_data.is_live
        if has_live_test_drive:
            if live_data_source is None:
                csv_file = test_drive_data.test_drive_data_info.csv_file_full_path
                buffered_writer = BufferedCsvWriter(csv_file, stop_event)

                def new_live_data_arrived(data: LiveDataRow):
                    logger.info("LiveDataArrived")
                    # send data to websocket
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
                    # Queue for writing
                    buffered_writer.enqueue(asdict(data))

                live_data_source = start_process(new_live_data_arrived)

        elif live_data_source is not None:

            # Stop writing thread
            buffered_writer.shutdown()
            live_data_source.stop()
            live_data_source = None

        sleep_with_event(stop_event, 5)

    if live_data_source is not None:
        # Stop writing thread
        buffered_writer.shutdown()
        live_data_source.stop()
        live_data_source = None


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
