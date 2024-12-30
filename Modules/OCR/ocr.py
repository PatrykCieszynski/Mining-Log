import cv2
from pytesseract import pytesseract


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