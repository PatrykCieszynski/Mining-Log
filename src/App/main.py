# python
import json
import sys

from PyQt6.QtWidgets import QApplication

from src.App.app_context import create_app_context
from src.Map.map_window import MapWindow


def main() -> None:
    ctx = create_app_context("config/default.yaml")

    app = QApplication(sys.argv)

    window = MapWindow(ctx)
    ctx.start_all()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
