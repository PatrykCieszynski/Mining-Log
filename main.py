import cv2
import pytesseract
import numpy as np
from mss import mss
import pygetwindow as gw
import time

# Funkcja do znajdowania okna gry
def get_game_window(window_name):
    """
    Znajduje okno o podanej nazwie.
    :param window_name: Nazwa okna (np. "Entropia Universe Client").
    :return: Słownik z pozycją i wymiarami okna lub None, jeśli nie znaleziono.
    """
    windows = gw.getWindowsWithTitle(window_name)
    if windows:
        win = windows[0]  # Zakładamy, że tylko jedno okno gry jest otwarte
        return {
            "left": win.left,
            "top": win.top,
            "width": win.width,
            "height": win.height
        }
    return None

# Funkcja do odczytywania współrzędnych Lon i Lat
def extract_coordinates_from_radar(screen_image):
    # Załóżmy, że radar zawsze znajduje się w prawym dolnym rogu
    radar_h, radar_w = 100, 260  # Przykładowe wymiary radaru
    screen_h, screen_w = screen_image.shape[:2]
    radar_x = screen_w - radar_w
    radar_y = screen_h - radar_h

    radar_image = screen_image[radar_y:radar_y+radar_h, radar_x:radar_x+radar_w]

    lon_region = radar_image[30:55, 37:83]
    lat_region = radar_image[55:75, 37:83]

    lon_gray = cv2.cvtColor(lon_region, cv2.COLOR_BGR2GRAY)
    lat_gray = cv2.cvtColor(lat_region, cv2.COLOR_BGR2GRAY)
    _, lon_thresh = cv2.threshold(lon_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, lat_thresh = cv2.threshold(lat_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    lon_text = pytesseract.image_to_string(lon_thresh, config='--psm 7')
    lat_text = pytesseract.image_to_string(lat_thresh, config='--psm 7')

    try:
        lon_value = int(''.join(filter(str.isdigit, lon_text)))
        lat_value = int(''.join(filter(str.isdigit, lat_text)))
        return {"Lon": lon_value, "Lat": lat_value}
    except ValueError:
        return None

# Funkcja główna
def main():
    # Znajdź okno gry
    window_name = "Entropia Universe Client"
    game_window = get_game_window(window_name)
    if not game_window:
        print(f"Nie znaleziono okna o nazwie: {window_name}")
        return

    print(f"Znaleziono okno gry: {game_window}")

    with mss() as sct:
        while True:
            start_time = time.time()

            # Przechwyć obraz tylko z obszaru okna gry
            monitor = {
                "left": game_window["left"],
                "top": game_window["top"],
                "width": game_window["width"],
                "height": game_window["height"]
            }
            screen = np.array(sct.grab(monitor))
            screen_bgr = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)

            # Wykrywanie i odczyt współrzędnych
            coordinates = extract_coordinates_from_radar(screen_bgr)
            if coordinates:
                print(f"Współrzędne: {coordinates}")
            else:
                print("Radar nie został znaleziony.")

            # Wyświetlanie czasu przetwarzania
            end_time = time.time()
            print(f"Czas przetwarzania: {end_time - start_time:.2f}s")

            # Wyświetlanie obrazu (opcjonalnie)
            cv2.imshow("Screen", screen_bgr)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Naciśnij 'q', aby zakończyć
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()