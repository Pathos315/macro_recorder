import logging
import platform
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("macro_recorder")


@dataclass
class Configuration:
    """Configuration for the macro recorder."""

    # Screen dimensions
    screen_width: int = field(default_factory=lambda: DisplayManager.get_screen_width())
    screen_height: int = field(
        default_factory=lambda: DisplayManager.get_screen_height()
    )

    # Mouse movement throttling
    min_move_distance: int = 5
    min_move_time: float = 0.02

    # Double-click detection
    double_click_threshold: float = 0.3
    double_click_distance: int = 5

    # Countdown settings
    countdown_duration: int = 3
    countdown_font: str = "Helvetica"
    countdown_font_size: int = 50
    countdown_background: str = "white"

    # Replay settings
    replay_delay: float = 0.5


class DisplayManager:
    """Manages display-related operations with platform independence."""

    @staticmethod
    def get_screen_width() -> int:
        """Get the screen width, with fallback for headless environments."""
        try:
            import pyautogui

            return pyautogui.size()[0]
        except Exception:
            # Fallback for headless environments
            return 1920

    @staticmethod
    def get_screen_height() -> int:
        """Get the screen height, with fallback for headless environments."""
        try:
            import pyautogui

            return pyautogui.size()[1]
        except Exception:
            # Fallback for headless environments
            return 1080

    @staticmethod
    def set_cursor_position(x: int, y: int) -> None:
        """Set the cursor position in a platform-independent way."""
        if platform.system() == "Windows":
            import ctypes

            ctypes.windll.user32.SetCursorPos(x, y)
        else:
            import pyautogui

            pyautogui.moveTo(x, y)
