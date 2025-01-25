import math
import time
import subprocess
import cv2
import os


def get_video_duration_opencv(video_path):
    """
    Get the duration of a video using OpenCV (cv2).

    Args:
        video_path (str): Path to the input video file.

    Returns:
        float: Video duration in seconds.
    """
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        raise RuntimeError(f"Failed to open video file: {video_path}")
    fps = video.get(cv2.CAP_PROP_FPS)  # Frames per second
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)  # Total frame count
    video_duration = frame_count / fps
    video.release()
    return video_duration


def get_video_duration_ffmpeg(video_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
             video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        video_duration = float(result.stdout.strip())
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve video duration: {e}")
    return video_duration


def generate_ffmpeg_row_sprite_command(video_path, output_path, interval, thumbnail_width, thumbnail_height):
    """
    Generate a sprite sheet with thumbnails in a single row using FFmpeg.

    Args:
        video_path (str): Path to the input video file.
        output_path (str): Path to the output sprite image.
        interval (float): Time interval between each thumbnail (in seconds).
        thumbnail_width (int): Width of each thumbnail.
        thumbnail_height (int): Height of each thumbnail.

    Returns:
        int: Number of thumbnails generated.
    """
    # Get video duration using FFmpeg

    video_duration = get_video_duration_ffmpeg(video_path)
    # Calculate the total number of thumbnails
    total_thumbnails = math.ceil(video_duration / interval)

    # Generate the FFmpeg command
    ffmpeg_command = [
        "ffmpeg", "-i", video_path,
        "-vf", f"fps=1/{interval},scale={thumbnail_width}:{thumbnail_height},tile={total_thumbnails}x1",
        "-frames:v", "1", output_path
    ]

    # Execute the FFmpeg command
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Sprite sheet created successfully: {output_path}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg command failed: {e}")

    return total_thumbnails


if __name__ == "__main__":
    video_path = "d:\\Praxisprojekt Herms\\2024-04-17 16-10-09 Mapping Trip 01-1.m4v"
    output_path = "sprite_row.png"
    interval = 3  # 2 seconds between each thumbnail
    thumbnail_width = 120
    thumbnail_height = 90

    # delete the output file if it already exists
    if os.path.exists(output_path):
        os.remove(output_path)
    start = time.time()
    # your code here

    try:
        total_thumbnails = generate_ffmpeg_row_sprite_command(
            video_path, output_path, interval, thumbnail_width, thumbnail_height
        )
        print(f"Total thumbnails: {total_thumbnails}")
    except RuntimeError as e:
        print(e)

    print(time.time() - start)
    pass
