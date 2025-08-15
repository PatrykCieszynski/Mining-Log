# python
from typing import Any, Optional

from PyQt6.QtCore import QObject
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtWidgets import QGraphicsEllipseItem


TILE_SIZE = 512


class PlayerPositionController:

    def __init__(
            self,
            ctx: Any,
            scene: Any,
            lonlat_to_scene: Any,
            coord_to_pixel_radius,
            radius_coord: Any,
            border_width: Any,
    ) -> None:
        self.ctx = ctx
        self.scene = scene
        self.lonlat_to_scene = lonlat_to_scene
        self.coord_to_pixel_radius = coord_to_pixel_radius
        self.radius_coord = radius_coord
        self.border_width = border_width
        self.player_item = QGraphicsEllipseItem(0, 0, 0, 0)
        self.player_item.setBrush(QBrush(QColor(255, 0, 0, 100)))
        self.player_item.setPen(QPen(QColor("red"), self.border_width))

        self.scene.addItem(self.player_item)
        self.player_scanner = ctx.player_scanner

        self.ctx.bus.player_position_found.connect(self._on_position_found)

    def _on_position_found(self, lon: int, lat: int) -> None:
        print("Player position found: ", lon, lat, "")
        self.update_position(lon, lat)

    def update_position(self, lon: int, lat: int) -> None:
        print("Updating player position with lon/lat: ", lon, lat, "")
        x, y = self.lonlat_to_scene(lon, lat)
        radius = self.coord_to_pixel_radius(self.radius_coord)
        self.player_item.setRect(x - radius, y - radius, 2 * radius, 2 * radius)

