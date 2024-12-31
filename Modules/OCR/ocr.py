import cv2
from pytesseract import pytesseract

def multi_scale_template_matching(image, template, scales):
    best_match = None
    best_val = -1
    for scale in scales:
        resized_template = cv2.resize(template, (0, 0), fx=scale, fy=scale)
        res = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val > best_val:
            best_val = max_val
            best_match = (max_loc, resized_template.shape)
    return best_match

def extract_coordinates_from_radar(screen_image):
    radar_h, radar_w = 400, 400  # Example radar dimensions
    screen_h, screen_w = screen_image.shape[:2]
    radar_x = screen_w - radar_w
    radar_y = screen_h - radar_h

    radar_image = screen_image[radar_y:radar_y+radar_h, radar_x:radar_x+radar_w]

    # Convert radar image to grayscale
    radar_gray = cv2.cvtColor(radar_image, cv2.COLOR_BGR2GRAY)

    # Load templates for "Lon" and "Lat" labels
    lon_template = cv2.imread('Assets/lon_template.png', 0)
    lat_template = cv2.imread('Assets/lat_template.png', 0)

    # Perform multi-scale template matching
    scales = [0.5, 0.75, 1.0, 1.25, 1.5]
    lon_match = multi_scale_template_matching(radar_gray, lon_template, scales)
    lat_match = multi_scale_template_matching(radar_gray, lat_template, scales)

    if lon_match and lat_match:
        lon_loc, lon_size = lon_match
        lat_loc, lat_size = lat_match

        # Define regions of interest based on template matching results
        lon_region = radar_image[lon_loc[1]:lon_loc[1]+lon_size[0], lon_loc[0]+40:lon_loc[0]+90]
        lat_region = radar_image[lat_loc[1]:lat_loc[1]+lat_size[0], lat_loc[0]+30:lat_loc[0]+90]

        # Convert regions to grayscale and apply thresholding
        lon_gray = cv2.cvtColor(lon_region, cv2.COLOR_BGR2GRAY)
        lat_gray = cv2.cvtColor(lat_region, cv2.COLOR_BGR2GRAY)
        _, lon_thresh = cv2.threshold(lon_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, lat_thresh = cv2.threshold(lat_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Extract text using pytesseract
        lon_text = pytesseract.image_to_string(lon_thresh, config='--psm 7')
        lat_text = pytesseract.image_to_string(lat_thresh, config='--psm 7')

        try:
            lon_value = int(''.join(filter(str.isdigit, lon_text)))
            lat_value = int(''.join(filter(str.isdigit, lat_text)))
            return {"Lon": lon_value, "Lat": lat_value}
        except ValueError:
            return None
    else:
        return None