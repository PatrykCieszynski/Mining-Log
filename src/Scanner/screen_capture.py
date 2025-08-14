# python
from typing import Dict, Optional, Any

import mss
import numpy as np
import win32gui

WINDOW_TITLE_SUBSTR = "Entropia Universe Client"
CROP_W, CROP_H = 445, 445  # rozmiar wycinka z lewego-górnego rogu okna gry


def _find_game_hwnd() -> Optional[int]:
    hwnd = None

    def enum_cb(h: Any, _: Any) -> Any:
        nonlocal hwnd
        title = win32gui.GetWindowText(h)
        if WINDOW_TITLE_SUBSTR.lower() in title.lower() and win32gui.IsWindowVisible(h):
            hwnd = h

    win32gui.EnumWindows(enum_cb, None)
    return hwnd


def build_capture_region(hwnd: int, offset_x: int, offset_y: int) -> Dict[str, int]:
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    screen_x, screen_y = win32gui.ClientToScreen(hwnd, (0, 0))
    return {
        "left": screen_x + offset_x,
        "top": screen_y + offset_y,
        "width": min(CROP_W, max(0, right - offset_x)),
        "height": min(CROP_H, max(0, bottom - offset_y)),
    }


def capture_corner_crop(offset_x: int, offset_y: int) -> np.ndarray[Any, Any]:
    """
    Zwraca obraz BGR (CROP_W x CROP_H) z lewego górnego rogu klienta okna gry.
    """
    hwnd = _find_game_hwnd()
    if not hwnd:
        raise RuntimeError(
            "Nie znaleziono okna gry (upewnij się, że jest uruchomione i widoczne)."
        )

    region = build_capture_region(hwnd, offset_x, offset_y)
    with mss.mss() as sct:
        shot = sct.grab(region)
        # BGRA -> BGR
        return np.array(shot)[:, :, :3]
