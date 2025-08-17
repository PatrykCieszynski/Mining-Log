from typing import List, Dict, Any
from PyQt6.QtCore import QObject, QPointF, QTimer

from src.app.signal_bus import SignalBus
from src.map.map_utils import lonlat_to_scene
from src.models.deed_model import DeedModel


class MarkerData:
    def __init__(self, marker_id: str, pos: QPointF, radius: float, deed: DeedModel):
        self.marker_id = marker_id
        self.pos = pos
        self.radius = radius
        self.deed = deed


class DeedMarkerService(QObject):
    def __init__(self, bus: SignalBus, config: Dict[str, Any]):
        super().__init__()
        self.bus = bus
        self.config = config
        self.deed_markers: List[MarkerData] = []
        self.player_pos: QPointF = QPointF(0, 0)

        self.bus.deed_found.connect(self._on_scan_result)
        self.bus.player_position_changed.connect(self._on_player_position_changed)
        self.bus.resource_depleted.connect(self.remove_nearest_deed)

    def _on_scan_result(self, deed: DeedModel) -> None:
        lon, lat = deed.x, deed.y
        if lon is None or lat is None:
            return

        x, y = lonlat_to_scene(lon, lat, self.config)
        pos = QPointF(x, y)
        ttl_sec = deed.ttl_sec or 0
        NEAR_PX = 10.0

        # Aktualizacja istniejącego markera
        for marker in self.deed_markers:
            if (marker.pos - pos).manhattanLength() <= NEAR_PX:
                if ttl_sec > (marker.deed.ttl_sec or 0):
                    marker.deed = deed
                self.bus.deed_marker_updated.emit(
                    marker.marker_id, pos.x(), pos.y(), marker.radius, marker.deed
                )
                return

        # Dodanie nowego markera
        marker_id = f"{lon}-{lat}-{len(self.deed_markers)}"
        radius_px = 0.2
        new_marker = MarkerData(marker_id, pos, radius_px, deed)
        self.deed_markers.append(new_marker)
        self.bus.deed_marker_added.emit(marker_id, pos.x(), pos.y(), radius_px, deed)

    def _on_player_position_changed(self, pos: QPointF) -> None:
        self.player_pos = pos

    def tick_deeds(self) -> None:
        alive = []
        for marker in self.deed_markers:
            if (marker.deed.ttl_sec or 0) <= 0:
                self.bus.deed_marker_removed.emit(marker.marker_id)
                continue
            self.bus.deed_marker_tick.emit(marker.marker_id, marker.deed.ttl_sec)
            alive.append(marker)
        self.deed_markers = alive

    def _on_resource_depleted(self) -> None:
        if self.player_pos is None:
            print("[DeedMarkerService] No player position, skipping removal")
            return
        self.remove_nearest_deed()

    def remove_nearest_deed(self) -> None:
        if not self.deed_markers or self.player_pos is None:
            return

        nearest = min(
            self.deed_markers,
            key=lambda mk: (mk.pos - self.player_pos).manhattanLength(),
            default=None
        )
        if nearest:
            self.bus.deed_marker_removed.emit(nearest.marker_id)
            self.deed_markers.remove(nearest)
