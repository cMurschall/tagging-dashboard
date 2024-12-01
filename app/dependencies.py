# app/dependencies.py
from .services.player import Player
from .services.testDriveDataService import TestDriveDataService
from .services.websocketConnectionManager import WebsocketConnectionManager

connection_manager_instance = WebsocketConnectionManager()
player_instance = Player(connection_manager_instance)
testdata_manager = TestDriveDataService()


def get_player():
    return player_instance


def get_connection_manager():
    return connection_manager_instance


def get_testdata_manager():
    return testdata_manager
