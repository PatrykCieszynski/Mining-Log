# python
import re
from typing import Dict

import cv2
import numpy as np
import pytesseract

# Wewnętrzny prostokąt (sekcja pól) wewnątrz wycinka rogu okna
DEFAULT_INNER = dict(x=20, y=110, w=410, h=180)

# Konfiguracje OCR
CFG_BLOCK = "-l eng --oem 1 --psm 6"
CFG_BLOCK_ALT = "-l eng --oem 1 --psm 4"

# Regexy
RE_DEPTH = re.compile(r"^Depth:\s*([0-9]{1,4})\s*m$", re.I | re.M)
RE_SIZE = re.compile(r"^Size:\s*([A-Za-z]+)\s*\((\d+)\)$", re.I | re.M)
RE_RESOURCE = re.compile(r"^Resource:\s*([A-Za-z][A-Za-z \-']+)$", re.I | re.M)
RE_TIME = re.compile(r"^Time\s*left:\s*([0-2]?\d:[0-5]\d:[0-5]\d)$", re.I | re.M)
RE_POS_WITH_PLANET = re.compile(
    r"^Position:\s*([A-Za-z]+)\s*\(\s*(\d{3,6})\s*,\s*(\d{3,6})\s*,\s*(\d{1,4})\s*\)$",
    re.I | re.M,
)
RE_POS_NUMBERS_ONLY = re.compile(
    r"^Position:\s*\(\s*(\d{3,6})\s*,\s*(\d{3,6})\s*,\s*(\d{1,4})\s*\)$",
    re.I | re.M,
)

# Proste autokorekty najczęstszych literówek
# COMMON_FIX: Dict[str, str] = {
#     "Altemative": "Alternative",
#     "Altemative Rock": "Alternative Rock",
#     "Time lelt": "Time left",
#     "lime left": "Time left",
# }

def preprocess_deed(bgr: np.ndarray) -> np.ndarray:
    """
    Stabilny pipeline do OCR:
    - gray
    - powiększenie x3.5 (CUBIC)
    - delikatny median blur
    """
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=3.5, fy=3.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.medianBlur(gray, 3)
    return gray

def _bin_from_white_mask(bgr):
    # „białe litery” – niska saturacja, wysoka wartość
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0, 0, 190), (179, 60, 255))  # dopasuj 190/60 gdy trzeba
    # wypełnij dziurki i lekko rozszerz
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((2,2), np.uint8), iterations=1)
    mask = cv2.dilate(mask, np.ones((2,2), np.uint8), iterations=1)
    # przekształć do „czarny tekst na białym”
    thr = 255 - mask
    return thr

def preprocess_coords(bgr: np.ndarray) -> np.ndarray:
    # 1) powiększ „bez cukru”
    h, w = bgr.shape[:2]
    scale = 3
    bgr = cv2.resize(bgr, (w*scale, h*scale), interpolation=cv2.INTER_LINEAR)

    # 2) wzmocnij jasność tylko na kanale L (Lab)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    L, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    L = clahe.apply(L)
    lab = cv2.merge([L, a, b])
    bgr_eq = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    thr2 = _bin_from_white_mask(bgr_eq)

    # podgląd (opcjonalnie)
    cv2.imshow("pre2", thr2); cv2.waitKey(1)
    return thr2

CFG_BLOCK = "-l eng --oem 1 --psm 6 -c tessedit_char_whitelist=0123456789:,LatLon "


def ocr_text_block(gray: np.ndarray) -> str:
    """
    OCR całego bloku; wybiera dłuższy wynik z dwóch profili (PSM 6 i 4).
    """
    t1 = pytesseract.image_to_string(gray, config=CFG_BLOCK).strip()
    t2 = pytesseract.image_to_string(gray, config=CFG_BLOCK_ALT).strip()
    text = t1 if len(t1) >= len(t2) else t2

    # for wrong, correct in COMMON_FIX.items():
    #     text = text.replace(wrong, correct)

    # Normalizacja spacji/tabów (zachowujemy podziały linii)
    text = re.sub(r"[ \t]+", " ", text)
    print("OCR text:", text)
    return text