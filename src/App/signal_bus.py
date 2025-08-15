from PyQt6.QtCore import QObject, pyqtSignal, QRectF, QPointF
from src.Models.deed_model import DeedModel

class SignalBus(QObject):
    # Chat / System
    system_event = pyqtSignal(str)           # raw system line
    globals_event = pyqtSignal(str)  # whole message from [Globals]
    other_event = pyqtSignal(str)    # other channels
    resource_depleted = pyqtSignal(str)      # filtered system event

    # Scanners / OCR
    deed_found = pyqtSignal(DeedModel)       # new deed extracted
    player_position_parsed = pyqtSignal(int, int)
    player_position_changed = pyqtSignal(QPointF, QRectF)

    # Deed
    deed_marker_added = pyqtSignal(str, float, float, float, object)   # id, x, y, radius, deed
    deed_marker_updated = pyqtSignal(str, float, float, float, object) # id, x, y, radius, deed
    deed_marker_removed = pyqtSignal(str)                                   # id
    deed_marker_tick    = pyqtSignal(str, int)    # id, ttl_sec