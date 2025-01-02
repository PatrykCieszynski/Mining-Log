import cv2

from Modules.Capture.capture_screen import get_game_window, capture_screen
from Modules.OCR.ocr import detect_radar_from_game

if __name__ == "__main__":
    window_name = "Entropia Universe Client"
    # game_image_path = "../../Assets/test.jpg"
    radar_template_path = "../../Assets/radar_template.png"

    game_window = get_game_window(window_name)
    if not game_window:
        print("Game window not found. Retrying...")

    capture = capture_screen(game_window)
    cv2.imwrite("capture.png", capture)

    try:
        # Find the radar
        radar_top_left, radar_bottom_right = detect_radar_from_game(capture, radar_template_path, debug=True)
    except Exception as e:
        print(f"Błąd: {e}")
