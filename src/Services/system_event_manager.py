import time
from PyQt6.QtCore import QObject
from src.App.signal_bus import SignalBus

class SystemEventManager(QObject):
    """Filter raw system messages and emit high-level events."""

    def __init__(self, bus: SignalBus) -> None:
        super().__init__()
        self.bus = bus
        self.bus.system_event.connect(self._on_system)

    def _on_system(self, text: str) -> None:
        if "resource is depleted" in text.lower():
                self.bus.resource_depleted.emit(text)
