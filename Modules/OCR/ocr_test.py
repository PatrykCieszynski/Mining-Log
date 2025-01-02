import cv2

from Modules.Capture.capture_screen import get_game_window, capture_screen
from Modules.OCR.ocr import detect_radar_from_game, detect_coords_from_radar, extract_lon_lat

if __name__ == "__main__":
    window_name = "Entropia Universe Client"
    # game_image_path = "../../Assets/test.jpg"
    radar_template_path = "../../Assets/radar_template.png"
    coords_template_path = "../../Assets/Coords.png"

    game_window = get_game_window(window_name)
    if not game_window:
        print("Game window not found. Retrying...")

    capture = capture_screen(game_window)
    cv2.imwrite("capture.png", capture)

    try:
        # Find the radar
        # radar_top_left, radar_bottom_right, scale = detect_radar_from_game(capture, radar_template_path, debug=True)
        # print(f"Radar znaleziony: {radar_top_left}, {radar_bottom_right}, przy skali {scale}")
        radar_top_left = (1637, 733)
        radar_bottom_right = (1907, 1052)
        scale = 0.79

        # lon, lat = extract_lon_lat_from_radar(capture, radar_top_left, radar_bottom_right, scale, debug=True)
        coords_top_left, coords_bottom_right = detect_coords_from_radar(capture, coords_template_path, radar_top_left, radar_bottom_right, scale, True)
        print(f"Współrzędne znalezione: {coords_top_left}, {coords_bottom_right}")

        #Add the coordinates of the radar to the coordinates of the coords
        coords_top_left = (coords_top_left[0] + radar_top_left[0], coords_top_left[1] + radar_top_left[1])
        coords_bottom_right = (coords_bottom_right[0] + radar_top_left[0], coords_bottom_right[1] + radar_top_left[1])

        # Wyodrębnij Lon i Lat z radaru
        while True:
            capture = capture_screen(game_window)
            lon, lat = extract_lon_lat(capture, coords_top_left, coords_bottom_right, debug=True)
            print(f"Współrzędne: Lon = {lon}, Lat = {lat}")

    except Exception as e:
        print(f"Błąd: {e}")
