# python
import json
import sys

from PyQt6.QtWidgets import QApplication

from src.ChatLogger.SystemEventsManager.system_event_manager import SystemEventsManager
from src.ChatLogger.log_listener import ChatLogListener
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

    # Creating a player scanner to track player position
    player_scanner = PlayerScanner(
        title_substr="Entropia Universe",
        compass_size=(370, 430),
        poll_interval=0.1,
    )

    # Creating a listener for logging chat messages
    # chat_listener = ChatLogListener(r"X:\Dokumenty\Entropia Universe\chat.log")
    # system_manager = SystemEventsManager(chat_listener)

    window = MapWindow(config, deed_scanner=hotkey_scanner, player_scanner=player_scanner)
    hotkey_scanner.start()
    player_scanner.start()
    # chat_listener.start()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
