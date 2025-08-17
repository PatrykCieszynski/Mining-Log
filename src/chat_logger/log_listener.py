import re
import threading
import time
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal

from src.app.signal_bus import SignalBus


class ChatLogListener(QObject):

    _channel_regex = re.compile(
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \[(?P<channel>\S+)\] .+$"
    )

    def __init__(self, bus: SignalBus, chat_log_path: str, poll_interval: float = 0.1) -> None:
        super().__init__()
        self.bus = bus
        self.chat_log_path = chat_log_path
        self.poll_interval = poll_interval
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._worker, name="ChatLogListener", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _emit_by_channel(self, channel: str, line: str) -> None:
        """Emit signal depending on channel."""
        if channel.lower() == "system":
            self.system_event.emit(line)
        elif channel.lower() == "globals":
            self.globals_event.emit(line)
        else:
            self.other_event.emit(line)

    def _worker(self) -> None:
        try:
            with open(self.chat_log_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(0, 2)  # jump to end of file
                while not self._stop_event.is_set():
                    line = f.readline()
                    if not line:
                        time.sleep(self.poll_interval)
                        continue

                    m = self._channel_regex.search(line)
                    if m:
                        self._emit_by_channel(m.group("channel"), line.strip())
        except Exception as e:
            print(f"[ChatLogListener] Error: {e}")
