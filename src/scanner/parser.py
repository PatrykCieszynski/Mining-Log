# python
from datetime import datetime, timedelta
from time import monotonic
from typing import Dict, List

from src.models.deed_model import DeedModel
from src.scanner.ocr_core import (
    RE_DEPTH,
    RE_POS_NUMBERS_ONLY,
    RE_POS_WITH_PLANET,
    RE_RESOURCE,
    RE_SIZE,
    RE_TIME,
)


def _merge_position_lines(lines: List[str]) -> List[str]:
    """
    Łączy 'Position:' z kolejną linią zawierającą liczby, kiedy OCR łamie wiersz.
    """
    merged: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lower().startswith("position:") and i + 1 < len(lines):
            nxt = lines[i + 1]
            if "," in nxt or ")" in nxt:
                line = f"{line} {nxt}"
                i += 1
        merged.append(line)
        i += 1
    return merged


def parse_deed_text(text: str) -> DeedModel:
    lines = [ln.strip() for ln in text.replace("\r", "").split("\n") if ln.strip()]
    lines = _merge_position_lines(lines)
    blob = "\n".join(lines)

    out: dict = {"raw": blob}

    # Depth
    if m := RE_DEPTH.search(blob):
        out["depth_m"] = int(m.group(1))

    # Size
    if m := RE_SIZE.search(blob):
        out["size_label"] = m.group(1).title()
        out["size_points"] = int(m.group(2))

    # Resource
    if m := RE_RESOURCE.search(blob):
        out["resource"] = " ".join(m.group(1).split())

    # Time
    if m := RE_TIME.search(blob):
        h, mi, s = map(int, m.group(1).split(":"))
        ttl_sec = h * 3600 + mi * 60 + s
        out["expire_monotonic"] = monotonic() + ttl_sec

    # Position
    m = RE_POS_WITH_PLANET.search(blob) or RE_POS_NUMBERS_ONLY.search(blob)
    if m:
        groups = m.groups()
        if len(groups) == 4:
            out["planet"] = groups[0].title()
            out["x"], out["y"], out["z"] = map(int, groups[1:])
        else:
            out["x"], out["y"], out["z"] = map(int, groups)

    return DeedModel(**out)
