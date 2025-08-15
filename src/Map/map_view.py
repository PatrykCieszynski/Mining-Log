# python
from typing import Any, Dict

from PyQt6.QtGui import QMouseEvent, QWheelEvent
from PyQt6.QtWidgets import QGraphicsView, QLabel

from src.Map.map_utils import get_planet_config


class MapView(QGraphicsView):
    def __init__(self, scene: Any, config: Dict[str, Any]) -> None:
        super().__init__(scene)
        self.planet_config = get_planet_config(config)
        self.tile_size = config["map"]["tile_size"]
        self.setMouseTracking(True)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.zoom_factor = 1.15

        self.coordinates_label = QLabel(self)
        self.coordinates_label.setStyleSheet(
            "color: white; background-color: rgba(0, 0, 0, 0.5); padding: 5px;"
        )
        self.coordinates_label.setGeometry(10, 10, 100, 50)
        self.coordinates_label.setText("Koordynaty: ")

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        if event is not None:
            if event.angleDelta().y() > 0:
                self.scale(self.zoom_factor, self.zoom_factor)
            elif event.angleDelta().y() < 0:
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        if event is not None:
            cursor_pos = self.mapToScene(event.pos())

            map_width = self.planet_config["tile_count_x"] * self.tile_size
            map_height = self.planet_config["tile_count_y"] * self.tile_size

            lon = self.planet_config["min_lon"] + (cursor_pos.x() / map_width) * (
                self.planet_config["max_lon"] - self.planet_config["min_lon"]
            )
            lat = self.planet_config["min_lat"] + ((map_height - cursor_pos.y()) / map_height) * (
                self.planet_config["max_lat"] - self.planet_config["min_lat"]
            )

            self.coordinates_label.setText(
                f"Koordynaty:\n Lon: {round(lon, 2)}\n Lat: {round(lat, 2)}"
            )
            super().mouseMoveEvent(event)
