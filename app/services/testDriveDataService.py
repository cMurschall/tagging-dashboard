import json
import os
from typing import Dict, List

from dataclasses import asdict

from pydantic import ValidationError

from app.models.tags import Tag
from app.models.testDriveData import TestDriveData


class TestDriveDataService:
    def __init__(self, storage_path: str = "test_drive_data.json"):
        self.storage_path = storage_path
        self.test_drive_data_store: Dict[int, TestDriveData] = {}
        self.current_id = 1
        self._load_data()

    # def _load_data(self):
    #     if os.path.exists(self.storage_path):
    #         with open(self.storage_path, "r") as f:
    #             data = json.load(f)
    #             self.test_drive_data_store = {int(k): TestDriveData(**v) for k, v in
    #                                           data.get("test_drive_data_store", {}).items()}
    #             self.current_id = data.get("current_id", 1)

    def _load_data(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                try:
                    data = json.load(f)
                    self.test_drive_data_store = {
                        int(k): TestDriveData.model_validate(v) for k, v in
                        data.get("test_drive_data_store", {}).items()
                    }
                    self.current_id = data.get("current_id", 1)
                except ValidationError as e:
                    print(f"Failed to parse data: {e}")
                except json.JSONDecodeError as e:
                    print(f"Failed to load JSON: {e}")

    def _save_data(self):
        with open(self.storage_path, "w") as f:
            data = {
                "test_drive_data_store": {k: v.__dict__ for k, v in self.test_drive_data_store.items()},
                "current_id": self.current_id
            }
            json.dump(data, f, default=str)

    def get_testdrives(self) -> List[TestDriveData]:
        return self.test_drive_data_store.values()

    def get_testdrive(self, testdrive_id: int) -> TestDriveData:
        if testdrive_id not in self.test_drive_data_store:
            return None
        return self.test_drive_data_store[testdrive_id]

    def create_testdrive(self, testdrive: TestDriveData) -> TestDriveData:
        testdrive.id = self.current_id
        self.test_drive_data_store[self.current_id] = testdrive
        self.current_id += 1
        self._save_data()
        return testdrive

    def create_testdrive_from_live_data(self, live_data_stream):
        test_drive_data = TestDriveData(raw_data={})
        for data_point in live_data_stream:
            for key, value in data_point.items():
                if key not in test_drive_data.raw_data:
                    test_drive_data.raw_data[key] = []
                test_drive_data.raw_data[key].append(value)
        self.test_drive_data_store[self.current_id] = test_drive_data
        self.current_id += 1
        self._save_data()
        return self.current_id - 1

    def add_tag(self, testdrive_id: int, tag: Tag):
        if testdrive_id not in self.test_drive_data_store:
            return None
        self.test_drive_data_store[testdrive_id].tags.append(tag)
        self._save_data()
        return tag

    def delete_tag(self, testdrive_id: int, tag_index: int):
        """
        Delete a tag from a test drive
        :param testdrive_id:
        :param tag_index:
        :return: None if the test drive or tag does not exist, the deleted tag otherwise
        """
        if testdrive_id not in self.test_drive_data_store:
            return None
        if tag_index < 0 or tag_index >= len(self.test_drive_data_store[testdrive_id].tags):
            return None
        tag = self.test_drive_data_store[testdrive_id].tags[tag_index]
        del self.test_drive_data_store[testdrive_id].tags[tag_index]
        self._save_data()
        return tag

    def list_csv_files(self, folder_path: str) -> List[str]:
        """
        List all CSV files in the specified folder.
        """
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise FileNotFoundError(f"The folder {folder_path} does not exist or is not a directory.")

        return [f for f in os.listdir(folder_path) if f.endswith(".csv")]

    def list_video_files(self, folder_path: str) -> List[str]:
        """
        List all MP4 video files in the specified folder.
        """
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise FileNotFoundError(f"The folder {folder_path} does not exist or is not a directory.")

        return [f for f in os.listdir(folder_path) if f.endswith(".m4v")]
