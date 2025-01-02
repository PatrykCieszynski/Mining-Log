from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor, QPen, QBrush
from PyQt5.QtCore import Qt
from PIL import Image
import os
import glob

from src.Modules.Map.map_view import MapView

TILE_SIZE = 512  # Tile size is always 512 px

class MapWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("Interactive Map")
        self.setGeometry(100, 100, 800, 600)

        # Set window flags to keep the window always on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Scene and view
        self.scene = QGraphicsScene()
        self.view = MapView(self.scene, self, config)
        self.view.setGeometry(0, 0, 800, 600)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self.view)

        # Load map tiles
        self.load_map_tiles(config["tile_folder"])

        # Set background color
        self.scene.setBackgroundBrush(QColor("#1a2f44"))

        # Player position
        self.player_radius_coord = 55  # Adjustable radius in coordinates
        self.player_border_width = 0.1  # Adjustable border width
        self.player_position = QGraphicsEllipseItem(0, 0, 0, 0)
        self.player_position.setBrush(QBrush(Qt.NoBrush))  # Empty inside
        self.player_position.setPen(QPen(Qt.red, self.player_border_width))  # Red border with specified width
        self.scene.addItem(self.player_position)

        # Zoom
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.zoom_factor = 1.15

        # Hide scroll bars
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

                        # Set interpolation mode when drawing on the scene
                        tile_item.setTransformationMode(Qt.SmoothTransformation)

                        self.scene.addItem(tile_item)
                    except Exception as e:
                        print(f"Failed to load file {tile_path}: {e}")
                else:
                    print(f"File does not exist: {tile_pattern}")

    def coord_to_pixel_radius(self, radius_coord):
        map_width = self.config["tile_count_x"] * TILE_SIZE
        lon_range = self.config["max_lon"] - self.config["min_lon"]
        if lon_range == 0:
            print("Error: Longitude range is zero.")
            return 0
        return (radius_coord / lon_range) * map_width

    def update_player_position(self, lon, lat):
        # Scale coordinates to map pixels
        map_width = self.config["tile_count_x"] * TILE_SIZE
        map_height = self.config["tile_count_y"] * TILE_SIZE

        lon_range = self.config["max_lon"] - self.config["min_lon"]
        lat_range = self.config["max_lat"] - self.config["min_lat"]

        if lon_range == 0 or lat_range == 0:
            print("Error: Longitude or latitude range is zero.")
            return

        x = ((lon - self.config["min_lon"]) / (self.config["max_lon"] - self.config["min_lon"])) * map_width
        y = map_height - ((lat - self.config["min_lat"]) / (self.config["max_lat"] - self.config["min_lat"])) * map_height  # Invert Y axis

        # Convert radius from coordinates to pixels
        self.player_radius = self.coord_to_pixel_radius(self.player_radius_coord)

        # Set player position
        self.player_position.setRect(x - self.player_radius, y - self.player_radius, self.player_radius * 2, self.player_radius * 2)