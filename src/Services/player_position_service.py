# python
from typing import Dict, Any

from src.App.signal_bus import SignalBus
from src.Map.map_utils import lonlat_to_scene, coord_to_pixel_radius


class PlayerPositionService:

    def __init__(
            self,
            bus: SignalBus,
            config: Dict[str, Any],
    ) -> None:
        self.bus = bus
        self.config = config
        self.player_position = (0, 0)
        self.player_position_rect = (0, 0, 0, 0)

        self.bus.player_position_parsed.connect(self._on_position_found)

    def _on_position_found(self, lon: int, lat: int) -> None:
        print("Player position found: ", lon, lat, "")
        self.update_position(lon, lat)

    def update_position(self, lon: int, lat: int) -> None:
        x, y = lonlat_to_scene(lon, lat, self.config)
        self.player_position = (x, y)
        radius = coord_to_pixel_radius(self.config)
        self.player_position_rect = (x - radius, y - radius, 2 * radius, 2 * radius)
        self.bus.player_position_changed.emit((x, y), self.player_position_rect)
