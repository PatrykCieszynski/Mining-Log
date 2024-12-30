import mss
import cv2
import numpy as np

def capture_screen(region=None):
    """
    Przechwytuje obraz ekranu z określonego regionu.

    :param region: Słownik określający obszar ekranu, np. {"top": 100, "left": 100, "width": 300, "height": 200}.
                   Jeśli None, przechwytuje cały ekran.
    :return: Przechwycony obraz jako macierz NumPy w odcieniach szarości.
    """
    with mss.mss() as sct:
        if region is None:
            # Jeśli region nie jest podany, przechwytuje cały ekran
            screenshot = sct.grab(sct.monitors[1])
        else:
            # Przechwytuje tylko wybrany region
            screenshot = sct.grab(region)

        # Konwertuje obraz na format NumPy i zmienia na odcienie szarości
        img = np.array(screenshot)
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        return gray_image