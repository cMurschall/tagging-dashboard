import json
import logging
import os
from pathlib import Path
from typing import Dict, List

from pydantic import ValidationError
import pandas as pd

from app.models.testDriveDataInfo import TestDriveDataInfo
from app.models.testDriveProjectInfo import TestDriveProjectInfo


class TestDriveDataService:
    def __init__(self, storage_path: str = "test_drive_data.json"):
        self.storage_path = storage_path
        self.test_drive_data_store: Dict[int, TestDriveProjectInfo] = {}
        self.current_id = 1
        self.active_testdrive_id = None
        self.active_testdrive_df = None

        self.logger = logging.getLogger('uvicorn.error')
        self._load_data()

    def load_csv_data(self, data_info: TestDriveDataInfo):
        file_path = Path(data_info.csv_file_full_path)
        if not file_path.exists():
            self.logger.warning(f"CSV file does not exist: {file_path}")
            return

        self.active_testdrive_df = pd.read_csv(data_info.csv_file_full_path, skiprows=[1])

    def get_csv_data_columns(self):
        if self.active_testdrive_df is None:
            return []
        return self.active_testdrive_df.dtypes.items()

    def get_csv_data(self, columns: List[str]) -> pd.DataFrame:
        # Column selection
        if not columns:
            self.logger.warning("No columns specified for data selection, returning empty DataFrame")
            return pd.DataFrame()

        if 'timestamp' not in columns:
            columns.append('timestamp')  # always include timestamp

            # Get set of columns in the DataFrame
        valid_columns_set = set(self.active_testdrive_df.columns)
        # Filter out invalid columns
        valid_columns_list = [col for col in columns if col in valid_columns_set]

        # If no valid columns remain, return an empty dataframe or handle otherwise
        if not valid_columns_list:
            self.logger.warning("No valid columns specified for data selection, returning empty DataFrame")
            return pd.DataFrame()

        df = self.active_testdrive_df[valid_columns_list]
        return df

    def _load_data(self):
        """
        Load the data from the storage file.
        :return:
        """
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                try:
                    data = json.load(f)
                    self.test_drive_data_store = {
                        int(k): TestDriveProjectInfo.model_validate(v) for k, v in
                        data.get("test_drive_data_store", {}).items()
                    }
                    self.current_id = max(self.test_drive_data_store.keys(), default=0) + 1
                except ValidationError as e:
                    self.logger.error(f"Failed to parse data: {e}")
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to load JSON: {e}")

        self.logger.info(f"Loaded {len(self.test_drive_data_store)} test drives")

    def _save_data(self):
        """
        Save the data to the storage file.
        :return:
        """
        with open(self.storage_path, "w") as f:
            data = {
                "test_drive_data_store": {key: model.model_dump() for key, model in self.test_drive_data_store.items()}
            }
            json.dump(data, f, default=str, indent=2)

    def get_testdrives(self) -> List[TestDriveProjectInfo]:
        """
        Get all test drives.
        :return:
        """
        return list(self.test_drive_data_store.values())

    def get_testdrive(self, testdrive_id: int) -> TestDriveProjectInfo | None:
        """
        Get a test drive by ID.
        :param testdrive_id:
        :return:
        """
        if testdrive_id not in self.test_drive_data_store:
            return None
        return self.test_drive_data_store[testdrive_id]

    def create_testdrive(self, testdrive: TestDriveProjectInfo) -> TestDriveProjectInfo:
        """
        Create a new test drive.
        :param testdrive:
        :return:
        """
        testdrive.id = self.current_id
        self.test_drive_data_store[self.current_id] = testdrive
        self.current_id += 1
        self._save_data()
        return testdrive

    def update_testdrive(self, testdrive) -> TestDriveProjectInfo | None:
        """
        Update a test drive.
        :param testdrive:
        :return:
        """
        if testdrive.id not in self.test_drive_data_store:
            return None
        self.test_drive_data_store[testdrive.id] = testdrive
        self._save_data()
        return testdrive

    def delete_testdrive(self, testdrive_id: int) -> TestDriveProjectInfo | None:
        """
        Delete a test drive.
        :param testdrive_id:
        :return:
        """
        if testdrive_id not in self.test_drive_data_store:
            return None
        testdrive = self.test_drive_data_store[testdrive_id]
        del self.test_drive_data_store[testdrive_id]
        self._save_data()
        return testdrive

    def get_active_testdrive(self) -> TestDriveProjectInfo | None:
        """
        Get the active test drive.
        """
        if self.active_testdrive_id is None:
            return None
        return self.get_testdrive(self.active_testdrive_id)

    def activate_testdrive(self, testdrive_id: int) -> TestDriveProjectInfo | None:
        """
        Activate a test drive.
        """
        if testdrive_id not in self.test_drive_data_store:
            return None
        self.active_testdrive_id = testdrive_id
        return self.get_active_testdrive()

    def deactivate_testdrive(self) -> TestDriveProjectInfo | None:
        """
        Deactivate the active test drive.
        :return:
        """
        if self.active_testdrive_id is None:
            return None
        testdrive = self.get_active_testdrive()
        self.active_testdrive_id = None
        return testdrive
