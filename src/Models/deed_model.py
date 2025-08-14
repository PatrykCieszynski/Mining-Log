# python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class DeedModel(BaseModel):
    depth_m: Optional[int] = None
    size_label: Optional[str] = None
    size_points: Optional[int] = None
    resource: Optional[str] = None
    expire_time: Optional[datetime] = None
    planet: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    z: Optional[int] = None
    raw: str

    # Computed property for time left in seconds
    @property
    def ttl_sec(self) -> Optional[int]:
        if self.expire_time:
            delta = self.expire_time - datetime.now()
            return max(int(delta.total_seconds()), 0)
        return None

    # Computed property for time left formatted as HH:MM:SS
    @property
    def time_left(self) -> Optional[str]:
        sec = self.ttl_sec
        if sec is not None:
            h, rem = divmod(sec, 3600)
            m, s = divmod(rem, 60)
            return f"{h:02}:{m:02}:{s:02}"
        return None