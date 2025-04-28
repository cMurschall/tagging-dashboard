# app/dependencies.py
from .services.testDriveDataService import TestDriveDataService
from .services.testDriveTagService import TestDriveTagService
from .services.websocketConnectionManager import WebsocketConnectionManager
from .settings import Settings

settings = Settings()

connection_manager_data_instance = WebsocketConnectionManager('data')
connection_manager_simulation_time_instance = WebsocketConnectionManager('simulation time')
connection_manager_tag_instance = WebsocketConnectionManager('tag')

testdata_manager = TestDriveDataService(settings)
tagdata_manager = TestDriveTagService(settings)


def get_connection_manager_data() -> WebsocketConnectionManager:
    return connection_manager_data_instance


def get_connection_manager_simulation_time() -> WebsocketConnectionManager:
    return connection_manager_simulation_time_instance


def get_connection_manager_tag() -> WebsocketConnectionManager:
    return connection_manager_tag_instance


def get_testdata_manager() -> TestDriveDataService:
    return testdata_manager


def get_settings() -> Settings:
    return settings


def get_tagdata_manager() -> TestDriveTagService:
    return tagdata_manager
