from dataclasses import dataclass
from typing import Any, Dict, Optional
from .signal_bus import SignalBus
from ..ChatLogger.log_listener import ChatLogListener
from ..Map.map_deed_controller import DeedMarkerController
from ..Map.player_position_controller import PlayerPositionController
from ..Scanner.player_position_scanner import PlayerScanner
from ..Services.system_event_manager import SystemEventManager
from ..Utils.hotkey_scanner_listener import HotkeyScannerListener


@dataclass
class AppContext:
    bus: SignalBus
    config: Dict[str, Any]

    #QObjects
    deed_scanner: HotkeyScannerListener
    player_scanner: PlayerScanner
    chat_listener: ChatLogListener

    #Services
    system_event_manager: SystemEventManager

    #Controllers
    deed_marker_controller: Optional[DeedMarkerController] = None
    player_position_controller: Optional[PlayerPositionController] = None

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

def create_app_context(config: Dict[str, Any]) -> AppContext:
    # Create a central signal bus and hold config
    bus = SignalBus()

    deed_scanner = HotkeyScannerListener(
        bus=bus,
        offset_x=0,
        offset_y=0,
        inner_rect=None,
        debug=False,
        save_dir=None,
        hotkey="f8",
        cooldown_sec=0.5,
    )

    player_scanner = PlayerScanner(
        bus=bus,
        title_substr="Entropia Universe Client",
        compass_size=(370, 430),
        poll_interval=0.5
    )

    system_event_manager = SystemEventManager(bus)

    chat_listener = ChatLogListener(bus , r"X:\Dokumenty\Entropia Universe\chat.log")

    return AppContext(
        bus=bus,
        config=config,
        deed_scanner=deed_scanner,
        player_scanner=player_scanner,
        chat_listener=chat_listener,
        system_event_manager=system_event_manager
    )