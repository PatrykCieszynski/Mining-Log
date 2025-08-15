from __future__ import annotations
from typing import List, Optional, Tuple, Callable
import math
from src.Models.deed_model import DeedModel

class DeedRepository:
    """In-memory store for active deeds."""

    def __init__(self) -> None:
        self._items: List[DeedModel] = []

    def all(self) -> List[DeedModel]:
        return list(self._items)

    def add_or_update(self, deed: DeedModel) -> None:
        # Simple dedupe by (x, y, resource)
        for i, d in enumerate(self._items):
            if d.x == deed.x and d.y == deed.y and d.resource == deed.resource:
                if (d.ttl_sec or 0) < (deed.ttl_sec or 0):
                    self._items[i] = deed
                return
        self._items.append(deed)

    def remove_nearest(
        self,
        player_scene_pos: Tuple[float, float],
        to_scene: Callable[[float, float], Tuple[float, float]],
        max_dist_px: float = 120.0,
    ) -> Optional[DeedModel]:
        # Remove nearest deed within max_dist_px
        nearest_i = -1
        nearest_d = float("inf")
        for i, d in enumerate(self._items):
            if d.x is None or d.y is None:
                continue
            mx, my = to_scene(float(d.x), float(d.y))
            dist = math.hypot(mx - player_scene_pos[0], my - player_scene_pos[1])
            if dist < nearest_d:
                nearest_d, nearest_i = dist, i
        if nearest_i >= 0 and nearest_d <= max_dist_px:
            return self._items.pop(nearest_i)
        return None

    def gc_expired(self) -> int:
        # Remove expired deeds and return removed count
        alive: List[DeedModel] = []
        removed = 0
        for d in self._items:
            if (d.ttl_sec or 0) <= 0:
                removed += 1
            else:
                alive.append(d)
        self._items = alive
        return removed
