from PyQt6.QtCore import QObject, pyqtSignal

from src.ChatLogger.log_listener import ChatLogListener


class SystemEventsManager(QObject):
    resource_depleted = pyqtSignal(str)

    def __init__(self, listener: ChatLogListener):
        super().__init__()
        listener.system_event.connect(self._on_system_event)

    def _on_system_event(self, message: str) -> None:
        if "resource is depleted" in message.lower():
            self.resource_depleted.emit(message)
