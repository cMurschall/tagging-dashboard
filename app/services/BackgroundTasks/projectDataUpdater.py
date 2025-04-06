import time
import logging
from threading import Event
from app.services.backgroundTasks.videoAnalyzer import analyze_video
from app.services.backgroundTasks.dataAnalyzer import analyze_data
from app.services.backgroundTasks.tagAnalyzer import analyze_tags

from ...dependencies import get_testdata_manager

logger = logging.getLogger(__name__)


def process_projects(stop_event: Event):
    while not stop_event.is_set():
        service = get_testdata_manager()

        test_drive_data = service.get_testdrives()

        for test_drive in test_drive_data:
            start = time.time()
            updated_video = analyze_video(test_drive.test_drive_video_info)
            updated_data = analyze_data(test_drive.test_drive_data_info)
            updated_tags = analyze_tags(test_drive.test_drive_tag_info)
            end = time.time()

            update_needed = updated_video or updated_data or updated_tags
            if update_needed:
                service.update_testdrive(test_drive)
                logger.info(f"Time to update project: {end - start}")

        sleep_with_event(stop_event, 10)


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
