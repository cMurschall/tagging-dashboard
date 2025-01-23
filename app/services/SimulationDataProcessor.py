from dataclasses import dataclass

import os
from datetime import datetime, timedelta
import re
from dataclasses import dataclass, asdict
from typing import List
import cv2
import pandas as pd
from easyocr import easyocr
import json


@dataclass
class SimulationFileData:
    file: str
    date_time_file_name: datetime
    simulation_start_time: float
    simulation_end_time: float
    type: str

    def to_serializable(self):
        data = asdict(self)
        data['date_time_file_name'] = self.date_time_file_name.isoformat()  # Serialize datetime as ISO string
        return data

    @property
    def absolute_start_time(self) -> datetime:
        return self.date_time_file_name + timedelta(seconds=self.simulation_start_time)

    @property
    def absolute_end_time(self) -> datetime:
        return self.date_time_file_name + timedelta(seconds=self.simulation_end_time)

    @classmethod
    def from_dict(cls, data):
        return cls(
            file=data["file"],
            date_time_file_name=datetime.fromisoformat(data["date_time_file_name"]),
            simulation_start_time=data["simulation_start_time"],
            simulation_end_time=data["simulation_end_time"],
            type=data["type"]
        )


class SimulationDataProcessor:
    def __init__(self, video_directory: str, csv_directory: str, data_file: str = "simulation_data.json"):
        self.video_directory = video_directory
        self.csv_directory = csv_directory
        self.data_file = data_file
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.csv_data: List[SimulationFileData] = []
        self.video_data: List[SimulationFileData] = []
        self.load_simulation_data()

    @staticmethod
    def parse_timestamp_to_seconds(timestamp: str):
        parts = [s.strip() for s in re.split(r'[;,:.\s]', timestamp)]
        if len(parts) != 4:
            return None

        hours, minutes, seconds, microseconds = map(int, parts)
        total_seconds = (
                hours * 3600 +
                minutes * 60 +
                seconds +
                microseconds / 1e6
        )
        return total_seconds

    def extract_timestamp_from_frame(self, frame):
        roi = frame[30:130, 20:650]
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        results = self.reader.readtext(roi, detail=0)
        text = results[0].strip() if results else None
        return text

    def process_n_frames(self, video_path: str, frames=20, from_end=False):
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if from_end:
            last_valid_frame = -1
            for frame_index in range(total_frames - 1, -1, -1):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
                ret, _ = cap.read()
                if ret:
                    last_valid_frame = frame_index
                    break

            if last_valid_frame == -1:
                print("No valid frame found at the end.")
                cap.release()
                return 0

            start_frame = last_valid_frame
            frame_range = range(start_frame, start_frame - frames, -1)
        else:
            start_frame = 0
            frame_range = range(start_frame, start_frame + frames)

        total_seconds = 0
        for frame_index in frame_range:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = cap.read()
            if not ret:
                print(f"Frame {frame_index}: Unable to read frame - continuing")
                continue

            timestamp = self.extract_timestamp_from_frame(frame, frame_index)
            if not timestamp:
                print(f"Frame {frame_index}: No timestamp found - continuing")
                continue

            parsed_time = self.parse_timestamp_to_seconds(timestamp)
            if not parsed_time:
                print(f"Frame {frame_index}: Invalid timestamp format: {timestamp}")
                continue

            total_seconds = parsed_time
            break

        cap.release()
        return total_seconds

    def parse_videos(self):
        video_files = os.listdir(self.video_directory)
        video_files = [file for file in video_files if file.endswith(".mp4")]
        pattern = r"(\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2})"
        found: List[SimulationFileData] = []

        for file in video_files:
            if any(video.file == file for video in self.video_data):
                continue
            match = re.search(pattern, file)
            if match:
                date_time = datetime.strptime(match.group(), "%Y-%m-%d %H-%M-%S")
            video_path = os.path.join(self.video_directory, file)
            simulation_start_time = self.process_n_frames(video_path, frames=5)
            simulation_end_time = self.process_n_frames(video_path, frames=30, from_end=True)

            simulation_time = simulation_end_time - simulation_start_time
            print(
                f"Video: {file}, Start Time: {simulation_start_time}, End Time: {simulation_end_time}, Simulation Time: {simulation_time}")
            found.append(SimulationFileData(file, date_time, simulation_start_time, simulation_end_time, "video"))

        self.video_data.extend(found)
        return found

    def parse_csv_files(self):

        def convert_to_float_list(column):
            return column.apply(lambda x: [float(i) for i in x.split(',')])

        csv_files = os.listdir(self.csv_directory)
        csv_files = [file for file in csv_files if file.endswith(".csv")]
        pattern = r"recording_(\d{4})_(\d{2})_(\d{2})__(\d{2})_(\d{2})_(\d{2})"
        found: List[SimulationFileData] = []

        for file in csv_files:
            if any(csv.file == file for csv in self.csv_data):
                continue
            match = re.search(pattern, file)
            if match:
                year, month, day, hour, minute, second = map(int, match.groups())
                date_time = datetime(year, month, day, hour, minute, second)

            csv_path = os.path.join(self.csv_directory, file)
            try:
                df = pd.read_csv(csv_path, header=0, skiprows=[1])

                list_columns = ['rrp_pos', 'rrp_lin_vel', 'rrp_quat', 'rrp_rot_vel', 'car0_vehicle_pos',
                                'car0_vehicle_quat', 'car0_vehicle_vel', 'car0_steer_quat', 'car0_wheel0_pos',
                                'car0_wheel0_quat', 'car0_caliper0_quat', 'car0_wheel1_pos', 'car0_wheel1_quat',
                                'car0_caliper1_quat', 'car0_wheel2_pos', 'car0_wheel2_quat', 'car0_caliper2_quat',
                                'car0_wheel3_pos', 'car0_wheel3_quat', 'car0_caliper3_quat', 'lin_vel', 'lin_acc',
                                'rot_vel', 'rot_acc']

                df[list_columns] = df[list_columns].apply(convert_to_float_list)
                df['car0_mask_objects'] = int(df['car0_mask_objects'])

                simulation_start = float(df["timestamp"].iloc[1])
                simulation_end = float(df["timestamp"].iloc[-1])
                simulation_time = simulation_end - simulation_start
                print(
                    f"CSV: {file}, Start Time: {simulation_start}, End Time: {simulation_end}, Simulation Time: {simulation_time}")
                found.append(SimulationFileData(file, date_time, simulation_start, simulation_end, "csv"))
            except Exception as e:
                print(f"Error reading file {file}: {e}")

        self.csv_data.extend(found)
        return found

    def parse_data(self):
        csv_data = self.parse_csv_files()
        video_data = self.parse_videos()
        self.save_simulation_data()
        return csv_data, video_data

    def get_csv_data(self):
        return self.csv_data

    def get_video_data(self):
        return self.video_data

    def save_simulation_data(self, output_file=None):
        if output_file is None:
            output_file = self.data_file
        all_data = {
            "csv": [item.to_serializable() for item in self.csv_data],
            "video": [item.to_serializable() for item in self.video_data],
        }
        with open(output_file, "w") as f:
            json.dump(all_data, f, indent=4)

    def load_simulation_data(self, input_file=None):
        if input_file is None:
            input_file = self.data_file
        if os.path.exists(input_file):
            with open(input_file, "r") as f:
                loaded_data = json.load(f)
            self.csv_data = [SimulationFileData.from_dict(item) for item in loaded_data.get("csv", [])]
            self.video_data = [SimulationFileData.from_dict(item) for item in loaded_data.get("video", [])]

    # Function to find matching pairs based on absolute times
    def find_matching_pairs(self):
        csv_files = self.get_csv_data()
        video_files = self.get_video_data()

        pairs = []
        for video in video_files:
            for csv in csv_files:
                # Check for overlap in absolute times
                if video.absolute_start_time <= csv.absolute_end_time and video.absolute_end_time >= csv.absolute_start_time:
                    pairs.append((csv, video))
        return pairs
