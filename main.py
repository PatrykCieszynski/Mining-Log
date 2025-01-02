import cv2
import json
import sys
import threading

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication

from Modules.Map.map_window import MapWindow
from Modules.Capture.capture_screen import get_game_window, capture_screen
from Modules.OCR.ocr import detect_coords_from_radar, extract_lon_lat, detect_radar_from_game

# Load planet configurations from JSON file
with open('planet_data.json', 'r') as f:
    planet_configs = json.load(f)


class OCRWorker(QObject):
    position_updated = pyqtSignal(int, int)

    def __init__(self, game_window, coords_top_left, coords_bottom_right):
        super().__init__()
        self.game_window = game_window
        self.coords_top_left = coords_top_left
        self.coords_bottom_right = coords_bottom_right

    def run(self):
        while True:
            capture = capture_screen(self.game_window)
            lon, lat = extract_lon_lat(capture, self.coords_top_left, self.coords_bottom_right, debug=True)
            if lon is not None and lat is not None:
                self.position_updated.emit(lon, lat)


def main():
    window_name = "Entropia Universe Client"
    radar_template_path = "Assets/radar_template.png"
    coords_template_path = "Assets/coords_template.png"

    selected_planet = "Arkadia"  # Change this to select a different planet
    config = planet_configs[selected_planet]

    app = QApplication(sys.argv)
    window = MapWindow(config)
    window.show()

    game_window = get_game_window(window_name)
    if not game_window:
        print("Game window not found. Retrying...")

    capture = capture_screen(game_window)

    try:
        radar_top_left, radar_bottom_right, scale = detect_radar_from_game(capture, radar_template_path)

        coords_top_left, coords_bottom_right = detect_coords_from_radar(capture, coords_template_path, radar_top_left, radar_bottom_right, scale, True)
        print(f"Współrzędne znalezione: {coords_top_left}, {coords_bottom_right}")

        coords_top_left = (coords_top_left[0] + radar_top_left[0], coords_top_left[1] + radar_top_left[1])
        coords_bottom_right = (coords_bottom_right[0] + radar_top_left[0], coords_bottom_right[1] + radar_top_left[1])

        worker = OCRWorker(game_window, coords_top_left, coords_bottom_right)
        worker.position_updated.connect(window.update_player_position)
        thread = threading.Thread(target=worker.run)
        thread.start()

        sys.exit(app.exec_())

    except Exception as e:
        print(f"Błąd: {e}")


if __name__ == "__main__":
    main()