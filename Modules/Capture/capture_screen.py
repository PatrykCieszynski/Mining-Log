import pygetwindow as gw
import numpy as np
from mss import mss
import cv2

def get_game_window(window_name):
    windows = gw.getWindowsWithTitle(window_name)
    if windows:
        win = windows[0]
        return {
            "left": win.left,
            "top": win.top,
            "width": win.width,
            "height": win.height
        }
    return None

def capture_screen(game_window):
    with mss() as sct:
        monitor = {
            "left": game_window["left"],
            "top": game_window["top"],
            "width": game_window["width"],
            "height": game_window["height"]
        }
        screen = np.array(sct.grab(monitor))
        return cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)