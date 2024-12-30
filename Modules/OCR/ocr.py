import pytesseract

def extract_text(image):
    """
    Odczytuje tekst z podanego obrazu za pomocą pytesseract.

    :param image: Obraz jako macierz NumPy.
    :return: Tekst odczytany z obrazu.
    """
    text = pytesseract.image_to_string(image, lang='eng')
    return text

def parse_coordinates(text):
    """
    Przetwarza odczytany tekst i próbuje wyodrębnić koordynaty (x, y).

    :param text: Tekst odczytany z obrazu.
    :return: Krotka (x, y) jeśli udane, w przeciwnym razie None.
    """
    try:
        # Przykład: Koordynaty w formacie "123.45, 678.90"
        x, y = map(float, text.strip().split(","))
        return x, y
    except ValueError:
        # Zwraca None, jeśli format tekstu jest nieprawidłowy
        return None
