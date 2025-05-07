from unittest.mock import patch
import pytest

from src.config import Configuration, DisplayManager


class TestConfiguration:
    def test_default_values(self):
        """Test that Configuration class initializes with expected default values."""
        with patch("src.config.DisplayManager.get_screen_width", return_value=1920):
            with patch(
                "src.config.DisplayManager.get_screen_height", return_value=1080
            ):
                config = Configuration()

                # Check screen dimensions
                assert config.screen_width == 1920
                assert config.screen_height == 1080

                # Check default settings
                assert config.min_move_distance == 5
                assert config.min_move_time == 0.02
                assert config.double_click_threshold == 0.3
                assert config.double_click_distance == 5
                assert config.countdown_duration == 3
                assert config.countdown_font == "Helvetica"
                assert config.countdown_font_size == 50
                assert config.countdown_background == "white"
                assert config.replay_delay == 0.5


class TestDisplayManager:
    def test_get_screen_width(self):
        """Test get_screen_width method."""
        with patch("pyautogui.size", return_value=(1920, 1080)):
            assert DisplayManager.get_screen_width() == 1920

    def test_get_screen_height(self):
        """Test get_screen_height method."""
        with patch("pyautogui.size", return_value=(1920, 1080)):
            assert DisplayManager.get_screen_height() == 1080

    @pytest.mark.skip
    def test_set_cursor_position_windows(self):
        """Test set_cursor_position on Windows platform."""
        with patch("platform.system", return_value="Windows"):
            with patch("ctypes.windll.user32.SetCursorPos") as mock_set_cursor:
                DisplayManager.set_cursor_position(100, 200)
                mock_set_cursor.assert_called_once_with(100, 200)

    def test_set_cursor_position_other(self):
        """Test set_cursor_position on non-Windows platform."""
        with patch("platform.system", return_value="Linux"):
            with patch("pyautogui.moveTo") as mock_move_to:
                DisplayManager.set_cursor_position(100, 200)
                mock_move_to.assert_called_once_with(100, 200)
