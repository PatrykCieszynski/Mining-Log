import re
import threading
import time
from typing import Callable, Optional, Tuple

import mss
import numpy as np
import win32gui
from PyQt6.QtCore import QObject, pyqtSignal

from src.Scanner.ocr_core import ocr_text_block, preprocess_coords

DEFAULT_COMPASS_W = 30
DEFAULT_COMPASS_H = 30

_RE_LONLAT = re.compile(r"Lon:\s*(\d{1,6})\s*[\r\n]+Lat:\s*(\d{1,6})", re.IGNORECASE)


def _find_game_hwnd(title_substr: str) -> Optional[int]:
    hwnd = None
    def enum_cb(h, _):
        nonlocal hwnd
        try:
            title = win32gui.GetWindowText(h)
            if title_substr.lower() in title.lower() and win32gui.IsWindowVisible(h):
                hwnd = h
        except Exception:
            pass
    win32gui.EnumWindows(enum_cb, None)
    return hwnd


def _build_compass_region(
    hwnd: int, w: int, h: int, pad_right: int = 8, pad_bottom: int = 10
) -> dict:
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    client_w = right - left
    client_h = bottom - top
    screen_x, screen_y = win32gui.ClientToScreen(hwnd, (0, 0))
    screen_right = screen_x + client_w
    screen_bottom = screen_y + client_h
    mon_left = max(0, screen_right - pad_right - w)
    mon_top = max(0, screen_bottom - pad_bottom - h)
    return {"left": mon_left, "top": mon_top, "width": w, "height": h}


class PlayerScanner(QObject):
    position_found = pyqtSignal(int, int)  # lon, lat

    def __init__(
        self,
        title_substr: str = "Entropia Universe",
        compass_size: Tuple[int, int] = (DEFAULT_COMPASS_W, DEFAULT_COMPASS_H),
        poll_interval: float = 1.0,
    ) -> None:
        super().__init__()
        self.title_substr = title_substr
        self.compass_w, self.compass_h = compass_size
        self.poll_interval = poll_interval
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._worker, name="PlayerScanner", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _worker(self) -> None:
        with mss.mss() as sct:
            while not self._stop.is_set():
                try:
                    hwnd = _find_game_hwnd(self.title_substr)
                    if not hwnd:
                        time.sleep(self.poll_interval)
                        continue

                    region = _build_compass_region(hwnd, self.compass_w, self.compass_h)
                    shot = sct.grab(region)
                    img = np.array(shot)[:, :, :3]

                    # crop coords area
                    x, y, w, h = 55, 372, 110, 47
                    roi = img[y:y + h, x:x + w]

                    gray = preprocess_coords(roi)
                    text = ocr_text_block(gray)

                    m = _RE_LONLAT.search(text)
                    if m:
                        try:
                            lon = int(m.group(1))
                            lat = int(m.group(2))
                            self.position_found.emit(lon, lat)
                        except ValueError:
                            pass
                except Exception:
                    pass

                time.sleep(self.poll_interval)
