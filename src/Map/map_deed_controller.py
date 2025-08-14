# python
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QColor, QFont
from typing import List, Dict, Optional

def _fmt_ttl(sec: int) -> str:
    if sec < 0:
        sec = 0
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:d}:{m:02d}:{s:02d}"

class DeedMarkerController:
    def __init__(self, scene, lonlat_to_scene):
        self.scene = scene
        self._lonlat_to_scene = lonlat_to_scene
        self._deed_markers: List[Dict] = []
        print(self.scene)

    def add_or_update_deed_marker(self, lon: int, lat: int, ttl_sec: int, label: Optional[str] = None):
        try:
            if ttl_sec is None:
                ttl_sec = 0
            print("Adding/updating deed marker from scan result:", lon, lat, ttl_sec, label)
            x, y = self._lonlat_to_scene(lon, lat)
            print("Scene coords:", x, y)

            NEAR_PX = 10.0
            for mk in self._deed_markers:
                mx, my = mk["pos"]
                if (mx - x) ** 2 + (my - y) ** 2 <= NEAR_PX ** 2:
                    mk["remaining"] = max(ttl_sec, mk["remaining"])
                    if label:
                        mk["label_text"] = label
                    self.update_marker_visual(mk)
                    return
            print(self.scene)
            dot = QGraphicsEllipseItem(627.75, 568.3125, 10, 10)
            dot.setBrush(QBrush(QColor("#ff0000")))
            self.scene.addItem(dot)

            radius_px = 50
            dot = QGraphicsEllipseItem(x - radius_px, y - radius_px, radius_px * 2, radius_px * 2)
            dot.setBrush(QBrush(QColor("#00ff99")))
            self.scene.addItem(dot)
            text_item = QGraphicsTextItem()
            text_item.setDefaultTextColor(QColor("white"))

            font = QFont()
            font.setPointSize(9)
            text_item.setFont(font)
            text_item.setFlag(text_item.GraphicsItemFlag.ItemIgnoresTransformations, True)
            text_item.setZValue(11)
            text_item.setPos(x + 8, y - 18)
            self.scene.addItem(text_item)
            mk = dict(
                dot=dot,
                text=text_item,
                pos=(x, y),
                remaining=int(ttl_sec),
                label_text=label or "",
                radius=radius_px
            )
            self._deed_markers.append(mk)
            print("Ticking deeds:", self._deed_markers)
            self.update_marker_visual(mk)
        except Exception as e:
            print("Błąd przy dodawaniu markera:", e)

    def update_marker_visual(self, mk: Dict):
        try:
            ttl_str = _fmt_ttl(mk["remaining"])
            caption = ttl_str if not mk["label_text"] else f"{mk['label_text']} | {ttl_str}"
            mk["text"].setPlainText(caption)
            x, y = mk["pos"]
            mk["text"].setPos(x + 0.5, y - 0.5)
        except Exception as e:
            print("Błąd przy aktualizacji markera:", e)

    def tick_deeds(self):
        try:
            alive: List[Dict] = []
            for mk in self._deed_markers:
                mk["remaining"] -= 1
                if mk["remaining"] <= 0:
                    self.scene.removeItem(mk["dot"])
                    self.scene.removeItem(mk["text"])
                    continue
                self.update_marker_visual(mk)
                alive.append(mk)
            self._deed_markers = alive
        except Exception as e:
            print("Błąd przy ticku:", e)