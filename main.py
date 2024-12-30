import cv2
import time
from Modules.Capture.capture_screen import get_game_window, capture_screen
from Modules.OCR.ocr import extract_coordinates_from_radar

def process_coordinates(screen_bgr):
    coordinates = extract_coordinates_from_radar(screen_bgr)
    if coordinates:
        print(f"Coordinates: {coordinates}")
    else:
        print("Radar not found.")
    return coordinates

def main():
    window_name = "Entropia Universe Client"
    game_window = get_game_window(window_name)
    if not game_window:
        print(f"Window not found: {window_name}")
        return

    print(f"Game window found: {game_window}")

    while True:
        start_time = time.time()
        screen_bgr = capture_screen(game_window)
        process_coordinates(screen_bgr)
        end_time = time.time()
        print(f"Processing time: {end_time - start_time:.2f}s")

        cv2.imshow("Screen", screen_bgr)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()