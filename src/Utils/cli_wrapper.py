# python
import json

import cv2

from src.Scanner.ocr_controller import extract_deed_from_image, extract_deed_from_window
from src.Scanner.ocr_core import DEFAULT_INNER


def cli_main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="OCR deed z lewego-górnego rogu okna (bez zewn. ROI)."
    )
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--window", action="store_true", help="Przechwyć fragment z okna gry."
    )
    g.add_argument("--image", help="Ścieżka do obrazu (PNG/JPG) z rogiem okna.")

    parser.add_argument(
        "--offset-x", type=int, default=0, help="Przesunięcie X dla rogu okna."
    )
    parser.add_argument(
        "--offset-y", type=int, default=0, help="Przesunięcie Y dla rogu okna."
    )
    parser.add_argument(
        "--inner-x",
        type=int,
        default=DEFAULT_INNER["x"],
        help="Wewnętrzny X (sekcja pól).",
    )
    parser.add_argument(
        "--inner-y",
        type=int,
        default=DEFAULT_INNER["y"],
        help="Wewnętrzny Y (sekcja pól).",
    )
    parser.add_argument(
        "--inner-w", type=int, default=DEFAULT_INNER["w"], help="Wewnętrzna szerokość."
    )
    parser.add_argument(
        "--inner-h", type=int, default=DEFAULT_INNER["h"], help="Wewnętrzna wysokość."
    )
    parser.add_argument(
        "--debug", action="store_true", help="Pokaż podgląd i wypisz surowy tekst OCR."
    )
    parser.add_argument(
        "--save-dir", default=None, help="Folder do zapisu debug (obrazy + ocr.txt)."
    )

    args = parser.parse_args()
    inner_rect = (args.inner_x, args.inner_y, args.inner_w, args.inner_h)

    if args.window:
        result = extract_deed_from_window(
            offset_x=args.offset_x,
            offset_y=args.offset_y,
            inner_rect=inner_rect,
            debug=args.debug,
            save_dir=args.save_dir,
        )
    else:
        corner = cv2.imread(args.image)
        if corner is None:
            raise SystemExit(f"Nie mogę wczytać obrazu: {args.image}")
        result = extract_deed_from_image(
            corner_image_bgr=corner,
            inner_rect=inner_rect,
            debug=args.debug,
            save_dir=args.save_dir,
        )

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.debug:
        cv2.waitKey(0)
