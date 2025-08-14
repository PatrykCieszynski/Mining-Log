# python
import json
import sys

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication
from src.Map.map_window import MapWindow
from src.Scanner.player_position_scanner import PlayerScanner
from src.Utils.hotkey_scanner_listener import HotkeyScannerListener

with open('config/planet_data.json', 'r') as f:
    planet_configs = json.load(f)

class ScanBus(QObject):
    deed_scanned = pyqtSignal(dict)

def main():
    selected_planet = "Rocktropia"
    config = planet_configs[selected_planet]

    app = QApplication(sys.argv)
    window = MapWindow(config)
    window.show()

    bus = ScanBus()

    def handle_deed(res: dict):
        # oczekujemy pól x, y (lon/lat) oraz ttl_sec/time_left z OCR
        lon = res.get("x")
        lat = res.get("y")
        ttl = 5000
        label = None
        if isinstance(lon, int) and isinstance(lat, int):
            window.add_or_update_deed_marker(lon, lat, ttl, label)
        else:
            print("[scanner] Brak poprawnych koordynatów w wyniku:", res)

    # Przekazujemy obsługę pozycji gracza do MapWindow
    player_scanner = PlayerScanner(
        on_position=window.update_player_position,
        title_substr="Entropia Universe",
        compass_size=(370, 430),
        poll_interval=0.8
    )
    player_scanner.start()

    bus.deed_scanned.connect(handle_deed)
    def on_result(res: dict):
        bus.deed_scanned.emit(res)

    # Przekazujemy obsługę skanowania claima do MapWindow
    hotkey_scanner = HotkeyScannerListener(
        offset_x=0,
        offset_y=0,
        inner_rect=None,
        debug=False,
        save_dir=None,
        on_result=on_result,
        hotkey="f8",
        cooldown_sec=0.5,
    )

    sys.exit(app.exec())

if __name__ == "__main__":
    main()