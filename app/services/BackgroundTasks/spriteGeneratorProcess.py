import json
import math
import os
import subprocess
import time
from threading import Event

from ...dependencies import get_settings, get_testdata_manager

PROCESSED_FILES_PATH = "processed_files.json"  # Path to the JSON file


def load_processed_files():
    if os.path.exists(PROCESSED_FILES_PATH):
        with open(PROCESSED_FILES_PATH, "r") as file:
            return json.load(file)
    return {}


def save_processed_files(processed_files):
    with open(PROCESSED_FILES_PATH, "w") as file:
        json.dump(processed_files, file, indent=4)


def process_videos_in_folder(stop_event: Event):
    while not stop_event.is_set():
        settings = get_settings()
        os.makedirs(settings.SPRITE_FOLDER, exist_ok=True)

        all_test_drives = get_testdata_manager().get_testdrives()

        # Load the list of already processed files
        processed_files = load_processed_files()

        for file_name in os.listdir(settings.VIDEO_PATH):
            # Skip non-video files if needed
            if not file_name.lower().endswith((".mp4", ".m4v", ".avi", ".mov")):
                continue

            video_path = os.path.join(settings.VIDEO_PATH, file_name)
            video_mod_time = os.path.getmtime(video_path)

            # Check if the video has already been processed
            if file_name in processed_files:
                file_metadata = processed_files[file_name]
                if file_metadata["mod_time"] == video_mod_time:
                    print(f"Skipping already processed video: {file_name}")
                    continue

            # Get video duration only if not already processed
            try:
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                video_duration = float(result.stdout.strip())
            except Exception as e:
                print(f"Failed to retrieve video duration for {file_name}: {e}")
                continue

            # Calculate total thumbnails and grid dimensions
            interval = 4  # Set the interval for thumbnails
            total_thumbnails = math.ceil(video_duration / interval)
            rows = math.ceil(math.sqrt(total_thumbnails))
            columns = math.ceil(total_thumbnails / rows)

            # Generate sprite name with grid dimensions
            base_name, ext = os.path.splitext(file_name)

            thumbnail_width = 120
            thumbnail_height = 90

            sprite_name = f"{base_name}_sprite_{columns}x{rows}_int{interval}_w{thumbnail_width}_h{thumbnail_height}.png"
            sprite_path = os.path.abspath(os.path.join(settings.SPRITE_FOLDER, sprite_name))

            # Generate the sprite if it doesn't already exist
            if not os.path.exists(sprite_path):
                try:
                    generate_ffmpeg_row_sprite(video_path, sprite_path,
                                               interval=interval,
                                               columns=columns,
                                               rows=rows,
                                               thumbnail_width=thumbnail_width,
                                               thumbnail_height=thumbnail_height)
                    print(f"Processed video: {file_name}")
                except Exception as e:
                    print(f"Failed to process video {file_name}: {e}")
                    continue

            # Update processed files metadata
            processed_files[file_name] = {
                "mod_time": video_mod_time,
                "duration": video_duration,
                "columns": columns,
                "rows": rows,
                "sprite_name": sprite_name
            }

            # Update the project with the sprite path
            for test_drive in all_test_drives:
                extracted_filename = os.path.basename(video_path)
                if test_drive.video_path == extracted_filename and test_drive.video_sprite_path != sprite_name:
                    test_drive.video_sprite_path = sprite_name
                    get_testdata_manager().update_testdrive(test_drive)

        # Save the processed files list
        save_processed_files(processed_files)

        time.sleep(10)  # Check the folder every 10 seconds


def generate_ffmpeg_row_sprite(video_path, output_path, interval, columns, rows, thumbnail_width, thumbnail_height):
    # Generate the FFmpeg command
    ffmpeg_command = [
        "ffmpeg", "-n", "-i", video_path,  # Prevent overwriting existing files
        "-vf", f"fps=1/{interval},scale={thumbnail_width}:{thumbnail_height},tile={columns}x{rows}",
        "-frames:v", "1", output_path
    ]

    try:
        print(f"Executing ffmpeg command: {' '.join(ffmpeg_command)}")
        subprocess.run(ffmpeg_command, check=True)
        print(f"Sprite sheet created successfully: {output_path}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg command failed: {e}")

    return output_path
