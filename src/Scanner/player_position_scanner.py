# python
"""
Player position scanner:
- okresowo przechwytuje mały obszar w prawym-dolnym rogu klienta okna gry (kompas)
- uruchamia preprocess + OCR (pytesseract pipeline z ocr_core) i próbuje sparsować lon, lat
- wywołuje callback(on_position) z argumentami (lon: int, lat: int) gdy odczyt się powiedzie

Wymagania:
- mss, numpy, OpenCV, pytesseract (tak jak w projekcie)
- działa w tle jako wątek daemon
"""

import re
import threading
import time
from typing import Callable, Optional, Tuple

import mss
import numpy as np
import win32gui

from src.Scanner.ocr_core import ocr_text_block, preprocess_coords

# Domyślne rozmiary regionu kompasu (dostosuj do UI gry)
DEFAULT_COMPASS_W = 30
DEFAULT_COMPASS_H = 30

# Przykładowy regex dopasowujący "12345, 67890" lub "12345 67890" lub "12345,67890"
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
    """
    Wylicza prostokąt w ekranowych współrzędnych odpowiadający obszarowi kompasu
    przystawionemu do prawego-dolnego rogu klienta okna (z małym paddingiem).
    - pad_right/pad_bottom: odległość od prawego/bottom krawędzi klienta
    """
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    client_w = right - left
    client_h = bottom - top
    screen_x, screen_y = win32gui.ClientToScreen(hwnd, (0, 0))

    # prawy dolny róg klienta w screen coords:
    screen_right = screen_x + client_w
    screen_bottom = screen_y + client_h

    mon_left = max(0, screen_right - pad_right - w)
    mon_top = max(0, screen_bottom - pad_bottom - h)

    return {"left": mon_left, "top": mon_top, "width": w, "height": h}


class PlayerScanner(threading.Thread):
    """
    Wątek skanujący pozycję gracza.
    - on_position: Callable[[int, int], None] wywoływany gdy odczytane lon/lat są poprawne.
    - title_substr: fragment tytułu okna gry (np. "Entropia Universe")
    - poll_interval: czas pomiędzy skanami w sekundach
    """

    def __init__(
        self,
        on_position: Callable[[int, int], None],
        title_substr: str = "Entropia Universe",
        compass_size: Tuple[int, int] = (DEFAULT_COMPASS_W, DEFAULT_COMPASS_H),
        poll_interval: float = 1.0,
    ):
        super().__init__(daemon=True)
        self.on_position = on_position
        self.title_substr = title_substr
        self.compass_w, self.compass_h = compass_size
        self.poll_interval = poll_interval
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
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

                    # Wycinamy tylko fragment z lon/lat
                    x, y, w, h = 55, 372, 110, 47
                    roi = img[y : y + h, x : x + w]

                    # Preprocess i OCR tylko na ROI
                    gray = preprocess_coords(roi)
                    text = ocr_text_block(gray)

                    m = _RE_LONLAT.search(text)
                    if m:
                        try:
                            lon = int(m.group(1))
                            lat = int(m.group(2))
                            try:
                                self.on_position(lon, lat)
                            except Exception:
                                pass
                        except ValueError:
                            pass

                except Exception:
                    pass

                time.sleep(self.poll_interval)
