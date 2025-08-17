from typing import Optional
from pydantic import BaseModel
import time

class DeedModel(BaseModel):
    depth_m: Optional[int] = None
    size_label: Optional[str] = None
    size_points: Optional[int] = None
    resource: Optional[str] = None
    planet: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    raw: str
    expire_monotonic: Optional[float] = None  # seconds since monotonic start

    @property
    def ttl_sec(self) -> Optional[int]:
        # Compute TTL using a monotonic clock
        if self.expire_monotonic is None:
            return None
        left = int(self.expire_monotonic - time.monotonic())
        return max(left, 0)

    @property
    def time_left(self) -> Optional[str]:
        # Format TTL as HH:MM:SS
        ttl = self.ttl_sec
        if ttl is None:
            return None
        h, r = divmod(ttl, 3600)
        m, s = divmod(r, 60)
        return f"{h:02}:{m:02}:{s:02}"
