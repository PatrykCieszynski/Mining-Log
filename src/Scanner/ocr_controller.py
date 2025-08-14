# python
import os
from typing import Dict, Optional, Tuple, Any

import cv2
import numpy as np

from src.Models.deed_model import DeedModel
from src.Scanner.ocr_core import DEFAULT_INNER, ocr_text_block, preprocess_deed
from src.Scanner.parser import parse_deed_text
from src.Scanner.screen_capture import capture_corner_crop


def extract_deed_from_image(
    corner_image_bgr: np.ndarray[Any, Any],
    inner_rect: Tuple[int, int, int, int] = (
        DEFAULT_INNER["x"],
        DEFAULT_INNER["y"],
        DEFAULT_INNER["w"],
        DEFAULT_INNER["h"],
    ),
    debug: bool = False,
    save_dir: Optional[str] = None,
) -> DeedModel:
    """
    Przyjmuje obraz rogu okna (BGR), wycina wewnętrzny prostokąt, robi OCR i parsuje pola.
    """
    x, y, w, h = inner_rect
    H, W = corner_image_bgr.shape[:2]

    x1 = max(0, min(W - 1, x))
    y1 = max(0, min(H - 1, y))
    x2 = max(1, min(W, x + w))
    y2 = max(1, min(H, y + h))
    roi = corner_image_bgr[y1:y2, x1:x2]

    gray = preprocess_deed(roi)
    text = ocr_text_block(gray)
    parsed = parse_deed_text(text)

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        cv2.imwrite(os.path.join(save_dir, "corner_crop.png"), corner_image_bgr)
        cv2.imwrite(os.path.join(save_dir, "roi_inner.png"), roi)
        cv2.imwrite(os.path.join(save_dir, "roi_preprocessed_deed.png"), gray)
        with open(os.path.join(save_dir, "ocr.txt"), "w", encoding="utf-8") as f:
            f.write(text)

    if debug:
        cv2.imshow("corner_crop", corner_image_bgr)
        cv2.imshow("roi_inner", roi)
        cv2.imshow("roi_preprocessed_deed", gray)
        print("\n--- OCR TEXT ---\n", text)

    return parsed


def extract_deed_from_window(
    offset_x: int = 0,
    offset_y: int = 0,
    inner_rect: Tuple[int, int, int, int] = (
        DEFAULT_INNER["x"],
        DEFAULT_INNER["y"],
        DEFAULT_INNER["w"],
        DEFAULT_INNER["h"],
    ),
    debug: bool = False,
    save_dir: Optional[str] = None,
) -> DeedModel:
    """
    Przechwytuje róg okna gry i wywołuje ścieżkę ekstrakcji.
    """
    corner = capture_corner_crop(offset_x=offset_x, offset_y=offset_y)
    return extract_deed_from_image(
        corner, inner_rect=inner_rect, debug=debug, save_dir=save_dir
    )
