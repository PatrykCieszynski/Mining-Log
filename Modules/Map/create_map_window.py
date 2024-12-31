from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor
from PyQt5.QtCore import Qt
from PIL import Image
import os
import glob

from Modules.Map.MapView import MapView

TILE_SIZE = 512  # Tile size is always 512 px

class MapWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("Mapa Interaktywna")
        self.setGeometry(100, 100, 800, 600)

        # Scena i widok
        self.scene = QGraphicsScene()
        self.view = MapView(self.scene, self, config)
        self.view.setGeometry(0, 0, 800, 600)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self.view)

        # Ładowanie mapy z plików .dds
        self.load_map_tiles(config["tile_folder"])

        # Ustawienie koloru tła
        self.scene.setBackgroundBrush(QColor("#1a2f44"))

        # Pozycja gracza
        self.player_position = QGraphicsEllipseItem(0, 0, 1, 1)
        self.player_position.setBrush(Qt.red)
        self.scene.addItem(self.player_position)

        # Zoom
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.zoom_factor = 1.15

        # Ukrycie pasków przewijania
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def load_map_tiles(self, tile_folder):
        for y in range(self.config["tile_count_y"]):
            for x in range(self.config["tile_count_x"]):
                tile_index = y * self.config['tile_count_x'] + x
                tile_pattern = os.path.join(tile_folder, f"map_*_{tile_index}.dds")
                tile_files = glob.glob(tile_pattern)

                if tile_files:
                    tile_path = tile_files[0]  # Use the first match
                    try:
                        image = Image.open(tile_path)

                        data = image.tobytes()
                        qt_image = QImage(data, image.width, image.height, QImage.Format_RGBA8888)

                        tile_x = x * TILE_SIZE
                        tile_y = y * TILE_SIZE

                        tile_item = QGraphicsPixmapItem(QPixmap.fromImage(qt_image))
                        tile_item.setPos(tile_x, tile_y)

                        # Ustawienie interpolacji podczas rysowania na scenie
                        tile_item.setTransformationMode(Qt.SmoothTransformation)

                        self.scene.addItem(tile_item)
                    except Exception as e:
                        print(f"Nie udało się załadować pliku {tile_path}: {e}")
                else:
                    print(f"Plik nie istnieje: {tile_pattern}")

    def update_player_position(self, lon, lat):
        # Skalowanie współrzędnych na piksele mapy
        map_width = self.config["tile_count_x"] * TILE_SIZE
        map_height = self.config["tile_count_y"] * TILE_SIZE

        lon_range = self.config["max_lon"] - self.config["min_lon"]
        lat_range = self.config["max_lat"] - self.config["min_lat"]

        if lon_range == 0 or lat_range == 0:
            print("Error: Longitude or latitude range is zero.")
            return

        x = ((lon - self.config["min_lon"]) / (self.config["max_lon"] - self.config["min_lon"])) * map_width
        y = map_height - ((lat - self.config["min_lat"]) / (self.config["max_lat"] - self.config["min_lat"])) * map_height  # Odwrócenie osi Y

        # Ustawienie pozycji punktu gracza
        self.player_position.setPos(x, y)