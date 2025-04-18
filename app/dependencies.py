# app/dependencies.py
from .services.testDriveDataService import TestDriveDataService
from .services.testDriveTagService import TestDriveTagService
from .services.websocketConnectionManager import WebsocketConnectionManager
from .settings import Settings

connection_manager_instance = WebsocketConnectionManager()
testdata_manager = TestDriveDataService()
tagdata_manager = TestDriveTagService()

settings = Settings()


def get_connection_manager() -> WebsocketConnectionManager:
    return connection_manager_instance


def get_testdata_manager() -> TestDriveDataService:
    return testdata_manager


def get_settings() -> Settings:
    return settings


def get_tagdata_manager() -> TestDriveTagService:
    return tagdata_manager
