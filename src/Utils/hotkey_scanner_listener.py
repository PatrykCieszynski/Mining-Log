# python
import threading
import time
import keyboard

from typing import Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal

from src.Models.deed_model import DeedModel
from src.Scanner.ocr_controller import extract_deed_from_window
from src.Scanner.ocr_core import DEFAULT_INNER


class HotkeyScannerListener(QObject):
    deed_found = pyqtSignal(DeedModel)

    def __init__(
        self,
        offset_x: int = 0,
        offset_y: int = 0,
        inner_rect: Optional[Tuple[int, int, int, int]] = None,
        debug: bool = False,
        save_dir: Optional[str] = None,
        hotkey: str = "f8",
        cooldown_sec: float = 0.5,
    ) -> None:
        super().__init__()
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.inner_rect = inner_rect or (
            DEFAULT_INNER["x"],
            DEFAULT_INNER["y"],
            DEFAULT_INNER["w"],
            DEFAULT_INNER["h"],
        )
        self.debug = debug
        self.save_dir = save_dir
        self.hotkey = hotkey
        self.cooldown_sec = cooldown_sec
        self._thread: Optional[threading.Thread] = None
        self._stop: threading.Event = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._worker, name="HotkeyScannerListener", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _worker(self) -> None:
        print(
            f"[scanner] Naciśnij {self.hotkey.upper()} aby zeskanować (cooldown {self.cooldown_sec}s)."
        )
        last_ts = 0.0
        while not self._stop.is_set():
            try:
                if keyboard.is_pressed(self.hotkey):
                    now = time.time()
                    if now - last_ts >= self.cooldown_sec:
                        try:
                            deed: DeedModel = extract_deed_from_window(
                                offset_x=self.offset_x,
                                offset_y=self.offset_y,
                                inner_rect=self.inner_rect,
                                debug=self.debug,
                                save_dir=self.save_dir,
                            )
                            try:
                                self.deed_found.emit(deed)
                            except Exception as e:
                                print(f"[scanner] Błąd emisji sygnału: {e}")
                        except Exception as e:
                            print(f"[scanner] Błąd skanowania: {e}")
                        last_ts = now
                    time.sleep(0.05)
                else:
                    time.sleep(0.01)
            except KeyboardInterrupt:
                print("[scanner] przerwano")
                break
            except Exception as e:
                print(f"[scanner] nieoczekiwany błąd pętli: {e}")
                time.sleep(0.5)