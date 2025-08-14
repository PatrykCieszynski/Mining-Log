# python
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtWidgets import QGraphicsEllipseItem


class PlayerPositionController:
    def __init__(self, scene, lonlat_to_scene, radius_coord, border_width):
        self.scene = scene
        self.lonlat_to_scene = lonlat_to_scene
        self.radius_coord = radius_coord
        self.border_width = border_width
        self.player_item = QGraphicsEllipseItem(0, 0, 0, 0)
        self.player_item.setBrush(QBrush(QColor(255, 0, 0, 100)))
        self.player_item.setPen(QPen(QColor("red"), self.border_width))
        self.scene.addItem(self.player_item)

    def update_position(self, lon, lat, coord_to_pixel_radius):
        print("Updating player position with lon/lat: ", lon, lat, "")
        x, y = self.lonlat_to_scene(lon, lat)
        radius = coord_to_pixel_radius(self.radius_coord)
        self.player_item.setRect(x - radius, y - radius, 2 * radius, 2 * radius)
