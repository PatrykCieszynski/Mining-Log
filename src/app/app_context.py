from dataclasses import dataclass
from typing import Any, Dict, Optional, cast

from PyQt6.QtCore import QTimer

from .config_loader import load_config
from .signal_bus import SignalBus
from ..chat_logger.log_listener import ChatLogListener
from ..scanner.player_position_scanner import PlayerScanner
from ..services.map_deed_service import DeedMarkerService
from ..services.player_position_service import PlayerPositionService
from ..services.system_event_manager import SystemEventManager
from ..utils.hotkey_scanner_listener import HotkeyScannerListener


@dataclass
class AppContext:
    bus: SignalBus
    config: Dict[str, Any]

    #QObjects
    deed_scanner: HotkeyScannerListener
    player_scanner: PlayerScanner
    chat_listener: ChatLogListener

    #services
    player_position_service: PlayerPositionService
    deed_marker_service: DeedMarkerService
    system_event_manager: SystemEventManager

    #Controllers

    #Timers
    deed_timer: QTimer

    def start_all(self) -> None:
        """Start all scanners/listeners."""
        self.player_scanner.start()
        self.deed_scanner.start()
        self.chat_listener.start()

    def stop_all(self) -> None:
        """Stop all scanners/listeners."""
        self.player_scanner.stop()
        self.deed_scanner.stop()
        self.chat_listener.stop()

def create_app_context(config_path: str = "../../config/default.yaml") -> AppContext:
    config = load_config(config_path)

    # Create a central signal bus
    bus = SignalBus()

    deed_scanner = HotkeyScannerListener(
        bus=bus,
        offset_x=0,
        offset_y=0,
        inner_rect=None,
        debug=False,
        save_dir=None,
        hotkey=config["hotkey_scanner"]["hotkey"],
        cooldown_sec=0.5,
    )

    player_scanner = PlayerScanner(
        bus=bus,
        title_substr=config["game_window"]["title"],
        compass_size=config["compass_ocr"]["compass_size"],
        poll_interval=config["compass_ocr"]["poll_interval"]
    )

    player_position_service = PlayerPositionService(bus, config)
    deed_marker_service = DeedMarkerService(bus, config)
    system_event_manager = SystemEventManager(bus)

    # Timer to refresh deed markers
    deed_timer = QTimer()
    deed_timer.timeout.connect(deed_marker_service.tick_deeds)
    deed_timer.start(1000)  # run every 1s

    chat_listener = ChatLogListener(bus , r"X:\Dokumenty\Entropia Universe\chat.log")

    return AppContext(
        bus=bus,
        config=config,
        deed_scanner=deed_scanner,
        player_scanner=player_scanner,
        chat_listener=chat_listener,
        player_position_service=player_position_service,
        deed_marker_service=deed_marker_service,
        system_event_manager=system_event_manager,
        deed_timer=deed_timer
    )