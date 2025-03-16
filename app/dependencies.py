# app/dependencies.py
from .services.player import Player
from .services.testDriveDataService import TestDriveDataService
from .services.websocketConnectionManager import WebsocketConnectionManager
from .settings import Settings

connection_manager_instance = WebsocketConnectionManager()
player_instance = Player(connection_manager_instance)
testdata_manager = TestDriveDataService()

settings = Settings()


def get_player() -> Player:
    return player_instance


def get_connection_manager() -> WebsocketConnectionManager:
    return connection_manager_instance


def get_testdata_manager() -> TestDriveDataService:
    return testdata_manager


def get_settings() -> Settings:
    return settings
