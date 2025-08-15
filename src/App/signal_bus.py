from PyQt6.QtCore import QObject, pyqtSignal
from src.Models.deed_model import DeedModel

class SignalBus(QObject):
    # Chat / System
    system_event = pyqtSignal(str)           # raw system line
    globals_event = pyqtSignal(str)  # whole message from [Globals]
    other_event = pyqtSignal(str)    # other channels
    resource_depleted = pyqtSignal(str)      # filtered system event

    # Scanners / OCR
    deed_found = pyqtSignal(DeedModel)       # new deed extracted
    player_position_found = pyqtSignal(float, float)
    player_moved = pyqtSignal(float, float)  # lon, lat
