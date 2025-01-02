import re

import cv2
import numpy as np
import pytesseract


def detect_radar_from_game(game_image, radar_template_path, threshold=0.8, scale_range=(0.65, 1.35), scale_step=0.01, debug=False):
    # Wczytaj szablon z kanałem alfa
    radar_template = cv2.imread(radar_template_path, cv2.IMREAD_UNCHANGED)  # Zachowuje kanał alfa
    if radar_template is None:
        raise FileNotFoundError(f"Nie udało się załadować szablonu radaru: {radar_template_path}")

    # Rozdziel kanały szablonu
    template_bgr = radar_template[:, :, :3]  # Kanały kolorów
    template_alpha = radar_template[:, :, 3]  # Kanał alfa (przezroczystość)

    # Utwórz maskę dla nieprzezroczystych pikseli
    mask = cv2.threshold(template_alpha, 1, 255, cv2.THRESH_BINARY)[1]

    # Konwersja obrazu gry do skali szarości
    game_image_gray = cv2.cvtColor(game_image, cv2.COLOR_BGR2GRAY)

    # Inicjalizacja zmiennych do śledzenia najlepszego dopasowania
    best_match_val = 0
    best_match_loc = None
    best_template_size = None
    best_scale = None

    # Iteracja po różnych skalach
    for scale in np.arange(scale_range[0], scale_range[1] + scale_step, scale_step):
        # Skalowanie szablonu
        scaled_template = cv2.resize(template_bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        scaled_mask = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)

        # Dopasowanie szablonu z maską
        result = cv2.matchTemplate(game_image_gray, cv2.cvtColor(scaled_template, cv2.COLOR_BGR2GRAY), cv2.TM_CCOEFF_NORMED, mask=scaled_mask)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # Aktualizacja najlepszego dopasowania
        if max_val > best_match_val:
            best_scale = scale
            best_match_val = max_val
            best_match_loc = max_loc
            best_template_size = scaled_template.shape[:2]

    # Sprawdź, czy znaleziono dopasowanie powyżej progu
    if best_match_val < threshold:
        raise ValueError(f"Nie udało się wykryć radaru (najlepsze dopasowanie: {best_match_val}).")

    # Oblicz pozycję i rozmiar najlepszego dopasowania
    radar_top_left = best_match_loc
    radar_height, radar_width = best_template_size
    radar_bottom_right = (radar_top_left[0] + radar_width, radar_top_left[1] + radar_height)

    print(f"Radar znaleziony z dopasowaniem: {best_match_val}")
    print(f"Pozycja: {radar_top_left}, Rozmiar: ({radar_width}, {radar_height})")

    # Zaznacz radar na obrazie
    #TODO Remove this block
    if debug:
        detected_image = game_image.copy()
        cv2.rectangle(detected_image, radar_top_left, radar_bottom_right, (0, 255, 0), 2)
        # From the game_image_path, we extract the name of the file to save the result
        save_name = f"Results/capture_{best_match_val}.jpg"
        print(f"Zapisano obraz z zaznaczonym radarem: {save_name}")
        cv2.imwrite(save_name, detected_image)

    return radar_top_left, radar_bottom_right, best_scale

def detect_coords_from_radar(game_image, coords_template_path, radar_top_left, radar_bottom_right, scale, debug=False):
    # Wytnij obszar radaru
    radar_area = game_image[radar_top_left[1]:radar_bottom_right[1], radar_top_left[0]:radar_bottom_right[0]]

    # Wczytaj szablon z kanałem alfa
    coords_template = cv2.imread(coords_template_path, cv2.IMREAD_UNCHANGED)  # Zachowuje kanał alfa
    if coords_template is None:
        raise FileNotFoundError(f"Nie udało się załadować szablonu współrzędnych: {coords_template_path}")

    # Rozdziel kanały szablonu
    template_bgr = coords_template[:, :, :3]  # Kanały kolorów
    template_alpha = coords_template[:, :, 3]  # Kanał alfa (przezroczystość)

    # Utwórz maskę dla nieprzezroczystych pikseli
    mask = cv2.threshold(template_alpha, 1, 255, cv2.THRESH_BINARY)[1]

    # Konwersja obrazu gry do skali szarości
    radar_area_gray = cv2.cvtColor(radar_area, cv2.COLOR_BGR2GRAY)

    # Skalowanie szablonu
    scaled_template = cv2.resize(template_bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    scaled_mask = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)

    # Dopasowanie szablonu z maską
    result = cv2.matchTemplate(radar_area_gray, cv2.cvtColor(scaled_template, cv2.COLOR_BGR2GRAY), cv2.TM_CCOEFF_NORMED, mask=scaled_mask)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    # Sprawdź, czy znaleziono dopasowanie powyżej progu
    if max_val < 0.75:
        raise ValueError(f"Nie udało się wykryć współrzędnych (najlepsze dopasowanie: {max_val}).")

    # Oblicz pozycję i rozmiar najlepszego dopasowania
    coords_top_left = max_loc

    coords_height, coords_width = scaled_template.shape[:2]
    coords_bottom_right = (coords_top_left[0] + coords_width, coords_top_left[1] + coords_height)

    print(f"Współrzędne znalezione z dopasowaniem: {max_val}")
    print(f"Pozycja: {coords_top_left}, Rozmiar: ({coords_width}, {coords_height})")

    # Zaznacz współrzędne na obrazie
    if debug:
        detected_image = radar_area.copy()
        cv2.rectangle(detected_image, coords_top_left, coords_bottom_right, (0, 0, 255), 2)
        # From the game_image_path, we extract the name of the file to save the result
        save_name = f"Results/capture_{max_val}.jpg"
        print(f"Zapisano obraz z zaznaczonymi współrzędnymi: {save_name}")
        cv2.imwrite(save_name, detected_image)

    return coords_top_left, coords_bottom_right

def extract_lon_lat(game_image, radar_top_left, radar_bottom_right, debug=False):
    # Wytnij obszar radaru
    radar_region = game_image[radar_top_left[1]:radar_bottom_right[1], radar_top_left[0]:radar_bottom_right[0]]
    detected_image = radar_region.copy()
    cv2.imwrite('coords.png', detected_image)

    # Wstępne przetwarzanie obrazu dla OCR
    radar_gray = cv2.cvtColor(radar_region, cv2.COLOR_BGR2GRAY)  # Skala szarości
    radar_thresh = cv2.adaptiveThreshold(radar_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 85, -55)  # Adaptacyjny próg binarny

    # Debug: zapisz wycięty radar
    if debug:
        cv2.imwrite("radar_processed_for_ocr.png", radar_thresh)

    # OCR na wyciętym fragmencie
    ocr_result = pytesseract.image_to_string(radar_thresh, config='--psm 6')  # PSM 6: Układ tekstu w bloku

    # Debug: Wyświetl wynik OCR
    if debug:
        print("Wynik OCR (surowy):")
        print(ocr_result)

    # Ekstrakcja współrzędnych Lon i Lat z wyniku OCR
    lines = ocr_result.split("\n")
    lon_match = re.search(r'\d+', lines[0].strip())
    lat_match = re.search(r'\d+', lines[1].strip())

    if lon_match and lat_match:
        lon = int(lon_match.group())
        lat = int(lat_match.group())

    if lon is None or lat is None:
        return None, None

    print(f"Lon: {lon}, Lat: {lat}")
    return lon, lat