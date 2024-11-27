# app/dependencies.py
from .services.player import Player
from .services.websocketConnectionManager import ConnectionManager

connection_manager_instance = ConnectionManager()
player_instance = Player(connection_manager_instance)

def get_player():
    return player_instance

def get_connection_manager():
    return connection_manager_instance