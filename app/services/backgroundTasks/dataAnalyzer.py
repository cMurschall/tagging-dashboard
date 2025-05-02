import logging

import pandas as pd

from app.models.testDriveDataInfo import TestDriveDataInfo

logger = logging.getLogger('uvicorn.error')


def analyze_data(data_info: TestDriveDataInfo) -> bool:
    is_data_analyzed = data_info.driven_time_s > 0
    if is_data_analyzed:
        return False  # no update needed

    logger.info(f"Analyzing data for {data_info.csv_file_name}...")

    # skip first row
    df = pd.read_csv(data_info.csv_file_full_path, skiprows=[1])

    velocity_column = "car0_velocity"

    df['time_interval'] = df['timestamp'].diff()  # Time difference between consecutive rows
    df['time_interval'] = df['time_interval'].fillna(0)
    # Calculate the distance for each interval
    df['distance'] = df[velocity_column] * df['time_interval']
    average_speed = df[velocity_column].mean()

    max_speed = df[velocity_column].max()

    # Calculate the total distance
    total_distance = df['distance'].sum()

    start_time = df.iloc[0]["timestamp"]
    end_time = df.iloc[-1]["timestamp"]
    duration = end_time - start_time

    data_info.driven_distance_m = total_distance
    data_info.driven_time_s = duration
    data_info.average_speed_m_s = average_speed
    data_info.max_speed_m_s = max_speed

    data_info.data_simulation_time_start_s = start_time
    data_info.data_simulation_time_end_s = end_time
    data_info.data_count_rows = len(df)

    return True  # update needed
