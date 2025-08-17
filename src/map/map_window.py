# python
import glob
import os
from typing import Any

from PIL import Image
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QRect
from PyQt6.QtGui import QBrush, QColor, QImage, QPainter, QPen, QPixmap, QFont
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow, QGraphicsTextItem,
)

from src.app.app_context import AppContext
from src.map.map_utils import get_planet_config
from src.map.map_view import MapView
from src.models.deed_model import DeedModel


class MapWindow(QMainWindow):
    def __init__(self, ctx: AppContext):
        super().__init__()
        self.map_height = None
        self.map_width = None
        self.ctx = ctx
        self.config = ctx.config
        self.bus = ctx.bus

        self.tile_size = self.config["map"]["tile_size"]
        self.setWindowTitle(self.config["map"]["window_title"])
        self.setGeometry(QRect(*self.config["map"]["window_geometry"]))
        self.planet_config = get_planet_config(self.config)

        # Always on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # Scene and view
        self.scene = QGraphicsScene()
        self.view = MapView(self.scene, self.config)
        self.view.setGeometry(QRect(*self.config["map"]["window_geometry"]))
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setCentralWidget(self.view)

        # Background color
        self.scene.setBackgroundBrush(QColor("#1a2f44"))

        # Load map tiles
        self.load_map_tiles(self.planet_config["tile_folder"])

        # Player position
        self.player_pos = QPointF(0, 0)
        self.player_radius_coord = self.config["player"]["radius_coord"]
        self.player_border_width = self.config["player"]["border_width"]
        self.player_rect = QGraphicsEllipseItem(0, 0, 0, 0)
        self.player_rect.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.player_rect.setPen(QPen(QColor("red"), self.player_border_width))
        self.scene.addItem(self.player_rect)
        self.bus.player_position_changed.connect(self._on_player_position_changed)

        # Zoom/drag
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.zoom_factor = self.config["map"]["zoom_factor"]

        # Hide scroll bars
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Marker data
        self.ui_markers = {}
        self.bus.deed_marker_added.connect(self._on_deed_marker_added)
        self.bus.deed_marker_updated.connect(self._on_deed_marker_updated)
        self.bus.deed_marker_removed.connect(self._on_deed_marker_removed)
        self.bus.deed_marker_tick.connect(self._on_deed_marker_tick)

        #Resource Claimed
        self.bus.resource_claimed.connect(self._on_resource_claimed)

    def load_map_tiles(self, tile_folder: Any) -> None:
        total_w = self.planet_config["tile_count_x"] * self.tile_size
        total_h = self.planet_config["tile_count_y"] * self.tile_size
        added = 0

        for y in range(self.planet_config["tile_count_y"]):
            for x in range(self.planet_config["tile_count_x"]):
                tile_index = y * self.planet_config["tile_count_x"] + x
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

                    tile_x = x * self.tile_size
                    tile_y = y * self.tile_size

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

        # ⬇️ zapamiętaj rozmiar sceny/mapy (użyjemy do QImage)
        self.map_width = int(total_w)
        self.map_height = int(total_h)

        if added == 0:
            print(
                "Uwaga: nie dodano żadnych kafli. Sprawdź ścieżkę tile_folder oraz obsługę DDS."
            )

    def _on_player_position_changed(self, position: QPointF, rect: QRectF) -> None:
        self.player_pos = position
        self.player_rect.setRect(rect)
        self.center_map_on_player(position)

        # ⬇️ coverage
        self._ensure_coverage_layer()
        if getattr(self, "_cov_img", None) is None:
            return

        x, y = position.x(), position.y()

        # promień pędzla: weź z configu, a jak brak – z rozmiaru 'rect' gracza
        r = getattr(self, "_brush_radius_px", 5)
        if r <= 0:
            r = int(max(rect.width(), rect.height()) * 0.5) or 10

        # clipping (nie rysuj poza obraz)
        if not (0 <= x < self._cov_img.width() and 0 <= y < self._cov_img.height()):
            return

        # Rysowanie do bufora (szybko + bez tworzenia nowych itemów)
        p = QPainter(self._cov_img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._brush_color)
        p.drawEllipse(position, 4, 4)  # QPointF w scenie == piksele obrazu maski
        p.end()

        # Zaktualizuj pikselmapę (możesz też zoptymalizować podając brudny rect)
        self._cov_item.setPixmap(QPixmap.fromImage(self._cov_img))

    def center_map_on_player(self, position: QPointF) -> None:
        self.view.centerOn(position)

    def _on_deed_marker_added(self, marker_id: str, x: float, y: float, radius_px: float, deed: DeedModel):
        dot = QGraphicsEllipseItem(
            x - radius_px, y - radius_px, radius_px * 2, radius_px * 2
        )
        dot.setBrush(QBrush(QColor("#00ff99")))
        dot.setPen(QPen(Qt.PenStyle.NoPen))  # brak obramowania
        self.scene.addItem(dot)

        # deed time
        print("Deed time left ", deed.time_left)
        text_item = QGraphicsTextItem(deed.time_left)
        text_item.setDefaultTextColor(QColor("white"))
        font = QFont()
        font.setPointSize(9)
        text_item.setFont(font)
        text_item.setFlag(
            text_item.GraphicsItemFlag.ItemIgnoresTransformations, True
        )
        text_item.setZValue(11)
        text_item.setPos(x, y)
        self.scene.addItem(text_item)

        # Zapisujemy w lokalnej mapie, żeby potem móc odwołać się po marker_id
        self.ui_markers[marker_id] = {
            "dot": dot,
            "text": text_item
        }

    def _on_deed_marker_updated(self, marker_id: str, x: float, y: float, radius_px: float, deed: DeedModel):
        if marker_id in self.ui_markers:
            caption = deed.time_left
            if deed.resource:
                caption = f"{deed.resource} | {caption}"
            self.ui_markers[marker_id]["text"].setPlainText(caption)
            self.ui_markers[marker_id]["text"].setPos(x + 8, y - 18)

    def _on_deed_marker_removed(self, marker_id: str):
        if marker_id in self.ui_markers:
            self.scene.removeItem(self.ui_markers[marker_id]["dot"])
            self.scene.removeItem(self.ui_markers[marker_id]["text"])
            del self.ui_markers[marker_id]

    def _on_deed_marker_tick(self, marker_id: str, ttl_sec: int):
        if marker_id in self.ui_markers:
            self.ui_markers[marker_id]["text"].setPlainText(f"{ttl_sec // 60}:{ttl_sec % 60:02}")

    def _on_resource_claimed(self):
        print()

    def _ensure_coverage_layer(self):
        if getattr(self, "_cov_img", None) is not None:
            return

        # upewnij się, że znamy rozmiar mapy
        w = getattr(self, "map_width", int(self.scene.sceneRect().width()))
        h = getattr(self, "map_height", int(self.scene.sceneRect().height()))
        if w <= 0 or h <= 0:
            return  # jeszcze za wcześnie (brak kafli)

        # półprzezroczysta maska RGBA (pusta)
        self._cov_img = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
        self._cov_img.fill(Qt.GlobalColor.transparent)

        # Item pokazujący maskę (na szczycie)
        self._cov_item = QGraphicsPixmapItem(QPixmap.fromImage(self._cov_img))
        self._cov_item.setPos(0, 0)
        self._cov_item.setZValue(10_000)  # nad markerami i mapą
        self._cov_item.setOpacity(0.35)  # ogólna przezroczystość
        self.scene.addItem(self._cov_item)

        # „pędzel” – promień w pikselach sceny
        self._brush_radius_px = int(self.config.get("coverage", {}).get("brush_radius_px", 14))
        self._brush_color = QColor(32, 160, 255, 110)  # niebieski półprzezr.