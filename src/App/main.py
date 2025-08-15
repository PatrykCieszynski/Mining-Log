# python
import json
import sys

from PyQt6.QtWidgets import QApplication

from src.App.app_context import create_app_context
from src.Map.map_window import MapWindow

with open("config/planet_data.json", "r") as f:
    planet_configs = json.load(f)


def main() -> None:
    selected_planet = "Rocktropia"
    config = planet_configs[selected_planet]

    ctx = create_app_context(config)

    app = QApplication(sys.argv)

    # Creating a listener for logging chat messages
    # system_manager = SystemEventsManager(chat_listener)

    window = MapWindow(ctx)
    ctx.start_all()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
