import csv
import importlib
import json
import logging
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from pydantic import ValidationError
import pandas as pd

from app.models.liveDataRow import LiveDataRow
from app.models.testDriveDataInfo import TestDriveDataInfo
from app.models.testDriveMetaData import TestDriveMetaData
from app.models.testDriveProjectInfo import TestDriveProjectInfo
from app.models.testDriveTagInfo import TestDriveTagInfo
from app.settings import Settings


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

        if self.has_live_data() or True:
            live_project_info = self.create_live_data_project(self.storage_path)
            if live_project_info:
                # push live project to the start of the list
                self.test_drive_data_store = {0: live_project_info, **self.test_drive_data_store}

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

        # check if the test drive is live
        testdrive = self.test_drive_data_store[testdrive_id]
        if testdrive.is_live:
            self.logger.info(f"Live drive {testdrive.id} activated")

        return self.get_active_testdrive()

    def deactivate_testdrive(self) -> TestDriveProjectInfo | None:
        """
        Deactivate the active test drive.
        :return: The deactivated test drive or None if no active test drive was set.
        """
        if self.active_testdrive_id is None:
            return None
        testdrive = self.get_active_testdrive()
        self.active_testdrive_id = None
        return testdrive

    def has_live_data(self) -> bool:
        """
        Check if the live data module is available.
        :return: True if the module is available, False otherwise.
        """
        return True
        module_name = "panthera"
        spec = importlib.util.find_spec(module_name)
        return spec is not None and spec.loader is not None

    def create_live_data_project(self, tag_storage_path: str) -> TestDriveProjectInfo | None:
        """
        Get the live data project.
        :return: The live data project or None if not available.
        """
        if not self.has_live_data():
            return None

        live_project_info = TestDriveProjectInfo(
            id=0,
            is_live=True,
            creation_date=datetime.now(),
            test_drive_meta_info=TestDriveMetaData(
                route_name="live route",
                driver_name="live driver",
                vehicle_name="live vehicle",
                notes=""
            )
        )
        return live_project_info

    def create_new_live_data(self, test_drive: TestDriveProjectInfo, settings: Settings):
        def get_next_live_tag_file(storage_path: Path) -> Path:
            pattern = re.compile(r"live_tags_(\d+)\.csv$")
            max_index = 0

            for file in storage_path.glob("live_tags_*.csv"):
                match = pattern.match(file.name)
                if match:
                    index = int(match.group(1))
                    max_index = max(max_index, index)

            next_index = max_index + 1
            return storage_path / f"live_tags_{next_index}.csv"

        tag_file = get_next_live_tag_file(Path(settings.TAG_PATH))
        test_drive.test_drive_tag_info.tag_file_name = tag_file.name
        test_drive.test_drive_tag_info.tag_file_full_path = str(tag_file.resolve())

        #
        temp_file_name = "live_data_temp.csv"
        header = LiveDataRow.get_field_mapping()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as tmpfile:
            writer = csv.DictWriter(tmpfile, fieldnames=[field for field in LiveDataRow.__annotations__])
            writer.writeheader()
            temp_path = Path(tmpfile.name)
            test_drive.test_drive_data_info.csv_file_name = tmpfile.name
            test_drive.test_drive_data_info.csv_file_full_path = str(temp_path.resolve())
