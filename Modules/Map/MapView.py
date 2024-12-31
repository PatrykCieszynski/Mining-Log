from PyQt5.QtWidgets import QGraphicsView, QLabel

TILE_SIZE = 512  # Tile size is always 512 px

class MapView(QGraphicsView):
    def __init__(self, scene, parent, config):
        super().__init__(scene, parent)
        self.config = config
        self.setMouseTracking(True)  # Włącz śledzenie ruchu myszy
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)  # Zoom w miejscu kursora
        self.setDragMode(QGraphicsView.ScrollHandDrag)  # Możliwość przesuwania mapy
        self.zoom_factor = 1.15  # Współczynnik zoomu

        # Etykieta z koordynatami
        self.coordinates_label = QLabel(self)
        self.coordinates_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 0.5); padding: 5px;")
        self.coordinates_label.setGeometry(10, 10, 100, 50)
        self.coordinates_label.setText("Koordynaty: ")

    def wheelEvent(self, event):
        """Obsługa kółka myszy dla zoomu."""
        # Sprawdzenie kierunku scrolla (zoom in lub zoom out)
        if event.angleDelta().y() > 0:  # Scroll w górę - zoom in
            self.scale(self.zoom_factor, self.zoom_factor)
        elif event.angleDelta().y() < 0:  # Scroll w dół - zoom out
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
        event.accept()  # Zablokowanie standardowego zachowania scrolla

    def mouseMoveEvent(self, event):
        """Obsługa ruchu myszy na widoku."""
        # Pobranie pozycji kursora względem sceny
        cursor_pos = self.mapToScene(event.pos())

        map_width = self.config["tile_count_x"] * TILE_SIZE
        map_height = self.config["tile_count_y"] * TILE_SIZE

        lon = self.config["min_lon"] + (cursor_pos.x() / map_width) * (self.config["max_lon"] - self.config["min_lon"])
        lat = self.config["min_lat"] + ((map_height - cursor_pos.y()) / map_height) * (self.config["max_lat"] - self.config["min_lat"])  # Invert Y-axis

        # Aktualizacja etykiety z koordynatami
        self.coordinates_label.setText(f"Koordynaty:\n Lon: {round(lon, 2)}\n Lat: {round(lat, 2)}")
        super().mouseMoveEvent(event)