# python
import glob
import os
from typing import Optional, Tuple, Any

from PIL import Image
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
)

from src.Map.map_deed_controller import DeedMarkerController
from src.Map.map_view import MapView
from src.Utils.hotkey_scanner_listener import HotkeyScannerListener

TILE_SIZE = 512  # Tile size is always 512 px


class MapWindow(QMainWindow):
    def __init__(self, config: Any, scanner: Optional[HotkeyScannerListener] = None):
        super().__init__()
        self.config = config
        self.setWindowTitle("Interactive Map")
        self.setGeometry(100, 100, 800, 600)

        # Always on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # Scene and view
        self.scene = QGraphicsScene()
        self.view = MapView(self.scene, self, config)
        self.view.setGeometry(0, 0, 800, 600)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setCentralWidget(self.view)

        # Background color
        self.scene.setBackgroundBrush(QColor("#1a2f44"))

        # Load map tiles
        self.load_map_tiles(config["tile_folder"])

        # Player position
        self.player_radius_coord = 55
        self.player_border_width = 0.1
        self.player_position = QGraphicsEllipseItem(0, 0, 0, 0)
        self.player_position.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.player_position.setPen(QPen(QColor("red"), self.player_border_width))
        self.scene.addItem(self.player_position)

        # Zoom/drag
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.zoom_factor = 1.15

        # Hide scroll bars
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Connect deed markers controller
        self.deed_marker_controller = DeedMarkerController(
            self.scene, self._lonlat_to_scene, scanner=scanner
        )

        # Timer to refresh deed markers
        self.deeds_timer = QTimer(self)
        self.deeds_timer.timeout.connect(self.deed_marker_controller.tick_deeds)
        self.deeds_timer.start(1000)  # run every 1s

    def load_map_tiles(self, tile_folder: Any) -> None:
        total_w = self.config["tile_count_x"] * TILE_SIZE
        total_h = self.config["tile_count_y"] * TILE_SIZE
        added = 0

        for y in range(self.config["tile_count_y"]):
            for x in range(self.config["tile_count_x"]):
                tile_index = y * self.config["tile_count_x"] + x
                tile_pattern = os.path.join(tile_folder, f"map_*_{tile_index}.dds")
                tile_files = glob.glob(tile_pattern)

                if not tile_files:
                    print(f"File does not exist: {tile_pattern}")
                    continue

                tile_path = tile_files[0]
                try:
                    img = Image.open(tile_path).convert("RGBA")
                    data = img.tobytes("raw", "RGBA")
                    bytes_per_line = img.width * 4

                    qt_image = QImage(
                        data,
                        img.width,
                        img.height,
                        bytes_per_line,
                        QImage.Format.Format_RGBA8888,
                    ).copy()

                    tile_x = x * TILE_SIZE
                    tile_y = y * TILE_SIZE

                    tile_item = QGraphicsPixmapItem(QPixmap.fromImage(qt_image))
                    tile_item.setPos(tile_x, tile_y)
                    tile_item.setTransformationMode(
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.scene.addItem(tile_item)
                    added += 1
                except Exception as e:
                    print(f"Failed to load file {tile_path}: {e}")

        # Scene rect
        self.scene.setSceneRect(0, 0, total_w, total_h)

        if added == 0:
            print(
                "Uwaga: nie dodano żadnych kafli. Sprawdź ścieżkę tile_folder oraz obsługę DDS."
            )

    def coord_to_pixel_radius(self, radius_coord: Any) -> float:
        map_width = self.config["tile_count_x"] * TILE_SIZE
        lon_range = self.config["max_lon"] - self.config["min_lon"]
        if lon_range == 0:
            print("Error: Longitude range is zero.")
            return 0
        return float ((radius_coord / lon_range) * map_width)

    def _lonlat_to_scene(self, lon: float, lat: float) -> Tuple[float, float]:
        map_width = self.config["tile_count_x"] * TILE_SIZE
        map_height = self.config["tile_count_y"] * TILE_SIZE
        x = (
            (lon - self.config["min_lon"])
            / (self.config["max_lon"] - self.config["min_lon"])
        ) * map_width
        y = (
            map_height
            - (
                (lat - self.config["min_lat"])
                / (self.config["max_lat"] - self.config["min_lat"])
            )
            * map_height
        )
        return x, y

    def update_player_position(self, lon, lat):
        print("player pos")