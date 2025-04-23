import json
import math
import os
import subprocess
import tempfile
import struct

from enum import Enum
from pathlib import Path
from typing import BinaryIO

import cv2
import easyocr

from app.models.testDriveVideoInfo import TestDriveVideoInfo
from app.dependencies import get_settings


def analyze_video(video_info: TestDriveVideoInfo) -> bool:
    faststart_location = find_moov_atom_location(Path(video_info.video_file_full_path))

    # here we check if the moov atom is at the start of the file. This is needed because if it is at the end of
    # the file, the video will not be playable in a web browser. This is a requirement for the video player
    # the moove atom is likely at the end of the simulation video, because the simulation video is recorded
    # and during the recording the final length is not known. So the recorder puts the moov atom at the end of the file
    if faststart_location != MoovPosition.Start:
        print(f"Video {video_info.video_file_name} is not fast start enabled. Processing...")
        move_moov_atom(video_info.video_file_full_path)

    has_duration = video_info.video_duration_s > 0
    if not has_duration:
        info = extract_video_info(video_info.video_file_full_path)
        if not info:
            return False

        video_info.video_duration_s = info["video_duration_s"]
        video_info.video_width = info["video_width"]
        video_info.video_height = info["video_height"]
        video_info.video_frame_rate = info["video_frame_rate"]

        start_by_timestamp_change = estimate_start_timestamp(video_info.video_file_full_path,
                                                             video_info.video_frame_rate)
        start = process_first_n_frames(video_info.video_file_full_path, video_info.video_frame_rate, 10)
        stop = process_last_n_frames(video_info.video_file_full_path, video_info.video_frame_rate, 10)

        video_info.video_simulation_time_start_s = start
        video_info.video_simulation_time_end_s = stop

    # here we generate the thumbnail preview images for the video. This is needed for the video player
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


def extract_timestamp_from_frame(frame) -> str | None:
    # Define the region of interest (ROI) for the timestamp (top-left corner)
    roi = frame[30:130, 20:650]

    reader = easyocr.Reader(['en'], gpu=True)
    results = reader.readtext(roi, detail=0)
    return results[0].strip() if results else None


def parse_timestamp_to_seconds(timestamp) -> float:
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


def estimate_start_timestamp(video_path, frame_rate, search_duration_secs=1.5) -> float:
    def extract_timestamp_at_frame(cap, frame_idx):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            return None
        return extract_timestamp_from_frame(frame)

    cap = cv2.VideoCapture(video_path)
    max_frame = int(search_duration_secs * frame_rate)

    start_frame = 10

    low = start_frame
    high = max_frame

    # Get initial timestamp at frame 0
    first_ts = extract_timestamp_at_frame(cap, start_frame)
    if not first_ts:
        cap.release()
        raise ValueError("No timestamp found at frame 0.")

    # Binary search for first timestamp change
    while low < high:
        mid = (low + high) // 2
        ts = extract_timestamp_at_frame(cap, mid)
        if not ts or ts == first_ts:
            low = mid + 1
        else:
            high = mid

    # Final extraction at frame with changed timestamp
    changed_ts = extract_timestamp_at_frame(cap, low)
    cap.release()

    if changed_ts:
        ts_seconds = parse_timestamp_to_seconds(changed_ts)
        seconds_offset = low / frame_rate
        seconds_at_frame_0 = ts_seconds - seconds_offset

        print(f"Timestamp at frame {low}: {changed_ts} = {ts_seconds:.6f}s")
        print(f"Estimated timestamp at frame 0: {seconds_at_frame_0:.6f}s")

        return seconds_at_frame_0
    else:
        raise ValueError("Unable to determine timestamp change within search window.")


def process_first_n_frames(video_path, frame_rate, frames=20) -> float:
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    total_seconds = 0

    while cap.isOpened() and frame_count < frames:
        ret, frame = cap.read()
        if not ret:
            break

        # Extract timestamp
        timestamp = extract_timestamp_from_frame(frame)
        if timestamp:
            total_seconds = parse_timestamp_to_seconds(timestamp)
            print(f"Frame {frame_count}: Extracted Timestamp: {timestamp}, Total Seconds: {total_seconds}")
            break
        else:
            print(f"Frame {frame_count}: No timestamp found")
        frame_count += 1

    seconds_at_frame_0 = total_seconds - (frame_count / frame_rate)
    cap.release()
    return seconds_at_frame_0


def process_last_n_frames(video_path, frame_rate, frames=20):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    start_frame = max(total_frames - frames, 0)

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frame_count = 0
    timestamp_found = False
    extracted_seconds = 0

    while cap.isOpened() and frame_count < frames:
        ret, frame = cap.read()
        if not ret:
            break

        current_frame_number = start_frame + frame_count
        timestamp = extract_timestamp_from_frame(frame)
        if timestamp:
            extracted_seconds = parse_timestamp_to_seconds(timestamp)
            print(f"Frame {current_frame_number}: Extracted Timestamp: {timestamp}, Total Seconds: {extracted_seconds}")
            timestamp_found = True
            break
        else:
            print(f"Frame {current_frame_number}: No timestamp found")
        frame_count += 1

    cap.release()

    if timestamp_found:
        # Estimate timestamp of the last frame based on current frame position and frame rate
        frames_remaining = (total_frames - 1) - (start_frame + frame_count)
        estimated_video_end = extracted_seconds + (frames_remaining / frame_rate)
        print(f"Estimated video end time: {estimated_video_end:.3f} seconds")
        return estimated_video_end
    else:
        print(f"No timestamp found in last N={frames} frames.")
        return None

    cap.release()
    return total_seconds


class MoovPosition(Enum):
    Start = 1
    Middle = 2
    End = 3


def find_moov_atom_location(file_path: Path, tolerance: int = 32) -> MoovPosition:
    """Checks if the 'moov' atom is at the start or end of an MP4 file."""

    with open(file_path, "rb") as f:
        file_size = file_path.stat().st_size
        offset = 0

        while offset < file_size:
            # Read atom size (4 bytes) and type (4 bytes)
            atom_header = f.read(8)
            if len(atom_header) < 8:
                break  # Reached end of file or invalid atom

            atom_size, atom_type = struct.unpack(">I4s", atom_header)
            atom_type = atom_type.decode("utf-8")

            if atom_type == "moov":
                if offset <= tolerance:
                    return MoovPosition.Start
                elif offset + atom_size + tolerance >= file_size:
                    return MoovPosition.End
                else:
                    return MoovPosition.Middle  # Moov atom is neither at the start nor end

            # Move to the next atom
            offset += atom_size
            f.seek(offset)

    return "moov atom not found"


def move_moov_atom(input_file):
    """
    Uses ffmpeg to repackage the file with the moov atom moved to the beginning.
    The conversion is written to a temporary file, which then overwrites the original file.
    """
    # Create a temporary file in the same directory as the input file
    dir_name = os.path.dirname(input_file)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4", dir=dir_name) as tmp:
        temp_file = tmp.name

    # Run ffmpeg to convert the file and output to the temporary file
    cmd = [
        "ffmpeg",
        "-y",  # Add -y to automatically overwrite existing files
        "-i", input_file,
        "-c", "copy",
        "-movflags", "+faststart",
        temp_file
    ]
    subprocess.run(cmd, check=True)

    # Replace the original file with the temporary file
    os.replace(temp_file, input_file)
    if os.path.exists(temp_file):
        os.remove(temp_file)  # remove the temp file if it still exists.
    print(f"Overwritten the original file with faststart enabled version: {input_file}")


def read_atom(file: BinaryIO) -> tuple[None, None, None] | tuple[int, int, str]:
    pos = file.tell()
    atom_header = file.read(8)

    if len(atom_header) < 8:
        return None, None, None  # EOF or invalid atom

    # ">I4s" = Big-endian unsigned int followed by 4 bytes string
    size, atom_type = struct.unpack(">I4s", atom_header)

    # check if the atom size is valid
    file_size = os.fstat(file.fileno()).st_size
    if size < 8 or pos + size > file_size:
        # invalid atom
        return None, None, None

    return pos, size, atom_type.decode("utf-8")


def parse_mp4(filename: str):
    with open(filename, "rb") as file:
        while True:
            pos, size, atom_type = read_atom(file)
            if not atom_type:
                break  # End of file or invalid atom

            print(f"Position: {pos}, Atom: {atom_type}, Größe: {size} Bytes")

            # Skip the rest of the file minus 8 bytes (size and type)
            if size > 8:
                file.seek(size - 8, 1)
