import cv2
import numpy as np

from Modules.Capture.capture_screen import get_game_window, capture_screen
from Modules.Map.create_map_window import stitch_map_fragments, center_map_on_coordinates
from Modules.OCR.ocr import extract_coordinates_from_radar

def main():
    window_name = "Entropia Universe Client"
    game_window = get_game_window(window_name)
    if not game_window:
        print(f"Window not found: {window_name}")
        return

    print(f"Game window found: {game_window}")

    map_image = stitch_map_fragments('Assets/Maps')
    zoom_factor = 1.0
    cursor_pos = (0, 0)
    zoom_cache = {}

    min_lon, max_lon = 16000, 90000
    min_lat, max_lat = 25000, 98000

    def on_mouse(event, x, y, flags, param):
        nonlocal cursor_pos, zoom_factor
        if event == cv2.EVENT_MOUSEMOVE:
            cursor_pos = (x, y)
        elif event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                zoom_factor *= 1.05  # Zoom in
            else:
                zoom_factor /= 1.05  # Zoom out
            zoom_factor = max(0.1, min(zoom_factor, 10))  # Limit zoom factor

    cv2.namedWindow("Map Window")
    cv2.setMouseCallback("Map Window", on_mouse)

    while True:
        screen_bgr = capture_screen(game_window)
        coordinates = extract_coordinates_from_radar(screen_bgr)
        if coordinates:
            if zoom_factor not in zoom_cache:
                zoom_cache[zoom_factor] = cv2.resize(map_image, None, fx=zoom_factor, fy=zoom_factor, interpolation=cv2.INTER_LINEAR)
            centered_map = center_map_on_coordinates(zoom_cache[zoom_factor], coordinates, window_size=(800, 800), zoom_factor=1.0)

            # Convert cursor position to in-game coordinates
            map_h, map_w = centered_map.shape[:2]
            norm_x = cursor_pos[0] / map_w
            norm_y = 1 - (cursor_pos[1] / map_h)  # Invert the normalization for latitude
            in_game_lon = int(norm_x * (max_lon - min_lon) + min_lon)
            in_game_lat = int(norm_y * (max_lat - min_lat) + min_lat)
            debug_info = f"Cursor Position: Lon {in_game_lon}, Lat {in_game_lat}"

            cv2.putText(centered_map, debug_info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow("Map Window", centered_map)
        else:
            print("Radar not found.")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()