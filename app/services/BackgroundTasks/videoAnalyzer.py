import json
import math
import os
import subprocess

import cv2
import easyocr

from app.models.testDriveVideoInfo import TestDriveVideoInfo
from app.dependencies import get_settings


def analyze_video(video_info: TestDriveVideoInfo) -> bool:
    has_duration = video_info.video_duration_s > 0
    if not has_duration:
        info = extract_video_info(video_info.video_file_full_path)
        if not info:
            return False

        video_info.video_duration_s = info["video_duration_s"]
        video_info.video_width = info["video_width"]
        video_info.video_height = info["video_height"]
        video_info.video_frame_rate = info["video_frame_rate"]

        start = process_first_n_frames(video_info.video_file_full_path, 10)
        stop = process_last_n_frames(video_info.video_file_full_path, 10)

        video_info.video_simulation_time_start_s = start
        video_info.video_simulation_time_end_s = stop

    has_thumbnail = video_info.video_sprite_info.sprite_file_name != ""
    if not has_thumbnail:
        settings = get_settings()

        # Generate sprite name with grid dimensions
        base_name, ext = os.path.splitext(video_info.video_file_name)

        sprite_name = f"{base_name}_sprite.png"
        sprite_file_path = os.path.abspath(os.path.join(settings.SPRITE_FOLDER, sprite_name))
        sprite_info = generate_sprites(
            video_info.video_file_full_path,
            sprite_file_path,
            video_info.video_duration_s
        )
        if not sprite_info:
            return False

        video_info.video_sprite_info.sprite_file_name = sprite_name
        video_info.video_sprite_info.sprite_file_full_path = sprite_file_path
        video_info.video_sprite_info.sprite_columns = sprite_info["sprite_columns"]
        video_info.video_sprite_info.sprite_rows = sprite_info["sprite_rows"]
        video_info.video_sprite_info.thumbnail_width = sprite_info["thumbnail_width"]
        video_info.video_sprite_info.thumbnail_height = sprite_info["thumbnail_height"]
        video_info.video_sprite_info.sprite_interval = sprite_info["sprite_interval"]
        video_info.video_sprite_info.sprites_total = sprite_info["sprites_total"]

        return True
    return False


def generate_sprites(video_path, output_path, video_duration_s):
    thumbnail_width = 120
    thumbnail_height = 90

    if video_duration_s < 5 * 60:
        interval = 1
    elif video_duration_s < 20 * 60:
        interval = video_duration_s // 100  # Aim for ~100 thumbnails
    elif video_duration_s < 60 * 60:
        interval = max(10, video_duration_s // 200)  # Reduce thumbnails for longer videos
    else:
        interval = max(30, video_duration_s // 300)  # Further reduce thumbnails for very long videos

    total_sprites = math.ceil(video_duration_s / interval)
    rows = math.ceil(math.sqrt(total_sprites))
    columns = math.ceil(total_sprites / rows)

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

    # return values as dictionary
    return {
        "sprite_columns": columns,
        "sprite_rows": rows,
        "thumbnail_width": thumbnail_width,
        "thumbnail_height": thumbnail_height,
        "sprite_interval": interval,
        "sprites_total": total_sprites
    }


def extract_video_info(video_file_path: str):
    try:
        command = [
            "ffprobe",
            "-v", "error",
            "-print_format", "json",
            "-show_streams",
            "-show_format",
            video_file_path]

        # Run the command and capture the output
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        metadata = json.loads(result.stdout)

        # Find the video stream
        video_stream = next(
            (stream for stream in metadata['streams'] if stream['codec_type'] == 'video'), None
        )
        if not video_stream:
            return None

        # Extract metadata
        duration = float(metadata['format']['duration'])
        width = int(video_stream['width'])
        height = int(video_stream['height'])
        frame_rate = eval(video_stream['r_frame_rate'])  # Converts "x/1" to float

        return {
            "video_duration_s": duration,
            "video_width": width,
            "video_height": height,
            "video_frame_rate": frame_rate
        }


    except subprocess.CalledProcessError as e:
        print(f"Error calling ffprobe: {e.stderr}")
    except Exception as e:
        print(f"Error extracting video info: {e}")
    return None


def extract_timestamp_from_frame(frame, frame_count):
    # Define the region of interest (ROI) for the timestamp (top-left corner)
    roi = frame[30:130, 20:650]  # Adjust as needed

    reader = easyocr.Reader(['en'], gpu=True)
    results = reader.readtext(roi, detail=0)
    return results[0].strip() if results else None


def parse_timestamp_to_seconds(timestamp):
    # Split the timestamp into hours, minutes, seconds, and microseconds
    parts = timestamp.split('.')  # Split by "."
    if len(parts) != 4:
        raise ValueError("Invalid timestamp format. Expected format: H.MM.SS.MICRO")

    hours, minutes, seconds, microseconds = map(int, parts)

    # Convert to total seconds
    total_seconds = (
            hours * 3600 +  # Convert hours to seconds
            minutes * 60 +  # Convert minutes to seconds
            seconds +  # Seconds
            microseconds / 1e6  # Convert microseconds to fractional seconds
    )
    return total_seconds


def process_first_n_frames(video_path, frames=20):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    total_seconds = 0

    while cap.isOpened() and frame_count < frames:
        ret, frame = cap.read()
        if not ret:
            break

        # Extract timestamp
        timestamp = extract_timestamp_from_frame(frame, frame_count)
        if timestamp:
            total_seconds = parse_timestamp_to_seconds(timestamp)
            print(f"Frame {frame_count}: Extracted Timestamp: {timestamp}, Total Seconds: {total_seconds}")
            break
        else:
            print(f"Frame {frame_count}: No timestamp found")
        frame_count += 1

    cap.release()
    return total_seconds


def process_last_n_frames(video_path, frames=20):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    start_frame = max(total_frames - frames, 0)

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frame_count = 0
    total_seconds = 0

    while cap.isOpened() and frame_count < frames:
        ret, frame = cap.read()
        if not ret:
            break

        # Extract timestamp
        timestamp = extract_timestamp_from_frame(frame, start_frame + frame_count)
        if timestamp:
            total_seconds = parse_timestamp_to_seconds(timestamp)
            print(
                f"Frame {start_frame + frame_count}: Extracted Timestamp: {timestamp}, Total Seconds: {total_seconds}")
            break
        else:
            print(f"Frame {start_frame + frame_count}: No timestamp found")
        frame_count += 1

    cap.release()
    return total_seconds
