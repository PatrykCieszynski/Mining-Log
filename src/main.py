# python
import json
import sys

from PyQt6.QtWidgets import QApplication

from src.Map.map_window import MapWindow
from src.Scanner.player_position_scanner import PlayerScanner
from src.Utils.hotkey_scanner_listener import HotkeyScannerListener

with open("config/planet_data.json", "r") as f:
    planet_configs = json.load(f)


def main() -> None:
    selected_planet = "Rocktropia"
    config = planet_configs[selected_planet]

    app = QApplication(sys.argv)

    # Creating a listener for scanning by hotkey
    hotkey_scanner: HotkeyScannerListener = HotkeyScannerListener(
        offset_x=0,
        offset_y=0,
        inner_rect=None,
        debug=False,
        save_dir=None,
        hotkey="f8",
        cooldown_sec=0.5,
    )

    window = MapWindow(config, scanner=hotkey_scanner)
    hotkey_scanner.start()

    window.show()

    # Przekazujemy obsługę pozycji gracza do MapWindow
    player_scanner = PlayerScanner(
        on_position=window.update_player_position,
        title_substr="Entropia Universe",
        compass_size=(370, 430),
        poll_interval=0.8,
    )
    player_scanner.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
