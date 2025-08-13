# python
import time
import threading
import json
from typing import Callable, Optional, Tuple

import keyboard
from src.Scanner.ocr_core import DEFAULT_INNER
from src.Scanner.ocr_controller import extract_deed_from_window

class HotkeyScannerListener:
    def __init__(
        self,
        offset_x: int = 0,
        offset_y: int = 0,
        inner_rect: Optional[Tuple[int, int, int, int]] = None,
        debug: bool = False,
        save_dir: Optional[str] = None,
        on_result: Optional[Callable[[dict], None]] = None,
        hotkey: str = "f8",
        cooldown_sec: float = 0.5,
    ):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.inner_rect = inner_rect or (
            DEFAULT_INNER["x"], DEFAULT_INNER["y"], DEFAULT_INNER["w"], DEFAULT_INNER["h"]
        )
        self.debug = debug
        self.save_dir = save_dir
        self.on_result = on_result
        self.hotkey = hotkey
        self.cooldown_sec = cooldown_sec
        self._thread = None
        self._stop = threading.Event()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._worker, name="HotkeyScannerListener", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _worker(self):
        print(f"[scanner] Naciśnij {self.hotkey.upper()} aby zeskanować (cooldown {self.cooldown_sec}s).")
        last_ts = 0.0
        while not self._stop.is_set():
            try:
                if keyboard.is_pressed(self.hotkey):
                    now = time.time()
                    if now - last_ts >= self.cooldown_sec:
                        try:
                            result = extract_deed_from_window(
                                offset_x=self.offset_x,
                                offset_y=self.offset_y,
                                inner_rect=self.inner_rect,
                                debug=self.debug,
                                save_dir=self.save_dir,
                            )
                            if self.on_result:
                                self.on_result(result)
                            else:
                                print(json.dumps(result, ensure_ascii=False))
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