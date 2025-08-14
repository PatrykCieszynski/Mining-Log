import math
from typing import Callable, Dict, List, Optional, Tuple, TypedDict

from PyQt6.QtCore import QObject, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPen
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsScene

from src.Models.deed_model import DeedModel


class MarkerData(TypedDict):
    dot: QGraphicsEllipseItem
    text: QGraphicsTextItem
    pos: Tuple[float, float]
    label_text: str | None
    radius: float
    deed: DeedModel


def _fmt_ttl(sec: int) -> str:
    if sec < 0:
        sec = 0
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:d}:{m:02d}:{s:02d}"


def update_marker_visual(mk: MarkerData) -> None:
    try:
        ttl: int = mk["deed"].ttl_sec or 0
        ttl_str: str = _fmt_ttl(ttl)
        caption: str = ttl_str if not mk["label_text"] else f"{mk['label_text']} | {ttl_str}"
        mk["text"].setPlainText(caption)
        x, y = mk["pos"]
        mk["text"].setPos(x + 0.5, y - 0.5)
    except Exception as e:
        print("Error updating marker:", e)


class DeedMarkerController:
    def __init__(
        self,
        scene: QGraphicsScene,
        lonlat_to_scene: Callable[[float, float], Tuple[float, float]],
        scanner: Optional[QObject] = None
    ) -> None:
        self.scene: QGraphicsScene = scene
        self._lonlat_to_scene: Callable[[float, float], Tuple[float, float]] = lonlat_to_scene
        self._deed_markers: List[MarkerData] = []
        if scanner is not None:
            self.attach_scanner(scanner)

    def attach_scanner(self, scanner: QObject) -> None:
        try:
            scanner.deed_found.connect(self._on_scan_result)  # type: ignore[attr-defined]
        except Exception as e:
            print("Error attaching scanner:", e)

    def detach_scanner(self, scanner: QObject) -> None:
        try:
            scanner.deed_found.disconnect(self._on_scan_result)  # type: ignore[attr-defined]
        except Exception as e:
            print("Error detaching scanner:", e)

    def _on_scan_result(self, deed: DeedModel) -> None:
        try:
            print("Scan result:", deed)
            self.add_or_update_deed_marker(deed)
        except Exception as e:
            print("Error in _on_scan_result:", e)

    def add_or_update_deed_marker(self, deed: DeedModel) -> None:
        try:
            lon, lat = deed.x, deed.y
            if lon is None or lat is None:
                print("Skipping deed without coordinates")
                return

            ttl_sec: int = deed.ttl_sec or 0
            label: Optional[str] = deed.resource

            print("Adding/updating deed marker:", lon, lat, ttl_sec, label)
            x, y = self._lonlat_to_scene(lon, lat)
            NEAR_PX: float = 10.0

            for marker in self._deed_markers:
                marker_x, marker_x = marker["pos"]
                if (marker_x - x) ** 2 + (marker_x - y) ** 2 <= NEAR_PX**2:
                    if deed.ttl_sec and (marker["deed"].ttl_sec or 0) < deed.ttl_sec:
                        marker["deed"] = deed
                    if label:
                        marker["label_text"] = label
                    update_marker_visual(marker)
                    return

            radius_px: float = 0.2
            dot = QGraphicsEllipseItem(
                x - radius_px, y - radius_px, radius_px * 2, radius_px * 2
            )
            dot.setBrush(QBrush(QColor("#00ff99")))
            dot.setPen(QPen(Qt.PenStyle.NoPen))  # no border
            self.scene.addItem(dot)

            text_item = QGraphicsTextItem()
            text_item.setDefaultTextColor(QColor("white"))
            font = QFont()
            font.setPointSize(9)
            text_item.setFont(font)
            text_item.setFlag(
                text_item.GraphicsItemFlag.ItemIgnoresTransformations, True
            )
            text_item.setZValue(11)
            text_item.setPos(x + 8, y - 18)
            self.scene.addItem(text_item)

            new_marker: MarkerData = {
                "dot": dot,
                "text": text_item,
                "pos": (x, y),
                "label_text": label or "",
                "radius": radius_px,
                "deed": deed
            }
            self._deed_markers.append(new_marker)
            update_marker_visual(new_marker)
        except Exception as e:
            print("Error adding marker:", e)

    def tick_deeds(self) -> None:
        """Remove expired deeds and refresh timers."""
        try:
            alive: List[MarkerData] = []
            for mk in self._deed_markers:
                if (mk["deed"].ttl_sec or 0) <= 0:
                    self.scene.removeItem(mk["dot"])
                    self.scene.removeItem(mk["text"])
                    continue
                update_marker_visual(mk)
                alive.append(mk)
            self._deed_markers = alive
        except Exception as e:
            print("Error in tick_deeds:", e)

    def remove_nearest_deed(self, player_pos: Tuple[float, float]) -> None:
        if not self._deed_markers:
            return

        nearest = None
        nearest_dist = float("inf")

        for mk in self._deed_markers:
            mx, my = mk["pos"]
            dist = math.hypot(mx - player_pos[0], my - player_pos[1])
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = mk

        if nearest:
            self.scene.removeItem(nearest["dot"])
            self.scene.removeItem(nearest["text"])
            self._deed_markers.remove(nearest)
            print(f"[DeedMarkerController] Removed nearest deed at distance {nearest_dist:.2f}")
