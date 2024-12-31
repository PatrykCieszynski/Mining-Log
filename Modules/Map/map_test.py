import json
import sys

from PyQt5.QtWidgets import QApplication

from Modules.Map.create_map_window import MapWindow

# Load planet configurations from JSON file
with open('PlanetData.json', 'r') as f:
    planet_configs = json.load(f)

# Uruchomienie aplikacji
if __name__ == "__main__":
    selected_planet = "Calypso"  # Change this to select a different planet
    config = planet_configs[selected_planet]

    app = QApplication(sys.argv)
    window = MapWindow(config)
    window.show()

    # Przykładowa pozycja gracza
    window.update_player_position(78049, 96387)
    sys.exit(app.exec_())