import json
import os
from typing import Dict, List

from pydantic import ValidationError

from app.models.tags import Tag
from app.models.testDriveProjectInfo import TestDriveProjectInfo
from app.settings import settings


class TestDriveDataService:
    def __init__(self, storage_path: str = "test_drive_data.json"):
        self.storage_path = storage_path
        self.test_drive_data_store: Dict[int, TestDriveProjectInfo] = {}
        self.current_id = 1
        self.active_testdrive_id = None

        self._load_data()

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
                    print(f"Failed to parse data: {e}")
                except json.JSONDecodeError as e:
                    print(f"Failed to load JSON: {e}")

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
        return self.test_drive_data_store.values()

    def get_testdrive(self, testdrive_id: int) -> TestDriveProjectInfo:
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

    def update_testdrive(self, testdrive):
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

    def delete_testdrive(self, testdrive_id: int) -> TestDriveProjectInfo:
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

    def create_testdrive_from_live_data(self, live_data_stream):
        test_drive_data = TestDriveProjectInfo(raw_data={})
        for data_point in live_data_stream:
            for key, value in data_point.items():
                if key not in test_drive_data.raw_data:
                    test_drive_data.raw_data[key] = []
                test_drive_data.raw_data[key].append(value)
        self.test_drive_data_store[self.current_id] = test_drive_data
        self.current_id += 1
        self._save_data()
        return self.current_id - 1

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

    def add_tag(self, testdrive_id: int, tag: Tag):
        """
        Add a tag to a test drive.
        :param testdrive_id:
        :param tag:
        :return:
        """
        if testdrive_id not in self.test_drive_data_store:
            # todo: we might be live here - so we will store in separate file
            return None

        self.test_drive_data_store[testdrive_id].tags.append(tag)
        self._save_data()
        return tag

    def delete_tag(self, testdrive_id: int, tag_index: int):
        """
        Delete a tag from a test drive.
        :param testdrive_id:
        :param tag_index:
        :return:
        """
        if testdrive_id not in self.test_drive_data_store:
            # todo: we might be live here - so we will store in separate file
            return None
        if tag_index < 0 or tag_index >= len(self.test_drive_data_store[testdrive_id].tags):
            return None
        tag = self.test_drive_data_store[testdrive_id].tags[tag_index]
        del self.test_drive_data_store[testdrive_id].tags[tag_index]
        self._save_data()
        return tag
